import os
import json
import google.protobuf.text_format as text_format
from google.protobuf.json_format import MessageToDict
from pyvis.network import Network
import networkx as nx
from family_tree_pb2 import FamilyTree
from utils_pb2 import Gender

COLOR_PALETTLE = {
    "cream": "#ffeabb",
    "light blue": "#97dde7",
    "light cream": "#e9ebdd",
    "gray": "#222222",
    "black": "#000000",
    "white": "#ffffff",
    "red": "#ff0000",
    "pink": "#f57db3",
}


class FamilyTreeHandler:
    def __init__(self, input_file=None, output_file="family_tree.html"):
        self.family_tree = FamilyTree()
        self.nx_graph = nx.DiGraph()
        self.input_file = input_file
        self.output_file = os.path.realpath(output_file)

    def update_data_source(self, input_file):
        self.input_file = input_file

    def update_output_file(self, output_file):
        self.output_file = output_file

    def load_from_protobuf(self):
        print(f"Loading data from: {self.input_file}")
        try:
            with open(self.input_file, "r") as f:
                text_format.Merge(f.read(), self.family_tree)
                print(f"Successfully loaded {self.input_file}")
        except FileNotFoundError as e:
            print(f"File not found: {e}")
            raise
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise

        # Populate nodes and edges
        self.populate_nodes_and_edges()

    def populate_nodes_and_edges(self):
        # M: <a href="https://www.freeiconspng.com/img/7920" title="Image from freeiconspng.com"><img src="https://www.freeiconspng.com/uploads/male-icon-19.png" width="350" alt="Free Download Vector Png Male" /></a>
        # F: <a href="https://www.freeiconspng.com/img/7875" title="Image from freeiconspng.com"><img src="https://www.freeiconspng.com/uploads/female-icon-4.png" width="350" alt="Female Icons No Attribution" /></a>
        # U: <a href="https://www.freeiconspng.com/img/6525" title="Image from freeiconspng.com"><img src="https://www.freeiconspng.com/uploads/person-head-icon-7.jpg" width="350" alt="person head icon" /></a>
        # F2: <a href="https://www.freeiconspng.com/img/7889" title="Image from freeiconspng.com"><img src="https://www.freeiconspng.com/uploads/businesswoman-female-icon-19.png" width="350" alt="businesswoman female icon" /></a>
        default_images_url = {
            "MALE": "https://www.freeiconspng.com/uploads/male-icon-19.png",
            "FEMALE": "https://www.freeiconspng.com/uploads/businesswoman-female-icon-19.png",
            "OTHER": "https://www.freeiconspng.com/uploads/person-head-icon-7.jpg",
            "UNKNOWN": "https://www.freeiconspng.com/uploads/person-head-icon-7.jpg",
        }
        brokenImage = (
            "https://www.freeiconspng.com/thumbs/no-image-icon/no-image-icon-7.png"
        )
        for member_id, member in self.family_tree.members.items():
            # Confirm that member_id of the tree is same as the member_id field in the node
            assert member_id == member.id

            # Add member to networkx graph
            member_dict = MessageToDict(member, preserving_proto_field_name=True)
            additional_info = member.additional_info
            image_url = additional_info.get("image_url")
            if not image_url:
                # Load the default image based on gender
                image_url = default_images_url[Gender.Name(member.gender)]
            node_options = {
                "label": member.name,
                "title": text_format.MessageToString(member),
                "shape": "circularImage",
                "image": image_url,
                "brokenImage": brokenImage,
                "size": 50,
                "font": {"size": 20},
                "color": COLOR_PALETTLE["light cream"],
            }
            self.nx_graph.add_node(
                member_id,
                **node_options,
            )

        for member_id, relationships in self.family_tree.relationships.items():
            # Add edges between spouses
            for spouse_id in relationships.spouse_ids:
                self.nx_graph.add_edge(
                    member_id, spouse_id, color=COLOR_PALETTLE["pink"]
                )

            # Add edges between parents and children
            for child_id in relationships.children_ids:
                self.nx_graph.add_edge(member_id, child_id)

    def display_family_tree(self):
        pyvis_network_graph = Network(
            directed=True,
            notebook=False,
            bgcolor=COLOR_PALETTLE["gray"],
            font_color=COLOR_PALETTLE["white"],
            height="1000px",  # Increased the height of the canvas
            width="100%",  # Increased the width of the canvas
        )
        pyvis_network_graph.from_nx(self.nx_graph)

        # Define options for the network graph
        options = {
            "physics": {
                "barnesHut": {
                    "gravitationalConstant": -4000,  # Increased repulsion
                    "centralGravity": 0.2,  # Reduced central gravity
                    "springLength": 250,  # Increased spring length
                    "springConstant": 0.05,
                    "damping": 0.09,
                    "avoidOverlap": 1,  # Added avoid overlap
                    "nodeDistance": 300,  # Increased node distance
                },
                "minVelocity": 0.75,
            },
            "interaction": {"hover": True},
        }

        # Set the options for the network graph
        pyvis_network_graph.set_options(json.dumps(options))

        # Enable the UI buttons
        # pyvis_network_graph.show_buttons(filter_=["physics"])

        # Generate the HTML file
        print(f"Saving family tree to: {self.output_file}")
        pyvis_network_graph.show(self.output_file, notebook=False)

    def find_person(self):
        person_name = input("Enter the name of the person to find: ")
        person_found = False
        for member_id, member in self.family_tree.members.items():
            if member.name.lower() == person_name.lower():
                person_found = True
                print(f"Person '{person_name}' found in the family tree.")
                self.print_member_details(member_id)
        if not person_found:
            print(f"Person '{person_name}' not found in the family tree.")

    def print_member_details(self, member_id):
        member = self.family_tree.members[member_id]
        print(member)

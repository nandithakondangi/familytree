import os
import json
import google.protobuf.text_format as text_format
from google.protobuf.json_format import MessageToDict
from pyvis.network import Network
import networkx as nx
import shutil
import pkg_resources
import proto.family_tree_pb2 as family_tree_pb2
import proto.utils_pb2 as utils_pb2
import pathlib
import random
import string

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


def get_vis_js_resource(file_path):
    # Copy vis.js to the output directory
    vis_js_resource = "vis-network.min.js"

    parent_dir = os.path.dirname(file_path)
    vis_js_destination = os.path.join(parent_dir, vis_js_resource)
    os.makedirs(parent_dir, exist_ok=True)

    if vis_js_resource in os.listdir(parent_dir):
        return

    try:
        # Use pkg_resources to find the vis-network.min.js file
        pyvis_path = pkg_resources.resource_filename("pyvis", "")
        # As this need not be present in the package directory itself
        resource_files_generator = pathlib.Path(pyvis_path).rglob(vis_js_resource)
        resource_files_list = [str(file) for file in resource_files_generator]
        # Pick the last file
        vis_js_source = resource_files_list[-1]
    except ImportError:
        print(f"Error: Could not find {vis_js_resource} in pyvis package.")
        return

    shutil.copy2(vis_js_source, vis_js_destination)
    print(f"Copied vis.js to the {parent_dir} directory.")


class FamilyTreeHandler:
    def __init__(
        self,
        input_file=None,
        output_file="family_tree.html",
        output_data_file="output_family_tree.txtpb",
    ):
        self.family_tree = family_tree_pb2.FamilyTree()
        self.nx_graph = nx.DiGraph()
        self.input_file = input_file
        self.output_file = os.path.realpath(output_file)
        self.output_proto_data_file = os.path.realpath(output_data_file)
        self.used_member_ids = set()  # Keep track of used IDs.
        # FIXME: Re-think if we need used_member_ids, or if we can simply rely on self.family_tree.members.keys
        # The second option is hashable. But it doesn't easily account for the case where there is a mismatch between
        # tree's key as an ID and member.id.

    def update_data_source(self, input_file):
        self.input_file = input_file

    def update_output_html_file(self, output_file):
        self.output_file = output_file

    def update_output_data_file(self, output_data_file):
        self.output_proto_data_file = output_data_file

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
        # Update the set of used member IDs after loading
        self.update_used_member_ids()

    def get_default_images(self):
        """
        # Source image links
        # M: <a href="https://www.freeiconspng.com/img/7920" title="Image from freeiconspng.com"><img src="https://www.freeiconspng.com/uploads/male-icon-19.png" width="350" alt="Free Download Vector Png Male" /></a>
        # F: <a href="https://www.freeiconspng.com/img/7875" title="Image from freeiconspng.com"><img src="https://www.freeiconspng.com/uploads/female-icon-4.png" width="350" alt="Female Icons No Attribution" /></a>
        # U: <a href="https://www.freeiconspng.com/img/6525" title="Image from freeiconspng.com"><img src="https://www.freeiconspng.com/uploads/person-head-icon-7.jpg" width="350" alt="person head icon" /></a>
        # F2: <a href="https://www.freeiconspng.com/img/7889" title="Image from freeiconspng.com"><img src="https://www.freeiconspng.com/uploads/businesswoman-female-icon-19.png" width="350" alt="businesswoman female icon" /></a>
        default_images_url = {
            "MALE": "https://www.freeiconspng.com/uploads/male-icon-19.png",
            "FEMALE": "https://www.freeiconspng.com/uploads/businesswoman-female-icon-19.png",
            "OTHER": "https://www.freeiconspng.com/uploads/person-head-icon-7.jpg",
            "GENDER_UNKNOWN": "https://www.freeiconspng.com/uploads/person-head-icon-7.jpg",
        }
        brokenImage = (
            "https://www.freeiconspng.com/thumbs/no-image-icon/no-image-icon-7.png"
        )"
        """
        images = os.path.abspath(f"{os.path.dirname(__file__)}/../resources")

        default_images = {
            "MALE": f"{images}/male.png",
            "FEMALE": f"{images}/female.png",
            "OTHER": f"{images}/person.png",
            "UNKNOWN": f"{images}/person.png",
        }
        brokenImage = f"{images}/broken.gif"
        return default_images, brokenImage

    def generate_member_id(self):
        """Generates a unique random 4-character alphanumeric member ID."""
        while True:
            member_id = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=4)
            )
            if member_id not in self.used_member_ids:
                self.used_member_ids.add(member_id)
                return member_id

    def create_node(self, input_dict):
        """Creates a new FamilyMember node and adds it to the family tree."""
        member_id = self.generate_member_id()
        member = family_tree_pb2.FamilyMember()
        member.id = member_id
        member.name = input_dict.get("name")
        member.nicknames.extend(
            list(map(str.strip, input_dict.get("nicknames").split(",")))
        )
        member.gender = input_dict.get("gender")
        if "dob_date" in input_dict:
            member.date_of_birth.date = input_dict.get("dob_date")
            member.date_of_birth.month = input_dict.get("dob_month")
            member.date_of_birth.year = input_dict.get("dob_year")

        # Proto expects to store these as integers
        member.traditional_date_of_birth.month = utils_pb2.TamilMonth.Value(
            input_dict.get("dob_traditional_month")
        )
        member.traditional_date_of_birth.star = utils_pb2.TamilStar.Value(
            input_dict.get("dob_traditional_star")
        )
        member.alive = input_dict.get("IsAlive")
        if not member.alive:
            member.date_of_death.date = input_dict.get("dod_date")
            member.date_of_death.month = input_dict.get("dod_month")
            member.date_of_death.year = input_dict.get("dod_year")
            # Proto expects to store these as integers
            member.traditional_date_of_death.month = utils_pb2.TamilMonth.Value(
                input_dict.get("dod_traditional_month")
            )
            member.traditional_date_of_death.paksham = utils_pb2.Paksham.Value(
                input_dict.get("dod_traditional_paksham")
            )
            member.traditional_date_of_death.thithi = utils_pb2.Thithi.Value(
                input_dict.get("dod_traditional_thithi")
            )

        self.family_tree.members[member_id].CopyFrom(member)
        self.add_node_from_proto_object(member)
        print(f"Created node with ID: {member_id}, Name: {input_dict.get('name')}")

    def add_node_from_proto_object(self, member: family_tree_pb2.FamilyMember):
        member_id = member.id
        default_images, brokenImage = self.get_default_images()
        additional_info = member.additional_info
        image_location = additional_info.get("image_location")
        if not image_location:
            # Load the default image based on gender
            image_location = default_images[utils_pb2.Gender.Name(member.gender)]
        node_options = {
            "label": member.name,
            "title": text_format.MessageToString(member),
            "shape": "circularImage",
            "image": image_location,
            "brokenImage": brokenImage,
            "size": 50,
            "font": {"size": 20},
            "color": COLOR_PALETTLE["light cream"],
        }
        get_vis_js_resource(image_location)
        self.nx_graph.add_node(
            member_id,
            **node_options,
        )

    def add_spouse_edges(self, member_id, spouse_id):
        self.nx_graph.add_edge(
            member_id, spouse_id, color=COLOR_PALETTLE["pink"], weight=0
        )
        self.nx_graph.add_edge(
            spouse_id, member_id, color=COLOR_PALETTLE["pink"], weight=0
        )

    def add_child_edges(self, member_id, child_id):
        self.nx_graph.add_edge(member_id, child_id, weight=1)
        # FIXME: Add future functionality to track parent with weight=-1 and filter that during pyvis rendering

    def populate_nodes_and_edges(self):
        for member_id_in_tree, member in self.family_tree.members.items():
            self.add_node_from_proto_object(member)

        for member_id, relationships in self.family_tree.relationships.items():
            # Add edges between spouses
            for spouse_id in relationships.spouse_ids:
                self.add_spouse_edges(member_id, spouse_id)

            # Add edges between parents and children
            for child_id in relationships.children_ids:
                self.add_child_edges(member_id, child_id)

    def update_used_member_ids(self):
        """Updates the set of used member IDs after loading from protobuf."""
        self.used_member_ids.update(self.family_tree.members.keys())

    def merge_another_tree(
        self, new_tree: family_tree_pb2.FamilyTree, connecting_member_id=None
    ):
        pass

    def display_family_tree(self):
        pyvis_network_graph = Network(
            directed=True,
            notebook=False,
            bgcolor=COLOR_PALETTLE["gray"],
            font_color=COLOR_PALETTLE["white"],
            cdn_resources="in_line",
            height="1000px",  # Increased the height of the canvas
            width="100%",  # Increased the width of the canvas
        )
        pyvis_network_graph.from_nx(self.nx_graph)
        """
        # Define options for the network graph
        options = {
            "physics": {
                "barnesHut": {
                    "gravitationalConstant": -4000,  # Increased repulsion
                    "centralGravity": 0.2,  # Reduced central gravity
                    "springLength": 50,  # Increased spring length
                    "springConstant": 0.05,
                    "damping": 0.09,
                    "avoidOverlap": 1,  # Added avoid overlap
                },
                "minVelocity": 0.75,
            },
            "interaction": {"hover": True},
        }"
        """
        # Define options for the network graph
        options = {
            "physics": {
                "barnesHut": {
                    "gravitationalConstant": -8000,  # Increased repulsion further
                    "centralGravity": 0.1,  # Reduced central gravity further
                    "springLength": 100,  # Increased spring length further
                    "springConstant": 0.04,  # Slightly decreased spring constant
                    "damping": 0.2,  # Increased damping
                    "avoidOverlap": 1,  # Added avoid overlap
                },
                "minVelocity": 0.5,  # Reduced min velocity
                "solver": "barnesHut",  # Explicitly set the solver
            },
            "interaction": {"hover": True},
        }

        # Set the options for the network graph
        pyvis_network_graph.set_options(json.dumps(options))

        # Enable the UI buttons
        # pyvis_network_graph.show_buttons(filter_=["physics"])

        # Get vs js resource to current directory:
        get_vis_js_resource(self.output_file)

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

    def save_to_protobuf(self):
        with open(self.output_proto_data_file, "w") as f:
            f.write(text_format.MessageToString(self.family_tree))
            print(f"Successfully saved {self.output_proto_data_file}")

    def get_member_fields_from_proto_schema(self):
        # Get the names of FamilyMember from proto schema progrmmatically
        family_member_descriptor = self.family_tree.members.DESCRIPTOR.fields_by_name[
            "value"
        ].message_type
        field_names = [field.name for field in family_member_descriptor.fields]
        return field_names

    def get_enum_values_from_proto_schema(self, enum_name, proto_module=utils_pb2):
        # Get the valid options for a given enum from utils.proto
        """
        Retrieves the valid values for a given enum from the protobuf schema.

        Args:
            enum_name (str): The name of the enum (e.g., "Gender").

        Returns:
            list: A list of strings representing the valid enum values, or None if the enum is not found.
        """
        try:
            # Dynamically get the enum from the utils_pb2 module
            enum_type = getattr(proto_module, enum_name)
            enum_values = enum_type.DESCRIPTOR.values
            # Get the enum values
            valid_values = [value.name for value in enum_values]
            return valid_values
        except AttributeError:
            print(f"Error: Enum '{enum_name}' not found in {proto_module}.")
            return None

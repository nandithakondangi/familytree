import os
import google.protobuf.text_format as text_format
from google.protobuf.json_format import MessageToDict
from pyvis.network import Network
import networkx as nx
from family_tree_pb2 import FamilyTree


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
        for member_id, member in self.family_tree.members.items():
            # Confirm that member_id of the tree is same as the member_id field in the node
            assert member_id == member.id

            # Add member to networkx graph
            member_dict = MessageToDict(member)
            self.nx_graph.add_node(
                member_id,
                label=member.name,
                title=text_format.MessageToString(member),
                shape="ellipse",
                font={"size": 20},
                **member_dict,
            )

        for member_id, relationships in self.family_tree.relationships.items():
            # Add edges between spouses
            for spouse_id in relationships.spouse_ids:
                self.nx_graph.add_edge(member_id, spouse_id, color="red")

            # Add edges between parents and children
            for child_id in relationships.children_ids:
                self.nx_graph.add_edge(member_id, child_id)

    def display_family_tree(self):
        pyvis_network_graph = Network(directed=True)
        pyvis_network_graph.from_nx(self.nx_graph)
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

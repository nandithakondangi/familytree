import os
from family_tree_pb2 import FamilyTree
import google.protobuf.text_format as text_format
from google.protobuf.json_format import MessageToDict
from pyvis.network import Network
import networkx as nx

class FamilyTreeHandler:
    def __init__(self):
        self.family_tree = FamilyTree()
        self.nx_graph = nx.DiGraph()
        self.menu_options = {
            "1": "Display family tree",
            "2": "Find person",
            "3": "Exit",
        }

    def load_from_protobuf(self, file_path):
        print(f"Loading data from: {file_path}")
        try:
            with open(file_path, "r") as f:
                text_format.Merge(f.read(), self.family_tree)
                print(f"Successfully loaded {file_path}")
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
            self.nx_graph.add_node(node_for_adding=member_id, label=member.name, title=text_format.MessageToString(member),**member_dict)

        for member_id, relationships in self.family_tree.relationships.items():
            # Add edges between spouses
            for spouse_id in relationships.spouse_ids:
                self.nx_graph.add_edge(member_id, spouse_id, color='red')

            # Add edges between parents and children
            for child_id in relationships.children_ids:
                self.nx_graph.add_edge(member_id, child_id)
        
    def display_menu(self):
        while True:
            print("Menu:")
            for key, value in self.menu_options.items():
                print(f"{key}: {value}")
            choice = input("Enter your choice: ")
            if choice == "1":
                self.display_family_tree(f"{os.environ.get('BUILD_WORKING_DIRECTORY')}/outputs/family_tree.html")
            elif choice == "2":
                self.find_person()
            elif choice == "3":
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please try again.")

    def display_family_tree(self, output_file):
        pyvis_network_graph = Network(directed=True)
        pyvis_network_graph.from_nx(self.nx_graph)
        # Generate the HTML file
        pyvis_network_graph.show(output_file, notebook=False)

    def find_person(self):
        person_name = input("Enter the name of the person to find: ")
        person_found = False
        for member_id, member in self.family_tree.members.items():
            if member.name.lower() == person_name.lower():
                person_found = True
                self.print_member_details(member_id)
        if not person_found:
            print(f"Person '{person_name}' not found in the family tree.")

    def print_member_details(self, member_id):
        member = self.family_tree.members[member_id]
        print(member)

if __name__ == "__main__":
    family_tree_handler = FamilyTreeHandler()
    working_directory = os.environ.get("BUILD_WORKING_DIRECTORY")
    input_file = f"{working_directory}/input_data/sample_data.txtpb"
    family_tree_handler.load_from_protobuf(file_path=input_file)
    family_tree_handler.display_menu()


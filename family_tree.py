#!/usr/bin/env python

import os
import networkx as nx
import matplotlib.pyplot as plt

# Import the generated protobuf code
from family_tree_proto import FamilyMember, Relationships, FamilyUnit, FamilyTree
from utils_proto import EnglishDate, TraditionalDate, TamilMonth, TamilStar, Paksham, Thithi

class Node:
    def __init__(self, name, **kwargs):
        self.name = name
        self.data = kwargs  # Store custom fields as a dictionary
        self.children = []
        self.parent = None

    def add_child(self, child):
        self.children.append(child)
        child.parent = self #Sets the parent attribute of the child.

    def __str__(self):
        return self.name
    
    def get_all_attributes(self):
        """Return all node attributes including name, parent and data"""
        all_attributes = {
            "name": self.name,
            "parent": str(self.parent) if self.parent else "None",
        }
        all_attributes.update(self.data) # Add custom data
        return all_attributes
    
    def delete_node(self, target_name):
        """Delete a node and its children. Does not delete self"""
        for child in self.children:
            if child.name == target_name:
                self.children.remove(child)
                print(f"Node '{target_name}' and its children deleted.")
                return
            child.delete_node(target_name) #Recursive call

class FamilyTree:
    def __init__(self):
        self.root = None
        self.nodes = {}  # Dictionary to quickly find nodes by name
        self.family_tree = FamilyTree() #Initialise the protobuf FamilyTree object.

    def add_node(self, parent_name=None, name=None, **kwargs):
        # ... (The logic for add_node is changed) ...
        if name is None:
            name = input("Enter the name of the person: ")

        if name in self.nodes:
            print(f"Error: A person named '{name}' already exists in the tree.")
            return

        # Create the protobuf FamilyMember
        new_member = FamilyMember()
        new_member.name = name
        
        # Add custom data to additional_info
        for key, value in kwargs.items():
            new_member.additional_info[key] = value
        
        # Add member to the family tree
        self.family_tree.members[new_member.id].CopyFrom(new_member)

        new_node = Node(name, **kwargs)
        self.nodes[name] = new_node

        if parent_name:
            parent_node = self.nodes.get(parent_name)
            if parent_node:
                parent_node.add_child(new_node)
            else:
                print(f"Error: Parent '{parent_name}' not found in the tree.")
        elif not self.root:
            self.root = new_node
        else:
            print("Error: Can't add node to the top level as a root node exists.")
    
    def save_to_protobuf(self, file_path):
        """Saves the family tree data to a protobuf file."""
        
        with open(file_path, "wb") as f:
            f.write(self.family_tree.SerializeToString())

        print(f"Family tree saved to '{file_path}'.")

    def load_from_protobuf(self, file_path):
        """Load family tree data from a protobuf file."""
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' not found.")
            return

        with open(file_path, "rb") as f:
            self.family_tree.ParseFromString(f.read())

        # Clear the current tree
        self.root = None
        self.nodes = {}

        for id, member_proto in self.family_tree.members.items():
            self.add_node(name=member_proto.name, **member_proto.additional_info)

        print(f"Family tree loaded from '{file_path}'.")

    def delete_node(self, node_name):
        """Delete a node from the tree by name."""
        if node_name not in self.nodes:
            print(f"Error: Node '{node_name}' not found.")
            return
        
        node_to_delete = self.nodes[node_name]
        if node_to_delete == self.root:
            print(f"Error: You can't delete the root node '{node_name}'.")
            return
            
        # Remove the node from parent's children
        parent = node_to_delete.parent
        if parent:
            parent.delete_node(node_name) #This will handle removing all of the children of the node as well.
        del self.nodes[node_name] #Delete the node from the lookup table.
        print(f"Node {node_name} deleted")

    def view_graph(self):
        if not self.root:
            print("The family tree is empty.")
            return

        graph = nx.DiGraph() #Creates a new graph using the networkx library.

        def add_nodes_edges(node, graph):
            graph.add_node(node.name, **node.get_all_attributes()) #Add node and its attributes
            for child in node.children:
                graph.add_edge(node.name, child.name)
                add_nodes_edges(child, graph)

        add_nodes_edges(self.root, graph)

        pos = nx.spring_layout(graph)
        nx.draw(graph, pos, with_labels=True, node_size=1500, node_color="skyblue", font_size=10, font_weight="bold", arrows=True)
        nx.draw_networkx_edge_labels(graph, pos, edge_labels={(u,v):"" for u,v in graph.edges()}) #Removed edge label, as it is not relevant here.
        plt.title("Family Tree")

        # Adding the attributes to the nodes.
        node_labels = {node: "\n".join([f"{key}: {value}" for key, value in data.items()])
                   for node, data in graph.nodes(data=True)}
        nx.draw_networkx_labels(graph, pos, labels=node_labels, font_size=8)
        #plt.show()
        # Save the figure to a file
        plt.savefig("family_tree.png")  # Or any other file name and format you want
        print("Family tree graph saved to family_tree.png")
        plt.close() # Closes the plot to free up resources


    def display_menu(self):
        while True:
            print("\nFamily Tree Menu:")
            print("1. Add a node")
            print("2. View the graph")
            print("3. Delete a node")
            print("4. Load from Protobuf")
            print("5. Save to Protobuf")
            print("6. Exit")

            choice = input("Enter your choice: ")

            if choice == '1':
                parent_name = input("Enter the name of the parent (leave blank for root): ")
                name = input("Enter the name of the person: ")
                other_info = input("Enter the custom data for the person in key=value pairs (e.g. DOB=1990-01-01,Location=London):")
                data = {}
                if other_info:
                    for pair in other_info.split(','):
                        key, value = pair.split("=")
                        data[key.strip()] = value.strip()

                self.add_node(parent_name, name, **data)
            elif choice == '2':
                self.view_graph()
            elif choice == '3':
                node_name = input("Enter the name of the node to delete: ")
                self.delete_node(node_name)
            elif choice == "4":
                file_path = input("Enter the path to the Protobuf file: ")
                self.load_from_protobuf(file_path)
            elif choice == "5":
                file_path = input("Enter the path to save the Protobuf file: ")
                self.save_to_protobuf(file_path)
            elif choice == '6':
                print("Exiting the program.")
                break
            else:
                print("Invalid choice. Please try again.")


# Example usage (you can expand this to a menu-driven system)
if __name__ == "__main__":
    family_tree = FamilyTree()
    family_tree.display_menu()

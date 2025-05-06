import logging
import os

from graph_handler import GraphHandler
from proto_handler import ProtoHandler

import proto.family_tree_pb2 as family_tree_pb2

# Get a logger instance for this module
logger = logging.getLogger(__name__)  # Added
logger.setLevel(logging.INFO)


class FamilyTreeHandler:
    def __init__(
        self,
        temp_dir_path,
        input_text_file=None,
        output_html_file=None,
        output_data_file=None,
    ):
        self.input_text_file = input_text_file

        if not output_html_file:
            if not temp_dir_path:
                raise Exception("Provide either temp_dir_path or output_html_file")
            output_html_file = os.path.join(temp_dir_path, "family_tree.html")
        else:
            output_html_file = output_html_file

        if not output_data_file:
            if not temp_dir_path:
                raise Exception("Provide either temp_dir_path or output_data_file")
            output_proto_data_file = os.path.join(
                temp_dir_path, "family_tree_data.txtpb"
            )
        else:
            output_proto_data_file = output_data_file
        self.proto_handler_instance = ProtoHandler(
            input_text_file, output_proto_data_file
        )
        self.graph_handler_instance = GraphHandler(output_html_file)

    def create_member(self, input_dict: dict) -> bool:
        successful = False
        logger.info(f"Attempting to add member with data: {input_dict}")
        new_empty_member = self.proto_handler_instance.generate_new_member()
        validated_proto_member, error_message = (
            self.proto_handler_instance.create_proto_member_from_dict(
                input_dict, new_empty_member
            )
        )
        if error_message:
            raise Exception(error_message)
        successful = self._add_member_to_protoobj_and_graphobj(validated_proto_member)
        if successful:
            member_id, name = self.proto_handler_instance.get_member_identifiers(
                validated_proto_member
            )
            logger.info(
                f"Successfully added member {member_id} ('{name}') in prototree and graph."
            )
        return successful

    def update_member(self, member_id: str, input_dict: dict):
        successful = False
        logger.info(f"Attempting to update member {member_id} with data: {input_dict}")
        existing_member = self.proto_handler_instance.query_proto_member_by_id(
            member_id
        )
        if not existing_member:
            raise Exception(f"Cannot update: Member with ID '{member_id}' not found.")

        validated_proto_member, error_message = (
            self.proto_handler_instance.create_proto_member_from_dict(
                input_dict, existing_member
            )
        )
        if error_message:
            raise Exception(error_message)
        successful = self._update_member_to_protoobj_and_graphobj(
            validated_proto_member
        )
        if successful:
            member_id, name = self.proto_handler_instance.get_member_identifiers(
                validated_proto_member
            )
            logging.info(
                f"Successfully updated member {member_id} ('{name}') in prototree and graph."
            )
        return successful

    # FIXME: we are not adding relations yet

    def delete_member(self):
        pass

    def clear(self):
        logger.info("Clearing any old data before loading new data.")
        self.proto_handler_instance.family_tree.Clear()
        self.graph_handler_instance.nx_graph.clear()

    def load_from_text_file(self):
        logger.info("Loading data from text file")
        self.clear()
        self.proto_handler_instance.load_from_protobuf()
        self._add_familytree_members_to_graph()

    @property
    def get_output_html_file(self):
        return self.graph_handler_instance.output_html_file

    @property
    def get_output_data_file(self):
        return self.proto_handler_instance.output_proto_data_file

    @property
    def get_input_text_file(self):
        return self.proto_handler_instance.input_text_file

    # Pass through method

    def query_member(self, member_id: str):
        return self.proto_handler_instance.query_proto_member_by_id(member_id)

    # Pass through method
    def get_members(self):
        return self.proto_handler_instance.get_family_members()

    # Pass through method
    def get_member_ids(self):
        return self.proto_handler_instance.get_family_member_ids()

    # Pass through method
    def display_tree(self):
        self.graph_handler_instance.display_family_tree()

    # Pass through method
    def save_to_text_file(self):
        self.proto_handler_instance.save_to_protobuf()

    # Pass through method
    def update_data_source(self, input_text_file):
        self.proto_handler_instance.update_data_source(input_text_file)

    # Pass through method
    def update_output_data_file(self, output_data_file):
        self.proto_handler_instance.update_output_data_file(output_data_file)

    # Pass through method
    def get_context_about_this_family(self) -> str:
        """Generates a textual summary of the family tree for the prompt."""
        return self.graph_handler_instance.get_graph_summary_text()

    def _add_familytree_members_to_graph(self):
        logger.info("Populating graph nodes...")
        # Use list comprehension for potentially slightly better performance if tree is large
        family_tree = self.proto_handler_instance.family_tree
        members_to_process = list(family_tree.members.items())

        for member_id_in_tree, member in members_to_process:
            # Ensure consistency between map key and member.id
            actual_member_id = member.id
            if not actual_member_id:
                logger.warning(
                    f"Skipping member with key '{member_id_in_tree}' due to missing member.id."
                )
                continue
            if member_id_in_tree != actual_member_id:
                logger.warning(
                    f"Mismatch between map key '{member_id_in_tree}' and member.id '{actual_member_id}'. Using member.id."
                )
                # Consider if the key in the map should be corrected if possible, or just log

            # Check if member object itself is valid before adding node
            if member.IsInitialized():
                attributes_dict = (
                    self.proto_handler_instance.prepare_node_attributes_for_member(
                        member
                    )
                )
                self.graph_handler_instance.add_node_in_graph(
                    member_id=attributes_dict.get("ID"),
                    final_image_path=attributes_dict.get("NodeImagePath"),
                    member_name=attributes_dict.get("Name"),
                    title_str=attributes_dict.get("Title"),
                    brokenImage=attributes_dict.get("BrokenImage"),
                )
            else:
                # This might indicate an issue during protobuf parsing or creation
                logger.warning(
                    f"Skipping uninitialized member with ID {actual_member_id}."
                )

        logger.info("Populating graph edges...")
        # Use list comprehension for potentially slightly better performance
        relationships_to_process = list(family_tree.relationships.items())

        for member_id, relationships in relationships_to_process:
            # Ensure the member_id for relationships exists as a node
            if member_id not in self.graph_handler_instance.nx_graph:
                logger.warning(
                    f"Skipping relationships for non-existent member ID: {member_id}"
                )
                continue

            # Add edges between spouses
            for spouse_id in relationships.spouse_ids:
                if member_id == spouse_id:
                    continue  # Skip self-loops
                if spouse_id in self.graph_handler_instance.nx_graph:
                    # Add edge only if the reverse doesn't exist to represent undirected marriage link
                    if not self.graph_handler_instance.nx_graph.has_edge(
                        spouse_id, member_id
                    ):
                        self.graph_handler_instance.add_spouse_edges(
                            member_id, spouse_id
                        )
                    # Always call add_spouse_edges if spouse exists
                    # self.add_spouse_edges(member_id, spouse_id)
                else:
                    logger.warning(
                        f"Spouse ID {spouse_id} not found for member {member_id}. Skipping edge."
                    )

            # Add edges between parents and children
            for child_id in relationships.children_ids:
                if member_id == child_id:
                    continue  # Skip self-loops
                if child_id in self.graph_handler_instance.nx_graph:
                    # Only add if the parent->child edge doesn't already exist
                    # FIXME: We are not checking for child->parent edges though. Think about this.
                    parent_to_child_edge_exists = (
                        self.graph_handler_instance.nx_graph.has_edge(
                            member_id, child_id
                        )
                    )
                    child_to_parent_edge_exists = (
                        self.graph_handler_instance.nx_graph.has_edge(
                            child_id, member_id
                        )
                    )
                    if (
                        not parent_to_child_edge_exists
                        and not child_to_parent_edge_exists
                    ):
                        self.graph_handler_instance.add_child_edges(
                            parent_id=member_id, child_id=child_id
                        )
                    elif parent_to_child_edge_exists ^ child_to_parent_edge_exists:
                        logger.error(
                            "There was already a unidirectional edge. This should not happen."
                        )
                else:
                    logger.warning(
                        f"Child ID {child_id} not found for parent {member_id}. Skipping edge."
                    )

    def _add_member_to_protoobj_and_graphobj(
        self, member_proto: family_tree_pb2.FamilyMember
    ) -> bool:
        """
        Adds member proto into the main family tree
        and the NetworkX graph.

        Args:
            member_proto: The validated FamilyMember object.

        Returns:
            bool: True on success, flase on failure.
        """

        try:
            # Add member to protoobj
            self.proto_handler_instance.add_member_to_proto_tree(member_proto)

            # Add/Update in the NetworkX graph
            attributes_dict = (
                self.proto_handler_instance.prepare_node_attributes_for_member(
                    member_proto
                )
            )
            self.graph_handler_instance.add_node_in_graph(
                member_id=attributes_dict.get("ID"),
                final_image_path=attributes_dict.get("NodeImagePath"),
                member_name=attributes_dict.get("Name"),
                title_str=attributes_dict.get("Title"),
                brokenImage=attributes_dict.get("BrokenImage"),
            )
            return True

        except Exception as e:
            logger.exception(f"Unexpected error adding member to prototree, graph: {e}")
            # Attempt to roll back if needed (complex, might leave inconsistent state)
            # For simplicity, we just report the error.
            return False

    def _update_member_to_protoobj_and_graphobj(
        self, member_proto: family_tree_pb2.FamilyMember
    ) -> bool:
        """
        Adds or updates a validated member proto into the main family tree
        and the NetworkX graph.

        Args:
            member_proto: The validated FamilyMember object.

        Returns:
            bool - True on success, false on failure.
        """

        try:
            # Update in the main protobuf structure
            # This will also update as it is a dictionary overwrite
            self.proto_handler_instance.add_member_to_proto_tree(member_proto)

            # Update in the NetworkX graph
            attributes_dict = (
                self.proto_handler_instance.prepare_node_attributes_for_member(
                    member_proto
                )
            )
            self.graph_handler_instance.add_node_in_graph(
                member_id=attributes_dict.get("ID"),
                final_image_path=attributes_dict.get("NodeImagePath"),
                member_name=attributes_dict.get("Name"),
                title_str=attributes_dict.get("Title"),
                brokenImage=attributes_dict.get("BrokenImage"),
            )
            return True
        except Exception as e:
            logger.exception(f"Unexpected error updating member to tree/graph: {e}")
            # Attempt to roll back if needed (complex, might leave inconsistent state)
            # For simplicity, we just report the error.
            return False

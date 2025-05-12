import logging
import os
import random
import string

from google.protobuf import text_format
from google.protobuf.json_format import MessageToDict
from utils import DateUtility, ResourceUtility

import proto.family_tree_pb2 as family_tree_pb2
import proto.utils_pb2 as utils_pb2

# Get a logger instance for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ProtoHandler:
    """
    Utility class for handling protobuf operations.
    """

    def __init__(self, input_text_file=None, output_data_file=None):
        self.family_tree = family_tree_pb2.FamilyTree()
        self.input_text_file = input_text_file
        self.output_proto_data_file = output_data_file
        self.message_to_propagate = ""

    def update_data_source(self, input_text_file):
        self.input_text_file = input_text_file

    def update_output_data_file(self, output_data_file):
        self.output_proto_data_file = output_data_file

    def load_from_protobuf(self):
        # logger is now defined at module level
        logger.debug(f"Loading data from: {self.input_text_file}")
        try:
            # Ensure file exists before opening
            if not self.input_text_file or not os.path.exists(self.input_text_file):
                raise FileNotFoundError(
                    f"Input file not specified or not found: {self.input_text_file}"
                )

            with open(self.input_text_file, "r", encoding="utf-8") as f:
                text_format.Merge(f.read(), self.family_tree)
                logger.info(f"Successfully loaded {self.input_text_file}")
        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            raise  # Re-raise for GUI to handle
        except text_format.ParseError as e:
            logger.error(
                f"Error parsing protobuf text file {self.input_text_file}: {e}"
            )
            raise  # Re-raise for GUI
        except Exception as e:
            logger.exception(f"An unexpected error occurred during loading: {e}")
            raise  # Re-raise for GUI

    def save_to_protobuf(self):
        # Ensure the output directory exists
        output_dir = os.path.dirname(self.output_proto_data_file)
        try:
            os.makedirs(output_dir, exist_ok=True)
        except OSError as e:
            logger.error(f"Error creating output directory {output_dir}: {e}")
            raise IOError(f"Cannot create output directory for saving: {e}") from e
        try:
            protobuf_string = text_format.MessageToString(
                self.family_tree, as_utf8=True
            )
            with open(self.output_proto_data_file, "w", encoding="utf-8") as f:
                f.write(protobuf_string)
                logger.info(f"Successfully saved data to {self.output_proto_data_file}")
        except IOError as e:
            logger.error(
                f"Error writing protobuf data to file {self.output_proto_data_file}: {e}"
            )
            # Optionally wrap IOError too, or keep as is if specific handling is needed
            raise IOError(
                f"Error writing protobuf data to file {self.output_proto_data_file}: {e}"
            ) from e
        except Exception as e:
            # Log the original exception details
            log_message = f"An unexpected error occurred during saving: {e}"
            logger.exception(log_message)

            # Raise a NEW, more informative exception, linking the original 'e' as the cause
            raise Exception(log_message) from e  # <--- MODIFIED LINE

    def query_proto_member_by_id(self, member_id: str):
        return self.family_tree.members.get(str(member_id), None)

    def get_family_members(self) -> family_tree_pb2.FamilyMember:
        return self.family_tree.members.values()

    def get_family_member_ids(self) -> list:
        return [str(key) for key in self.family_tree.members.keys()]

    def get_member_identifiers(self, member_proto: family_tree_pb2.FamilyMember):
        """Returns the main identifiers like ID and name"""
        return str(member_proto.id), member_proto.name

    def get_children_ids_of_member(self, member_id: str) -> list[str]:
        """Returns a list of children IDs for a given member."""
        children_ids_list = []
        if member_id in self.family_tree.relationships:
            # self.family_tree.relationships[member_id].children_ids is a RepeatedScalarContainer
            for child_id_proto in self.family_tree.relationships[
                member_id
            ].children_ids:
                children_ids_list.append(str(child_id_proto))
        return children_ids_list

    def get_spouse_ids_of_member(self, member_id: str) -> list[str]:
        """Returns a list of spouse IDs for a given member."""
        spouse_ids_list = []
        if member_id in self.family_tree.relationships:
            # self.family_tree.relationships[member_id].spouse_ids is a RepeatedScalarContainer
            for spouse_id_proto in self.family_tree.relationships[member_id].spouse_ids:
                spouse_ids_list.append(str(spouse_id_proto))
        return spouse_ids_list

    def get_parent_ids_of_member(self, member_id: str) -> list[str]:
        """Returns a list of parent IDs for a given child by checking all relationships."""
        parent_ids_list = []
        if member_id in self.family_tree.relationships:
            # self.family_tree.relationships[member_id].parent_ids is a RepeatedScalarContainer
            for parent_id_proto in self.family_tree.relationships[member_id].parent_ids:
                parent_ids_list.append(str(parent_id_proto))
        return parent_ids_list

    def add_member_to_proto_tree(self, member_proto: family_tree_pb2.FamilyMember):
        self.family_tree.members[member_proto.id].CopyFrom(member_proto)

    def _sanity_check_and_get_member_names(
        self, member1_id: str, member2_id: str
    ) -> tuple[str, str]:
        member1_id = str(member1_id)
        member2_id = str(member2_id)
        logger.debug(f"Sanity check for member IDs: {member1_id}, {member2_id}")

        all_family_member_ids = self.get_family_member_ids()
        if (
            member1_id not in all_family_member_ids
            or member2_id not in all_family_member_ids
        ):
            logger.error(
                f"Invalid member IDs during sanity check: {member1_id} or {member2_id} not in {all_family_member_ids}"
            )
            raise ValueError(
                f"Invalid member IDs: {member1_id} or {member2_id} not found."
            )
        if member1_id == member2_id:
            logger.error(f"Member IDs cannot be the same in sanity check: {member1_id}")
            raise ValueError("Member IDs cannot be the same.")
        member1_name = self.family_tree.members[member1_id].name
        member2_name = self.family_tree.members[member2_id].name
        return member1_name, member2_name

    def delete_member_from_proto_tree(self, member_id: str):
        """Deletes a member from the family tree."""
        member_id = str(member_id)
        if member_id in self.family_tree.members:
            # 1. Delete the member from the members map
            del self.family_tree.members[member_id]
            # Remove references to this member in relationship of others
            logger.debug(f"Deleted member {member_id} from members map.")

            # 2. Remove the relationship entry keyed by the deleted member_id, if it exists
            if member_id in self.family_tree.relationships:
                del self.family_tree.relationships[member_id]
                logger.debug(f"Deleted relationship entry for {member_id}.")

            # 3. Remove references to this member_id in relationship lists of *other* members
            # Use list() for safe iteration while modifying
            for rel_id, relationships in list(self.family_tree.relationships.items()):
                if member_id in relationships.spouse_ids:
                    # These should be mutable changes
                    relationships.spouse_ids.remove(member_id)
                    logger.debug(f"Removed {member_id} from spouse_ids of {rel_id}")
                if member_id in relationships.children_ids:
                    relationships.children_ids.remove(member_id)
                    logger.debug(f"Removed {member_id} from children_ids of {rel_id}")
                if member_id in relationships.parent_ids:  # Address the FIXME
                    relationships.parent_ids.remove(member_id)
                    logger.debug(f"Removed {member_id} from parent_ids of {rel_id}")
        else:
            logger.warning(f"Attempted to delete non-existent member: {member_id}")

    def _add_spouse_relation(
        self, spouse1_id: str, spouse2_id: str, infer_relations: bool = True
    ) -> list:
        established_relations_list = []
        spouse1_id = str(spouse1_id)
        spouse2_id = str(spouse2_id)
        spouse1_name, spouse2_name = self._sanity_check_and_get_member_names(
            spouse1_id, spouse2_id
        )
        relation_entry_for_member1 = self.family_tree.relationships[spouse1_id]
        relation_entry_for_member2 = self.family_tree.relationships[spouse2_id]

        newly_added = False
        if spouse2_id not in relation_entry_for_member1.spouse_ids:
            relation_entry_for_member1.spouse_ids.append(spouse2_id)
            newly_added = True
        if spouse1_id not in relation_entry_for_member2.spouse_ids:
            relation_entry_for_member2.spouse_ids.append(spouse1_id)
            newly_added = True  # Even if one side was new, consider it added for graph

        if newly_added:
            established_relations_list.append(("spouse", spouse1_id, spouse2_id))
            logger.info(
                f"Added spouse relationship between {spouse1_name} ({spouse1_id}) and {spouse2_name} ({spouse2_id})"
            )

        if infer_relations:  # Inference can happen even if direct relation existed, to catch other implications
            inferred_list = self._infer_relations_for_spouse(
                member1_id=spouse1_id, member2_id=spouse2_id
            )
            established_relations_list.extend(inferred_list)
        return established_relations_list

    def _add_child_relation(
        self, parent_id: str, child_id: str, infer_relations: bool = True
    ) -> list:
        # parent_id is parent, child_id is child
        established_relations_list = []
        parent_name, child_name = self._sanity_check_and_get_member_names(
            parent_id, child_id
        )
        relation_entry_for_parent = self.family_tree.relationships[parent_id]
        relation_entry_for_child = self.family_tree.relationships[child_id]
        if child_id not in relation_entry_for_parent.children_ids:
            relation_entry_for_parent.children_ids.append(child_id)
            established_relations_list.append(("child", parent_id, child_id))
            logger.info(
                f"Added {parent_name} as parent of {child_name} (child {child_id} to parent {parent_id})"
            )

        if parent_id not in relation_entry_for_child.parent_ids:
            relation_entry_for_child.parent_ids.append(parent_id)
            # Avoid double-adding to list if already added above, but ensure logging if this path adds it
            if ("child", parent_id, child_id) not in established_relations_list:
                established_relations_list.append(("child", parent_id, child_id))
                logger.info(
                    f"Added {parent_name} as parent of {child_name} (parent {parent_id} to child {child_id})"
                )

        if infer_relations:
            inferred_list = self._infer_relations_for_child(
                member1_id=parent_id, member2_id=child_id
            )
            established_relations_list.extend(inferred_list)
        return established_relations_list

    def _add_parent_relation(
        self, child_id: str, parent_id: str, infer_relations: bool = True
    ) -> list:
        # child_id is child, parent_id is parent
        established_relations_list = []
        # child_id is the ID of the child, parent_id is the ID of the parent.
        parent_name, child_name = self._sanity_check_and_get_member_names(
            parent_id,
            child_id,  # Order for name fetching doesn't strictly matter here
        )

        relation_entry_for_child = self.family_tree.relationships[child_id]
        relation_entry_for_parent = self.family_tree.relationships[parent_id]

        # Add parent_id to the child's list of parents
        if parent_id not in relation_entry_for_child.parent_ids:
            relation_entry_for_child.parent_ids.append(parent_id)
            # Canonical form is ("child", parent_id, child_id)
            established_relations_list.append(("child", parent_id, child_id))
            logger.info(
                f"Added {child_name} ({child_id}) as child of {parent_name} ({parent_id}) (parent {parent_id} to child {child_id}'s list)"
            )

        # Add child_id to the parent's list of children
        if child_id not in relation_entry_for_parent.children_ids:
            relation_entry_for_parent.children_ids.append(child_id)
            if (
                "child",
                parent_id,
                child_id,
            ) not in established_relations_list:  # Avoid double add
                established_relations_list.append(("child", parent_id, child_id))
                logger.info(
                    f"Added {child_name} ({child_id}) as child of {parent_name} ({parent_id}) (child {child_id} to parent {parent_id}'s list)"
                )

        if infer_relations:
            # member1_id is child, member2_id is parent for _infer_relations_for_parent
            inferred_list = self._infer_relations_for_parent(
                member1_id=child_id,
                member2_id=parent_id,
            )
            established_relations_list.extend(inferred_list)
        return established_relations_list

    def _infer_relations_for_spouse(self, member1_id: str, member2_id: str) -> list:
        """M1 and M2 are spouses. Infer children relationships."""
        inferred_relations_list = []
        logger.debug(f"Inferring relations for spouses: {member1_id} and {member2_id}")
        children_of_M1 = self.get_children_ids_of_member(member1_id)
        children_of_M2 = self.get_children_ids_of_member(member2_id)

        # Add other existing children of M2 as children of M1
        other_children_of_M2 = set(children_of_M2) - set(children_of_M1)
        for child_id in other_children_of_M2:
            # logger.debug(
            #     f"Making {member1_id} a parent of {child_id} (child of {member2_id}) due to spousal inference"
            # )
            newly_established = self._add_child_relation(
                parent_id=member1_id, child_id=child_id, infer_relations=False
            )
            inferred_relations_list.extend(newly_established)

        # Add other existing children of M1 as children of M2
        other_children_of_M1 = set(children_of_M1) - set(children_of_M2)
        for child_id in other_children_of_M1:
            # logger.debug(
            #     f"Making {member2_id} a parent of {child_id} (child of {member1_id}) due to spousal inference"
            # )
            newly_established = self._add_child_relation(
                parent_id=member2_id, child_id=child_id, infer_relations=False
            )
            inferred_relations_list.extend(newly_established)
        return inferred_relations_list

    def _infer_relations_for_child(self, member1_id: str, member2_id: str) -> list:
        """M1 is parent of M2 (child). Infer other parent for M2."""
        inferred_relations_list = []
        logger.debug(
            f"Inferring relations for child: parent={member1_id}, child={member2_id}"
        )
        spouse_of_M1 = self.get_spouse_ids_of_member(member1_id)
        # Add the spouse of parent (M1) as the other parent to child M2
        for spouse_id in spouse_of_M1:
            # logger.debug(
            #     f"Making {spouse_id} (spouse of {member1_id}) a parent of child {member2_id} due to child inference"
            # )
            newly_established = self._add_parent_relation(
                child_id=member2_id, parent_id=spouse_id, infer_relations=False
            )
            inferred_relations_list.extend(newly_established)
        return inferred_relations_list

    def _infer_relations_for_parent(self, member1_id: str, member2_id: str) -> list:
        """M1 (member1_id) is child of M2 (member2_id, the new parent). Infer spousal and step-sibling relations for M2."""
        inferred_relations_list = []
        logger.debug(
            f"Inferring relations for new parent: child_id={member1_id}, new_parent_id={member2_id}"
        )

        parents_of_M1 = self.get_parent_ids_of_member(member1_id)
        logger.debug(f"Existing parents of child {member1_id}: {parents_of_M1}")

        # Find other parents of M1, excluding the new parent M2.
        other_parents_of_M1_set = set(parents_of_M1) - {
            member2_id
        }  # Corrected set difference
        logger.debug(
            f"Other parents of child {member1_id} (excluding new parent {member2_id}): {other_parents_of_M1_set}"
        )

        if len(other_parents_of_M1_set) == 1:
            the_single_other_parent_id = list(other_parents_of_M1_set)[0]
            # logger.debug(
            #     f"Child {member1_id} has one other parent: {the_single_other_parent_id}. Adding new parent {member2_id} and {the_single_other_parent_id} as spouses due to parent inference."
            # )
            newly_established = self._add_spouse_relation(
                spouse1_id=member2_id,
                spouse2_id=the_single_other_parent_id,
                infer_relations=True,
            )
            inferred_relations_list.extend(newly_established)
        elif len(other_parents_of_M1_set) > 1:
            self.message_to_propagate += (
                f"Child {member1_id} has multiple other parents ({other_parents_of_M1_set}). "
                f"Cannot automatically infer spousal relationship for new parent {member2_id} with all of them. "
                "Spousal relationships may need to be added manually if appropriate. "
            )
            logger.warning(self.message_to_propagate)
            # M2 (new parent) becomes step-parent to M1's half-siblings through each other parent.
            for other_parent_id_element in other_parents_of_M1_set:
                if other_parent_id_element:  # Ensure not empty string
                    siblings_via_other_parent = self.get_children_ids_of_member(
                        other_parent_id_element
                    )
                    # logger.debug(
                    #     f"Considering siblings of {member1_id} via other parent {other_parent_id_element}: {siblings_via_other_parent} for parent inference"
                    # )
                    for sibling_id in siblings_via_other_parent:
                        if sibling_id != member1_id:  # M1 is already child of M2
                            # logger.debug(
                            #     f"Adding new parent {member2_id} as (step-)parent to sibling {sibling_id} due to parent inference"
                            # )
                            newly_established = self._add_child_relation(
                                parent_id=member2_id,
                                child_id=sibling_id,
                                infer_relations=False,
                            )
                            inferred_relations_list.extend(newly_established)
        return inferred_relations_list

    def add_relationship(
        self,
        member1_id: str,
        member2_id: str,
        relationship_type: str,
        infer_relations: bool = True,
    ) -> tuple[list, str]:
        """Updates the Relationships message in the family_tree protobuf."""
        self.message_to_propagate = ""
        member1_id = str(member1_id)
        member2_id = str(member2_id)

        if relationship_type == "spouse":
            all_established_relations = self._add_spouse_relation(
                member1_id, member2_id, infer_relations
            )
        elif relationship_type == "child":
            # member1 is parent, member2 is child
            all_established_relations = self._add_child_relation(
                parent_id=member1_id,
                child_id=member2_id,
                infer_relations=infer_relations,
            )
        elif relationship_type == "parent":
            # member1 is child, member2 is parent
            all_established_relations = self._add_parent_relation(
                child_id=member1_id,
                parent_id=member2_id,
                infer_relations=infer_relations,
            )
        else:
            raise ValueError(f"Unknown relationship type: {relationship_type}")

        # self.message_to_propagate can be appended to by inference methods.
        return (
            all_established_relations,
            self.message_to_propagate or "Relationships processed.",
        )

    def merge_another_family_tree(
        self, new_tree: family_tree_pb2.FamilyTree, connecting_member_id=None
    ):
        # TODO: Implement merging logic
        logger.warning("merge_another_family_tree is not yet implemented.")
        pass

    def generate_member_id(self):
        """Generates a unique random 4-character alphanumeric member ID."""
        # Use a larger keyspace or check against existing IDs more robustly if collisions become likely
        chars = string.ascii_uppercase + string.digits
        while True:
            member_id = "".join(random.choices(chars, k=4))
            # Check against actual keys in the protobuf map for ground truth
            if member_id not in self.family_tree.members:
                return member_id

    def generate_new_member(self):
        new_member = family_tree_pb2.FamilyMember()
        new_member.id = self.generate_member_id()
        return new_member

    def create_proto_member_from_dict(
        self, input_dict, member_to_update: family_tree_pb2.FamilyMember
    ) -> tuple[family_tree_pb2.FamilyMember | None, str]:
        """
        Validates input data and populates a FamilyMember protobuf object.
        Does NOT modify self.family_tree
        If existing_member is provided, it works on a COPY and returns the
        validated copy on success.
        Args:
            input_dict: Dictionary containing the raw input data.
            member_to_update: The FamilyMember protobuf object to be populated.
                              This can be a new shell (from generate_new_member)
                              or an existing member from the tree.
        Returns:
            tuple[FamilyMember | None, str | None]:
                (populated_member_proto, None) on successful validation and population.
                (None, error_message) if validation fails.
        """
        error_message = ""
        # Create a working copy of the member_to_update.
        # This ensures that if validation fails, the original member_to_update
        # (especially if it's an existing member from the tree) is not altered.
        # The ID is preserved from member_to_update.
        working_member = family_tree_pb2.FamilyMember()
        working_member.CopyFrom(member_to_update)

        # --- Basic Info ---
        working_member.name = input_dict.get("name", "").strip()
        if not working_member.name:
            return None, "Validation Error: Name cannot be empty."

        # Clear existing nicknames before adding new ones (important for updates)
        working_member.ClearField("nicknames")
        nicknames_str = input_dict.get("nicknames", "")
        if nicknames_str:
            working_member.nicknames.extend(
                [nick.strip() for nick in nicknames_str.split(",") if nick.strip()]
            )

        try:
            working_member.gender = utils_pb2.Gender.Value(
                input_dict.get("gender", "GENDER_UNKNOWN")
            )
            working_member.gender = utils_pb2.Gender.Value(
                input_dict.get("gender", "GENDER_UNKNOWN")
            )
        except ValueError:
            logger.warning(
                f"Invalid gender value '{input_dict.get('gender')}' for {working_member.name}. Setting to UNKNOWN."
            )
            working_member.gender = utils_pb2.GENDER_UNKNOWN

        # --- DOB Population and Validation ---
        # Clear existing date fields before potentially repopulating (important for updates)
        working_member.ClearField("date_of_birth")
        working_member.ClearField("traditional_date_of_birth")

        dob_provided = any(
            k in input_dict for k in ["dob_date", "dob_month", "dob_year"]
        )
        if dob_provided:
            is_valid, error_msg = DateUtility.populate_gregorian_date(
                working_member.date_of_birth, input_dict, "dob"
            )
            if not is_valid:
                return None, f"Date of Birth Error: {error_msg}"
        trad_dob_provided = any(
            k in input_dict for k in ["dob_traditional_month", "dob_traditional_star"]
        )
        if trad_dob_provided:
            is_valid, error_msg = DateUtility.populate_traditional_date(
                working_member.traditional_date_of_birth,
                input_dict,
                "dob",
                utils_pb2.TamilMonth,
                star_enum=utils_pb2.TamilStar,
            )
            if not is_valid:
                return None, f"Traditional Date of Birth Error: {error_msg}"

        working_member.alive = input_dict.get("IsAlive", True)
        # --- DOD Population and Validation ---
        # Clear existing DoD fields before potentially repopulating (important for updates)
        working_member.ClearField("date_of_death")
        working_member.ClearField("traditional_date_of_death")
        if not working_member.alive:
            dod_provided = any(
                k in input_dict for k in ["dod_date", "dod_month", "dod_year"]
            )
            if dod_provided:
                is_valid, error_msg = DateUtility.populate_gregorian_date(
                    working_member.date_of_death, input_dict, "dod"
                )
                if not is_valid:
                    return None, f"Date of Death Error: {error_msg}"

            trad_dod_provided = any(
                k in input_dict
                for k in [
                    "dod_traditional_month",
                    "dod_traditional_paksham",
                    "dod_traditional_thithi",
                ]
            )
            if trad_dod_provided:
                is_valid, error_msg = DateUtility.populate_traditional_date(
                    working_member.traditional_date_of_death,
                    input_dict,
                    "dod",
                    utils_pb2.TamilMonth,
                    paksham_enum=utils_pb2.Paksham,
                    thithi_enum=utils_pb2.Thithi,
                )
                if not is_valid:
                    return None, f"Traditional Date of Death Error: {error_msg}"

            # Perform DOB vs DOD comparison if both might be populated
            is_valid_comparison, comparison_error_msg = DateUtility.compare_dob_and_dod(
                working_member
            )
            if not is_valid_comparison:  # is_valid_comparison will be None on error
                return None, comparison_error_msg

        # If all validations passed
        return working_member, error_message

    def prepare_node_attributes_for_member(self, member: family_tree_pb2.FamilyMember):
        member_id = member.id
        if not member_id:
            logger.warning(
                f"Skipping node creation for member without ID: {member.name}"
            )
            return

        default_images, brokenImage = ResourceUtility.get_default_images()
        additional_info = member.additional_info
        image_location = additional_info.get("image_location")

        # Determine image path (prioritize user-provided local, then default local)
        final_image_path = None
        if image_location:
            # Assume image_location is a valid local path if provided
            # Add a check if it actually exists?
            if os.path.exists(image_location):
                final_image_path = image_location
            else:
                logger.warning(
                    f"Provided image_location does not exist: {image_location}"
                )

        if not final_image_path and default_images:
            gender_name = utils_pb2.Gender.Name(member.gender)
            final_image_path = default_images.get(gender_name)
            if not final_image_path:  # Fallback if gender name not in dict
                final_image_path = default_images.get("GENDER_UNKNOWN")

        # Prepare node title (tooltip)
        title_str = self.generate_node_title(member)
        identifiers = {
            "ID": member_id,
            "Name": member.name,
            "Title": title_str,
            "NodeImagePath": final_image_path,
            "BrokenImage": brokenImage,
        }
        return identifiers

    def generate_node_title(self, member: family_tree_pb2.FamilyMember):
        """Generates a formatted string for the node tooltip."""
        try:
            # Use MessageToDict for a structured representation
            member_dict = MessageToDict(
                member,
                preserving_proto_field_name=True,
                use_integers_for_enums=False,  # Show enum names
            )
            # Basic formatting - could be enhanced (e.g., remove empty fields)
            title_parts = []
            for key, value in member_dict.items():
                # Only show non-empty fields and boolean fields
                if value or isinstance(value, bool):
                    # Simple formatting for common types
                    if isinstance(value, dict) and all(v == 0 for v in value.values()):
                        continue  # Skip empty date objects etc.
                    if isinstance(value, list) and not value:
                        continue  # Skip empty lists
                    title_parts.append(f"{key.replace('_', ' ').title()}: {value}")
            title_str = "\n".join(title_parts)
            # Fallback if formatting fails or results in empty string
            if not title_str:
                raise ValueError("Formatted title is empty")
        except Exception as e:
            logger.warning(f"Could not format member {member.id} for tooltip: {e}")
            # Fallback to simple text format
            try:
                title_str = text_format.MessageToString(member, as_utf8=True)
            except Exception:
                title_str = f"Error generating title for {member.id}"  # Final fallback
        return title_str

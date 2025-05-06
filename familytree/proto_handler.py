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

    def update_data_source(self, input_text_file):
        self.input_text_file = input_text_file

    def update_output_data_file(self, output_data_file):
        self.output_proto_data_file = output_data_file

    def load_from_protobuf(self):
        # logger is now defined at module level
        logger.info(f"Loading data from: {self.input_text_file}")
        try:
            # Ensure file exists before opening
            if not self.input_text_file or not os.path.exists(self.input_text_file):
                raise FileNotFoundError(
                    f"Input file not specified or not found: {self.input_text_file}"
                )

            with open(
                self.input_text_file, "r", encoding="utf-8"
            ) as f:  # Specify encoding
                text_format.Merge(f.read(), self.family_tree)
                logger.info(
                    f"Successfully loaded {self.input_text_file}"
                )  # Kept as logger.info
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
            logger.exception(log_message)  # logger.exception includes traceback

            # Raise a NEW, more informative exception, linking the original 'e' as the cause
            raise Exception(log_message) from e  # <--- MODIFIED LINE

    def print_member_details(self, member_id):
        member = self.family_tree.members[member_id]
        print(f"Member Details ({member_id}):\n{member}")

    def query_proto_member_by_id(self, member_id):
        return self.family_tree.members.get(member_id, None)

    def get_family_members(self):
        return self.family_tree.members.values()

    def get_family_member_ids(self):
        return self.family_tree.members.keys()

    def get_member_identifiers(self, member_proto: family_tree_pb2.FamilyMember):
        """Returns the main identifiers like ID and name"""
        return member_proto.id, member_proto.name

    def add_member_to_proto_tree(self, member_proto: family_tree_pb2.FamilyMember):
        self.family_tree.members[member_proto.id].CopyFrom(member_proto)

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
            existing_member: If provided, updates this existing member object.
                             If None, creates and returns a new member object.

        Returns:
            tuple[FamilyMember | None, str | None]:
                (populated_member_proto, None) on successful validation and population.
                (None, error_message) if validation fails.
        """
        error_message = ""
        member = member_to_update

        # --- Basic Info ---
        member.name = input_dict.get("name", "").strip()
        if not member.name:
            return None, "Validation Error: Name cannot be empty."

        # Clear existing nicknames before adding new ones (important for updates)
        member.ClearField("nicknames")
        nicknames_str = input_dict.get("nicknames", "")
        if nicknames_str:
            member.nicknames.extend(
                [nick.strip() for nick in nicknames_str.split(",") if nick.strip()]
            )

        try:
            member.gender = utils_pb2.Gender.Value(
                input_dict.get("gender", "GENDER_UNKNOWN")
            )
        except ValueError:
            logger.warning(
                f"Invalid gender value '{input_dict.get('gender')}' for {member.name}. Setting to UNKNOWN."
            )
            member.gender = utils_pb2.GENDER_UNKNOWN

        # --- DOB Population and Validation ---
        # Clear existing date fields before potentially repopulating (important for updates)
        member.ClearField("date_of_birth")
        member.ClearField("traditional_date_of_birth")

        dob_provided = any(
            k in input_dict for k in ["dob_date", "dob_month", "dob_year"]
        )
        if dob_provided:
            is_valid, error_msg = DateUtility.populate_gregorian_date(
                member.date_of_birth, input_dict, "dob"
            )
            if not is_valid:
                return None, f"Date of Birth Error: {error_msg}"

        trad_dob_provided = any(
            k in input_dict for k in ["dob_traditional_month", "dob_traditional_star"]
        )
        if trad_dob_provided:
            is_valid, error_msg = DateUtility.populate_traditional_date(
                member.traditional_date_of_birth,
                input_dict,
                "dob",
                utils_pb2.TamilMonth,
                star_enum=utils_pb2.TamilStar,
            )
            if not is_valid:
                return None, f"Traditional Date of Birth Error: {error_msg}"

        member.alive = input_dict.get("IsAlive", True)
        # --- DOD Population and Validation ---
        # Clear existing DoD fields before potentially repopulating (important for updates)
        member.ClearField("date_of_death")
        member.ClearField("traditional_date_of_death")
        if not member.alive:
            dod_provided = any(
                k in input_dict for k in ["dod_date", "dod_month", "dod_year"]
            )
            if dod_provided:
                is_valid, error_msg = DateUtility.populate_gregorian_date(
                    member.date_of_death, input_dict, "dod"
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
                    member.traditional_date_of_death,
                    input_dict,
                    "dod",
                    utils_pb2.TamilMonth,
                    paksham_enum=utils_pb2.Paksham,
                    thithi_enum=utils_pb2.Thithi,
                )
                if not is_valid:
                    return None, f"Traditional Date of Death Error: {error_msg}"

            DateUtility.compare_dob_and_dod(member)

        # If all validations passed
        return member, error_message

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

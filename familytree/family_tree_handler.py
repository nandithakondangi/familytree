import datetime
import json
import logging
import os
import pathlib
import random
import string

import google.protobuf.text_format as text_format
import networkx as nx
from google.protobuf.json_format import MessageToDict

# Import Jinja2
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pyvis.network import Network

import proto.family_tree_pb2 as family_tree_pb2
import proto.utils_pb2 as utils_pb2

# Get a logger instance for this module
logger = logging.getLogger(__name__)  # Added

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


class DateUtility:
    """
    Utility class for handling date parsing, validation, and population
    for FamilyMember protobufs.
    Methods return a tuple: (success: bool, error_message: str | None).
    """

    @staticmethod
    def populate_gregorian_date(
        date_proto, input_data, prefix
    ) -> tuple[bool, str | None]:
        """
        Populates and validates a GregorianDate protobuf message from input data.

        Args:
            date_proto: The GregorianDate message to populate (e.g., member.date_of_birth).
            input_data: The dictionary containing potential date parts.
            prefix: The prefix for the keys in input_data (e.g., "dob", "dod").

        Returns:
            tuple[bool, str | None]: (True, None) if the date was successfully populated
                                     or no relevant input was found.
                                     (False, error_message) if invalid data was provided.
        """
        day_str = input_data.get(f"{prefix}_date")
        month_str = input_data.get(f"{prefix}_month")
        year_str = input_data.get(f"{prefix}_year")

        # Check if any date part was actually provided (treat empty strings as not provided)
        if not (day_str or month_str or year_str):
            return True, None  # No data provided, nothing to validate or set, success.

        try:
            # Attempt conversion, default to 0 if empty string or None
            day = int(day_str or 0)
            month = int(month_str or 0)
            year = int(year_str or 0)

            # Ensure all parts were provided if at least one was
            if not (day and month and year):
                return (
                    False,
                    f"Incomplete Gregorian date provided for '{prefix}'. Please provide day, month, and year.",
                )

            # --- Comprehensive Validation ---
            # 1. Use datetime for calendar validity (handles leap years, days in month)
            try:
                parsed_date = datetime.date(year, month, day)
            except ValueError as e:
                # More specific error based on common ValueError messages
                if "month must be in 1..12" in str(e):
                    return (
                        False,
                        f"Invalid month ({month}) for '{prefix}'. Month must be between 1 and 12.",
                    )
                elif "day is out of range for month" in str(e):
                    return (
                        False,
                        f"Invalid day ({day}) for '{prefix}' month {month} and year {year}.",
                    )
                elif "year" in str(e):  # Catch other year-related errors if any
                    return False, f"Invalid year ({year}) provided for '{prefix}'. {e}"
                else:  # Generic fallback
                    return (
                        False,
                        f"Invalid Gregorian date for '{prefix}': Day={day}, Month={month}, Year={year}. Reason: {e}",
                    )

            # 2. Check if the date is in the future
            if parsed_date > datetime.date.today():
                return (
                    False,
                    f"Gregorian date for '{prefix}' ({parsed_date.strftime('%Y-%m-%d')}) cannot be in the future.",
                )

            # 3. Check for reasonably sensible year (optional, adjust as needed)
            if year < 1000:  # Or some other sensible minimum year
                return (
                    False,
                    f"Year ({year}) for '{prefix}' seems too far in the past. Please check.",
                )
            # --- End Validation ---

            # If all checks pass, populate the proto
            date_proto.date = day
            date_proto.month = month
            date_proto.year = year
            return True, None  # Successfully populated

        except (ValueError, TypeError):
            # Catches errors during int() conversion if non-numeric provided
            return (
                False,
                f"Non-numeric value encountered for '{prefix}' date parts (Day='{day_str}', Month='{month_str}', Year='{year_str}'). Please enter numbers.",
            )
        except Exception as e:
            logger.exception(
                f"Unexpected error validating/populating Gregorian date for prefix '{prefix}': {e}"
            )
            return (
                False,
                f"An unexpected error occurred processing the Gregorian date for '{prefix}'.",
            )  # Generic message for unexpected

    @staticmethod
    def populate_traditional_date(
        trad_date_proto,
        input_data,
        prefix,
        month_enum,
        star_enum=None,
        paksham_enum=None,
        thithi_enum=None,
    ) -> tuple[bool, str | None]:
        """
        Populates and validates a TraditionalDate protobuf message from input data using enums.

        Args:
            trad_date_proto: The TraditionalDate message to populate.
            input_data: The dictionary containing potential date parts.
            prefix: The prefix for the keys in input_data (e.g., "dob", "dod").
            month_enum: The protobuf enum type for the Tamil month.
            star_enum: Optional protobuf enum type for the Tamil star.
            paksham_enum: Optional protobuf enum type for Paksham.
            thithi_enum: Optional protobuf enum type for Thithi.

        Returns:
            tuple[bool, str | None]: (True, None) if the date was successfully populated
                                     or no relevant input was found.
                                     (False, error_message) if an invalid enum value string was provided.
        """
        try:
            field_updated = False  # Track if we actually set any field

            # --- Month ---
            month_str = input_data.get(f"{prefix}_traditional_month")
            if month_str and month_str != month_enum.Name(
                0
            ):  # Check against default "UNKNOWN"
                try:
                    trad_date_proto.month = month_enum.Value(month_str)
                    field_updated = True
                except ValueError:
                    return (
                        False,
                        f"Invalid traditional month value '{month_str}' for prefix '{prefix}'.",
                    )

            # --- Star (if applicable) ---
            if star_enum:
                star_str = input_data.get(f"{prefix}_traditional_star")
                if star_str and star_str != star_enum.Name(0):
                    try:
                        trad_date_proto.star = star_enum.Value(star_str)
                        field_updated = True
                    except ValueError:
                        return (
                            False,
                            f"Invalid traditional star value '{star_str}' for prefix '{prefix}'.",
                        )

            # --- Paksham (if applicable) ---
            if paksham_enum:
                paksham_str = input_data.get(f"{prefix}_traditional_paksham")
                if paksham_str and paksham_str != paksham_enum.Name(0):
                    try:
                        trad_date_proto.paksham = paksham_enum.Value(paksham_str)
                        field_updated = True
                    except ValueError:
                        return (
                            False,
                            f"Invalid traditional paksham value '{paksham_str}' for prefix '{prefix}'.",
                        )

            # --- Thithi (if applicable) ---
            if thithi_enum:
                thithi_str = input_data.get(f"{prefix}_traditional_thithi")
                if thithi_str and thithi_str != thithi_enum.Name(0):
                    try:
                        trad_date_proto.thithi = thithi_enum.Value(thithi_str)
                        field_updated = True
                    except ValueError:
                        return (
                            False,
                            f"Invalid traditional thithi value '{thithi_str}' for prefix '{prefix}'.",
                        )

            # If we reached here without returning False, validation passed for provided fields
            return True, None

        except Exception as e:
            logger.exception(
                f"Unexpected error validating/populating traditional date for prefix '{prefix}': {e}"
            )
            return (
                False,
                f"An unexpected error occurred processing the traditional date for '{prefix}'.",
            )


class FamilyTreeHandler:
    def __init__(
        self,
        temp_dir_path,
        input_file=None,
        output_file=None,
        output_data_file=None,
    ):
        self.family_tree = family_tree_pb2.FamilyTree()
        self.nx_graph = nx.DiGraph()
        self.input_file = input_file
        self.temp_dir_path = temp_dir_path

        if not output_file:
            self.output_file = os.path.join(self.temp_dir_path, "family_tree.html")
        else:
            self.output_file = output_file

        if not output_data_file:
            self.output_proto_data_file = os.path.join(
                self.temp_dir_path, "family_tree_data.txtpb"
            )
        else:
            self.output_proto_data_file = output_data_file

    def update_data_source(self, input_file):
        self.input_file = input_file

    def update_output_html_file(self, output_file):
        self.output_file = output_file

    def update_output_data_file(self, output_data_file):
        self.output_proto_data_file = output_data_file

    def load_from_protobuf(self):
        # logger is now defined at module level
        logger.info(f"Loading data from: {self.input_file}")
        try:
            # Ensure file exists before opening
            if not self.input_file or not os.path.exists(self.input_file):
                raise FileNotFoundError(
                    f"Input file not specified or not found: {self.input_file}"
                )

            with open(self.input_file, "r", encoding="utf-8") as f:  # Specify encoding
                text_format.Merge(f.read(), self.family_tree)
                logger.info(
                    f"Successfully loaded {self.input_file}"
                )  # Kept as logger.info
        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            raise  # Re-raise for GUI to handle
        except text_format.ParseError as e:
            logger.error(f"Error parsing protobuf text file {self.input_file}: {e}")
            raise  # Re-raise for GUI
        except Exception as e:
            logger.exception(f"An unexpected error occurred during loading: {e}")
            raise  # Re-raise for GUI

        # Populate nodes and edges
        self.populate_nodes_and_edges()

    def get_default_images(self):
        """Gets paths for default local images."""
        default_images = {}
        brokenImage = ""
        try:
            # Use pathlib for more robust path handling
            script_dir = pathlib.Path(__file__).parent.resolve()  # familytree directory
            base_dir = script_dir.parent  # Project root directory
            images_dir = base_dir / "resources"

            default_image_files = {
                "MALE": "male.png",
                "FEMALE": "female.png",
                "OTHER": "person.jpg",
                "GENDER_UNKNOWN": "person.jpg",
            }
            broken_image_file = "broken.gif"

            for key, filename in default_image_files.items():
                path = images_dir / filename
                if path.is_file():
                    default_images[key] = str(path)  # Store as string path
                else:
                    logger.warning(f"Default image not found for {key} at {path}")

            broken_path = images_dir / broken_image_file
            if broken_path.is_file():
                brokenImage = str(broken_path)
            else:
                logger.warning(f"Broken image not found at {broken_path}")

        except Exception as e:
            logger.error(f"Error determining default image paths: {e}")
            # Return empty dicts/strings on error
            default_images = {}
            brokenImage = ""

        return default_images, brokenImage

    def generate_member_id(self):
        """Generates a unique random 4-character alphanumeric member ID."""
        # Use a larger keyspace or check against existing IDs more robustly if collisions become likely
        chars = string.ascii_uppercase + string.digits
        while True:
            member_id = "".join(random.choices(chars, k=4))
            # Check against actual keys in the protobuf map for ground truth
            if member_id not in self.family_tree.members:
                return member_id

    def _prepare_member_data(
        self, input_dict, existing_member: family_tree_pb2.FamilyMember | None = None
    ) -> tuple[family_tree_pb2.FamilyMember | None, str | None]:
        """
        Validates input data and populates a FamilyMember protobuf object.
        Does NOT modify self.family_tree or self.nx_graph.
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
        if existing_member:
            # Create a copy to modify, leave the original untouched until validation passes
            member = family_tree_pb2.FamilyMember()
            member.CopyFrom(existing_member)
            # Ensure the ID is preserved in the copy if we are updating
            member.id = existing_member.id
        else:
            member = family_tree_pb2.FamilyMember()  # Create a new object for creation

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

            # --- DOD vs DOB Check (after both are potentially populated) ---
            dob_populated = member.date_of_birth.year != 0
            dod_populated = member.date_of_death.year != 0

            if dob_populated and dod_populated:
                try:
                    dob = datetime.date(
                        member.date_of_birth.year,
                        member.date_of_birth.month,
                        member.date_of_birth.date,
                    )
                    dod = datetime.date(
                        member.date_of_death.year,
                        member.date_of_death.month,
                        member.date_of_death.date,
                    )
                    if dod < dob:
                        return (
                            None,
                            "Validation Error: Date of Death cannot be before Date of Birth.",
                        )
                except ValueError:
                    logger.error(
                        "Inconsistency: Could not create date objects for comparison after individual validation passed."
                    )
                    return None, "Internal Error: Could not compare DOB and DOD."
        # If all validations passed
        return member, None

    def _add_member_to_tree_and_graph(
        self, member_proto: family_tree_pb2.FamilyMember
    ) -> tuple[bool, str | None]:
        """
        Adds or updates a validated member proto into the main family tree
        and the NetworkX graph.

        Args:
            member_proto: The validated FamilyMember object.

        Returns:
            tuple[bool, str | None]: (True, None) on success.
                                     (False, error_message) on failure.
        """
        member_id = member_proto.id
        if not member_id:
            return False, "Internal Error: Member proto has no ID."

        try:
            # Add/Update in the main protobuf structure
            # Use CopyFrom to ensure the map entry is correctly updated/created
            self.family_tree.members[member_id].CopyFrom(member_proto)

            # Add/Update in the NetworkX graph
            self.add_or_update_node_from_proto_object(
                member_proto
            )  # This function already handles add/update

            logger.info(
                f"Successfully added/updated member {member_id} ('{member_proto.name}') in tree and graph."
            )
            return True, None
        except Exception as e:
            logger.exception(
                f"Unexpected error adding/updating member {member_id} to tree/graph: {e}"
            )
            # Attempt to roll back if needed (complex, might leave inconsistent state)
            # For simplicity, we just report the error.
            return (
                False,
                f"Internal error occurred while saving/updating member state: {e}",
            )

    def create_node(self, input_dict) -> tuple[str | None, str | None]:
        """
        Creates a new FamilyMember node by preparing data, validating,
        and then adding it to the tree and graph.

        Args:
            input_dict: Dictionary containing the raw input data for the new member.

        Returns:
            tuple[str | None, str | None]: (member_id, None) on successful creation.
                                           (None, error_message) if validation or saving fails.
        """
        # 1. Prepare and validate data (without modifying state yet)
        member_proto, error_message = self._prepare_member_data(
            input_dict, existing_member=None
        )

        if error_message:
            return None, error_message  # Validation failed

        # 2. Generate ID and add to tree/graph (modify state)
        member_id = self.generate_member_id()
        member_proto.id = member_id  # Assign the generated ID to the prepared proto

        success, save_error_message = self._add_member_to_tree_and_graph(member_proto)

        if not success:
            # Attempt to clean up the generated ID if it was somehow added partially? Unlikely here.
            return None, save_error_message  # Saving/Graphing failed
        else:
            return member_id, None  # Success

    def update_node(self, member_id, input_dict) -> tuple[bool, str | None]:
        """
        Updates an existing FamilyMember node by preparing data, validating,
        and then updating it in the tree and graph.

        Args:
            member_id: The ID of the member to update.
            input_dict: Dictionary containing the raw input data for the update.

        Returns:
            tuple[bool, str | None]: (True, None) on successful update.
                                     (False, error_message) if validation or update fails.
        """
        # 1. Check if member exists and get the existing proto
        if member_id not in self.family_tree.members:
            return False, f"Cannot update: Member with ID '{member_id}' not found."
        existing_member = self.family_tree.members[member_id]

        # 2. Prepare and validate data (getting a *copy* or None from _prepare_member_data)
        validated_member_copy, error_message = self._prepare_member_data(
            input_dict, existing_member=existing_member
        )

        if error_message:
            # Validation failed, the original existing_member was NOT modified
            return False, error_message

        # 3. Validation passed, now update the actual member in the tree using the validated copy
        # Use CopyFrom to apply the changes from the validated copy to the original member
        self.family_tree.members[member_id].CopyFrom(validated_member_copy)

        # 4. Update the graph using the now-updated member from the tree
        # Pass the actual object from the tree to ensure consistency
        success, save_error_message = self._add_member_to_tree_and_graph(
            self.family_tree.members[member_id]  # Pass the updated original
        )

        if not success:
            return False, save_error_message  # Saving/Graphing failed
        else:
            return True, None  # Success

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

    def add_or_update_node_from_proto_object(
        self, member: family_tree_pb2.FamilyMember
    ):
        member_id = member.id
        if not member_id:
            logger.warning(
                f"Skipping node creation for member without ID: {member.name}"
            )
            return

        default_images, brokenImage = self.get_default_images()
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

        node_options = {
            "label": member.name,
            "title": title_str,
            "shape": "circularImage" if final_image_path else "dot",
            "image": final_image_path if final_image_path else None,
            "brokenImage": brokenImage,  # Use the locally determined broken image path
            "size": 50,
            "font": {
                "size": 14,
                "color": COLOR_PALETTLE.get("white", "#FFFFFF"),
            },  # Consistent font
            "color": COLOR_PALETTLE.get("light cream", "#E9EBDD"),
        }

        # Add or update the node in the networkx graph
        if member_id not in self.nx_graph:
            self.nx_graph.add_node(member_id, **node_options)
        else:
            # Update existing node data
            self.nx_graph.nodes[member_id].update(node_options)
            logger.info(f"Updated node data for existing node: {member_id}")

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
        # Clear existing graph before populating
        # FIXME: check if we need this. what if a user adds a node and then loads a txtpb file?
        self.nx_graph.clear()
        logger.info("Populating graph nodes...")
        # Use list comprehension for potentially slightly better performance if tree is large
        members_to_process = list(self.family_tree.members.items())

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
                self.add_or_update_node_from_proto_object(member)
            else:
                # This might indicate an issue during protobuf parsing or creation
                logger.warning(
                    f"Skipping uninitialized member with ID {actual_member_id}."
                )

        logger.info("Populating graph edges...")
        # Use list comprehension for potentially slightly better performance
        relationships_to_process = list(self.family_tree.relationships.items())

        for member_id, relationships in relationships_to_process:
            # Ensure the member_id for relationships exists as a node
            if member_id not in self.nx_graph:
                logger.warning(
                    f"Skipping relationships for non-existent member ID: {member_id}"
                )
                continue

            # Add edges between spouses
            for spouse_id in relationships.spouse_ids:
                if member_id == spouse_id:
                    continue  # Skip self-loops
                if spouse_id in self.nx_graph:
                    # Add edge only if the reverse doesn't exist to represent undirected marriage link
                    if not self.nx_graph.has_edge(spouse_id, member_id):
                        self.add_spouse_edges(member_id, spouse_id)
                else:
                    logger.warning(
                        f"Spouse ID {spouse_id} not found for member {member_id}. Skipping edge."
                    )

            # Add edges between parents and children
            for child_id in relationships.children_ids:
                if member_id == child_id:
                    continue  # Skip self-loops
                if child_id in self.nx_graph:
                    self.add_child_edges(member_id, child_id)
                else:
                    logger.warning(
                        f"Child ID {child_id} not found for parent {member_id}. Skipping edge."
                    )

    def merge_another_tree(
        self, new_tree: family_tree_pb2.FamilyTree, connecting_member_id=None
    ):
        # TODO: Implement merging logic
        logger.warning("merge_another_tree is not yet implemented.")
        pass

    # --- Modify display_family_tree ---
    def display_family_tree(self):
        # Ensure the output directory exists
        output_dir = os.path.dirname(self.output_file)
        try:
            os.makedirs(output_dir, exist_ok=True)
        except OSError as e:
            logger.error(f"Error creating output directory {output_dir}: {e}")
            # Handle error appropriately, maybe raise to GUI
            raise IOError(f"Cannot create output directory: {e}") from e

        # Check if graph has nodes before trying to render
        if not self.nx_graph:
            logger.info("NetworkX graph is empty. Cannot generate Pyvis graph.")
            with open(self.output_file, "w", encoding="utf-8") as f:
                f.write(
                    "<html><body style='background-color: #222; color: #fff;'><p>No family tree data loaded.</p></body></html>"
                )
            return

        pyvis_network_graph = Network(
            directed=True,
            notebook=False,
            bgcolor=COLOR_PALETTLE.get("gray", "#222222"),
            font_color=COLOR_PALETTLE.get("white", "#FFFFFF"),
            cdn_resources="in_line",
            height="1000px",  # Consider making height/width dynamic or configurable
            width="100%",
        )
        pyvis_network_graph.from_nx(self.nx_graph)
        options = self._get_pyvis_graph_options()

        try:
            options_json = json.dumps(options)
            pyvis_network_graph.set_options(options_json)
        except TypeError as e:
            logger.error(f"Error serializing pyvis options to JSON: {e}")
            # Continue without options? Or raise?

        # --- JavaScript Injection for Double Click ---
        js_injection_code = ""  # Initialize to empty string
        try:
            # Find the path to qwebchannel.js (adjust if necessary)
            script_dir = pathlib.Path(__file__).parent.resolve()
            base_dir = script_dir.parent
            resources_dir = os.path.join(base_dir, "resources")
            qwebchannel_js_path = str(os.path.join(resources_dir, "qwebchannel.js"))
            # FIXME: If getting it as an online resource:
            #    <script src="https://cdn.jsdelivr.net/npm/qwebchannel/qwebchannel.js"></script>

            if not os.path.exists(qwebchannel_js_path):
                logger.error(
                    f"qwebchannel.js not found at expected location: {qwebchannel_js_path}"
                )
                # Handle error: maybe raise, or proceed without edit functionality
                # For now, log error and proceed, edit won't work.
                js_injection_code = """
                <script type="text/javascript">
                    console.error("qwebchannel.js not found. Double-click editing disabled.");
                </script>
                """
            else:
                # Use file URI for local access
                qwebchannel_js_uri = (
                    pathlib.Path(qwebchannel_js_path).resolve().as_uri()
                )
                logger.info(f"Using qwebchannel.js from: {qwebchannel_js_uri}")
                # --- Jinja Setup ---
                # Set up the environment to load templates from the 'resources/' directory
                template_loader = FileSystemLoader(searchpath=str(resources_dir))
                jinja_env = Environment(
                    loader=template_loader,
                    autoescape=select_autoescape(
                        ["html", "xml", "js"]
                    ),  # Enable autoescaping for safety
                )

                # Load the template file
                template_name = "pyvis_interaction.js.template"
                template = jinja_env.get_template(template_name)

                # Render the template with the dynamic URI
                rendered_js = template.render(qwebchannel_js_uri=qwebchannel_js_uri)

                # Wrap the rendered JS in <script> tags
                js_injection_code = f"""
                <script type="text/javascript">
                {rendered_js}
                </script>
                """
                # --- End Jinja Setup ---
        except Exception as e:
            logger.exception(f"Error preparing JS injection code: {e}")
            js_injection_code = (
                "<script>console.error('Error setting up JS injection.');</script>"
            )

        # --- Generate HTML and Inject JS ---
        try:
            logger.info("Generating family tree HTML content...")
            # 1. Get the HTML content from pyvis first
            # Use generate_html() which returns the string
            html_content = pyvis_network_graph.generate_html(notebook=False)
            logger.info("HTML content generated.")

            # 2. Inject the JavaScript code before the closing </body> tag
            # A simple string replacement is usually sufficient
            if "</body>" in html_content:
                html_content = html_content.replace(
                    "</body>", js_injection_code + "\n</body>", 1
                )
                logger.info("JavaScript injection code inserted before </body>.")
            else:
                # Fallback if </body> tag isn't found (less likely for full HTML)
                html_content += js_injection_code
                logger.warning(
                    "</body> tag not found in generated HTML. Appending JS code."
                )

            # 3. Write the modified HTML content to the file
            logger.info(f"Saving modified family tree HTML to: {self.output_file}")
            with open(self.output_file, "w", encoding="utf-8") as f:
                f.write(html_content)

            logger.info(f"Successfully generated and saved {self.output_file}")
        except Exception as e:
            logger.exception(f"Error generating or saving pyvis HTML file: {e}")
            raise IOError(f"Failed to write Pyvis HTML: {e}") from e

    def _get_pyvis_graph_options(self):
        # Define options (keep as is, seems reasonable)
        options = {
            "physics": {
                "enabled": True,
                "barnesHut": {
                    "gravitationalConstant": -15000,
                    "centralGravity": 0.15,
                    "springLength": 120,
                    "springConstant": 0.05,
                    "damping": 0.15,
                    "avoidOverlap": 0.8,
                },
                "minVelocity": 0.75,
                "solver": "barnesHut",
            },
            "interaction": {
                "hover": True,
                "tooltipDelay": 300,
                "navigationButtons": True,
                "keyboard": {"enabled": True},
            },
            "nodes": {
                "font": {
                    "size": 14,  # Already set in add_or_update_node_from_proto_object, maybe remove redundancy?
                    "color": COLOR_PALETTLE.get("white", "#FFFFFF"),
                }
            },
            "edges": {
                "smooth": {"enabled": True, "type": "dynamic"},
                "arrows": {"to": {"enabled": True, "scaleFactor": 0.5}},
                "color": {
                    "color": COLOR_PALETTLE.get("light blue", "#97DDE7"),
                    "highlight": COLOR_PALETTLE.get("white", "#FFFFFF"),
                    "hover": COLOR_PALETTLE.get("white", "#FFFFFF"),
                },
            },
        }
        return options

    def print_member_details(self, member_id):
        member = self.family_tree.members[member_id]
        print(f"Member Details ({member_id}):\n{member}")

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
                print(self.output_proto_data_file)
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

    def get_member_fields_from_proto_schema(self):
        # This method seems unused currently. Keep or remove?
        try:
            family_member_descriptor = family_tree_pb2.FamilyMember.DESCRIPTOR
            field_names = [field.name for field in family_member_descriptor.fields]
            return field_names
        except Exception as e:
            logger.error(f"Error getting member fields from schema: {e}")
            return []

    def get_enum_values_from_proto_schema(self, enum_name, proto_module=utils_pb2):
        """Retrieves the valid string names for a given enum from the protobuf schema."""
        try:
            enum_descriptor = proto_module.DESCRIPTOR.enum_types_by_name.get(enum_name)
            if enum_descriptor:
                # Return names, including the default/unknown (usually index 0)
                return [value.name for value in enum_descriptor.values]
            else:
                logger.error(
                    f"Enum '{enum_name}' not found in {proto_module.__name__}."
                )
                return []
        except AttributeError as e:
            logger.error(f"Error accessing descriptor for enum '{enum_name}': {e}")
            return []
        except Exception as e:
            logger.exception(
                f"An unexpected error occurred getting enum values for '{enum_name}': {e}"
            )
            return []

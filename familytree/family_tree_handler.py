import json
import logging  # Added
import os
import pathlib
import random
import string

import google.protobuf.text_format as text_format
import networkx as nx
from google.protobuf.json_format import MessageToDict
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
    Utility class for handling date parsing and population for FamilyMember protobufs.
    Methods return True if processing was successful (or no relevant data was found),
    and False if invalid data was encountered that prevented setting the field.
    """

    @staticmethod
    def populate_gregorian_date(date_proto, input_data, prefix) -> bool:
        """
        Populates a GregorianDate protobuf message from input data.

        Args:
            date_proto: The GregorianDate message to populate (e.g., member.date_of_birth).
            input_data: The dictionary containing potential date parts.
            prefix: The prefix for the keys in input_data (e.g., "dob", "dod").

        Returns:
            True if the date was successfully populated or no relevant input was found.
            False if invalid data (e.g., non-integer, out of range) was provided.
        """
        try:
            # Get values, defaulting to 0 if not present or not convertible
            day = int(input_data.get(f"{prefix}_date", 0) or 0)
            month = int(input_data.get(f"{prefix}_month", 0) or 0)
            year = int(input_data.get(f"{prefix}_year", 0) or 0)

            # Check if any date part was actually provided
            if not day and not month and not year:
                return True  # No data provided, nothing to validate or set, success.

            # Basic validation
            # TODO: Add more robust date validation (e.g., check days in month) if needed
            if year > 1000 and 1 <= month <= 12 and 1 <= day <= 31:
                date_proto.date = day
                date_proto.month = month
                date_proto.year = year
                return True  # Successfully populated
            else:
                logger.warning(
                    f"Invalid Gregorian date parts provided for prefix '{prefix}': "
                    f"Day={day}, Month={month}, Year={year}. Field will be cleared."
                )
                return False  # Invalid data provided

        except (ValueError, TypeError) as e:
            logger.warning(
                f"Non-integer or invalid value encountered for '{prefix}' date parts: {e}. "
                f"Field will be cleared."
            )
            return False  # Type error during conversion
        except Exception as e:
            logger.exception(
                f"Unexpected error populating Gregorian date for prefix '{prefix}': {e}"
            )
            return False  # Unexpected error

    @staticmethod
    def populate_traditional_date(
        trad_date_proto,
        input_data,
        prefix,
        month_enum,
        star_enum=None,
        paksham_enum=None,
        thithi_enum=None,
    ) -> bool:
        """
        Populates a TraditionalDate protobuf message from input data using enums.

        Args:
            trad_date_proto: The TraditionalDate message to populate.
            input_data: The dictionary containing potential date parts.
            prefix: The prefix for the keys in input_data (e.g., "dob", "dod").
            month_enum: The protobuf enum type for the Tamil month.
            star_enum: Optional protobuf enum type for the Tamil star.
            paksham_enum: Optional protobuf enum type for Paksham.
            thithi_enum: Optional protobuf enum type for Thithi.

        Returns:
            True if the date was successfully populated or no relevant input was found.
            False if an invalid enum value string was provided.
        """
        try:
            # Assume success unless an invalid enum value is found
            success = True
            field_updated = False  # Track if we actually set any field

            month_str = input_data.get(f"{prefix}_traditional_month")
            if month_str and month_str != month_enum.Name(
                0
            ):  # Check against default "UNKNOWN"
                try:
                    trad_date_proto.month = month_enum.Value(month_str)
                    field_updated = True
                except ValueError:
                    logger.warning(
                        f"Invalid traditional month value '{month_str}' for prefix '{prefix}'. "
                        f"Traditional date field will be cleared."
                    )
                    success = False

            if star_enum and success:  # Only proceed if previous steps were okay
                star_str = input_data.get(f"{prefix}_traditional_star")
                if star_str and star_str != star_enum.Name(0):
                    try:
                        trad_date_proto.star = star_enum.Value(star_str)
                        field_updated = True
                    except ValueError:
                        logger.warning(
                            f"Invalid traditional star value '{star_str}' for prefix '{prefix}'. "
                            f"Traditional date field will be cleared."
                        )
                        success = False

            if paksham_enum and success:
                paksham_str = input_data.get(f"{prefix}_traditional_paksham")
                if paksham_str and paksham_str != paksham_enum.Name(0):
                    try:
                        trad_date_proto.paksham = paksham_enum.Value(paksham_str)
                        field_updated = True
                    except ValueError:
                        logger.warning(
                            f"Invalid traditional paksham value '{paksham_str}' for prefix '{prefix}'. "
                            f"Traditional date field will be cleared."
                        )
                        success = False

            if thithi_enum and success:
                thithi_str = input_data.get(f"{prefix}_traditional_thithi")
                if thithi_str and thithi_str != thithi_enum.Name(0):
                    try:
                        trad_date_proto.thithi = thithi_enum.Value(thithi_str)
                        field_updated = True
                    except ValueError:
                        logger.warning(
                            f"Invalid traditional thithi value '{thithi_str}' for prefix '{prefix}'. "
                            f"Traditional date field will be cleared."
                        )
                        success = False

            # If no fields were updated and success is still true, it means no data was provided.
            # If fields were updated and success is true, it means valid data was provided.
            # If success is false, it means invalid data was provided.
            return success

        except Exception as e:
            logger.exception(
                f"Unexpected error populating traditional date for prefix '{prefix}': {e}"
            )
            return False  # Unexpected error


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

    def create_node(self, input_dict):
        """Creates a new FamilyMember node and adds it to the family tree."""
        member_id = self.generate_member_id()
        member = family_tree_pb2.FamilyMember()
        member.id = member_id
        member.name = input_dict.get("name", "").strip()
        if not member.name:
            logger.error("Cannot create node with empty name.")
            # Consider raising ValueError("Cannot create node with empty name.")
            return None  # Return None or raise error

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

        # --- Use DateUtility for DOB ---
        # Check if DOB data was intended (e.g., not explicitly marked as unknown in GUI)
        # The GUI logic prevents sending dob_date etc. if the "unknown" checkbox is checked.
        # So, if the keys exist, we attempt to populate.
        if (
            "dob_date" in input_dict
            or "dob_month" in input_dict
            or "dob_year" in input_dict
        ):
            dob_success = DateUtility.populate_gregorian_date(
                member.date_of_birth, input_dict, "dob"
            )
            if not dob_success:
                # Clear the field if population failed due to invalid data
                member.ClearField("date_of_birth")
                logger.info(
                    f"Cleared date_of_birth for {member.name} due to invalid input."
                )

        # Check if traditional DOB data was provided
        if (
            "dob_traditional_month" in input_dict
            or "dob_traditional_star" in input_dict
        ):
            trad_dob_success = DateUtility.populate_traditional_date(
                member.traditional_date_of_birth,
                input_dict,
                "dob",
                utils_pb2.TamilMonth,
                star_enum=utils_pb2.TamilStar,
            )
            if not trad_dob_success:
                # Clear the field if population failed due to invalid enum value
                member.ClearField("traditional_date_of_birth")
                logger.info(
                    f"Cleared traditional_date_of_birth for {member.name} due to invalid input."
                )

        member.alive = input_dict.get("IsAlive", True)

        if not member.alive:
            # --- Use DateUtility for DOD ---
            # Check if DOD data was intended
            if (
                "dod_date" in input_dict
                or "dod_month" in input_dict
                or "dod_year" in input_dict
            ):
                dod_success = DateUtility.populate_gregorian_date(
                    member.date_of_death, input_dict, "dod"
                )
                if not dod_success:
                    member.ClearField("date_of_death")
                    logger.info(
                        f"Cleared date_of_death for {member.name} due to invalid input."
                    )

            # Check if traditional DOD data was provided
            if (
                "dod_traditional_month" in input_dict
                or "dod_traditional_paksham" in input_dict
                or "dod_traditional_thithi" in input_dict
            ):
                trad_dod_success = DateUtility.populate_traditional_date(
                    member.traditional_date_of_death,
                    input_dict,
                    "dod",
                    utils_pb2.TamilMonth,
                    paksham_enum=utils_pb2.Paksham,
                    thithi_enum=utils_pb2.Thithi,
                )
                if not trad_dod_success:
                    member.ClearField("traditional_date_of_death")
                    logger.info(
                        f"Cleared traditional_date_of_death for {member.name} due to invalid input."
                    )

        # Add to the protobuf structure
        self.family_tree.members[member_id].CopyFrom(member)
        # Add to the networkx graph
        self.add_node_from_proto_object(member)
        logger.info(f"Created node with ID: {member_id}, Name: {member.name}")
        return member_id  # Return the ID of the created member

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
                # FIXME: This implies that bool fields of false (Eg: alive) are also missed out
                if value:  # Only show non-empty fields
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

    def add_node_from_proto_object(self, member: family_tree_pb2.FamilyMember):
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
                self.add_node_from_proto_object(member)
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
                    "size": 14,  # Already set in add_node_from_proto_object, maybe remove redundancy?
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

        try:
            options_json = json.dumps(options)
            pyvis_network_graph.set_options(options_json)
        except TypeError as e:
            logger.error(f"Error serializing pyvis options to JSON: {e}")
            # Continue without options? Or raise?

        # Generate the HTML file
        try:
            logger.info(f"Saving family tree HTML to: {self.output_file}")
            # Ensure the file is written with UTF-8 encoding, Pyvis should handle this
            # pyvis_network_graph.show(self.output_file, notebook=False)
            pyvis_network_graph.write_html(self.output_file, notebook=False)
            logger.info(f"Successfully generated {self.output_file}")
        except Exception as e:
            logger.exception(f"Error generating pyvis HTML file: {e}")
            # Re-raise the exception so the GUI knows rendering failed
            raise IOError(f"Failed to write Pyvis HTML: {e}") from e

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

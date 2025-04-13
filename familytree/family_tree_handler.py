import os
import json
import google.protobuf.text_format as text_format
from google.protobuf.json_format import MessageToDict
from pyvis.network import Network
import networkx as nx
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


# --- Remove or comment out this entire function ---
# def get_vis_js_resource(file_path):
#     # Copy vis.js to the output directory
#     vis_js_resource = "vis-network.min.js"
#
#     parent_dir = os.path.dirname(file_path)
#     vis_js_destination = os.path.join(parent_dir, vis_js_resource)
#     os.makedirs(parent_dir, exist_ok=True)
#
#     if vis_js_resource in os.listdir(parent_dir):
#         return
#
#     try:
#         # Use pkg_resources to find the vis-network.min.js file
#         pyvis_path = pkg_resources.resource_filename("pyvis", "")
#         # As this need not be present in the package directory itself
#         resource_files_generator = pathlib.Path(pyvis_path).rglob(vis_js_resource)
#         resource_files_list = [str(file) for file in resource_files_generator]
#         # Pick the last file
#         vis_js_source = resource_files_list[-1]
#     except ImportError:
#         print(f"Error: Could not find {vis_js_resource} in pyvis package.")
#         return
#     except Exception as e: # Catch potential pkg_resources errors more broadly
#         print(f"Error finding {vis_js_resource} via pkg_resources: {e}")
#         return
#
#     try:
#         shutil.copy2(vis_js_source, vis_js_destination)
#         print(f"Copied vis.js to the {parent_dir} directory.")
#     except Exception as e:
#         print(f"Error copying {vis_js_resource}: {e}")
# --- End of function removal ---


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

        self.used_member_ids = set()
        # FIXME: Re-think if we need used_member_ids, or if we can simply rely on self.family_tree.members.keys
        # The second option is hashable. But it doesn't easily account for the case where there is a mismatch between
        # tree's key as an ID and member.id.

    # ... (other methods like update_data_source, etc.) ...

    def load_from_protobuf(self):
        print(f"Loading data from: {self.input_file}")
        try:
            # Ensure file exists before opening
            if not self.input_file or not os.path.exists(self.input_file):
                raise FileNotFoundError(
                    f"Input file not specified or not found: {self.input_file}"
                )

            with open(self.input_file, "r", encoding="utf-8") as f:  # Specify encoding
                text_format.Merge(f.read(), self.family_tree)
                print(f"Successfully loaded {self.input_file}")
        except FileNotFoundError as e:
            print(f"File not found: {e}")
            raise  # Re-raise for GUI to handle
        except text_format.ParseError as e:
            print(f"Error parsing protobuf text file {self.input_file}: {e}")
            raise  # Re-raise for GUI
        except Exception as e:
            print(f"An unexpected error occurred during loading: {e}")
            raise  # Re-raise for GUI

        # Populate nodes and edges
        self.populate_nodes_and_edges()
        # Update the set of used member IDs after loading
        self.update_used_member_ids()

    # --- Modify get_default_images ---
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
                "OTHER": "person.jpg",  # Make sure this file exists
                "GENDER_UNKNOWN": "person.jpg",  # Make sure this file exists
            }
            broken_image_file = "broken.gif"  # Make sure this file exists

            for key, filename in default_image_files.items():
                path = images_dir / filename
                if path.is_file():
                    default_images[key] = str(path)  # Store as string path
                else:
                    print(f"Warning: Default image not found for {key} at {path}")

            broken_path = images_dir / broken_image_file
            if broken_path.is_file():
                brokenImage = str(broken_path)
            else:
                print(f"Warning: Broken image not found at {broken_path}")

        except Exception as e:
            print(f"Error determining default image paths: {e}")
            # Return empty dicts/strings on error
            default_images = {}
            brokenImage = ""

        return default_images, brokenImage

    # --- End modification ---

    def generate_member_id(self):
        """Generates a unique random 4-character alphanumeric member ID."""
        # Use a larger keyspace or check against existing IDs more robustly if collisions become likely
        chars = string.ascii_uppercase + string.digits
        while True:
            member_id = "".join(random.choices(chars, k=4))
            # Check against actual keys in the protobuf map for ground truth
            if member_id not in self.family_tree.members:
                # No need to maintain self.used_member_ids separately if we always check self.family_tree.members
                # self.used_member_ids.add(member_id) # Can be removed
                return member_id

    def create_node(self, input_dict):
        """Creates a new FamilyMember node and adds it to the family tree."""
        member_id = self.generate_member_id()
        member = family_tree_pb2.FamilyMember()
        member.id = member_id
        member.name = input_dict.get("name", "").strip()  # Ensure name is stripped
        if not member.name:
            # This should ideally be caught by GUI validation, but double-check here
            print("Error: Cannot create node with empty name.")
            return  # Or raise an error

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
            print(
                f"Warning: Invalid gender value '{input_dict.get('gender')}' for {member.name}. Setting to UNKNOWN."
            )
            member.gender = utils_pb2.GENDER_UNKNOWN  # Use the enum value directly

        # --- Simplified Date Handling ---
        def set_date_field(date_proto, input_data, prefix):
            try:
                day = int(input_data.get(f"{prefix}_date", 0))
                month = int(input_data.get(f"{prefix}_month", 0))
                year = int(input_data.get(f"{prefix}_year", 0))
                # Basic validation: Check if year, month, day seem plausible (though not calendar accurate here)
                if year > 1000 and 1 <= month <= 12 and 1 <= day <= 31:
                    date_proto.date = day
                    date_proto.month = month
                    date_proto.year = year
                elif day or month or year:  # If any part was provided but invalid
                    print(
                        f"Warning: Invalid {prefix.upper()} date provided for {member.name}. Clearing field."
                    )
                    member.ClearField(
                        f"date_of_{prefix}"
                    )  # Clear the specific date field
            except (ValueError, TypeError):
                print(
                    f"Warning: Non-integer {prefix.upper()} date value for {member.name}. Clearing field."
                )
                member.ClearField(f"date_of_{prefix}")

        def set_traditional_date_field(
            trad_date_proto,
            input_data,
            prefix,
            month_enum,
            star_enum=None,
            paksham_enum=None,
            thithi_enum=None,
        ):
            try:
                month_str = input_data.get(f"{prefix}_traditional_month")
                if month_str and month_str != month_enum.Name(0):
                    trad_date_proto.month = month_enum.Value(month_str)

                if star_enum:
                    star_str = input_data.get(f"{prefix}_traditional_star")
                    if star_str and star_str != star_enum.Name(0):
                        trad_date_proto.star = star_enum.Value(star_str)
                if paksham_enum:
                    paksham_str = input_data.get(f"{prefix}_traditional_paksham")
                    if paksham_str and paksham_str != paksham_enum.Name(0):
                        trad_date_proto.paksham = paksham_enum.Value(paksham_str)
                if thithi_enum:
                    thithi_str = input_data.get(f"{prefix}_traditional_thithi")
                    if thithi_str and thithi_str != thithi_enum.Name(0):
                        trad_date_proto.thithi = thithi_enum.Value(thithi_str)

            except ValueError:
                print(
                    f"Warning: Invalid traditional {prefix.upper()} enum value for {member.name}. Skipping."
                )
                member.ClearField(f"traditional_date_of_{prefix}")

        # --- End Simplified Date Handling ---

        # Handle DOB (only if known via checkbox in GUI)
        if "dob_date" in input_dict:
            set_date_field(member.date_of_birth, input_dict, "dob")

        # Handle traditional DOB
        set_traditional_date_field(
            member.traditional_date_of_birth,
            input_dict,
            "dob",
            utils_pb2.TamilMonth,
            star_enum=utils_pb2.TamilStar,
        )

        member.alive = input_dict.get("IsAlive", True)

        if not member.alive:
            # Handle DOD (only if known via checkbox in GUI)
            if "dod_date" in input_dict:
                set_date_field(member.date_of_death, input_dict, "dod")

            # Handle traditional DOD
            set_traditional_date_field(
                member.traditional_date_of_death,
                input_dict,
                "dod",
                utils_pb2.TamilMonth,
                paksham_enum=utils_pb2.Paksham,
                thithi_enum=utils_pb2.Thithi,
            )

        # Add to the protobuf structure
        self.family_tree.members[member_id].CopyFrom(member)
        # Add to the networkx graph
        self.add_node_from_proto_object(member)
        print(f"Created node with ID: {member_id}, Name: {member.name}")
        # Consider returning the member_id or member object if needed by caller

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
            print(f"Warning: Could not format member {member.id} for tooltip: {e}")
            # Fallback to simple text format
            try:
                title_str = text_format.MessageToString(member, as_utf8=True)
            except Exception:
                title_str = f"Error generating title for {member.id}"  # Final fallback
        return title_str

    def add_node_from_proto_object(self, member: family_tree_pb2.FamilyMember):
        member_id = member.id
        if not member_id:
            print(
                f"Warning: Skipping node creation for member without ID: {member.name}"
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
                print(
                    f"Warning: Provided image_location does not exist: {image_location}"
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

        # --- Remove the call to get_vis_js_resource ---
        # if final_image_path and os.path.exists(final_image_path):
        #     if not final_image_path.startswith(('http://', 'https://')):
        #         # get_vis_js_resource(final_image_path) # REMOVE THIS LINE
        #         pass # No action needed here for local images
        # --- End removal ---

        # Add or update the node in the networkx graph
        if member_id not in self.nx_graph:
            self.nx_graph.add_node(member_id, **node_options)
        else:
            # Update existing node data
            self.nx_graph.nodes[member_id].update(node_options)
            print(f"Updated node data for existing node: {member_id}")

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
        self.nx_graph.clear()
        print("Populating graph nodes...")
        # Use list comprehension for potentially slightly better performance if tree is large
        members_to_process = list(self.family_tree.members.items())

        for member_id_in_tree, member in members_to_process:
            # Ensure consistency between map key and member.id
            actual_member_id = member.id
            if not actual_member_id:
                print(
                    f"Warning: Skipping member with key '{member_id_in_tree}' due to missing member.id."
                )
                continue
            if member_id_in_tree != actual_member_id:
                print(
                    f"Warning: Mismatch between map key '{member_id_in_tree}' and member.id '{actual_member_id}'. Using member.id."
                )
                # Consider if the key in the map should be corrected if possible, or just log

            # Check if member object itself is valid before adding node
            if member.IsInitialized():
                self.add_node_from_proto_object(member)
            else:
                # This might indicate an issue during protobuf parsing or creation
                print(
                    f"Warning: Skipping uninitialized member with ID {actual_member_id}."
                )

        print("Populating graph edges...")
        # Use list comprehension for potentially slightly better performance
        relationships_to_process = list(self.family_tree.relationships.items())

        for member_id, relationships in relationships_to_process:
            # Ensure the member_id for relationships exists as a node
            if member_id not in self.nx_graph:
                print(
                    f"Warning: Skipping relationships for non-existent member ID: {member_id}"
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
                    print(
                        f"Warning: Spouse ID {spouse_id} not found for member {member_id}. Skipping edge."
                    )

            # Add edges between parents and children
            for child_id in relationships.children_ids:
                if member_id == child_id:
                    continue  # Skip self-loops
                if child_id in self.nx_graph:
                    self.add_child_edges(member_id, child_id)
                else:
                    print(
                        f"Warning: Child ID {child_id} not found for parent {member_id}. Skipping edge."
                    )

    def update_used_member_ids(self):
        """Updates the set of used member IDs from the loaded protobuf data."""
        # Rely solely on the keys from the members map as the source of truth for existing IDs
        self.used_member_ids = set(self.family_tree.members.keys())
        print(
            f"Refreshed used member IDs from protobuf. Count: {len(self.used_member_ids)}"
        )

    def merge_another_tree(
        self, new_tree: family_tree_pb2.FamilyTree, connecting_member_id=None
    ):
        # TODO: Implement merging logic
        print("Warning: merge_another_tree is not yet implemented.")
        pass

    # --- Modify display_family_tree ---
    def display_family_tree(self):
        # Ensure the output directory exists
        output_dir = os.path.dirname(self.output_file)
        try:
            os.makedirs(output_dir, exist_ok=True)
            # print(f"Ensured output directory exists: {output_dir}") # Less verbose
        except OSError as e:
            print(f"Error creating output directory {output_dir}: {e}")
            # Handle error appropriately, maybe raise to GUI
            raise IOError(f"Cannot create output directory: {e}") from e

        # Check if graph has nodes before trying to render
        if not self.nx_graph:
            print("NetworkX graph is empty. Cannot generate Pyvis graph.")
            # Optionally, create an empty HTML file or handle in GUI
            # For now, just return to prevent Pyvis errors
            # You might want to write a placeholder HTML:
            # with open(self.output_file, "w", encoding='utf-8') as f:
            #     f.write("<html><body style='background-color: #222; color: #fff;'><p>No family tree data loaded.</p></body></html>")
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
            print(f"Error serializing pyvis options to JSON: {e}")
            # Continue without options? Or raise?

        # --- Remove call to get_vis_js_resource ---
        # get_vis_js_resource(self.output_file) # REMOVE THIS LINE
        # --- End removal ---

        # Generate the HTML file
        try:
            print(f"Saving family tree HTML to: {self.output_file}")
            # Ensure the file is written with UTF-8 encoding, Pyvis should handle this
            pyvis_network_graph.show(self.output_file, notebook=False)
            print(f"Successfully generated {self.output_file}")
        except Exception as e:
            print(f"Error generating pyvis HTML file: {e}")
            # Re-raise the exception so the GUI knows rendering failed
            raise IOError(f"Failed to write Pyvis HTML: {e}") from e

    # --- End modification ---

    def print_member_details(self, member_id):
        member = self.family_tree.members[member_id]
        print(member)

    def save_to_protobuf(self):
        # Ensure the output directory exists
        output_dir = os.path.dirname(self.output_proto_data_file)
        try:
            os.makedirs(output_dir, exist_ok=True)
        except OSError as e:
            print(f"Error creating output directory {output_dir}: {e}")
            raise IOError(f"Cannot create output directory for saving: {e}") from e

        try:
            protobuf_string = text_format.MessageToString(
                self.family_tree, as_utf8=True
            )
            with open(self.output_proto_data_file, "w", encoding="utf-8") as f:
                f.write(protobuf_string)
                print(f"Successfully saved data to {self.output_proto_data_file}")
        except IOError as e:
            print(
                f"Error writing protobuf data to file {self.output_proto_data_file}: {e}"
            )
            raise  # Re-raise for GUI
        except Exception as e:
            print(f"An unexpected error occurred during saving: {e}")
            raise  # Re-raise for GUI

    def get_member_fields_from_proto_schema(self):
        # This method seems unused currently. Keep or remove?
        try:
            family_member_descriptor = family_tree_pb2.FamilyMember.DESCRIPTOR
            field_names = [field.name for field in family_member_descriptor.fields]
            return field_names
        except Exception as e:
            print(f"Error getting member fields from schema: {e}")
            return []

    def get_enum_values_from_proto_schema(self, enum_name, proto_module=utils_pb2):
        """Retrieves the valid string names for a given enum from the protobuf schema."""
        try:
            enum_descriptor = proto_module.DESCRIPTOR.enum_types_by_name.get(enum_name)
            if enum_descriptor:
                # Return names, including the default/unknown (usually index 0)
                return [value.name for value in enum_descriptor.values]
            else:
                print(
                    f"Error: Enum '{enum_name}' not found in {proto_module.__name__}."
                )
                return []
        except AttributeError as e:
            print(f"Error accessing descriptor for enum '{enum_name}': {e}")
            return []
        except Exception as e:
            print(
                f"An unexpected error occurred getting enum values for '{enum_name}': {e}"
            )
            return []

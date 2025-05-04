import json
import logging
import os
import pathlib

import networkx as nx
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pyvis.network import Network
from utils import ResourceUtility

# Get a logger instance for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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


class GraphHandler:
    """
    Utility class for handling graph operations.
    """

    def __init__(self, output_html_file=None):
        self.nx_graph = nx.DiGraph()
        self.output_html_file = output_html_file

    def update_output_html_file(self, output_html_file):
        self.output_html_file = output_html_file

    def add_node_in_graph(
        self,
        member_id: str,
        member_name: str,
        title_str: str,
        final_image_path: str,
        brokenImage: str,
    ):
        node_options = {
            "label": member_name,
            "title": title_str,
            "shape": "circularImage" if final_image_path else "dot",
            "image": final_image_path if final_image_path else None,
            "brokenImage": brokenImage,
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

    def add_child_edges(self, parent_id, child_id):
        """Adds edges representing parent-child relationship."""
        # Add the visible parent -> child edge (e.g., weight=1 or default)
        # Using weight=1 to distinguish from spouse edges (weight=0)
        self.nx_graph.add_edge(parent_id, child_id, weight=1)

        # Add the hidden child -> parent edge (weight=-1) for relationship tracing
        hidden_edge_weight = -1
        self.nx_graph.add_edge(child_id, parent_id, weight=hidden_edge_weight)
        logger.debug(
            f"Added hidden edge {child_id}->{parent_id} with weight {hidden_edge_weight}"
        )

    # --- Modify display_family_tree ---
    def display_family_tree(self):
        self._create_dir_to_save_html()
        graph_to_render = self._sanitycheck_and_filter_graph()

        pyvis_networkx_graph = Network(
            directed=True,
            notebook=False,
            bgcolor=COLOR_PALETTLE.get("gray", "#222222"),
            font_color=COLOR_PALETTLE.get("white", "#FFFFFF"),
            cdn_resources="in_line",
            height="1000px",  # Consider making height/width dynamic or configurable
            width="100%",
        )
        # Pass the filtered graph to pyvis
        if not graph_to_render:
            return
        pyvis_networkx_graph.from_nx(graph_to_render)

        options = self._get_pyvis_graph_options()

        try:
            options_json = json.dumps(options)
            pyvis_networkx_graph.set_options(options_json)
        except TypeError as e:
            logger.error(f"Error serializing pyvis options to JSON: {e}")
            # Continue without options? Or raise?
        self._generate_html_from_pyvis_graph(pyvis_networkx_graph)

    def _create_dir_to_save_html(self):
        # Ensure the output directory exists
        output_dir = os.path.dirname(self.output_html_file)
        try:
            os.makedirs(output_dir, exist_ok=True)
        except OSError as e:
            logger.error(f"Error creating output directory {output_dir}: {e}")
            # Handle error appropriately, maybe raise to GUI
            raise IOError(f"Cannot create output directory: {e}") from e

    def _get_js_injection_code(self) -> str:
        # JavaScript Injection for Double Click
        js_injection_code = ""  # Initialize to empty string
        try:
            qwebchannel_js_path = str(ResourceUtility.get_resource("qwebchannel.js"))
            logger.debug(f"qwebchannel.js path: {qwebchannel_js_path}")
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
                template_loader = FileSystemLoader(
                    searchpath=str(ResourceUtility.get_resource())
                )
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
        return js_injection_code

    def _sanitycheck_and_filter_graph(self):
        # Check if graph has nodes before trying to render
        if not self.nx_graph.nodes:
            logger.info("NetworkX graph is empty. Cannot render.")
            with open(self.output_html_file, "w", encoding="utf-8") as f:
                f.write(
                    "<html><body style='background-color: #222; color: #fff;'><p>No family tree data loaded.</p></body></html>"
                )
            return

        # --- Filter the graph before passing to pyvis ---
        # Define the weight used for hidden parent edges
        hidden_edge_weight = -1
        logger.info(
            f"Filtering out edges with weight {hidden_edge_weight} for display."
        )
        # Get the filtered graph (which is a new nx.Graph instance)
        filtered_graph = self._filter_graph_by_weight(hidden_edge_weight)
        # --- End filtering ---
        # Check if the filtered graph is empty (might happen if only hidden edges existed)
        if not filtered_graph:
            logger.warning("Filtered graph is empty. Displaying empty visualization.")
            with open(self.output_html_file, "w", encoding="utf-8") as f:
                f.write(
                    "<html><body style='background-color: #222; color: #fff;'><p>Graph contains only hidden edges or filtering failed.</p></body></html>"
                )
            return
        return filtered_graph

    def _generate_html_from_pyvis_graph(self, pyvis_graph):
        # --- Generate HTML and Inject JS ---
        try:
            logger.info("Generating family tree HTML content...")
            # 1. Get the HTML content from pyvis first
            # Use generate_html() which returns the string
            html_content = pyvis_graph.generate_html(notebook=False)
            logger.info("HTML content generated.")

            # 2. Inject the JavaScript code before the closing </body> tag
            # A simple string replacement is usually sufficient
            js_injection_code = self._get_js_injection_code()
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
            logger.info(f"Saving modified family tree HTML to: {self.output_html_file}")
            with open(self.output_html_file, "w", encoding="utf-8") as f:
                f.write(html_content)

            logger.info(f"Successfully generated and saved {self.output_html_file}")
        except Exception as e:
            logger.exception(f"Error generating or saving pyvis HTML file: {e}")
            raise IOError(f"Failed to write Pyvis HTML: {e}") from e

    def _filter_graph_by_weight(self, weight_to_filter_out):
        """
        Creates a filtered NetworkX graph instance excluding edges with a specific weight.

        This uses a subgraph view for efficiency and then creates a new graph
        instance from that view, suitable for passing to libraries like Pyvis.

        Args:
            weight_to_filter_out: The weight value of edges to exclude.

        Returns:
            nx.Graph: A new NetworkX graph instance containing only the desired edges.
                      Note: This currently returns an undirected nx.Graph based on the
                      original implementation. If directionality needs to be strictly
                      preserved for Pyvis, consider returning nx.DiGraph(filtered_view).
        """
        if not isinstance(self.nx_graph, nx.DiGraph):
            logger.error("Filtering requires a valid NetworkX graph instance.")
            # Return an empty graph or raise an error, depending on desired handling
            return nx.DiGraph()

        # Define the filter function using a standard def for readability and debugging
        # This function returns True if the edge should be *kept*
        def filter_edge_func(u, v):
            # Access the original graph's data using get_edge_data for safety
            edge_data = self.nx_graph.get_edge_data(u, v, default={})
            # Keep the edge if its weight is NOT the one to filter out
            # Also keeps edges that don't have a 'weight' attribute (None != weight_to_filter_out)
            return edge_data.get("weight") != weight_to_filter_out

        try:
            # Create a subgraph view using the filter function
            # This view reflects the original graph but only shows allowed edges/nodes
            filtered_view = nx.subgraph_view(
                self.nx_graph, filter_edge=filter_edge_func
            )

            # Create a new concrete graph instance from the view.
            # Pyvis might work better with a concrete instance than a view.
            # NOTE: This converts to an undirected Graph. If the original was a DiGraph
            # and directionality is crucial for the pyvis layout/arrows,
            # you might need: filtered_graph = nx.DiGraph(filtered_view)
            # However, let's stick to the original code's use of nx.Graph for now.
            filtered_graph = nx.DiGraph(filtered_view)
            logger.info(
                f"Created filtered graph with {filtered_graph.number_of_nodes()} nodes and {filtered_graph.number_of_edges()} edges."
            )

            return filtered_graph

        except Exception as e:
            logger.exception(f"Error during graph filtering: {e}")
            # Return the original graph or an empty one in case of error?
            # Returning original might be safer if filtering fails unexpectedly.
            return self.nx_graph  # Fallback to original graph on error

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
                    "size": 14,  # Already set in prepare_node_attributes_for_member, maybe remove redundancy?
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

    def get_graph_summary_text(self, max_nodes: int = 100) -> str:
        """
        Generates a textual summary of the family tree graph for context.

        Args:
            max_nodes: The maximum number of nodes to detail to keep context concise.

        Returns:
            A string summarizing the graph nodes and basic relationships.
        """
        if not self.nx_graph or not self.nx_graph.nodes:
            return "The family tree data is not loaded or is empty."

        context_lines = ["Family Tree Summary:"]
        nodes_listed = 0

        # Sort nodes for consistent output (optional)
        sorted_nodes = sorted(
            self.nx_graph.nodes(data=True),
            key=lambda item: item[1].get("label", item[0]),
        )

        for node_id, data in sorted_nodes:
            if nodes_listed >= max_nodes:
                context_lines.append(
                    f"... (and {len(self.nx_graph.nodes) - max_nodes} more members)"
                )
                break

            label = data.get("label", f"ID: {node_id}")
            line = f"- {label} (ID: {node_id})"

            # Get relationships using graph edges
            successors = list(self.nx_graph.successors(node_id))
            # predecessors = list(self.nx_graph.predecessors(node_id))

            spouses = [
                s
                for s in successors
                if self.nx_graph.edges[node_id, s].get("weight") == 0
            ]

            children = [
                c
                for c in successors
                if self.nx_graph.edges[node_id, c].get("weight") == 1
            ]

            # Infer parents from hidden edges (weight=-1) pointing *from* this node
            # Cannot use predecessors because there'll be an edge from both spouse and child->parent.
            parents = [
                p
                for p in successors
                if self.nx_graph.edges[node_id, p].get("weight") == -1
            ]
            logger.info(line)
            logger.info(f"spouses: {spouses}")
            logger.info(f"children: {children}")
            logger.info(f"parents: {parents}")

            relation_info = []

            for s in spouses:
                spouse_name = self._get_node_info(s, only_label=True)
                relation_info.append(f"married to {spouse_name} whose ID is {s}")
            for c in children:
                child_name = self._get_node_info(c, only_label=True)
                relation_info.append(f"has child {child_name} whose ID is {c}")
            for p in parents:
                parent_name = self._get_node_info(p, only_label=True)
                relation_info.append(f"has parent {parent_name} whose ID is {p}")
            if relation_info:
                line += f" Relationships= [{'; '.join(relation_info)}];"

            personal_info = self._get_node_info(node_id)
            if personal_info:
                line += f" Personal Info= [{personal_info}]"

            context_lines.append(line)
            nodes_listed += 1

        return "\n".join(context_lines)

    def _get_node_info(self, node_id, only_label=False):
        if node_id in self.nx_graph.nodes:
            node_obj = self.nx_graph.nodes[node_id]
            node_label = node_obj.get("label", node_id)
            if only_label:
                return node_label
            else:
                node_title = node_obj.get("title", "")
                node_title_clear_string = node_title.replace("\n", "; ")
                return node_title_clear_string
        else:
            return None

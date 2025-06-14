import json
import logging
import os
from typing import Any, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape
from networkx import DiGraph
from pyvis.network import Network

from familytree.proto import family_tree_pb2
from familytree.proto.utils_pb2 import Gender
from familytree.utils import resource_utils as ResourceUtility
from familytree.utils.graph_types import EdgeType, GraphEdge, GraphNode

logger = logging.getLogger(__name__)

COLOR_PALETTE = {
    "cream": "#ffeabb",
    "light blue": "#97dde7",
    "light cream": "#e9ebdd",
    "gray": "#222222",
    "black": "#000000",
    "white": "#ffffff",
    "red": "#ff0000",
    "pink": "#f57db3",
}


class PyvisRenderer:
    """
    Renders a family tree graph (from the new GraphHandler format) into an HTML
    visualization using PyVis.
    """

    def __init__(self):
        self.jinja_env: Optional[Environment] = None
        try:
            # Ensure ResourceUtility.get_resource() returns the path to the 'resources' directory
            # where templates like 'pyvis_interaction.js.template' are located.
            resources_dir_path = ResourceUtility.get_resource()
            if not resources_dir_path.is_dir():
                logger.error(
                    f"Resources directory not found or not a directory: {resources_dir_path}"
                )
            else:
                template_loader = FileSystemLoader(searchpath=str(resources_dir_path))
                self.jinja_env = Environment(
                    loader=template_loader,
                    autoescape=select_autoescape(["html", "xml", "js"]),
                )
        except Exception as e:
            logger.error(
                f"Failed to initialize Jinja2 environment: {e}. JS injection might fail."
            )

    def _build_node_title_from_proto(
        self, member_proto: family_tree_pb2.FamilyMember
    ) -> str:
        """Constructs a multi-line title string for node tooltips from FamilyMember proto."""
        parts = []
        if member_proto.name:
            parts.append(f"Name: {member_proto.name}")
        if member_proto.id:
            parts.append(f"ID: {member_proto.id}")

        # Add more details from the proto as needed for the tooltip
        # Example: Date of Birth
        if member_proto.HasField("date_of_birth"):
            dob = member_proto.date_of_birth
            parts.append(f"DOB: {dob.year}-{dob.month:02d}-{dob.date:02d}")

        # Example: Date of Death
        if member_proto.HasField("date_of_death"):
            dod = member_proto.date_of_death
            parts.append(f"DOD: {dod.year}-{dod.month:02d}-{dod.date:02d}")

        if member_proto.additional_info:
            for key, value in member_proto.additional_info.items():
                parts.append(f"{key.replace('_', ' ').title()}: {value}")

        return "\n".join(parts)

    def _determine_node_image(
        self,
        member_proto: family_tree_pb2.FamilyMember,
        default_images_map: dict[str, str],
    ) -> Optional[str]:
        """Helper to determine the image URL for a node, prioritizing specific, then gender-based, then general default."""
        # pyrefly: ignore
        gender_key = Gender.Name(member_proto.gender).upper()
        return default_images_map.get(
            gender_key, default_images_map.get("GENDER_UNKNOWN")
        )

    def _prepare_pyvis_display_graph(self, source_nx_graph: DiGraph) -> DiGraph:
        """
        Creates a new DiGraph suitable for PyVis, transforming nodes and edges
        from the GraphHandler's format. Only visible nodes and edges are included.
        """
        pyvis_display_graph = DiGraph()
        default_images_map, global_broken_image_path = (
            ResourceUtility.get_default_images()
        )

        # Add all nodes
        for node_id, node_attributes_wrapper in source_nx_graph.nodes(data=True):
            graph_node_obj: Optional[GraphNode] = node_attributes_wrapper.get("data")
            if not graph_node_obj:
                continue

            member_proto = graph_node_obj.attributes
            title_str = self._build_node_title_from_proto(member_proto)
            actual_image_to_use = self._determine_node_image(
                member_proto, default_images_map
            )

            node_options: dict[str, Any] = {
                "label": member_proto.name if member_proto else str(node_id),
                "title": title_str,
                "shape": "circularImage" if actual_image_to_use else "dot",
                "image": actual_image_to_use,
                "brokenImage": global_broken_image_path,
                "size": 50,
                "font": {
                    "size": 14,
                    "color": COLOR_PALETTE.get("white", "#FFFFFF"),
                },
                "color": {"background": COLOR_PALETTE.get("light cream", "#E9EBDD")},
            }

            if graph_node_obj.is_poi:
                node_options["borderWidth"] = 3
                node_options["color"]["border"] = COLOR_PALETTE.get("red", "#FF0000")

            pyvis_display_graph.add_node(node_id, **node_options)

        # Add visible edges
        for u, v, edge_attributes_wrapper in source_nx_graph.edges(data=True):
            graph_edge_obj: Optional[GraphEdge] = edge_attributes_wrapper.get("data")
            if not graph_edge_obj or not graph_edge_obj.is_rendered:
                continue

            edge_options: dict[str, Any] = {
                "arrows": {"to": {"enabled": True, "scaleFactor": 0.5}}
            }
            edge_options.update(graph_edge_obj.attributes)

            if graph_edge_obj.edge_type == EdgeType.SPOUSE:
                edge_options["color"] = COLOR_PALETTE.get("pink", "#F57DB3")
                edge_options["arrows"] = {
                    "to": {"enabled": True, "scaleFactor": 0.5},
                    "from": {"enabled": True, "scaleFactor": 0.5},
                }
            elif graph_edge_obj.edge_type == EdgeType.PARENT_TO_CHILD:
                edge_options["color"] = COLOR_PALETTE.get("light blue", "#97DDE7")

            pyvis_display_graph.add_edge(u, v, **edge_options)

        return pyvis_display_graph

    def _get_pyvis_graph_options(self, node_font_color: str) -> str:
        """Returns the PyVis graph options dictionary."""
        return json.dumps(
            {
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
                        "size": 14,
                        "color": node_font_color,
                    }
                },
                "edges": {
                    "smooth": {"enabled": True, "type": "dynamic"},
                    "arrows": {"to": {"enabled": True, "scaleFactor": 0.5}},
                    "color": {  # Default edge color
                        "color": COLOR_PALETTE.get("light blue", "#97DDE7"),
                        "highlight": COLOR_PALETTE.get("white", "#FFFFFF"),
                        "hover": COLOR_PALETTE.get("white", "#FFFFFF"),
                    },
                },
            }
        )

    def _get_font_color(self, theme: str) -> str:
        return (
            COLOR_PALETTE.get("white", "#FFFFFF")
            if theme == "dark"
            else COLOR_PALETTE.get("black", "#000000")
        )

    def _get_background_color(self, theme: str) -> str:
        return (
            COLOR_PALETTE.get("gray", "#222222")
            if theme == "dark"
            else COLOR_PALETTE.get("white", "#FFFFFF")
        )

    def _create_dir_if_not_exists(self, file_path: str) -> None:
        """Ensures the directory for the given file_path exists."""
        output_dir = os.path.dirname(file_path)
        if (
            output_dir
        ):  # Ensure output_dir is not empty (e.g. for relative paths in current dir)
            try:
                os.makedirs(output_dir, exist_ok=True)
            except OSError as e:
                logger.error(f"Error creating output directory {output_dir}: {e}")
                raise IOError(f"Cannot create output directory: {e}") from e

    def _write_html_to_file(self, html_content: str, file_path: str) -> None:
        """Writes the given HTML content to the specified file path."""
        self._create_dir_if_not_exists(file_path)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            logger.info(f"Successfully generated and saved HTML to {file_path}")
        except IOError as e:
            logger.error(f"Failed to write HTML to {file_path}: {e}")
            # Depending on desired behavior, you might want to re-raise here
            # or let the caller decide if this is a critical failure.

    def _handle_empty_graph(
        self, output_html_file_path: Optional[str], theme: str = "light"
    ) -> str:
        """Handles the case where the source graph is empty."""
        logger.info("Source NetworkX graph is empty. Cannot render.")
        bg_color = self._get_background_color(theme)
        text_color = self._get_font_color(theme)
        empty_html = f"<html><body style='background-color: {bg_color}; color: {text_color};'><p>No family tree data to display.</p></body></html>"
        if output_html_file_path:
            self._write_html_to_file(empty_html, output_html_file_path)
        return empty_html

    def render_graph_to_html(
        self,
        source_nx_graph: DiGraph,
        theme: str,
        output_html_file_path: Optional[str] = None,
    ) -> str:
        """
        Renders the given NetworkX graph (from GraphHandler) to an HTML string
        and optionally saves it to a file.

        Args:
            source_nx_graph: The NetworkX DiGraph from GraphHandler.
            output_html_file_path: Optional path to save the generated HTML.
            theme: The current theme ('light' or 'dark') to adjust background.

        Returns:
            An HTML string representing the visualized graph.
        """
        if not source_nx_graph or not source_nx_graph.nodes:
            return self._handle_empty_graph(output_html_file_path, theme)

        pyvis_display_graph: DiGraph = self._prepare_pyvis_display_graph(
            source_nx_graph
        )
        bg_color = self._get_background_color(theme)
        text_color = self._get_font_color(theme)

        # Handle case where filtering results in an empty graph for PyVis
        if not pyvis_display_graph or not pyvis_display_graph.nodes:
            logger.info(
                "Prepared PyVis graph is empty (no visible nodes/edges after filtering). Cannot render."
            )
            empty_filtered_html = f"<html><body style='background-color: {bg_color}; color: {text_color};'><p>No visible family members to display based on current filters.</p></body></html>"
            if output_html_file_path:
                self._write_html_to_file(empty_filtered_html, output_html_file_path)
            return empty_filtered_html

        pyvis_network = Network(
            directed=True,
            notebook=False,
            bgcolor=bg_color,
            font_color=text_color,
            cdn_resources="in_line",  # For offline compatibility
            height="1000px",
            width="100%",
        )

        pyvis_network.from_nx(pyvis_display_graph)

        try:
            options_str = self._get_pyvis_graph_options(text_color)
            pyvis_network.set_options(options_str)
        except TypeError as e:
            logger.error(f"Error serializing pyvis options to JSON: {e}")

        html_content = pyvis_network.generate_html(notebook=False)

        if output_html_file_path:
            self._write_html_to_file(html_content, output_html_file_path)

        return html_content

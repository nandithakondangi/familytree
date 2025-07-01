import logging
from typing import Any, Optional

from google.protobuf.json_format import MessageToDict
from networkx import DiGraph

from familytree.exceptions import InvalidInputError
from familytree.proto import family_tree_pb2
from familytree.rendering.pyvis_renderer import PyvisRenderer
from familytree.utils import id_utils
from familytree.utils.graph_types import EdgeType, GraphEdge, GraphNode

logger = logging.getLogger(__name__)


class GraphHandler:
    """
    Handler class to perform graph operations.
    """

    def __init__(self):
        """
        Initializes the GraphHandler with an empty directed graph.
        """
        self._graph: DiGraph = DiGraph()
        self._family_unit_map: dict[str, family_tree_pb2.FamilyUnit] = {}

    def _check_if_node_exists(self, node_id: str, type: str) -> bool:
        """
        Checks if a node exists in the graph, raising an error if not.

        Args:
            node_id: The ID of the node to check.
            type: The type of the node (e.g., "Source", "Child") for the error message.

        Returns:
            True if the node exists.

        Raises:
            InvalidInputError: If the node with the given ID is not found.
        """
        if not self._graph.has_node(node_id):
            error_message = f"{type} ID '{node_id}' not found in graph nodes."
            logger.error(error_message)
            raise InvalidInputError(
                operation="Adding edges",
                field=f"{type}_id",
                description=error_message,
            )
        return True

    def _update_family_units_map(
        self, family_unit_id: str, data_to_update: dict[str, Any]
    ) -> None:
        """
        Updates the family unit map with new parent or child information.

        If the family unit does not exist, it creates a new one.
        It also updates the name of the family unit based on the parents.

        Args:
            family_unit_id: The ID of the family unit to update.
            data_to_update: A dictionary containing 'parents' or 'children' keys with lists of member IDs.
        """
        logger.info("Updating family units map...")
        family_unit_to_update = self._family_unit_map.get(
            family_unit_id, family_tree_pb2.FamilyUnit()
        )
        if not family_unit_to_update.id:
            family_unit_to_update.id = family_unit_id
        if "parents" in data_to_update:
            for parent_id in data_to_update["parents"]:
                if parent_id not in family_unit_to_update.parent_ids:
                    family_unit_to_update.parent_ids.append(parent_id)
        if "children" in data_to_update:
            for child_id in data_to_update["children"]:
                if child_id not in family_unit_to_update.child_ids:
                    family_unit_to_update.child_ids.append(child_id)

        parent_names = [
            self.get_member_info(id)["name"]
            for id in family_unit_to_update.parent_ids
        ]
        family_unit_to_update.name = " and ".join(f"{name}'s" for name in parent_names) + " family"
        self._family_unit_map[family_unit_id] = family_unit_to_update


    def _get_birth_family_id(self, member_id: str) -> str:
        """
        Retrieves the birth family unit ID for a member.

        Args:
            member_id: The ID of the member.

        Returns:
            The birth family unit ID string.
        """
        node_data: GraphNode = self._graph.nodes[member_id]["data"]
        return node_data.attributes.birth_family_unit_id

    def _get_acquired_family_id(self, member_id: str) -> str:
        """
        Retrieves the acquired family unit ID for a member.

        Args:
            member_id: The ID of the member.

        Returns:
            The acquired family unit ID string.
        """
        node_data: GraphNode = self._graph.nodes[member_id]["data"]
        return node_data.attributes.acquired_family_unit_id

    def _set_birth_family_id(self, member_id: str, family_unit_id: str):
        """
        Sets the birth family unit ID for a member.

        Args:
            member_id: The ID of the member.
            family_unit_id: The birth family unit ID to set.
        """
        self._graph.nodes[member_id][
            "data"
        ].attributes.birth_family_unit_id = family_unit_id

    def _set_acquired_family_id(self, member_id: str, family_unit_id: str):
        """
        Sets the acquired family unit ID for a member.

        Args:
            member_id: The ID of the member.
            family_unit_id: The acquired family unit ID to set.
        """
        self._graph.nodes[member_id][
            "data"
        ].attributes.acquired_family_unit_id = family_unit_id

    def get_family_graph(self) -> DiGraph:
        """
        Returns the internal NetworkX DiGraph instance.

        Returns:
            nx.DiGraph: The family graph.
        """
        return self._graph

    def get_family_unit_graph(self) -> dict[str, family_tree_pb2.FamilyUnit]:
        """
        Returns the map of family units.

        Returns:
            A dictionary mapping family unit IDs to FamilyUnit protobuf messages.
        """
        return self._family_unit_map

    def get_member_info(self, member_id: str) -> dict[str, Any]:
        """
        Retrieves all stored information for a given family member.

        Args:
            member_id: The ID of the member.

        Returns:
            A dictionary containing the member's attributes.
        """
        node_data: GraphNode = self._graph.nodes[member_id]["data"]
        return MessageToDict(node_data.attributes, preserving_proto_field_name=True)

    def has_parent(self, member_id: str) -> bool:
        """
        Checks if a member has a recorded parent relationship.

        Note: This checks for the existence of a parent link, not whether
        the parent node is currently visible in a rendered graph.

        Args:
            member_id: The ID of the member.

        Returns:
            True if the member has a parent relationship, False otherwise.
        """
        node_data: GraphNode = self._graph.nodes[member_id]["data"]
        return node_data.has_visible_parents is not None

    def has_child(self, member_id: str) -> bool:
        """
        Checks if a member has a recorded child relationship.

        Note: This checks for the existence of a child link, not whether
        the child node is currently visible in a rendered graph.

        Args:
            member_id: The ID of the member.

        Returns:
            True if the member has a child relationship, False otherwise.
        """
        node_data: GraphNode = self._graph.nodes[member_id]["data"]
        return node_data.has_visible_children is not None

    def has_spouse(self, member_id: str) -> bool:
        """
        Checks if a member has a recorded spouse relationship.

        Note: This checks for the existence of a spouse link, not whether
        the spouse node is currently visible in a rendered graph.

        Args:
            member_id: The ID of the member.

        Returns:
            True if the member has a spouse relationship, False otherwise.
        """
        node_data: GraphNode = self._graph.nodes[member_id]["data"]
        return node_data.has_visible_spouse is not None

    def get_spouse(self, member_id: str) -> Optional[str]:
        """
        Retrieves the ID of the first found spouse of a member.

        It iterates through the neighbors and returns the first one connected
        by a SPOUSE edge.

        Args:
            member_id: The ID of the member.

        Returns:
            The ID of the spouse, or None if no spouse is found.
        """
        for neighbor in self._graph.neighbors(member_id):
            edge_obj: GraphEdge = self._graph.get_edge_data(member_id, neighbor)["data"]
            if edge_obj.edge_type == EdgeType.SPOUSE:
                return neighbor
        return None

    def get_children(self, member_id: str) -> list[str]:
        """
        Retrieves a list of children IDs for a member.

        It iterates through the neighbors and collects all those connected
        by a PARENT_TO_CHILD edge.

        Args:
            member_id: The ID of the member (parent).

        Returns:
            A list of children member IDs.
        """
        children: list[str] = []
        for neighbor in self._graph.neighbors(member_id):
            edge_obj: GraphEdge = self._graph.get_edge_data(member_id, neighbor)["data"]
            if edge_obj.edge_type == EdgeType.PARENT_TO_CHILD:
                children.append(neighbor)
        return children

    def get_parent(self, member_id: str) -> Optional[str]:
        """
        Retrieves the ID of the first found parent of a member.

        It iterates through the neighbors and returns the first one connected
        by a CHILD_TO_PARENT edge.

        Args:
            member_id: The ID of the member (child).

        Returns:
            The ID of the parent, or None if no parent is found.
        """
        for neighbor in self._graph.neighbors(member_id):
            edge_obj: GraphEdge = self._graph.get_edge_data(member_id, neighbor)["data"]
            if edge_obj.edge_type == EdgeType.CHILD_TO_PARENT:
                return neighbor
        return None

    def create_from_proto(self, family_tree: family_tree_pb2.FamilyTree) -> None:
        """
        Creates a NetworkX directed graph from a FamilyTree protobuf message.

        The graph nodes represent family members, and edges represent relationships
        like parent-child and spouse.

        Args:
            family_tree: A family_tree_pb2.FamilyTree message instance.
        """
        logger.info("Creating NetworkX graph from FamilyTree proto...")
        self._graph = DiGraph()  # Initialize the private graph
        self._family_unit_map = {} # Initialize the family unit map

        # 1. Add all members as nodes
        for (
            member_id,
            member_data,
        ) in family_tree.members.items():  # Use the passed parameter
            self.add_member(member_id, member_data)

        # 2. Add relationships as edges
        for (
            source_member_id,
            relationships_data,
        ) in family_tree.relationships.items():  # Use the passed parameter
            # Children relationships: source_member_id is PARENT of child_id
            for child_id in relationships_data.children_ids:
                self.add_child_relation(source_member_id, child_id)
            # Spouse relationships: source_member_id is SPOUSE of spouse_id
            for spouse_id in relationships_data.spouse_ids:
                self.add_spouse_relation(source_member_id, spouse_id)
            # Parent relationships: source_member_id is CHILD of parent_id
            for parent_id in relationships_data.parent_ids:
                self.add_parent_relation(source_member_id, parent_id)

        for family_unit_id, family_unit in family_tree.family_units.items():
            self._family_unit_map[family_unit_id] = family_unit

        logger.info("Finished creating NetworkX graph from FamilyTree proto.")

    def add_member(
        self, member_id: str, member_data: family_tree_pb2.FamilyMember
    ) -> None:
        """
        Adds a family member as a node to the graph.

        The node's 'data' attribute will store a GraphNode object containing
        the member's attributes from `member_data`.
        - `is_poi` is initialized to `False`.
        - `is_visible` (for the node itself) is initialized to `False`.
        - All `has_visible_*` relationship flags are initialized to `None`.

        Args:
            member_id: The unique identifier for the family member.
            member_data: The FamilyMember protobuf message containing member details.
        """
        node_obj = GraphNode(attributes=member_data)

        self._graph.add_node(member_id, data=node_obj)
        logger.debug(f"Added node: {member_id}")

    def add_child_relation(self, source_member_id: str, child_id: str) -> None:
        """
        Adds a directed edge from `source_member_id` to `child_id` of type PARENT_TO_CHILD.

        This edge `source_member_id -> child_id` with `EdgeType.PARENT_TO_CHILD` implies
        that `source_member_id` is a parent of `child_id`.

        The edge is created with `is_rendered = True` by default.
        It also updates the `has_visible_children` flag on the `source_member_id`
        node's data to `False` which implies existence of children but not visible yet.

        This also updates the family unit map. It creates an acquired family for the parent
        if one doesn't exist, and sets the child's birth family to be this family.

        Args:
            source_member_id: The ID of the member who is the source of the edge (parent).
            child_id: The ID of the member who is the target of the edge (child).
        """
        self._check_if_node_exists(source_member_id, "Source")
        self._check_if_node_exists(child_id, "Child")

        # Edge: source_member_id -> child_id (CHILD)
        edge_data_child = GraphEdge(
            edge_type=EdgeType.PARENT_TO_CHILD, is_rendered=True
        )
        self._graph.add_edge(source_member_id, child_id, data=edge_data_child)
        self._graph.nodes[source_member_id]["data"].has_visible_children = False
        logger.debug(f"Added CHILD edge: {source_member_id} -> {child_id}")

        # Update family_units
        if not self._get_acquired_family_id(source_member_id):
            new_family_unit_id = id_utils.generate_family_unit_id()
            self._set_acquired_family_id(source_member_id, new_family_unit_id)
            self._update_family_units_map(
                new_family_unit_id, {"parents": [source_member_id]}
            )
        family_unit_to_update = self._get_acquired_family_id(source_member_id)
        self._set_birth_family_id(child_id, family_unit_to_update)
        self._update_family_units_map(
            family_unit_to_update,
            {"children": [child_id]},
        )

    def add_spouse_relation(self, source_member_id: str, spouse_id: str) -> None:
        """
        Adds a directed edge from `source_member_id` to `spouse_id` of type SPOUSE.

        This edge `source_member_id -> spouse_id` with `EdgeType.SPOUSE` implies
        that `source_member_id` is a spouse of `spouse_id`.

        The edge's `is_rendered` attribute is set to `True` unless an edge
        already exists from `spouse_id` to `source_member_id`, in which case
        this new edge's `is_rendered` is set to `False` to avoid duplicate display.
        It also updates the `has_visible_spouse` flag on the `source_member_id`
        node's data to `False`.

        This also updates the family unit map, grouping the spouses into an
        acquired family unit.

        Args:
            source_member_id: The ID of the member who is the source of the edge.
            spouse_id: The ID of the member who is the target of the edge (the spouse).
        """
        self._check_if_node_exists(source_member_id, "Source")
        self._check_if_node_exists(spouse_id, "Spouse")

        # Edge: source_member_id -> spouse_id (SPOUSE)
        is_edge_rendered = (
            False if self._graph.has_edge(spouse_id, source_member_id) else True
        )
        edge_data = GraphEdge(edge_type=EdgeType.SPOUSE, is_rendered=is_edge_rendered)
        self._graph.add_edge(source_member_id, spouse_id, data=edge_data)
        self._graph.nodes[source_member_id]["data"].has_visible_spouse = False
        logger.debug(f"Added SPOUSE edge: {source_member_id} -> {spouse_id}")

        # Update family_units
        if not self._get_acquired_family_id(source_member_id):
            new_family_unit_id = id_utils.generate_family_unit_id()
            self._set_acquired_family_id(source_member_id, new_family_unit_id)
            self._update_family_units_map(
                new_family_unit_id, {"parents": [source_member_id]}
            )
        family_unit_to_update = self._get_acquired_family_id(source_member_id)
        self._set_acquired_family_id(spouse_id, family_unit_to_update)
        self._update_family_units_map(
            family_unit_to_update,
            {"parents": [spouse_id]},
        )

    def add_parent_relation(self, source_member_id: str, parent_id: str) -> None:
        """
        Adds a directed edge from `source_member_id` to `parent_id` of type CHILD_TO_PARENT.

        This edge `source_member_id -> parent_id` with `EdgeType.CHILD_TO_PARENT` implies
        that `source_member_id` is a child of `parent_id`.

        The edge is created with `is_rendered = False` by default, as the primary
        relationship is expected to be PARENT_TO_CHILD.
        It also updates the `has_visible_parents` flag on the `source_member_id`
        node's data to `False`.

        This also updates the family unit map. It creates a birth family for the child
        if one doesn't exist, and adds the parent to that family unit.

        Args:
            source_member_id: The ID of the member who is the source of the edge (child).
            parent_id: The ID of the member who is the target of the edge (parent).
        """
        self._check_if_node_exists(source_member_id, "Source")
        self._check_if_node_exists(parent_id, "Parent")

        # Edge: source_member_id -> parent_id (PARENT)
        edge_data_parent = GraphEdge(
            edge_type=EdgeType.CHILD_TO_PARENT, is_rendered=False
        )
        self._graph.add_edge(source_member_id, parent_id, data=edge_data_parent)
        self._graph.nodes[source_member_id]["data"].has_visible_parents = False
        logger.debug(f"Added PARENT edge: {source_member_id} -> {parent_id}")

        # Update family_units
        if not self._get_birth_family_id(source_member_id):
            new_family_unit_id = id_utils.generate_family_unit_id()
            self._set_birth_family_id(source_member_id, new_family_unit_id)
            self._update_family_units_map(
                new_family_unit_id, {"children": [source_member_id]}
            )
        family_unit_to_update = self._get_birth_family_id(source_member_id)
        self._set_acquired_family_id(parent_id, family_unit_to_update)
        self._update_family_units_map(
            family_unit_to_update,
            {"parents": [parent_id]},
        )

    def render_graph_to_html(
        self, theme: str, output_html_file_path: Optional[str] = None
    ) -> str:
        """
        Renders the current family tree graph to an HTML string using PyvisRenderer
        and optionally saves it to a file.

        The visibility of nodes and edges is determined by the 'is_rendered'
        attribute on GraphNode and GraphEdge objects within self._graph.
        The 'is_poi' attribute on GraphNode objects can be used to highlight
        a person of interest.

        Args:
            theme: The color theme to use for rendering (e.g., 'light', 'dark').
            output_html_file_path: Optional. If provided, the HTML will be saved
                                   to this path.
        Returns:
            str: The HTML content of the rendered graph.
        """
        renderer = PyvisRenderer()
        return renderer.render_graph_to_html(self._graph, theme, output_html_file_path)

import logging
from enum import Enum, auto

import networkx as nx
from networkx import DiGraph

from familytree.proto import family_tree_pb2

logger = logging.getLogger(__name__)


class EdgeType(Enum):
    """
    Defines the types of relationships (edges) in the family graph.
    """

    SPOUSE = auto()
    PARENT = auto()
    CHILD = auto()


class GraphHandler:
    """
    Handler class to perform graph operations.
    """

    class GraphNode:
        """
        Represents a node in the graph with its properties.
        """

        attributes: family_tree_pb2.FamilyMember
        is_poi: bool
        is_visible: bool
        has_visible_spouse: bool | None
        has_visible_parents: bool | None
        has_visible_children: bool | None
        has_visible_siblings: bool | None
        has_visible_inlaws: bool | None

    class GraphEdge:
        """
        Represents an edge in the graph with properties.
        """

        edge_type: EdgeType
        is_visible: bool
        attributes: dict

    def __init__(self):
        """
        Initializes the GraphHandler with an empty directed graph.
        """
        self._graph = nx.DiGraph()

    def get_family_graph(self) -> nx.DiGraph:
        """
        Returns the internal NetworkX DiGraph instance.

        Returns:
            nx.DiGraph: The family graph.
        """
        return self._graph

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
            if not self._graph.has_node(source_member_id):
                logger.warning(
                    f"Source member ID '{source_member_id}' in relationships not found in graph nodes. "
                    "Skipping relationships for this member."
                )
                continue
            # Children relationships: source_member_id is PARENT of child_id
            for child_id in relationships_data.children_ids:
                self.add_child_relation(source_member_id, child_id)
            # Spouse relationships: source_member_id is SPOUSE of spouse_id
            for spouse_id in relationships_data.spouse_ids:
                self.add_spouse_relation(source_member_id, spouse_id)
            # Parent relationships: source_member_id is CHILD of parent_id
            for parent_id in relationships_data.parent_ids:
                self.add_parent_relation(source_member_id, parent_id)

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
        node_obj = GraphHandler.GraphNode()
        node_obj.attributes = member_data
        node_obj.is_poi = False  # Default
        node_obj.is_visible = False  # Default
        # Initialize other boolean flags to None since relationships are not added yet.
        # This will be updated as we add edges to the graph.
        node_obj.has_visible_spouse = None
        node_obj.has_visible_parents = None
        node_obj.has_visible_children = None
        node_obj.has_visible_siblings = None
        node_obj.has_visible_inlaws = None

        self._graph.add_node(member_id, data=node_obj)
        logger.debug(f"Added node: {member_id}")

    def add_child_relation(self, source_member_id: str, child_id: str) -> None:
        """
        Adds a directed edge from `source_member_id` to `child_id` of type CHILD.

        This edge `source_member_id -> child_id` with `EdgeType.CHILD` implies
        that `source_member_id` is a child of `child_id`.

        The edge is created with `is_visible = True` by default.
        It also updates the `has_visible_children` flag on the `source_member_id`
        node's data to `False`.

        Args:
            source_member_id: The ID of the member who is the source of the edge.
            child_id: The ID of the member who is the target of the edge.
        """
        if not self._graph.has_node(child_id):
            logger.warning(
                f"Child ID '{child_id}' is not found in graph nodes.Edges not created."
            )
            return

        # Edge: source_member_id -> child_id (CHILD)
        edge_data_child = GraphHandler.GraphEdge()
        edge_data_child.edge_type = EdgeType.CHILD
        edge_data_child.is_visible = True  # Default
        edge_data_child.attributes = {}  # Default
        self._graph.add_edge(source_member_id, child_id, data=edge_data_child)
        self._graph.nodes[source_member_id]["data"].has_visible_children = False
        logger.debug(f"Added CHILD edge: {source_member_id} -> {child_id}")

    def add_spouse_relation(self, source_member_id: str, spouse_id: str) -> None:
        """
        Adds a directed edge from `source_member_id` to `spouse_id` of type SPOUSE.

        This edge `source_member_id -> spouse_id` with `EdgeType.SPOUSE` implies
        that `source_member_id` is a spouse of `spouse_id`.

        The edge's `is_visible` attribute is set to `True` unless an edge
        already exists from `spouse_id` to `source_member_id`, in which case
        this new edge's `is_visible` is set to `False`.
        It also updates the `has_visible_spouse` flag on the `source_member_id`
        node's data to `False`.

        Args:
            source_member_id: The ID of the member who is the source of the edge.
            spouse_id: The ID of the member who is the target of the edge (the spouse).
        """
        if not self._graph.has_node(spouse_id):
            logger.warning(
                f"Spouse ID '{spouse_id}' is not found in graph nodes. "
                "Edges not created."
            )
            return

        # Edge: source_member_id -> spouse_id (SPOUSE)
        edge_data_spouse = GraphHandler.GraphEdge()
        edge_data_spouse.edge_type = EdgeType.SPOUSE
        edge_data_spouse.is_visible = (
            False if self._graph.has_edge(spouse_id, source_member_id) else True
        )
        edge_data_spouse.attributes = {}  # Default
        self._graph.add_edge(source_member_id, spouse_id, data=edge_data_spouse)
        self._graph.nodes[source_member_id]["data"].has_visible_spouse = False
        logger.debug(f"Added SPOUSE edge: {source_member_id} -> {spouse_id}")

    def add_parent_relation(self, source_member_id: str, parent_id: str) -> None:
        """
        Adds a directed edge from `source_member_id` to `parent_id` of type PARENT.

        This edge `source_member_id -> parent_id` with `EdgeType.PARENT` implies
        that `source_member_id` is a parent of `parent_id`.

        The edge is created with `is_visible = False` by default.
        It also updates the `has_visible_parents` flag on the `source_member_id`
        node's data to `False`.

        Args:
            source_member_id: The ID of the member who is the source of the edge.
            parent_id: The ID of the member who is the target of the edge.
        """
        if not self._graph.has_node(parent_id):
            logger.warning(
                f"Parent ID '{parent_id}' is not found in graph nodes. "
                "Edges not created."
            )
            return

        # Edge: source_member_id -> parent_id (PARENT)
        edge_data_parent = GraphHandler.GraphEdge()
        edge_data_parent.edge_type = EdgeType.PARENT
        edge_data_parent.is_visible = False
        edge_data_parent.attributes = {}
        self._graph.add_edge(source_member_id, parent_id, data=edge_data_parent)
        self._graph.nodes[source_member_id]["data"].has_visible_parents = False
        logger.debug(f"Added PARENT edge: {source_member_id} -> {parent_id}")

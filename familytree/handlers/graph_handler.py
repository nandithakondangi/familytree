import logging
from enum import Enum, auto
from typing import Optional

from networkx import DiGraph

from familytree.proto import family_tree_pb2

logger = logging.getLogger(__name__)


class EdgeType(Enum):
    """
    Defines the types of relationships (edges) in the family graph.
    """

    SPOUSE = auto()
    PARENT_TO_CHILD = auto()
    CHILD_TO_PARENT = auto()


class GraphHandler:
    """
    Handler class to perform graph operations.
    """

    class GraphNode:
        """
        Represents a node in the graph with its properties.
        """

        def __init__(self, attributes: family_tree_pb2.FamilyMember):
            self.attributes: family_tree_pb2.FamilyMember = attributes
            self.is_poi: bool = False
            self.is_visible: bool = False  # Default as per current add_member
            self.has_visible_spouse: Optional[bool] = None
            self.has_visible_parents: Optional[bool] = None
            self.has_visible_children: Optional[bool] = None
            self.has_visible_siblings: Optional[bool] = None
            self.has_visible_inlaws: Optional[bool] = None

    class GraphEdge:
        """
        Represents an edge in the graph with properties.
        """

        def __init__(
            self,
            edge_type: EdgeType,
            is_visible: bool = True,
            attributes: Optional[dict] = None,
        ):
            self.edge_type: EdgeType = edge_type
            self.is_visible: bool = is_visible
            self.attributes: dict = attributes if attributes is not None else {}

    def __init__(self):
        """
        Initializes the GraphHandler with an empty directed graph.
        """
        self._graph: DiGraph = DiGraph()

    def get_family_graph(self) -> DiGraph:
        """
        Returns the internal NetworkX DiGraph instance.

        Returns:
            nx.DiGraph: The family graph.
        """
        return self._graph

    def has_parent(self, member_id: str) -> bool:
        node_data: GraphHandler.GraphNode = self._graph.nodes[member_id]["data"]
        return node_data.has_visible_parents is not None

    def has_child(self, member_id: str) -> bool:
        node_data: GraphHandler.GraphNode = self._graph.nodes[member_id]["data"]
        return node_data.has_visible_children is not None

    def has_spouse(self, member_id: str) -> bool:
        node_data: GraphHandler.GraphNode = self._graph.nodes[member_id]["data"]
        return node_data.has_visible_spouse is not None

    def get_spouse(self, member_id: str) -> Optional[str]:
        for neighbor in self._graph.neighbors(member_id):
            edge_obj: GraphHandler.GraphEdge = self._graph.get_edge_data(
                member_id, neighbor
            )["data"]
            if edge_obj.edge_type == EdgeType.SPOUSE:
                return neighbor
        return None

    def get_children(self, member_id: str) -> list[str]:
        children: list[str] = []
        for neighbor in self._graph.neighbors(member_id):
            edge_obj: GraphHandler.GraphEdge = self._graph.get_edge_data(
                member_id, neighbor
            )["data"]
            if edge_obj.edge_type == EdgeType.PARENT_TO_CHILD:
                children.append(neighbor)
        return children

    def get_parent(self, member_id: str) -> Optional[str]:
        for neighbor in self._graph.neighbors(member_id):
            edge_obj: GraphHandler.GraphEdge = self._graph.get_edge_data(
                member_id, neighbor
            )["data"]
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
        node_obj = GraphHandler.GraphNode(attributes=member_data)

        self._graph.add_node(member_id, data=node_obj)
        logger.debug(f"Added node: {member_id}")

    def add_child_relation(self, source_member_id: str, child_id: str) -> None:
        """
        Adds a directed edge from `source_member_id` to `child_id` of type PARENT_TO_CHILD.

        This edge `source_member_id -> child_id` with `EdgeType.PARENT_TO_CHILD` implies
        that `source_member_id` is a parent of `child_id`.

        The edge is created with `is_visible = True` by default.
        It also updates the `has_visible_children` flag on the `source_member_id`
        node's data to `False` which implies existence of children but not visible yet.

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
        edge_data_child = GraphHandler.GraphEdge(
            edge_type=EdgeType.PARENT_TO_CHILD, is_visible=True
        )
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
        is_edge_visible = (
            False if self._graph.has_edge(spouse_id, source_member_id) else True
        )
        edge_data = GraphHandler.GraphEdge(
            edge_type=EdgeType.SPOUSE, is_visible=is_edge_visible
        )
        self._graph.add_edge(source_member_id, spouse_id, data=edge_data)
        self._graph.nodes[source_member_id]["data"].has_visible_spouse = False
        logger.debug(f"Added SPOUSE edge: {source_member_id} -> {spouse_id}")

    def add_parent_relation(self, source_member_id: str, parent_id: str) -> None:
        """
        Adds a directed edge from `source_member_id` to `parent_id` of type CHILD_TO_PARENT.

        This edge `source_member_id -> parent_id` with `EdgeType.CHILD_TO_PARENT` implies
        that `source_member_id` is a child of `parent_id`.

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
        edge_data_parent = GraphHandler.GraphEdge(
            edge_type=EdgeType.CHILD_TO_PARENT, is_visible=False
        )
        self._graph.add_edge(source_member_id, parent_id, data=edge_data_parent)
        self._graph.nodes[source_member_id]["data"].has_visible_parents = False
        logger.debug(f"Added PARENT edge: {source_member_id} -> {parent_id}")

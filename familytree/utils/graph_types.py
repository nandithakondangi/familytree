from enum import Enum, auto
from typing import Optional

from familytree.proto import family_tree_pb2


class EdgeType(Enum):
    """
    Defines the types of relationships (edges) in the family graph.
    """

    SPOUSE = auto()
    PARENT_TO_CHILD = auto()
    CHILD_TO_PARENT = auto()


class GraphNode:
    """
    Represents a node in the graph with its properties.
    """

    def __init__(self, attributes: family_tree_pb2.FamilyMember):
        self.attributes: family_tree_pb2.FamilyMember = attributes
        self.is_poi: bool = False
        self.is_visible: bool = False
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
        is_rendered: bool = True,
        attributes: Optional[dict] = None,
    ):
        self.edge_type: EdgeType = edge_type
        self.is_rendered: bool = is_rendered
        self.attributes: dict = attributes if attributes is not None else {}

import networkx as nx
import pytest

from familytree.handlers.graph_handler import EdgeType, GraphHandler
from familytree.proto import family_tree_pb2


@pytest.fixture
def graph_handler_instance():
    """Provides an empty GraphHandler instance for each test."""
    return GraphHandler()


def test_init(graph_handler_instance):
    """Tests GraphHandler initialization."""
    assert isinstance(graph_handler_instance._graph, nx.DiGraph)
    assert len(graph_handler_instance._graph.nodes) == 0
    assert len(graph_handler_instance._graph.edges) == 0


def test_get_family_graph(graph_handler_instance):
    """Tests retrieval of the internal graph."""
    assert graph_handler_instance.get_family_graph() is graph_handler_instance._graph


def test_add_member(graph_handler_instance):
    """Tests adding a member to the graph."""
    member_id = "M001"
    member_data = family_tree_pb2.FamilyMember(id=member_id, name="Test Member")
    graph_handler_instance.add_member(member_id, member_data)

    assert member_id in graph_handler_instance._graph.nodes
    node_obj: GraphHandler.GraphNode = graph_handler_instance._graph.nodes[member_id][
        "data"
    ]
    assert isinstance(node_obj, GraphHandler.GraphNode)
    assert node_obj.attributes == member_data
    assert node_obj.is_poi is False
    assert node_obj.is_visible is False  # Default as per implementation
    assert node_obj.has_visible_spouse is None
    assert node_obj.has_visible_parents is None
    assert node_obj.has_visible_children is None


def test_add_child_relation(graph_handler_instance):
    """Tests adding a parent-child relationship.
    add_child_relation(parent_id, child_id)
    """
    parent_id = "P001"
    child_id = "C001"
    graph_handler_instance.add_member(
        parent_id, family_tree_pb2.FamilyMember(id=parent_id, name="Parent")
    )
    graph_handler_instance.add_member(
        child_id, family_tree_pb2.FamilyMember(id=child_id, name="Child")
    )
    # P001 is parent of C001
    graph_handler_instance.add_child_relation(parent_id, child_id)

    assert graph_handler_instance._graph.has_edge(parent_id, child_id)
    edge_data: GraphHandler.GraphEdge = graph_handler_instance._graph.edges[
        parent_id, child_id
    ]["data"]
    assert isinstance(edge_data, GraphHandler.GraphEdge)
    assert edge_data.edge_type == EdgeType.PARENT_TO_CHILD
    assert edge_data.is_visible is True
    assert (
        graph_handler_instance._graph.nodes[parent_id]["data"].has_visible_children
        is False
    )


def test_add_child_relation_target_missing(graph_handler_instance, caplog):
    """Tests adding child relation when child node is missing."""
    parent_id = "P001"
    missing_child_id = "C_MISSING"
    graph_handler_instance.add_member(
        parent_id, family_tree_pb2.FamilyMember(id=parent_id)
    )
    graph_handler_instance.add_child_relation(parent_id, missing_child_id)
    assert not graph_handler_instance._graph.has_edge(parent_id, missing_child_id)
    assert f"Child ID '{missing_child_id}' is not found in graph nodes." in caplog.text


def test_add_spouse_relation(graph_handler_instance):
    """Tests adding a spouse relationship."""
    s1_id = "S001"
    s2_id = "S002"
    graph_handler_instance.add_member(
        s1_id, family_tree_pb2.FamilyMember(id=s1_id, name="Spouse1")
    )
    graph_handler_instance.add_member(
        s2_id, family_tree_pb2.FamilyMember(id=s2_id, name="Spouse2")
    )

    graph_handler_instance.add_spouse_relation(s1_id, s2_id)
    assert graph_handler_instance._graph.has_edge(s1_id, s2_id)
    edge1_data: GraphHandler.GraphEdge = graph_handler_instance._graph.edges[
        s1_id, s2_id
    ]["data"]
    assert edge1_data.edge_type == EdgeType.SPOUSE
    assert edge1_data.is_visible is True  # First edge is visible
    assert (
        graph_handler_instance._graph.nodes[s1_id]["data"].has_visible_spouse is False
    )

    # Add reverse relationship
    graph_handler_instance.add_spouse_relation(s2_id, s1_id)
    assert graph_handler_instance._graph.has_edge(s2_id, s1_id)
    edge2_data: GraphHandler.GraphEdge = graph_handler_instance._graph.edges[
        s2_id, s1_id
    ]["data"]
    assert edge2_data.edge_type == EdgeType.SPOUSE
    assert edge2_data.is_visible is False  # Reverse edge should be hidden
    assert (
        graph_handler_instance._graph.nodes[s2_id]["data"].has_visible_spouse is False
    )


def test_add_parent_relation(graph_handler_instance):
    """Tests adding a child-parent relationship.
    add_parent_relation(child_id, parent_id)
    """
    parent_id = "P001"
    child_id = "C001"
    graph_handler_instance.add_member(
        parent_id, family_tree_pb2.FamilyMember(id=parent_id, name="Parent")
    )
    graph_handler_instance.add_member(
        child_id, family_tree_pb2.FamilyMember(id=child_id, name="Child")
    )
    # C001 is child of P001
    graph_handler_instance.add_parent_relation(child_id, parent_id)

    assert graph_handler_instance._graph.has_edge(child_id, parent_id)
    edge_data: GraphHandler.GraphEdge = graph_handler_instance._graph.edges[
        child_id, parent_id
    ]["data"]
    assert isinstance(edge_data, GraphHandler.GraphEdge)
    assert edge_data.edge_type == EdgeType.CHILD_TO_PARENT
    assert edge_data.is_visible is False  # Default for parent relation
    assert (
        graph_handler_instance._graph.nodes[child_id]["data"].has_visible_parents
        is False
    )


def test_create_from_proto_empty(graph_handler_instance):
    """Tests creating graph from an empty protobuf message."""
    ft_proto = family_tree_pb2.FamilyTree()
    graph_handler_instance.create_from_proto(ft_proto)
    assert len(graph_handler_instance._graph.nodes) == 0
    assert len(graph_handler_instance._graph.edges) == 0


def test_create_from_proto_with_data(graph_handler_instance, weasley_family_tree_pb):
    """Tests creating graph from a populated protobuf message (Weasley family)."""
    graph_handler_instance.create_from_proto(weasley_family_tree_pb)

    # Check nodes
    assert len(graph_handler_instance._graph.nodes) == len(
        weasley_family_tree_pb.members
    )
    assert "ARTHW" in graph_handler_instance._graph.nodes
    arthur_node_data: GraphHandler.GraphNode = graph_handler_instance._graph.nodes[
        "ARTHW"
    ]["data"]
    assert arthur_node_data.attributes.name == "Arthur Weasley"

    # Arthur (ARTHW) is parent of Bill (BILLW)
    # Proto: relationships["ARTHW"].children_ids contains "BILLW"
    # create_from_proto calls: add_child_relation("ARTHW", "BILLW") -> edge ARTHW -> BILLW (PARENT_TO_CHILD)
    assert graph_handler_instance._graph.has_edge("ARTHW", "BILLW")
    edge_arthur_bill: GraphHandler.GraphEdge = graph_handler_instance._graph.edges[
        "ARTHW", "BILLW"
    ]["data"]
    assert edge_arthur_bill.edge_type == EdgeType.PARENT_TO_CHILD

    # Molly (MOLLW) is spouse of Arthur (ARTHW)
    # Proto: relationships["MOLLW"].spouse_ids contains "ARTHW"
    # create_from_proto calls: add_spouse_relation("MOLLW", "ARTHW") -> edge MOLLW -> ARTHW (SPOUSE)
    assert graph_handler_instance._graph.has_edge("MOLLW", "ARTHW")
    edge_molly_arthur: GraphHandler.GraphEdge = graph_handler_instance._graph.edges[
        "MOLLW", "ARTHW"
    ]["data"]
    assert edge_molly_arthur.edge_type == EdgeType.SPOUSE

    # Ron (RONAW) has parent Arthur (ARTHW)
    # Proto: relationships["RONAW"].parent_ids contains "ARTHW"
    # create_from_proto calls: add_parent_relation("RONAW", "ARTHW") -> edge RONAW -> ARTHW (CHILD_TO_PARENT)
    if (
        "RONAW" in weasley_family_tree_pb.relationships
        and "ARTHW" in weasley_family_tree_pb.relationships["RONAW"].parent_ids
    ):
        assert graph_handler_instance._graph.has_edge("RONAW", "ARTHW")
        edge_ron_arthur: GraphHandler.GraphEdge = graph_handler_instance._graph.edges[
            "RONAW", "ARTHW"
        ]["data"]
        assert edge_ron_arthur.edge_type == EdgeType.CHILD_TO_PARENT
    else:
        # Fallback check if parent_ids not explicitly in fixture for Ron for some reason
        # (though the conftest populates them)
        assert graph_handler_instance._graph.has_edge("ARTHW", "RONAW")
        assert (
            graph_handler_instance._graph.edges["ARTHW", "RONAW"]["data"].edge_type
            == EdgeType.PARENT_TO_CHILD
        )


def test_create_from_proto_missing_source_in_relationships(
    graph_handler_instance, caplog
):
    """Tests graph creation when a source_member_id in relationships doesn't exist as a node."""
    ft_proto = family_tree_pb2.FamilyTree()
    ft_proto.members["M001"].id = "M001"  # Valid member
    # Relationship for a non-existent member
    ft_proto.relationships["M_GHOST"].children_ids.append("M001")

    graph_handler_instance.create_from_proto(ft_proto)
    assert "Skipping relationships for this member" in caplog.text
    assert not graph_handler_instance._graph.has_edge("M_GHOST", "M001")


def test_create_from_proto_missing_target_in_relationships(
    graph_handler_instance, caplog
):
    """Tests graph creation when a target_id in relationships doesn't exist as a node."""
    ft_proto = family_tree_pb2.FamilyTree()
    ft_proto.members["M001"].id = "M001"
    ft_proto.relationships["M001"].children_ids.append(
        "C_GHOST"
    )  # C_GHOST is not a member

    graph_handler_instance.create_from_proto(ft_proto)
    # The warning for missing target is logged inside add_child_relation, etc.
    assert "Child ID 'C_GHOST' is not found in graph nodes." in caplog.text
    assert not graph_handler_instance._graph.has_edge("M001", "C_GHOST")


def _setup_node_with_visibility_flags(
    handler,
    node_id,
    has_visible_parents=None,
    has_visible_children=None,
    has_visible_spouse=None,
):
    member_data = family_tree_pb2.FamilyMember(id=node_id)
    handler.add_member(node_id, member_data)
    node: GraphHandler.GraphNode = handler._graph.nodes[node_id]["data"]
    node.has_visible_parents = has_visible_parents
    node.has_visible_children = has_visible_children
    node.has_visible_spouse = has_visible_spouse


def test_has_parent(graph_handler_instance):
    _setup_node_with_visibility_flags(
        graph_handler_instance, "node1", has_visible_parents=False
    )
    assert graph_handler_instance.has_parent("node1") is True
    _setup_node_with_visibility_flags(
        graph_handler_instance, "node2", has_visible_parents=None
    )
    assert graph_handler_instance.has_parent("node2") is False


def test_has_child(graph_handler_instance):
    _setup_node_with_visibility_flags(
        graph_handler_instance, "node1", has_visible_children=True
    )
    assert graph_handler_instance.has_child("node1") is True
    _setup_node_with_visibility_flags(
        graph_handler_instance, "node2", has_visible_children=None
    )
    assert graph_handler_instance.has_child("node2") is False


def test_has_spouse(graph_handler_instance):
    _setup_node_with_visibility_flags(
        graph_handler_instance, "node1", has_visible_spouse=False
    )
    assert graph_handler_instance.has_spouse("node1") is True
    _setup_node_with_visibility_flags(
        graph_handler_instance, "node2", has_visible_spouse=None
    )
    assert graph_handler_instance.has_spouse("node2") is False


def test_get_spouse(graph_handler_instance):
    graph_handler_instance.add_member("p1", family_tree_pb2.FamilyMember(id="p1"))
    graph_handler_instance.add_member("p2", family_tree_pb2.FamilyMember(id="p2"))
    graph_handler_instance.add_member(
        "p3", family_tree_pb2.FamilyMember(id="p3")
    )  # Not a spouse
    graph_handler_instance.add_spouse_relation("p1", "p2")
    graph_handler_instance.add_child_relation("p1", "p3")  # Different type of relation

    assert graph_handler_instance.get_spouse("p1") == "p2"
    assert graph_handler_instance.get_spouse("p3") is None  # p3 has no spouse edge
    with pytest.raises(nx.NetworkXError):  # Accessing non-existent node
        graph_handler_instance.get_spouse("non_existent_node")


def test_get_children(graph_handler_instance):
    graph_handler_instance.add_member(
        "parent", family_tree_pb2.FamilyMember(id="parent")
    )
    graph_handler_instance.add_member(
        "child1", family_tree_pb2.FamilyMember(id="child1")
    )
    graph_handler_instance.add_member(
        "child2", family_tree_pb2.FamilyMember(id="child2")
    )
    graph_handler_instance.add_member(
        "spouse", family_tree_pb2.FamilyMember(id="spouse")
    )  # Not a child

    graph_handler_instance.add_child_relation("parent", "child1")
    graph_handler_instance.add_child_relation("parent", "child2")
    graph_handler_instance.add_spouse_relation("parent", "spouse")

    children: list[str] = graph_handler_instance.get_children("parent")
    assert sorted(children) == sorted(["child1", "child2"])  # Order doesn't matter
    assert graph_handler_instance.get_children("child1") == []
    with pytest.raises(nx.NetworkXError):  # Accessing non-existent node
        graph_handler_instance.get_children("non_existent_node")


def test_get_parent(graph_handler_instance):
    # get_parent looks for CHILD_TO_PARENT edges *from* the member_id
    graph_handler_instance.add_member("child", family_tree_pb2.FamilyMember(id="child"))
    graph_handler_instance.add_member(
        "parent1", family_tree_pb2.FamilyMember(id="parent1")
    )
    graph_handler_instance.add_member(
        "sibling", family_tree_pb2.FamilyMember(id="sibling")
    )  # Not a parent

    graph_handler_instance.add_parent_relation(
        "child", "parent1"
    )  # child -> parent1 (CHILD_TO_PARENT)

    assert graph_handler_instance.get_parent("child") == "parent1"
    assert graph_handler_instance.get_parent("parent1") is None
    with pytest.raises(nx.NetworkXError):  # Accessing non-existent node
        graph_handler_instance.get_parent("non_existent_node")

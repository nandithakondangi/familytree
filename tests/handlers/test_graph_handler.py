from unittest.mock import MagicMock, patch

import networkx as nx
import pytest
from familytree.proto import family_tree_pb2, utils_pb2

from familytree.exceptions import InvalidInputError
from familytree.handlers.graph_handler import GraphHandler
from familytree.utils.graph_types import EdgeType, GraphEdge, GraphNode


@pytest.fixture
def graph_handler_instance():
    """Provides an empty GraphHandler instance for each test."""
    return GraphHandler()


def test_init(graph_handler_instance):
    """Tests GraphHandler initialization."""
    assert isinstance(graph_handler_instance._graph, nx.DiGraph)
    assert len(graph_handler_instance._graph.nodes) == 0
    assert len(graph_handler_instance._graph.edges) == 0
    assert graph_handler_instance.get_family_unit_graph() == {}


def test_get_family_graph(graph_handler_instance):
    """Tests retrieval of the internal graph."""
    assert graph_handler_instance.get_family_graph() is graph_handler_instance._graph


def test_add_member(graph_handler_instance):
    """Tests adding a member to the graph."""
    member_id = "M001"
    member_data = family_tree_pb2.FamilyMember(id=member_id, name="Test Member")
    graph_handler_instance.add_member(member_id, member_data)

    assert member_id in graph_handler_instance._graph.nodes
    node_obj: GraphNode = graph_handler_instance._graph.nodes[member_id]["data"]
    assert isinstance(node_obj, GraphNode)
    assert node_obj.attributes == member_data
    assert node_obj.is_poi is False
    assert node_obj.is_visible is False  # Default as per implementation
    assert node_obj.has_visible_spouse is None
    assert node_obj.has_visible_parents is None
    assert node_obj.has_visible_children is None


def test_add_child_relation(graph_handler_instance):
    """Tests adding a parent-child relationship and its effect on family units."""
    parent_id = "P001"
    child_id = "C001"
    graph_handler_instance.add_member(
        parent_id, family_tree_pb2.FamilyMember(id=parent_id, name="Parent")
    )
    graph_handler_instance.add_member(
        child_id, family_tree_pb2.FamilyMember(id=child_id, name="Child")
    )
    graph_handler_instance.add_child_relation(parent_id, child_id)

    # Test edge creation
    assert graph_handler_instance._graph.has_edge(parent_id, child_id)
    edge_data: GraphEdge = graph_handler_instance._graph.edges[parent_id, child_id][
        "data"
    ]
    assert isinstance(edge_data, GraphEdge)
    assert edge_data.edge_type == EdgeType.PARENT_TO_CHILD
    assert edge_data.is_rendered is True
    assert (
        graph_handler_instance._graph.nodes[parent_id]["data"].has_visible_children
        is False
    )

    # Test family unit creation and updates
    family_units = graph_handler_instance.get_family_unit_graph()
    assert len(family_units) == 1
    family_unit = list(family_units.values())[0]
    assert parent_id in family_unit.parent_ids
    assert child_id in family_unit.child_ids
    assert family_unit.name == "Parent's family"
    assert (
        graph_handler_instance._get_acquired_family_id(parent_id) == family_unit.id
    )
    assert graph_handler_instance._get_birth_family_id(child_id) == family_unit.id


def test_add_child_relation_node_missing(graph_handler_instance):
    """Tests adding child relation when a node is missing."""
    parent_id = "P001"
    missing_child_id = "C_MISSING"
    graph_handler_instance.add_member(
        parent_id, family_tree_pb2.FamilyMember(id=parent_id, name="Parent")
    )

    with pytest.raises(InvalidInputError) as excinfo:
        graph_handler_instance.add_child_relation(parent_id, missing_child_id)
    assert f"Child ID '{missing_child_id}' not found in graph nodes." in str(
        excinfo.value
    )
    assert not graph_handler_instance._graph.has_edge(parent_id, missing_child_id)

    with pytest.raises(InvalidInputError) as excinfo:
        graph_handler_instance.add_child_relation(missing_child_id, parent_id)
    assert f"Source ID '{missing_child_id}' not found in graph nodes." in str(
        excinfo.value
    )


def test_add_spouse_relation(graph_handler_instance):
    """Tests adding a spouse relationship and its effect on family units."""
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
    edge1_data: GraphEdge = graph_handler_instance._graph.edges[s1_id, s2_id]["data"]
    assert edge1_data.edge_type == EdgeType.SPOUSE
    assert edge1_data.is_rendered is True
    assert (
        graph_handler_instance._graph.nodes[s1_id]["data"].has_visible_spouse is False
    )

    # Test family unit creation
    family_units = graph_handler_instance.get_family_unit_graph()
    assert len(family_units) == 1
    family_unit = list(family_units.values())[0]
    assert s1_id in family_unit.parent_ids
    assert s2_id in family_unit.parent_ids
    assert family_unit.name == "Spouse1's and Spouse2's family"

    # Add reverse relationship
    graph_handler_instance.add_spouse_relation(s2_id, s1_id)
    assert graph_handler_instance._graph.has_edge(s2_id, s1_id)
    edge2_data: GraphEdge = graph_handler_instance._graph.edges[s2_id, s1_id]["data"]
    assert edge2_data.edge_type == EdgeType.SPOUSE
    assert edge2_data.is_rendered is False
    assert (
        graph_handler_instance._graph.nodes[s2_id]["data"].has_visible_spouse is False
    )

    # Test family unit update
    family_units = graph_handler_instance.get_family_unit_graph()
    assert len(family_units) == 1  # Should still be one family unit
    family_unit = list(family_units.values())[0]
    assert s1_id in family_unit.parent_ids
    assert s2_id in family_unit.parent_ids
    assert family_unit.name == "Spouse1's and Spouse2's family"
    assert graph_handler_instance._get_acquired_family_id(s1_id) == family_unit.id
    assert graph_handler_instance._get_acquired_family_id(s2_id) == family_unit.id


def test_add_parent_relation(graph_handler_instance):
    """Tests adding a child-parent relationship and its effect on family units."""
    parent_id = "P001"
    child_id = "C001"
    graph_handler_instance.add_member(
        parent_id, family_tree_pb2.FamilyMember(id=parent_id, name="Parent")
    )
    graph_handler_instance.add_member(
        child_id, family_tree_pb2.FamilyMember(id=child_id, name="Child")
    )
    graph_handler_instance.add_parent_relation(child_id, parent_id)

    assert graph_handler_instance._graph.has_edge(child_id, parent_id)
    edge_data: GraphEdge = graph_handler_instance._graph.edges[child_id, parent_id][
        "data"
    ]
    assert isinstance(edge_data, GraphEdge)
    assert edge_data.edge_type == EdgeType.CHILD_TO_PARENT
    assert edge_data.is_rendered is False
    assert (
        graph_handler_instance._graph.nodes[child_id]["data"].has_visible_parents
        is False
    )

    # Test family unit creation
    family_units = graph_handler_instance.get_family_unit_graph()
    assert len(family_units) == 1
    family_unit = list(family_units.values())[0]
    assert parent_id in family_unit.parent_ids
    assert child_id in family_unit.child_ids
    assert family_unit.name == "Parent's family"
    assert graph_handler_instance._get_birth_family_id(child_id) == family_unit.id
    assert (
        graph_handler_instance._get_acquired_family_id(parent_id) == family_unit.id
    )


def test_create_from_proto_empty(graph_handler_instance):
    """Tests creating graph from an empty protobuf message."""
    ft_proto = family_tree_pb2.FamilyTree()
    graph_handler_instance.create_from_proto(ft_proto)
    assert len(graph_handler_instance._graph.nodes) == 0
    assert len(graph_handler_instance._graph.edges) == 0
    assert len(graph_handler_instance.get_family_unit_graph()) == 0


def test_create_from_proto_with_data(graph_handler_instance, weasley_family_tree_pb):
    """Tests creating graph from a populated protobuf message (Weasley family)."""
    graph_handler_instance.create_from_proto(weasley_family_tree_pb)

    # Check nodes
    assert len(graph_handler_instance._graph.nodes) == len(
        weasley_family_tree_pb.members
    )
    assert "ARTHW" in graph_handler_instance._graph.nodes
    arthur_node_data: GraphNode = graph_handler_instance._graph.nodes["ARTHW"]["data"]
    assert arthur_node_data.attributes.name == "Arthur Weasley"

    # Check edges
    assert graph_handler_instance._graph.has_edge("ARTHW", "BILLW")
    edge_arthur_bill: GraphEdge = graph_handler_instance._graph.edges["ARTHW", "BILLW"][
        "data"
    ]
    assert edge_arthur_bill.edge_type == EdgeType.PARENT_TO_CHILD

    assert graph_handler_instance._graph.has_edge("MOLLW", "ARTHW")
    edge_molly_arthur: GraphEdge = graph_handler_instance._graph.edges[
        "MOLLW", "ARTHW"
    ]["data"]
    assert edge_molly_arthur.edge_type == EdgeType.SPOUSE

    assert graph_handler_instance._graph.has_edge("RONAW", "ARTHW")
    edge_ron_arthur: GraphEdge = graph_handler_instance._graph.edges["RONAW", "ARTHW"][
        "data"
    ]
    assert edge_ron_arthur.edge_type == EdgeType.CHILD_TO_PARENT

    # Check family units
    family_units = graph_handler_instance.get_family_unit_graph()
    assert len(family_units) == 1
    arthur_molly_family_id = graph_handler_instance._get_acquired_family_id("ARTHW")
    assert arthur_molly_family_id
    arthur_molly_family = family_units[arthur_molly_family_id]
    assert "ARTHW" in arthur_molly_family.parent_ids
    assert "MOLLW" in arthur_molly_family.parent_ids
    assert "BILLW" in arthur_molly_family.child_ids
    assert "RONAW" in arthur_molly_family.child_ids


def test_create_from_proto_missing_node_in_relationships(graph_handler_instance):
    """Tests graph creation when a member_id in relationships doesn't exist as a node."""
    ft_proto = family_tree_pb2.FamilyTree()
    ft_proto.members["M001"].id = "M001"
    ft_proto.relationships["M_GHOST"].children_ids.append("M001")

    with pytest.raises(InvalidInputError) as excinfo:
        graph_handler_instance.create_from_proto(ft_proto)
    assert "Source ID 'M_GHOST' not found in graph nodes." in str(excinfo.value)


def _setup_node_with_visibility_flags(
    handler,
    node_id,
    has_visible_parents=None,
    has_visible_children=None,
    has_visible_spouse=None,
):
    member_data = family_tree_pb2.FamilyMember(id=node_id, name=node_id)
    handler.add_member(node_id, member_data)
    node: GraphNode = handler._graph.nodes[node_id]["data"]
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
    graph_handler_instance.add_member("p1", family_tree_pb2.FamilyMember(id="p1", name="p1"))
    graph_handler_instance.add_member("p2", family_tree_pb2.FamilyMember(id="p2", name="p2"))
    graph_handler_instance.add_member(
        "p3", family_tree_pb2.FamilyMember(id="p3", name="p3")
    )  # Not a spouse
    graph_handler_instance.add_spouse_relation("p1", "p2")
    graph_handler_instance.add_child_relation("p1", "p3")  # Different type of relation

    assert graph_handler_instance.get_spouse("p1") == "p2"
    assert graph_handler_instance.get_spouse("p3") is None  # p3 has no spouse edge
    with pytest.raises(nx.NetworkXError):  # Accessing non-existent node
        graph_handler_instance.get_spouse("non_existent_node")


def test_get_children(graph_handler_instance):
    graph_handler_instance.add_member(
        "parent", family_tree_pb2.FamilyMember(id="parent", name="Parent")
    )
    graph_handler_instance.add_member(
        "child1", family_tree_pb2.FamilyMember(id="child1", name="Child1")
    )
    graph_handler_instance.add_member(
        "child2", family_tree_pb2.FamilyMember(id="child2", name="Child2")
    )
    graph_handler_instance.add_member(
        "spouse", family_tree_pb2.FamilyMember(id="spouse", name="Spouse")
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
    graph_handler_instance.add_member("child", family_tree_pb2.FamilyMember(id="child", name="Child"))
    graph_handler_instance.add_member(
        "parent1", family_tree_pb2.FamilyMember(id="parent1", name="Parent1")
    )
    graph_handler_instance.add_member(
        "sibling", family_tree_pb2.FamilyMember(id="sibling", name="Sibling")
    )  # Not a parent

    graph_handler_instance.add_parent_relation(
        "child", "parent1"
    )  # child -> parent1 (CHILD_TO_PARENT)

    assert graph_handler_instance.get_parent("child") == "parent1"
    assert graph_handler_instance.get_parent("parent1") is None
    with pytest.raises(nx.NetworkXError):  # Accessing non-existent node
        graph_handler_instance.get_parent("non_existent_node")


def test_render_graph_to_html(graph_handler_instance):
    """Tests rendering the graph to HTML."""
    with patch(
        "familytree.handlers.graph_handler.PyvisRenderer"
    ) as mock_pyvis_renderer_cls:
        mock_renderer_instance = MagicMock()
        mock_pyvis_renderer_cls.return_value = mock_renderer_instance
        mock_renderer_instance.render_graph_to_html.return_value = (
            "<html><body>Mocked Graph</body></html>"
        )

        graph_handler_instance.add_member(
            "M001", family_tree_pb2.FamilyMember(id="M001", name="M001")
        )

        html_output = graph_handler_instance.render_graph_to_html(
            theme="dark", output_html_file_path="dummy.html"
        )

        mock_pyvis_renderer_cls.assert_called_once()
        mock_renderer_instance.render_graph_to_html.assert_called_once_with(
            graph_handler_instance._graph, "dark", "dummy.html"
        )
        assert html_output == "<html><body>Mocked Graph</body></html>"

        # Test without output_html_file_path
        mock_renderer_instance.render_graph_to_html.reset_mock()
        html_output_no_path = graph_handler_instance.render_graph_to_html(theme="light")
        mock_renderer_instance.render_graph_to_html.assert_called_once_with(
            graph_handler_instance._graph, "light", None
        )
        assert html_output_no_path == "<html><body>Mocked Graph</body></html>"


def test_get_member_info(graph_handler_instance):
    """Tests retrieving member information."""
    member_id = "M001"
    member_data = family_tree_pb2.FamilyMember(
        id=member_id, name="John Doe", gender=utils_pb2.MALE
    )
    graph_handler_instance.add_member(member_id, member_data)

    info = graph_handler_instance.get_member_info(member_id)
    assert info["id"] == member_id
    assert info["name"] == "John Doe"
    assert info["gender"] == "MALE"

    with pytest.raises(KeyError):  # Node not found
        graph_handler_instance.get_member_info("non_existent_node")
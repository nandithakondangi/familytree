from unittest.mock import patch

import networkx as nx
import pytest
from google.protobuf import text_format

from familytree.handlers.proto_handler import ProtoHandler
from familytree.proto import family_tree_pb2, utils_pb2
from familytree.utils.graph_types import EdgeType, GraphEdge, GraphNode


@pytest.fixture
def proto_handler_instance():
    """Provides an empty ProtoHandler instance for each test."""
    return ProtoHandler()


@pytest.fixture
def family_tree_1():
    """Provides a sample family tree for testing."""
    tree = family_tree_pb2.FamilyTree()
    tree.members["1"].name = "John Smith"
    tree.members["1"].id = "1"
    tree.members["1"].gender = utils_pb2.MALE
    tree.members["1"].date_of_birth.year = 1980
    tree.members["2"].name = "Jane Smith"
    tree.members["2"].id = "2"
    tree.members["2"].gender = utils_pb2.FEMALE
    tree.relationships["1"].spouse_ids.append("2")
    tree.relationships["2"].spouse_ids.append("1")
    return tree


@pytest.fixture
def family_tree_2():
    """Provides another sample family tree for testing deduplication."""
    tree = family_tree_pb2.FamilyTree()
    tree.members["101"].name = "Johnathan Smith"
    tree.members["101"].id = "101"
    tree.members["101"].nicknames.append("John")
    tree.members["101"].gender = utils_pb2.MALE
    tree.members["101"].date_of_birth.year = 1980
    tree.members["102"].name = "Janet Smith"
    tree.members["102"].id = "102"
    tree.members["102"].gender = utils_pb2.FEMALE
    tree.relationships["101"].spouse_ids.append("102")
    tree.relationships["102"].spouse_ids.append("101")
    return tree


@pytest.fixture
def sample_nx_graph():
    """Provides a sample NetworkX graph for testing."""
    graph = nx.DiGraph()
    graph.add_node(
        "1",
        data=GraphNode(
            attributes=family_tree_pb2.FamilyMember(
                name="John Smith", gender=utils_pb2.MALE
            )
        ),
    )
    graph.add_node(
        "2", data=GraphNode(attributes=family_tree_pb2.FamilyMember(name="Jane Smith"))
    )
    graph.add_edge(
        "1", "2", data=GraphEdge(edge_type=EdgeType.SPOUSE, is_rendered=True)
    )
    return graph


def test_init(proto_handler_instance):
    """Tests ProtoHandler initialization."""
    assert isinstance(proto_handler_instance._family_tree, family_tree_pb2.FamilyTree)
    assert not proto_handler_instance._family_tree.members


def test_get_family_tree(proto_handler_instance, family_tree_1):
    """Tests retrieval of the internal FamilyTree message."""
    proto_handler_instance._family_tree = family_tree_1
    assert proto_handler_instance.get_family_tree() is family_tree_1


def test_load_from_textproto_success(proto_handler_instance, family_tree_1):
    """Tests successful loading from a text protobuf string."""
    textproto = text_format.MessageToString(family_tree_1)
    proto_handler_instance.load_from_textproto(textproto)
    assert "1" in proto_handler_instance._family_tree.members
    assert proto_handler_instance._family_tree.members["1"].name == "John Smith"


@patch("google.protobuf.text_format.Merge", side_effect=Exception("Mocked error"))
def test_load_from_textproto_generic_exception(
    mock_merge, proto_handler_instance, caplog
):
    """Tests that a generic exception during loading is caught and logged."""
    proto_handler_instance.load_from_textproto("some content")
    assert "An unexpected error occured" in caplog.text


def test_load_from_textproto_parse_error(proto_handler_instance, caplog):
    """Tests loading from a malformed text protobuf string."""
    with pytest.raises(text_format.ParseError):
        proto_handler_instance.load_from_textproto("malformed { proto content")
    assert "Error parsing text proto" in caplog.text


def test_save_to_textproto(proto_handler_instance, family_tree_1):
    """Tests saving the FamilyTree message to a text protobuf string."""
    proto_handler_instance._family_tree = family_tree_1
    saved_text = proto_handler_instance.save_to_textproto()
    new_tree = family_tree_pb2.FamilyTree()
    text_format.Merge(saved_text, new_tree)
    assert "1" in new_tree.members
    assert new_tree.members["1"].name == "John Smith"


def test_update_from_nx_graph(proto_handler_instance, sample_nx_graph):
    """Tests updating the family tree from a NetworkX graph."""
    proto_handler_instance.update_from_nx_graph(sample_nx_graph, {})
    assert "1" in proto_handler_instance._family_tree.members
    assert proto_handler_instance._family_tree.members["1"].name == "John Smith"
    assert "2" in proto_handler_instance._family_tree.relationships["1"].spouse_ids


def test_update_from_nx_graph_with_existing_members(
    proto_handler_instance, sample_nx_graph
):
    """Tests that updating from a graph merges with existing members."""
    proto_handler_instance._family_tree.members["1"].name = "Old Name"
    proto_handler_instance.update_from_nx_graph(sample_nx_graph, {})
    assert proto_handler_instance._family_tree.members["1"].name == "John Smith"


def test_update_missing_relationships(proto_handler_instance):
    """Tests adding parent-child relationships."""
    graph = nx.DiGraph()
    graph.add_edge(
        "1", "2", data=GraphEdge(edge_type=EdgeType.PARENT_TO_CHILD, is_rendered=True)
    )
    graph.add_edge(
        "3", "1", data=GraphEdge(edge_type=EdgeType.CHILD_TO_PARENT, is_rendered=True)
    )
    proto_handler_instance._update_missing_relationships(graph.edges(data=True))
    assert "2" in proto_handler_instance._family_tree.relationships["1"].children_ids
    assert "1" in proto_handler_instance._family_tree.relationships["3"].parent_ids


def test_update_family_units(proto_handler_instance):
    """Tests adding and updating family units."""
    unit1 = family_tree_pb2.FamilyUnit(name="Unit 1")
    proto_handler_instance._update_family_units({"u1": unit1})
    assert proto_handler_instance._family_tree.family_units["u1"].name == "Unit 1"
    unit1_updated = family_tree_pb2.FamilyUnit(name="Unit 1 Updated")
    proto_handler_instance._update_family_units({"u1": unit1_updated})
    assert (
        proto_handler_instance._family_tree.family_units["u1"].name == "Unit 1 Updated"
    )


def test_calculate_similarity_no_names(proto_handler_instance):
    """Tests similarity calculation when one member has no name."""
    member1 = family_tree_pb2.FamilyMember(name="John")
    member2 = family_tree_pb2.FamilyMember()  # No name
    score = proto_handler_instance._calculate_similarity(member1, member2)
    assert score == 0


def test_get_neighbor_similarity_parents_and_children(proto_handler_instance):
    """Tests neighbor similarity with parents and children."""
    tree1 = family_tree_pb2.FamilyTree()
    tree1.members["p1"].name = "Parent 1"
    tree1.members["c1"].name = "Child 1"
    tree1.relationships["m1"].parent_ids.append("p1")
    tree1.relationships["m1"].children_ids.append("c1")

    tree2 = family_tree_pb2.FamilyTree()
    tree2.members["p2"].name = "Parent 1"
    tree2.members["c2"].name = "Child 1"
    tree2.relationships["m2"].parent_ids.append("p2")
    tree2.relationships["m2"].children_ids.append("c2")

    score = proto_handler_instance._get_neighbor_similarity(
        "m1", "m2", tree1, tree2, {}
    )
    assert score > 0.9  # Should be a very high score


def test_deduplicate_family_members_exact_match(
    proto_handler_instance, family_tree_1, family_tree_2
):
    """Tests deduplication with a very close match."""
    merged_tree = proto_handler_instance._deduplicate_family_members(
        family_tree_1, family_tree_2
    )
    assert len(merged_tree.members) < len(family_tree_1.members) + len(
        family_tree_2.members
    )
    assert "2" in merged_tree.relationships["1"].spouse_ids


def test_deduplicate_family_members_no_match(proto_handler_instance, family_tree_1):
    """Tests deduplication with no clear matches."""
    tree2 = family_tree_pb2.FamilyTree()
    tree2.members["3"].name = "Peter Pan"
    tree2.members["3"].id = "3"
    with patch("familytree.utils.id_utils.generate_member_id", return_value="4"):
        merged_tree = proto_handler_instance._deduplicate_family_members(
            family_tree_1, tree2
        )
    assert len(merged_tree.members) == 3


def test_deduplicate_with_nicknames(proto_handler_instance):
    """Tests that nicknames are used in matching."""
    tree1 = family_tree_pb2.FamilyTree()
    tree1.members["1"].name = "Robert"
    tree1.members["1"].id = "1"
    tree1.members["1"].nicknames.append("Bob")

    tree2 = family_tree_pb2.FamilyTree()
    tree2.members["101"].name = "Bob"
    tree2.members["101"].id = "101"

    merged = proto_handler_instance._deduplicate_family_members(tree1, tree2)
    assert len(merged.members) == 1


def test_deduplicate_with_neighbor_similarity(proto_handler_instance):
    """Tests that neighbor similarity influences matching."""
    tree1 = family_tree_pb2.FamilyTree()
    tree1.members["1"].name = "John A"
    tree1.members["1"].id = "1"
    tree1.members["2"].name = "Jane A"
    tree1.members["2"].id = "2"
    tree1.relationships["1"].spouse_ids.append("2")
    tree1.relationships["2"].spouse_ids.append("1")

    tree2 = family_tree_pb2.FamilyTree()
    tree2.members["101"].name = "Jon A"
    tree2.members["101"].id = "101"
    tree2.members["102"].name = "Jane A"
    tree2.members["102"].id = "102"
    tree2.relationships["101"].spouse_ids.append("102")
    tree2.relationships["102"].spouse_ids.append("101")

    merged = proto_handler_instance._deduplicate_family_members(tree1, tree2)
    assert len(merged.members) == 2


def test_merge_family_trees_integration(proto_handler_instance, sample_nx_graph):
    """An integration test for the entire merge process."""
    other_tree = family_tree_pb2.FamilyTree()
    other_tree.members["101"].name = "Johnathan Smith"
    other_tree.members["101"].id = "101"
    other_tree.members["101"].gender = utils_pb2.MALE
    other_tree_text = text_format.MessageToString(other_tree)

    proto_handler_instance.merge_family_trees(sample_nx_graph, {}, other_tree_text)

    # After merge, we expect John Smith from the graph and Johnathan Smith to merge.
    assert len(proto_handler_instance._family_tree.members) == 2
    assert "Johnathan Smith" in [
        m.name for m in proto_handler_instance._family_tree.members.values()
    ]

from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from familytree.handlers.chat_handler import ChatHandler
from familytree.handlers.family_tree_handler import FamilyTreeHandler
from familytree.handlers.graph_handler import GraphHandler
from familytree.handlers.proto_handler import ProtoHandler
from familytree.models.base_model import OK_STATUS
from familytree.models.manage_model import (
    AddFamilyMemberRequest,
    AddFamilyMemberResponse,
    LoadFamilyRequest,
    LoadFamilyResponse,
)
from familytree.proto import family_tree_pb2
from familytree.utils.graph_types import EdgeType, GraphNode


def test_family_tree_handler_init():
    """
    Tests that FamilyTreeHandler initializes its component handlers.
    """
    handler = FamilyTreeHandler()
    assert isinstance(handler.graph_handler, GraphHandler), (
        "graph_handler should be an instance of GraphHandler"
    )
    assert isinstance(handler.proto_handler, ProtoHandler), (
        "proto_handler should be an instance of ProtoHandler"
    )
    assert isinstance(handler.chat_handler, ChatHandler), (
        "chat_handler should be an instance of ChatHandler"
    )


def test_load_family_tree(
    weasley_family_tree_textproto,  # Fixture from conftest.py
    weasley_family_tree_pb,  # Fixture from conftest.py
):
    """
    Tests the load_family_tree method as an integration test,
    verifying the state of ProtoHandler and GraphHandler.
    """
    handler = FamilyTreeHandler()

    request = LoadFamilyRequest(
        filename="test.textpb", content=weasley_family_tree_textproto
    )

    response = handler.load_family_tree(request)

    # Assert response
    assert isinstance(response, LoadFamilyResponse)
    assert response.status == OK_STATUS
    assert response.message == "Family tree loaded successfully."

    weasley_children_ids = [
        "BILLW",
        "CHARW",
        "PERCW",
        "FREDW",
        "GEORW",
        "RONAW",
        "GINNW",
    ]

    assert weasley_family_tree_pb == handler.proto_handler.get_family_tree()

    # Assert GraphHandler state
    graph = handler.graph_handler.get_family_graph()
    assert "ARTHW" in graph.nodes
    assert "MOLLW" in graph.nodes
    for child_id in weasley_children_ids:
        assert child_id in graph.nodes

    assert graph.number_of_nodes() == 9
    assert graph.number_of_edges() == 30

    # Check node data
    arthur_node_data = graph.nodes["ARTHW"]["data"]
    assert isinstance(arthur_node_data, GraphNode)
    assert arthur_node_data.attributes.name == "Arthur Weasley"
    molly_node_data = graph.nodes["MOLLW"]["data"]
    assert isinstance(molly_node_data, GraphNode)
    assert molly_node_data.attributes.name == "Molly Weasley"

    assert graph.edges["ARTHW", "MOLLW"]["data"].edge_type == EdgeType.SPOUSE
    assert graph.edges["MOLLW", "ARTHW"]["data"].edge_type == EdgeType.SPOUSE

    for child_id in weasley_children_ids:
        # Arthur is parent of child_id
        assert (
            graph.edges["ARTHW", child_id]["data"].edge_type == EdgeType.PARENT_TO_CHILD
        )
        assert graph.edges["ARTHW", child_id]["data"].is_rendered
        # child_id is child of Arthur
        assert (
            graph.edges[child_id, "ARTHW"]["data"].edge_type == EdgeType.CHILD_TO_PARENT
        )
        assert not graph.edges[child_id, "ARTHW"]["data"].is_rendered
        # Molly is parent of child_id
        assert (
            graph.edges["MOLLW", child_id]["data"].edge_type == EdgeType.PARENT_TO_CHILD
        )
        # child_id is child of Molly
        assert (
            graph.edges[child_id, "MOLLW"]["data"].edge_type == EdgeType.CHILD_TO_PARENT
        )


def test_add_reverse_relationship():
    handler = FamilyTreeHandler()
    # Parent to Child -> Child to Parent
    rel1 = {
        "source_id": "p1",
        "target_id": "c1",
        "relationship_type": EdgeType.PARENT_TO_CHILD,
    }
    rev1 = handler._add_reverse_relationship(rel1)
    assert rev1 == {
        "source_id": "c1",
        "target_id": "p1",
        "relationship_type": EdgeType.CHILD_TO_PARENT,
    }

    # Child to Parent -> Parent to Child
    rel2 = {
        "source_id": "c1",
        "target_id": "p1",
        "relationship_type": EdgeType.CHILD_TO_PARENT,
    }
    rev2 = handler._add_reverse_relationship(rel2)
    assert rev2 == {
        "source_id": "p1",
        "target_id": "c1",
        "relationship_type": EdgeType.PARENT_TO_CHILD,
    }

    # Spouse -> Spouse
    rel3 = {"source_id": "s1", "target_id": "s2", "relationship_type": EdgeType.SPOUSE}
    rev3 = handler._add_reverse_relationship(rel3)
    assert rev3 == {
        "source_id": "s2",
        "target_id": "s1",
        "relationship_type": EdgeType.SPOUSE,
    }


def test_infer_relationships_integration():
    # Scenario 1: PARENT_TO_CHILD -> infers other parent for child
    handler_ptc = FamilyTreeHandler()
    # Setup graph: parent1 --spouse-- parent2, child1 is unrelated yet
    handler_ptc.graph_handler.add_member(
        "parent1", family_tree_pb2.FamilyMember(id="parent1")
    )
    handler_ptc.graph_handler.add_member(
        "parent2", family_tree_pb2.FamilyMember(id="parent2")
    )
    handler_ptc.graph_handler.add_member(
        "child1", family_tree_pb2.FamilyMember(id="child1")
    )
    handler_ptc.graph_handler.add_spouse_relation("parent1", "parent2")
    handler_ptc.graph_handler.add_spouse_relation(
        "parent2", "parent1"
    )  # Ensure bi-directional for get_spouse

    main_rel_parent_to_child = {
        "source_id": "parent1",
        "target_id": "child1",
        "relationship_type": EdgeType.PARENT_TO_CHILD,
    }
    inferred_ptc = handler_ptc.infer_relationships(main_rel_parent_to_child)
    assert len(inferred_ptc) == 2
    assert {
        "source_id": "parent2",
        "target_id": "child1",
        "relationship_type": EdgeType.PARENT_TO_CHILD,
    } in inferred_ptc
    assert {
        "source_id": "child1",
        "target_id": "parent2",
        "relationship_type": EdgeType.CHILD_TO_PARENT,
    } in inferred_ptc

    # Scenario 2: CHILD_TO_PARENT -> infers spouse for the new parent
    handler_ctp = FamilyTreeHandler()
    # Setup graph: child1 --parent_of-- existing_parent, new_parent is unrelated
    handler_ctp.graph_handler.add_member(
        "child1", family_tree_pb2.FamilyMember(id="child1")
    )
    handler_ctp.graph_handler.add_member(
        "existing_parent", family_tree_pb2.FamilyMember(id="existing_parent")
    )
    handler_ctp.graph_handler.add_member(
        "new_parent", family_tree_pb2.FamilyMember(id="new_parent")
    )
    handler_ctp.graph_handler.add_parent_relation(
        "child1", "existing_parent"
    )  # child1 -> existing_parent (CHILD_TO_PARENT)
    # For get_parent to work, the CHILD_TO_PARENT edge must exist from child1

    main_rel_child_to_parent = {
        "source_id": "child1",
        "target_id": "new_parent",
        "relationship_type": EdgeType.CHILD_TO_PARENT,
    }
    inferred_ctp = handler_ctp.infer_relationships(main_rel_child_to_parent)
    assert len(inferred_ctp) == 2
    assert {
        "source_id": "existing_parent",
        "target_id": "new_parent",
        "relationship_type": EdgeType.SPOUSE,
    } in inferred_ctp
    assert {
        "source_id": "new_parent",
        "target_id": "existing_parent",
        "relationship_type": EdgeType.SPOUSE,
    } in inferred_ctp

    # Scenario 3: SPOUSE -> infers parent for children of one spouse with the other spouse
    handler_s = FamilyTreeHandler()
    # Setup graph: spouse1 has children childA, childB. spouse2 is unrelated.
    handler_s.graph_handler.add_member(
        "spouse1", family_tree_pb2.FamilyMember(id="spouse1")
    )
    handler_s.graph_handler.add_member(
        "spouse2", family_tree_pb2.FamilyMember(id="spouse2")
    )
    handler_s.graph_handler.add_member(
        "childA", family_tree_pb2.FamilyMember(id="childA")
    )
    handler_s.graph_handler.add_member(
        "childB", family_tree_pb2.FamilyMember(id="childB")
    )
    handler_s.graph_handler.add_child_relation(
        "spouse1", "childA"
    )  # spouse1 -> childA (PARENT_TO_CHILD)
    handler_s.graph_handler.add_child_relation(
        "spouse1", "childB"
    )  # spouse1 -> childB (PARENT_TO_CHILD)

    main_rel_spouse = {
        "source_id": "spouse1",
        "target_id": "spouse2",
        "relationship_type": EdgeType.SPOUSE,
    }
    inferred_s = handler_s.infer_relationships(main_rel_spouse)
    assert len(inferred_s) == 4
    assert {
        "source_id": "childA",
        "target_id": "spouse2",
        "relationship_type": EdgeType.CHILD_TO_PARENT,
    } in inferred_s
    assert {
        "source_id": "spouse2",
        "target_id": "childA",
        "relationship_type": EdgeType.PARENT_TO_CHILD,
    } in inferred_s
    assert {
        "source_id": "childB",
        "target_id": "spouse2",
        "relationship_type": EdgeType.CHILD_TO_PARENT,
    } in inferred_s
    assert {
        "source_id": "spouse2",
        "target_id": "childB",
        "relationship_type": EdgeType.PARENT_TO_CHILD,
    } in inferred_s


def test_add_family_member_no_inference():
    handler = FamilyTreeHandler()
    # Add source member to graph
    source_member_id = "source_id"
    handler.graph_handler.add_member(
        source_member_id,
        family_tree_pb2.FamilyMember(id=source_member_id, name="Source"),
    )

    new_member_dict = {"id": "new_id", "name": "New Member"}
    request = AddFamilyMemberRequest(
        new_member_data=new_member_dict,
        source_family_member_id=source_member_id,
        relationship_type=EdgeType.PARENT_TO_CHILD,
        infer_relationships=False,
    )

    response = handler.add_family_member(request)

    # Assert new member was added to graph
    assert handler.graph_handler._graph.has_node("new_id")
    assert (
        handler.graph_handler._graph.nodes["new_id"]["data"].attributes.name
        == "New Member"
    )

    # Assert primary relationship (PARENT_TO_CHILD: source_id -> new_id)
    assert handler.graph_handler._graph.has_edge(source_member_id, "new_id")
    edge_data_primary = handler.graph_handler._graph.get_edge_data(
        source_member_id, "new_id"
    )["data"]
    assert edge_data_primary.edge_type == EdgeType.PARENT_TO_CHILD

    # Assert reverse relationship (CHILD_TO_PARENT: new_id -> source_id)
    assert handler.graph_handler._graph.has_edge("new_id", source_member_id)
    edge_data_reverse = handler.graph_handler._graph.get_edge_data(
        "new_id", source_member_id
    )["data"]
    assert edge_data_reverse.edge_type == EdgeType.CHILD_TO_PARENT

    # Ensure no other edges were created (total 2 edges)
    assert handler.graph_handler._graph.number_of_edges() == 2

    assert isinstance(response, AddFamilyMemberResponse)
    assert response.status == OK_STATUS
    assert response.message == "Family member added successfully."


def test_add_family_member_with_inference_adds_child_to_both_parents():
    handler = FamilyTreeHandler()
    # Setup: parent1 and parent2 are spouses
    parent1_id = "parent1_id"
    parent2_id = "parent2_id"
    handler.graph_handler.add_member(
        parent1_id, family_tree_pb2.FamilyMember(id=parent1_id, name="Parent 1")
    )
    handler.graph_handler.add_member(
        parent2_id, family_tree_pb2.FamilyMember(id=parent2_id, name="Parent 2")
    )
    handler.graph_handler.add_spouse_relation(parent1_id, parent2_id)
    handler.graph_handler.add_spouse_relation(
        parent2_id, parent1_id
    )  # Bidirectional for get_spouse

    new_member_dict = {"id": "child_id", "name": "New Child"}
    request = AddFamilyMemberRequest(
        new_member_data=new_member_dict,
        source_family_member_id=parent1_id,
        relationship_type=EdgeType.PARENT_TO_CHILD,  # parent1 -> child_id
        infer_relationships=True,
    )

    handler.add_family_member(request)

    # Assert new member "child_id" is added
    assert handler.graph_handler._graph.has_node("child_id")

    # Primary relationship: parent1_id -> child_id (PARENT_TO_CHILD)
    assert handler.graph_handler._graph.has_edge(parent1_id, "child_id")
    assert (
        handler.graph_handler._graph.get_edge_data(parent1_id, "child_id")[
            "data"
        ].edge_type
        == EdgeType.PARENT_TO_CHILD
    )
    # Reverse of primary: child_id -> parent1_id (CHILD_TO_PARENT)
    assert handler.graph_handler._graph.has_edge("child_id", parent1_id)
    assert (
        handler.graph_handler._graph.get_edge_data("child_id", parent1_id)[
            "data"
        ].edge_type
        == EdgeType.CHILD_TO_PARENT
    )

    # Inferred relationship: parent2_id -> child_id (PARENT_TO_CHILD)
    assert handler.graph_handler._graph.has_edge(parent2_id, "child_id")
    assert (
        handler.graph_handler._graph.get_edge_data(parent2_id, "child_id")[
            "data"
        ].edge_type
        == EdgeType.PARENT_TO_CHILD
    )
    # Reverse of inferred: child_id -> parent2_id (CHILD_TO_PARENT)
    assert handler.graph_handler._graph.has_edge("child_id", parent2_id)
    assert (
        handler.graph_handler._graph.get_edge_data("child_id", parent2_id)[
            "data"
        ].edge_type
        == EdgeType.CHILD_TO_PARENT
    )

    # Total edges: 2 for parent1-child1, 2 for parent2-child1, 2 for parent1-parent2 spouse = 6
    assert handler.graph_handler._graph.number_of_edges() == 6


def test_add_family_member_invalid_relationship_type(caplog):
    handler = FamilyTreeHandler()
    source_member_id = "source_id"
    handler.graph_handler.add_member(
        source_member_id,
        family_tree_pb2.FamilyMember(id=source_member_id, name="Source"),
    )

    new_member_dict = {"id": "new_id", "name": "New Member"}
    with pytest.raises(ValidationError):
        handler.add_family_member(
            AddFamilyMemberRequest(
                new_member_data=new_member_dict,
                source_family_member_id=source_member_id,
                relationship_type=10,  # Not an EdgeType enum
                infer_relationships=False,
            )
        )


def test_render_family_tree():
    """Tests the render_family_tree method."""
    handler = FamilyTreeHandler()
    expected_html = "<html>Mocked Tree</html>"

    # Mock the graph_handler's render_graph_to_html method
    handler.graph_handler.render_graph_to_html = MagicMock(return_value=expected_html)

    html_output = handler.render_family_tree()

    handler.graph_handler.render_graph_to_html.assert_called_once_with()
    assert html_output == expected_html

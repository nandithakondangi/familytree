import re
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from familytree.exceptions import InvalidInputError, MemberNotFoundError
from familytree.handlers.chat_handler import ChatHandler
from familytree.handlers.family_tree_handler import FamilyTreeHandler
from familytree.handlers.graph_handler import GraphHandler
from familytree.handlers.proto_handler import ProtoHandler
from familytree.models.base_model import OK_STATUS
from familytree.models.manage_model import (
    AddFamilyMemberRequest,
    AddFamilyMemberResponse,
    AddRelationshipRequest,
    DeleteFamilyMemberRequest,
    DeleteRelationshipRequest,
    LoadFamilyRequest,
    LoadFamilyResponse,
    UpdateFamilyMemberRequest,
)
from familytree.proto import family_tree_pb2
from familytree.utils.graph_types import EdgeType, GraphNode

MEMBER_ID_PATTERN = r"^F[A-Z0-9]{3}-M[A-Z0-9]{3}-B[A-Z0-9]{3}-R[A-Z0-9]{3}$"


@pytest.fixture
def loaded_handler(weasley_family_tree_textproto):
    """Provides a FamilyTreeHandler with the Weasley family tree loaded."""
    handler = FamilyTreeHandler()
    request = LoadFamilyRequest(
        filename="test.textpb", content=weasley_family_tree_textproto
    )
    handler.load_family_tree(request)
    return handler


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
        "parent1", family_tree_pb2.FamilyMember(id="parent1", name="Parent 1")
    )
    handler_ptc.graph_handler.add_member(
        "parent2", family_tree_pb2.FamilyMember(id="parent2", name="Parent 2")
    )
    handler_ptc.graph_handler.add_member(
        "child1", family_tree_pb2.FamilyMember(id="child1", name="Child 1")
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
    inferred_ptc = handler_ptc._infer_relationships(main_rel_parent_to_child)
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
        "child1", family_tree_pb2.FamilyMember(id="child1", name="Child 1")
    )
    handler_ctp.graph_handler.add_member(
        "existing_parent",
        family_tree_pb2.FamilyMember(id="existing_parent", name="Existing Parent"),
    )
    handler_ctp.graph_handler.add_member(
        "new_parent", family_tree_pb2.FamilyMember(id="new_parent", name="New Parent")
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
    inferred_ctp = handler_ctp._infer_relationships(main_rel_child_to_parent)
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
        "spouse1", family_tree_pb2.FamilyMember(id="spouse1", name="Spouse 1")
    )
    handler_s.graph_handler.add_member(
        "spouse2", family_tree_pb2.FamilyMember(id="spouse2", name="Spouse 2")
    )
    handler_s.graph_handler.add_member(
        "childA", family_tree_pb2.FamilyMember(id="childA", name="Child A")
    )
    handler_s.graph_handler.add_member(
        "childB", family_tree_pb2.FamilyMember(id="childB", name="Child B")
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
    inferred_s = handler_s._infer_relationships(main_rel_spouse)
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

    new_member_name = "New Member"
    new_member_dict = {"name": new_member_name}  # ID is no longer provided
    request = AddFamilyMemberRequest(
        new_member_data=new_member_dict,
        source_family_member_id=source_member_id,
        relationship_type=EdgeType.PARENT_TO_CHILD,
        infer_relationships=False,
    )
    initial_nodes = set(handler.graph_handler._graph.nodes())
    response = handler.add_family_member(request)
    current_nodes = set(handler.graph_handler._graph.nodes())
    new_member_ids = current_nodes - initial_nodes
    assert len(new_member_ids) == 1
    generated_id = new_member_ids.pop()

    # Assert new member was added to graph
    assert re.match(MEMBER_ID_PATTERN, generated_id) is not None
    assert handler.graph_handler._graph.has_node(generated_id)
    assert (
        handler.graph_handler._graph.nodes[generated_id]["data"].attributes.name
        == new_member_name
    )

    # Assert primary relationship (PARENT_TO_CHILD: source_id -> new_id)
    assert handler.graph_handler._graph.has_edge(source_member_id, generated_id)
    edge_data_primary = handler.graph_handler._graph.get_edge_data(
        source_member_id, generated_id
    )["data"]
    assert edge_data_primary.edge_type == EdgeType.PARENT_TO_CHILD

    # Assert reverse relationship (CHILD_TO_PARENT: new_id -> source_id)
    assert handler.graph_handler._graph.has_edge(generated_id, source_member_id)
    edge_data_reverse = handler.graph_handler._graph.get_edge_data(
        generated_id, source_member_id
    )["data"]
    assert edge_data_reverse.edge_type == EdgeType.CHILD_TO_PARENT

    # Ensure no other edges were created (total 2 edges)
    assert handler.graph_handler._graph.number_of_edges() == 2

    assert isinstance(response, AddFamilyMemberResponse)
    assert response.status == OK_STATUS
    assert response.message == f"{new_member_name} added successfully to the family."


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

    new_member_name = "New Child"
    new_member_dict = {"name": new_member_name}  # ID is no longer provided
    request = AddFamilyMemberRequest(
        new_member_data=new_member_dict,
        source_family_member_id=parent1_id,
        relationship_type=EdgeType.PARENT_TO_CHILD,  # parent1 -> child_id
        infer_relationships=True,
    )
    initial_nodes = set(handler.graph_handler._graph.nodes())
    handler.add_family_member(request)
    current_nodes = set(handler.graph_handler._graph.nodes())
    new_member_ids = (
        current_nodes - initial_nodes - {parent1_id, parent2_id}
    )  # Exclude existing nodes
    assert len(new_member_ids) == 1
    generated_child_id = new_member_ids.pop()

    # Assert new member "child_id" is added
    assert re.match(MEMBER_ID_PATTERN, generated_child_id) is not None
    assert handler.graph_handler._graph.has_node(generated_child_id)
    assert (
        handler.graph_handler._graph.nodes[generated_child_id]["data"].attributes.name
        == new_member_name
    )

    # Primary relationship: parent1_id -> child_id (PARENT_TO_CHILD)
    assert handler.graph_handler._graph.has_edge(parent1_id, generated_child_id)
    assert (
        handler.graph_handler._graph.get_edge_data(parent1_id, generated_child_id)[
            "data"
        ].edge_type
        == EdgeType.PARENT_TO_CHILD
    )
    # Reverse of primary: child_id -> parent1_id (CHILD_TO_PARENT)
    assert handler.graph_handler._graph.has_edge(generated_child_id, parent1_id)
    assert (
        handler.graph_handler._graph.get_edge_data(generated_child_id, parent1_id)[
            "data"
        ].edge_type
        == EdgeType.CHILD_TO_PARENT
    )

    # Inferred relationship: parent2_id -> child_id (PARENT_TO_CHILD)
    assert handler.graph_handler._graph.has_edge(parent2_id, generated_child_id)
    assert (
        handler.graph_handler._graph.get_edge_data(parent2_id, generated_child_id)[
            "data"
        ].edge_type
        == EdgeType.PARENT_TO_CHILD
    )
    # Reverse of inferred: child_id -> parent2_id (CHILD_TO_PARENT)
    assert handler.graph_handler._graph.has_edge(generated_child_id, parent2_id)
    assert (
        handler.graph_handler._graph.get_edge_data(generated_child_id, parent2_id)[
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
                relationship_type=10,  # pyrefly: ignore
                infer_relationships=False,
            )
        )


def test_render_family_tree(loaded_handler):
    """Tests the render_family_tree method."""
    handler = loaded_handler
    expected_html = "<html>Mocked Tree</html>"

    # Mock the graph_handler's render_graph_to_html method
    handler.graph_handler.render_graph_to_html = MagicMock(return_value=expected_html)

    html_output = handler.render_family_tree("light")

    handler.graph_handler.render_graph_to_html.assert_called_once_with("light")
    assert html_output == expected_html


def test_add_first_family_member_no_relationship():
    """
    Test adding the very first family member without providing
    source_family_member_id or relationship_type.
    """
    handler = FamilyTreeHandler()

    new_member_name = "Alice"
    new_member_data = {
        "name": new_member_name,
    }

    request = AddFamilyMemberRequest(
        infer_relationships=False,
        new_member_data=new_member_data,
    )
    initial_nodes = set(handler.graph_handler.get_family_graph().nodes())
    response = handler.add_family_member(request)
    current_nodes = set(handler.graph_handler.get_family_graph().nodes())
    new_member_ids = current_nodes - initial_nodes
    assert len(new_member_ids) == 1
    generated_id = new_member_ids.pop()

    graph = handler.graph_handler.get_family_graph()
    assert re.match(MEMBER_ID_PATTERN, generated_id) is not None
    assert graph.has_node(generated_id)

    # 2. Verify node attributes (optional, but good for completeness)
    node_data = graph.nodes[generated_id]["data"]
    assert isinstance(node_data, GraphNode)
    assert node_data.attributes.name == new_member_data["name"]

    # 3. Verify that NO relationships (edges) were created
    assert graph.number_of_edges() == 0

    assert isinstance(response, AddFamilyMemberResponse)
    assert response.status == OK_STATUS
    assert (
        response.message
        == f"{new_member_data['name']} added successfully to the family."
    )


def test_save_family_tree(weasley_family_tree_textproto):
    """
    Tests the save_family_tree method.
    """
    handler = FamilyTreeHandler()

    # Load a known family tree to have some data to save
    request = LoadFamilyRequest(
        filename="test.textpb", content=weasley_family_tree_textproto
    )
    handler.load_family_tree(request)

    # Call the save method
    response = handler.save_family_tree(visible_only=False)

    # Assert the response
    assert response.status == OK_STATUS
    assert response.message == "Created family tree text proto"

    assert response.family_tree_txtpb == weasley_family_tree_textproto


def test_add_relationship(loaded_handler):
    handler = loaded_handler
    # Add Fleur Delacour and connect her to Bill
    fleur_id = "FLEUD"
    handler.graph_handler.add_member(
        fleur_id, family_tree_pb2.FamilyMember(id=fleur_id, name="Fleur Delacour")
    )

    request = AddRelationshipRequest(
        source_member_id="BILLW",
        target_member_id=fleur_id,
        relationship_type=EdgeType.SPOUSE,
        add_inverse_relationship=True,
    )
    response = handler.add_relationship(request)

    assert response.status == OK_STATUS
    assert (
        "Relationship between BILLW and FLEUD added successfully." in response.message
    )

    graph = handler.graph_handler.get_family_graph()
    assert graph.has_edge("BILLW", fleur_id)
    assert graph.get_edge_data("BILLW", fleur_id)["data"].edge_type == EdgeType.SPOUSE
    assert graph.has_edge(fleur_id, "BILLW")
    assert graph.get_edge_data(fleur_id, "BILLW")["data"].edge_type == EdgeType.SPOUSE


def test_add_relationship_no_inverse(loaded_handler):
    handler = loaded_handler
    fleur_id = "FLEUD"
    handler.graph_handler.add_member(
        fleur_id, family_tree_pb2.FamilyMember(id=fleur_id, name="Fleur Delacour")
    )

    request = AddRelationshipRequest(
        source_member_id="BILLW",
        target_member_id=fleur_id,
        relationship_type=EdgeType.SPOUSE,
        add_inverse_relationship=False,
    )
    response = handler.add_relationship(request)

    assert response.status == OK_STATUS

    graph = handler.graph_handler.get_family_graph()
    assert graph.has_edge("BILLW", fleur_id)
    assert not graph.has_edge(fleur_id, "BILLW")


def test_add_relationship_invalid_type(loaded_handler):
    handler = loaded_handler
    with pytest.raises(InvalidInputError):
        handler._add_relationship_to_graph(
            {
                "source_id": "ARTHW",
                "target_id": "MOLLW",
                "relationship_type": "INVALID_RELATIONSHIP",
            }
        )


def test_update_family_member(loaded_handler):
    handler = loaded_handler
    member_id_to_update = "RONAW"
    updated_data = {
        "name": "Ronald Bilius Weasley",
        "nicknames": ["Ron", "Won-Won"],
    }

    request = UpdateFamilyMemberRequest(
        member_id=member_id_to_update,
        updated_member_data=updated_data,
    )

    response = handler.update_family_member(request)

    assert response.status == OK_STATUS
    assert f"Member {member_id_to_update} updated successfully." in response.message

    response = handler.get_member_info(member_id_to_update)
    updated_member_info = response.member_info
    assert updated_member_info["name"] == "Ronald Bilius Weasley"
    assert "Ron" in updated_member_info["nicknames"]


def test_get_member_info(loaded_handler):
    handler = loaded_handler
    member_id = "GINNW"

    response = handler.get_member_info(member_id)

    assert response.status == OK_STATUS
    assert response.message == "Member info retrieved successfully."
    assert response.member_info["name"] == "Ginny Weasley"
    assert response.member_info["id"] == member_id


def test_get_member_info_not_found(loaded_handler):
    handler = loaded_handler
    with pytest.raises(MemberNotFoundError):
        handler.get_member_info("UNKNOWN_ID")


def test_delete_family_member(loaded_handler):
    handler = loaded_handler
    member_id_to_delete = "PERCW"

    graph = handler.graph_handler.get_family_graph()
    assert graph.has_node(member_id_to_delete)

    request = DeleteFamilyMemberRequest(member_id=member_id_to_delete)
    response = handler.delete_family_member(request)

    assert response.status == OK_STATUS
    assert response.message == "Member deleted successfully."

    assert not graph.has_node(member_id_to_delete)
    # Check that edges are also removed
    assert not graph.has_edge("ARTHW", member_id_to_delete)
    assert not graph.has_edge(member_id_to_delete, "ARTHW")


def test_delete_family_member_with_orphaned_neighbors(loaded_handler):
    # The spouse should be removed if remove_orphaned_neighbors is true.
    handler = loaded_handler
    percy_id = "PERCW"
    audrey_id = "AUDW"
    handler.graph_handler.add_member(
        audrey_id, family_tree_pb2.FamilyMember(id=audrey_id, name="Audrey Weasley")
    )
    handler.graph_handler.add_spouse_relation(percy_id, audrey_id)
    handler.graph_handler.add_spouse_relation(audrey_id, percy_id)

    graph = handler.graph_handler.get_family_graph()
    assert graph.has_node(audrey_id)

    request = DeleteFamilyMemberRequest(
        member_id=percy_id, remove_orphaned_neighbors=True
    )
    handler.delete_family_member(request)

    assert not graph.has_node(percy_id)
    assert not graph.has_node(audrey_id)  # Audrey is an orphan and should be removed.


def test_delete_relationship(loaded_handler):
    handler = loaded_handler
    source_id = "ARTHW"
    target_id = "MOLLW"

    graph = handler.graph_handler.get_family_graph()
    assert graph.has_edge(source_id, target_id)

    request = DeleteRelationshipRequest(
        source_member_id=source_id,
        target_member_id=target_id,
        remove_inverse_relationship=False,
    )
    response = handler.delete_relationship(request)

    assert response.status == OK_STATUS
    assert response.message == "Relationship deleted successfully."

    assert not graph.has_edge(source_id, target_id)
    assert graph.has_edge(target_id, source_id)  # Inverse should still exist


def test_delete_relationship_with_inverse(loaded_handler):
    handler = loaded_handler
    source_id = "ARTHW"
    target_id = "MOLLW"

    graph = handler.graph_handler.get_family_graph()
    assert graph.has_edge(source_id, target_id)
    assert graph.has_edge(target_id, source_id)

    request = DeleteRelationshipRequest(
        source_member_id=source_id,
        target_member_id=target_id,
        remove_inverse_relationship=True,
    )
    response = handler.delete_relationship(request)

    assert response.status == OK_STATUS

    assert not graph.has_edge(source_id, target_id)
    assert not graph.has_edge(target_id, source_id)

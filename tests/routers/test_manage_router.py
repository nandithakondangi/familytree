import re
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from familytree import app_state

# Assuming your FastAPI app instance is in family_tree_webapp.py
# and app_state is globally accessible from familytree.globals
from familytree.family_tree_webapp import app  # Make sure this path is correct
from familytree.handlers.graph_handler import EdgeType
from familytree.models.base_model import OK_STATUS
from familytree.models.manage_model import AddFamilyMemberRequest, LoadFamilyRequest
from familytree.proto import family_tree_pb2

MEMBER_ID_PATTERN = r"^F[A-Z0-9]{3}-M[A-Z0-9]{3}-B[A-Z0-9]{3}-R[A-Z0-9]{3}$"


@pytest.fixture
def client():
    return TestClient(app)


def test_create_new_family_success(client):
    """E2E test for creating a new family tree."""
    response = client.post("/api/v1/manage/create_family")
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == OK_STATUS
    assert json_response["message"] == "New family tree created."

    # Verify app_state
    handler = app_state.get_current_family_tree_handler()
    assert not handler.proto_handler.get_family_tree().members, (
        "Proto members should be empty"
    )
    assert not handler.graph_handler.get_family_graph().nodes, (
        "Graph nodes should be empty"
    )
    assert not handler.graph_handler.get_family_graph().edges, (
        "Graph edges should be empty"
    )


@patch("familytree.routers.manage_router.app_state")
@patch("familytree.routers.manage_router.logger")
def test_create_new_family_exception(mock_logger, mock_app_state_in_router, client):
    """Tests create_family endpoint when app_state.reset raises an exception."""
    mock_app_state_in_router.reset_current_family_tree_handler.side_effect = Exception(
        "Simulated reset error"
    )
    response = client.post("/api/v1/manage/create_family")
    assert response.status_code == 500
    assert (
        response.json()["detail"]
        == "Unexpected error occured during create family operation."
    )
    mock_logger.exception.assert_called_once()


def test_load_family_data_success(
    client, weasley_family_tree_textproto, weasley_family_tree_pb
):
    """E2E test for loading family data."""
    request_data = LoadFamilyRequest(
        filename="test.textpb",  # pyrefly: ignore
        content=weasley_family_tree_textproto,
    )
    response = client.post("/api/v1/manage/load_family", json=request_data.model_dump())

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == OK_STATUS
    assert json_response["message"] == "Family tree loaded successfully."

    # Verify app_state and handler contents
    handler = app_state.get_current_family_tree_handler()

    # ProtoHandler assertions
    loaded_proto_tree = handler.proto_handler.get_family_tree()
    assert loaded_proto_tree == weasley_family_tree_pb

    # GraphHandler assertions
    graph = handler.graph_handler.get_family_graph()

    assert graph.number_of_nodes() == 9
    assert graph.number_of_edges() == 30


@patch("familytree.routers.manage_router.app_state")
@patch("familytree.routers.manage_router.logger")
def test_load_family_data_exception(mock_logger, mock_app_state_in_router, client):
    """Tests load_family endpoint when app_state.reset raises an exception."""
    mock_app_state_in_router.reset_current_family_tree_handler.side_effect = Exception(
        "Simulated reset error before load"
    )
    # pyrefly: ignore
    request_data = LoadFamilyRequest(filename="test.textpb", content="any_content")
    response = client.post("/api/v1/manage/load_family", json=request_data.model_dump())
    assert response.status_code == 500
    assert (
        response.json()["detail"]
        == "Unexpected error occured during load family operation."
    )
    mock_logger.exception.assert_called_once()


def test_add_family_member_e2e_no_inference(client):
    """E2E test for adding a family member without relationship inference."""
    handler = app_state.get_current_family_tree_handler()

    source_member_id = "source001"
    source_member_pb2 = family_tree_pb2.FamilyMember(
        id=source_member_id, name="Source Member"
    )

    # Manually add to handler's graph for setup, as if it was loaded/created previously
    handler.graph_handler.add_member(source_member_id, source_member_pb2)

    new_member_name = "New Member"
    request_payload = AddFamilyMemberRequest(
        new_member_data={"name": new_member_name},  # ID is no longer provided
        source_family_member_id=source_member_id,
        relationship_type=EdgeType.PARENT_TO_CHILD,
        infer_relationships=False,
    )

    initial_nodes = set(handler.graph_handler.get_family_graph().nodes())
    response = client.post(
        "/api/v1/manage/add_family_member", json=request_payload.model_dump()
    )
    current_nodes = set(handler.graph_handler.get_family_graph().nodes())
    new_member_ids = current_nodes - initial_nodes
    assert len(new_member_ids) == 1
    generated_id = new_member_ids.pop()

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == OK_STATUS
    assert (
        json_response["message"]
        == f"{new_member_name} added successfully to the family."
    )

    # Verify graph state in the handler
    graph = handler.graph_handler.get_family_graph()

    assert re.match(MEMBER_ID_PATTERN, generated_id) is not None
    assert graph.has_node(generated_id)
    assert graph.nodes[generated_id]["data"].attributes.name == new_member_name

    # Check primary relationship: source_member_id -> new_member_id (PARENT_TO_CHILD)
    assert graph.has_edge(source_member_id, generated_id)
    edge_primary = graph.get_edge_data(source_member_id, generated_id)["data"]
    assert edge_primary.edge_type == EdgeType.PARENT_TO_CHILD

    # Check reverse relationship: new_member_id -> source_member_id (CHILD_TO_PARENT)
    assert graph.has_edge(generated_id, source_member_id)
    edge_reverse = graph.get_edge_data(generated_id, source_member_id)["data"]
    assert edge_reverse.edge_type == EdgeType.CHILD_TO_PARENT

    assert graph.number_of_edges() == 2  # Only primary and its reverse


def test_add_first_family_member_e2e(client):
    """E2E test for adding the very first family member to a new tree."""
    handler = app_state.get_current_family_tree_handler()

    new_member_name = "Adam"
    request_payload = AddFamilyMemberRequest(
        new_member_data={
            "name": new_member_name,
        },
        # source_family_member_id is None by default
        # relationship_type is None by default
        infer_relationships=False,  # Inference is not applicable here
    )

    initial_nodes = set(handler.graph_handler.get_family_graph().nodes())
    response = client.post(
        "/api/v1/manage/add_family_member",
        json=request_payload.model_dump(exclude_none=True),
    )
    current_nodes = set(handler.graph_handler.get_family_graph().nodes())
    new_member_ids = current_nodes - initial_nodes
    assert len(new_member_ids) == 1
    generated_id = new_member_ids.pop()

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == OK_STATUS
    assert (
        json_response["message"]
        == f"{new_member_name} added successfully to the family."
    )

    # Verify graph state in the handler
    graph = handler.graph_handler.get_family_graph()

    assert re.match(MEMBER_ID_PATTERN, generated_id) is not None
    assert graph.has_node(generated_id)
    assert graph.nodes[generated_id]["data"].attributes.name == new_member_name
    assert graph.number_of_edges() == 0


def test_add_family_member_e2e_with_inference(client):
    """E2E test for adding a family member with relationship inference (child to spouses)."""
    handler = app_state.get_current_family_tree_handler()
    parent1_id = "parent1"
    parent2_id = "parent2"
    handler.graph_handler.add_member(
        parent1_id, family_tree_pb2.FamilyMember(id=parent1_id, name="Parent 1")
    )
    handler.graph_handler.add_member(
        parent2_id, family_tree_pb2.FamilyMember(id=parent2_id, name="Parent 2")
    )
    handler.graph_handler.add_spouse_relation(parent1_id, parent2_id)
    handler.graph_handler.add_spouse_relation(
        parent2_id, parent1_id
    )  # Ensure bidirectional for inference

    new_child_name = "New Child"
    request_payload = AddFamilyMemberRequest(
        new_member_data={"name": new_child_name},  # ID is no longer provided
        source_family_member_id=parent1_id,
        relationship_type=EdgeType.PARENT_TO_CHILD,
        infer_relationships=True,
    )

    initial_nodes = set(handler.graph_handler.get_family_graph().nodes())
    response = client.post(
        "/api/v1/manage/add_family_member", json=request_payload.model_dump()
    )
    current_nodes = set(handler.graph_handler.get_family_graph().nodes())
    new_member_ids = current_nodes - initial_nodes
    assert len(new_member_ids) == 1
    generated_child_id = new_member_ids.pop()

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == OK_STATUS
    assert (
        json_response["message"]
        == f"{new_child_name} added successfully to the family."
    )

    graph = handler.graph_handler.get_family_graph()

    assert re.match(MEMBER_ID_PATTERN, generated_child_id) is not None
    assert graph.has_node(generated_child_id)
    assert graph.nodes[generated_child_id]["data"].attributes.name == new_child_name

    # Primary: parent1 -> child1 (PARENT_TO_CHILD) & reverse
    assert graph.has_edge(parent1_id, generated_child_id)
    assert (
        graph.get_edge_data(parent1_id, generated_child_id)["data"].edge_type
        == EdgeType.PARENT_TO_CHILD
    )
    assert graph.has_edge(generated_child_id, parent1_id)
    assert (
        graph.get_edge_data(generated_child_id, parent1_id)["data"].edge_type
        == EdgeType.CHILD_TO_PARENT
    )

    # Inferred: parent2 -> child1 (PARENT_TO_CHILD) & reverse
    assert graph.has_edge(parent2_id, generated_child_id)
    assert (
        graph.get_edge_data(parent2_id, generated_child_id)["data"].edge_type
        == EdgeType.PARENT_TO_CHILD
    )
    assert graph.has_edge(generated_child_id, parent2_id)
    assert (
        graph.get_edge_data(generated_child_id, parent2_id)["data"].edge_type
        == EdgeType.CHILD_TO_PARENT
    )

    # Edges: 2 for parent1-spouse, 2 for parent1-child, 2 for parent2-child = 6
    assert graph.number_of_edges() == 6


@patch("familytree.routers.manage_router.app_state")
@patch("familytree.routers.manage_router.logger")
def test_add_family_member_exception(mock_logger, mock_app_state_in_router, client):
    """Tests add_family_member endpoint when an exception occurs."""
    mock_app_state_in_router.get_current_family_tree_handler.side_effect = Exception(
        "Simulated add member error"
    )
    request_payload = AddFamilyMemberRequest(
        new_member_data={"name": "Test Name"},  # ID is no longer provided
        source_family_member_id="source_id",
        relationship_type=EdgeType.PARENT_TO_CHILD,
        infer_relationships=False,
    )
    response = client.post(
        "/api/v1/manage/add_family_member", json=request_payload.model_dump()
    )
    assert response.status_code == 500
    assert (
        response.json()["detail"]
        == "Unexpected error occured during add family member operation"
    )
    mock_logger.exception.assert_called_once()


@pytest.mark.parametrize(
    "method, endpoint_template, detail_template",
    [
        (
            "POST",
            "/api/v1/manage/add_relationship",
            "Endpoint /manage/add_relationship is not yet implemented.",
        ),
        (
            "POST",
            "/api/v1/manage/update_family_member",
            "Endpoint /manage/update_family_member is not yet implemented.",
        ),
        (
            "POST",
            "/api/v1/manage/delete_family_member",
            "Endpoint /manage/delete_family_member is not yet implemented.",
        ),
        (
            "POST",
            "/api/v1/manage/delete_relationship",
            "Endpoint /manage/delete_relationship is not yet implemented.",
        ),
        (
            "GET",
            "/api/v1/manage/save_family",
            "Endpoint /manage/save_family_data is not yet implemented.",
        ),
        (
            "GET",
            "/api/v1/manage/export_family_snapshot",
            "Endpoint /manage/export_family_snapshot is not yet implemented.",
        ),
        (
            "GET",
            "/api/v1/manage/export_interactive_graph",
            "Endpoint /manage/export_interactive_graph is not yet implemented.",
        ),
    ],
)
def test_not_implemented_manage_endpoints(
    method, endpoint_template, detail_template, client
):
    """Tests that unimplemented management endpoints return 501."""
    if method == "POST":
        response = client.post(endpoint_template)  # No JSON body needed for 501 check
    else:  # GET
        response = client.get(endpoint_template)
    assert response.status_code == 501
    assert response.json()["detail"] == detail_template

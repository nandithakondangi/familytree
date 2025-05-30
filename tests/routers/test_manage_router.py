from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from familytree import app_state

# Assuming your FastAPI app instance is in family_tree_webapp.py
# and app_state is globally accessible from familytree.globals
from familytree.family_tree_webapp import app  # Make sure this path is correct
from familytree.models.base_model import OK_STATUS
from familytree.models.manage_model import LoadFamilyRequest


@pytest.fixture
def client():
    return TestClient(app)


def test_create_new_family_success(client):
    """E2E test for creating a new family tree."""
    response = client.post("/manage/create_family")
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
    response = client.post("/manage/create_family")
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
        filename="test.textpb", content=weasley_family_tree_textproto
    )
    response = client.post("/manage/load_family", json=request_data.model_dump())

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
    request_data = LoadFamilyRequest(content="any_content")
    response = client.post("/manage/load_family", json=request_data.model_dump())
    assert response.status_code == 500
    assert (
        response.json()["detail"]
        == "Unexpected error occured during load family operation."
    )
    mock_logger.exception.assert_called_once()


@pytest.mark.parametrize(
    "endpoint",
    [
        "/manage/add_family_member",
        "/manage/update_family_member",
        "/manage/delete_family_member",
        "/manage/save_family",
        "/manage/export_family_snapshot",
        "/manage/export_interactive_graph",
    ],
)
def test_not_implemented_endpoints(endpoint, client):
    if "save_family" in endpoint or "export" in endpoint:  # GET endpoints
        response = client.get(endpoint)
    else:  # POST endpoints
        response = client.post(endpoint)
    assert response.status_code == 501
    assert f"Endpoint {endpoint} is not yet implemented." in response.json()["detail"]

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from familytree.family_tree_webapp import app


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture
def mock_app_state():
    """Mocks the app_state module."""
    with patch("familytree.routers.graph_router.app_state") as mock_state:
        yield mock_state


@pytest.fixture
def mock_family_tree_handler():
    """Mocks the FamilyTreeHandler instance returned by app_state."""
    mock_handler = MagicMock()
    return mock_handler


def test_get_data_with_poi_not_implemented(client):
    """Tests the /graph/render endpoint with a POI (should return 501)."""
    response = client.get("/api/v1/graph/render?poi=some_id&degree=3")
    assert response.status_code == 501
    assert (
        response.json()["detail"]
        == "Endpoint /graph/render?poi=some_id&degree=3 is not implemented yet."
    )


def test_get_data_without_poi_success(mock_app_state, mock_family_tree_handler, client):
    """Tests the /graph/render endpoint without a POI (success case)."""
    # Configure the mock handler to return some HTML
    mock_app_state.get_current_family_tree_handler.return_value = (
        mock_family_tree_handler
    )
    mock_family_tree_handler.render_family_tree.return_value = (
        "<html><body>Graph HTML</body></html>"
    )

    response = client.get("/api/v1/graph/render")

    assert response.status_code == 200
    assert response.json()["message"] == "Family tree rendered successfully"
    assert response.json()["graph_html"] == "<html><body>Graph HTML</body></html>"

    # Ensure the handler and its render method were called
    mock_app_state.get_current_family_tree_handler.assert_called_once()
    mock_family_tree_handler.render_family_tree.assert_called_once_with()


def test_get_data_without_poi_handler_exception(
    mock_app_state, mock_family_tree_handler, client
):
    """Tests the /graph/render endpoint without a POI when handler raises an exception."""
    mock_app_state.get_current_family_tree_handler.return_value = (
        mock_family_tree_handler
    )
    mock_family_tree_handler.render_family_tree.side_effect = Exception(
        "Simulated handler error"
    )

    response = client.get("/api/v1/graph/render")

    assert response.status_code == 500
    assert response.json() == {
        "detail": "Unexpected error occured while rendering family tree: Simulated handler error"
    }
    mock_app_state.get_current_family_tree_handler.assert_called_once()
    mock_family_tree_handler.render_family_tree.assert_called_once_with()


# Test suite for the unimplemented expansion/collapse endpoints
@pytest.mark.parametrize(
    "endpoint, detail_template",
    [
        (
            "/api/v1/graph/expand_parents/user123",
            "Endpoint /graph/expand_parents/user123 is not implemented yet.",
        ),
        (
            "/api/v1/graph/expand_siblings/user123",
            "Endpoint /graph/expand_siblings/user123 is not implemented yet.",
        ),
        (
            "/api/v1/graph/expand_children/user123",
            "Endpoint /graph/expand_children/user123 is not implemented yet.",
        ),
        (
            "/api/v1/graph/expand_spouse/user123",
            "Endpoint /graph/expand_spouse/user123 is not implemented yet.",
        ),
        (
            "/api/v1/graph/expand_inlaws/user123",
            "Endpoint /graph/expand_inlaws/user123 is not implemented yet.",
        ),
        (
            "/api/v1/graph/collapse_parents/user123",
            "Endpoint /graph/collapse_parents/user123 is not implemented yet.",
        ),
        (
            "/api/v1/graph/collapse_siblings/user123",
            "Endpoint /graph/collapse_siblings/user123 is not implemented yet.",
        ),
        (
            "/api/v1/graph/collapse_children/user123",
            "Endpoint /graph/collapse_children/user123 is not implemented yet.",
        ),
        (
            "/api/v1/graph/collapse_spouse/user123",
            "Endpoint /graph/collapse_spouse/user123 is not implemented yet.",
        ),
        (
            "/api/v1/graph/collapse_inlaws/user123",
            "Endpoint /graph/collapse_inlaws/user123 is not implemented yet.",
        ),
    ],
)
def test_unimplemented_endpoints(endpoint, detail_template, client):
    """Tests that all expand/collapse endpoints return 501 Not Implemented."""
    response = client.get(endpoint)
    assert response.status_code == 501
    assert response.json()["detail"] == detail_template

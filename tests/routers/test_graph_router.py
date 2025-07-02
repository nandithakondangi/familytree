import pytest

from familytree.models.manage_model import LoadFamilyRequest


def test_get_data_with_poi_not_implemented(client):
    """Tests the /graph/render endpoint with a POI (should return 501)."""
    response = client.get("/api/v1/graph/render?theme=light&poi=some_id&degree=3")
    json_response = response.json()
    assert response.status_code == 501
    assert json_response["status"] == "ERROR"
    assert (
        json_response["message"]
        == "Unsupported operation 'render_with_poi'. Feature 'poi=some_id, degree=3' is not implemented."
    )


def test_get_data_without_poi_success(
    client, weasley_family_tree_textproto, reset_app_state_between_tests
):
    """Tests the /graph/render endpoint without a POI (success case)."""
    # Load some data into the family tree first (E2E style)
    load_request = LoadFamilyRequest(
        filename="weasley.txtpb", content=weasley_family_tree_textproto
    )
    load_response = client.post(
        "/api/v1/manage/load_family", json=load_request.model_dump()
    )
    assert load_response.status_code == 200
    assert load_response.json()["status"] == "OK"

    response = client.get("/api/v1/graph/render?theme=dark")

    assert response.status_code == 200
    assert response.json()["message"] == "Family tree rendered successfully"
    graph_html = response.json()["graph_html"]
    assert isinstance(graph_html, str)
    assert len(graph_html) > 0
    # Basic check for HTML structure (e.g., contains <html>, <body>, <canvas>)
    assert "<html>" in graph_html
    assert "<body>" in graph_html
    # Check for some expected content from the Weasley family
    assert "Arthur Weasley" in graph_html
    assert "Molly Weasley" in graph_html
    assert "Ron Weasley" in graph_html


def test_get_data_without_poi_handler_exception(
    client_with_mock_handler, mock_family_tree_handler
):
    """Tests the /graph/render endpoint without a POI when handler raises an exception."""
    # The dependency is now correctly overridden to return the mock handler.
    # We just need to configure the mock's behavior for this test.
    mock_family_tree_handler.render_family_tree.side_effect = Exception(
        "Simulated handler error"
    )

    response = client_with_mock_handler.get("/api/v1/graph/render?theme=light")
    json_response = response.json()
    assert response.status_code == 500
    assert json_response["status"] == "ERROR"
    assert "An unexpected internal server error occurred" in json_response["message"]
    assert "Simulated handler error" in json_response["message"]


def test_get_member_info_success(
    client, weasley_family_tree_textproto, reset_app_state_between_tests
):
    """Tests the /graph/member_info/{user_id} endpoint."""
    load_request = LoadFamilyRequest(
        filename="weasley.txtpb", content=weasley_family_tree_textproto
    )
    load_response = client.post(
        "/api/v1/manage/load_family", json=load_request.model_dump()
    )
    assert load_response.status_code == 200
    assert load_response.json()["status"] == "OK"

    response = client.get("/api/v1/graph/member_info/ARTHW")
    json_response = response.json()
    assert response.status_code == 200
    assert json_response["status"] == "OK"
    assert json_response["message"] == "Member info retrieved successfully."
    assert json_response["member_info"]["id"] == "ARTHW"
    assert json_response["member_info"]["name"] == "Arthur Weasley"
    assert json_response["member_info"]["gender"] == "MALE"
    assert json_response["member_info"]["date_of_birth"]["year"] == 1950
    assert json_response["member_info"]["date_of_birth"]["month"] == 2
    assert json_response["member_info"]["date_of_birth"]["date"] == 6
    assert json_response["member_info"]["alive"] is True


def test_get_member_info_member_not_found(
    client, weasley_family_tree_textproto, reset_app_state_between_tests
):
    """Tests the /graph/member_info/{user_id} endpoint."""
    load_request = LoadFamilyRequest(
        filename="weasley.txtpb", content=weasley_family_tree_textproto
    )
    load_response = client.post(
        "/api/v1/manage/load_family", json=load_request.model_dump()
    )
    assert load_response.status_code == 200
    assert load_response.json()["status"] == "OK"

    response = client.get("/api/v1/graph/member_info/ARTHY")
    json_response = response.json()
    assert response.status_code == 404
    assert json_response["status"] == "ERROR"
    assert (
        json_response["message"]
        == "Member with ID 'ARTHY' not found during operation 'get_member_info'."
    )


# Test suite for the unimplemented expansion/collapse endpoints
@pytest.mark.parametrize(
    "endpoint, operation, user",
    [
        (
            "/api/v1/graph/expand_parents/user123",
            "expand_parents",
            "user123",
        ),
        (
            "/api/v1/graph/expand_siblings/user123",
            "expand_siblings",
            "user123",
        ),
        (
            "/api/v1/graph/expand_children/user123",
            "expand_children",
            "user123",
        ),
        (
            "/api/v1/graph/expand_spouse/user123",
            "expand_spouse",
            "user123",
        ),
        (
            "/api/v1/graph/expand_inlaws/user123",
            "expand_inlaws",
            "user123",
        ),
        (
            "/api/v1/graph/collapse_parents/user123",
            "collapse_parents",
            "user123",
        ),
        (
            "/api/v1/graph/collapse_siblings/user123",
            "collapse_siblings",
            "user123",
        ),
        (
            "/api/v1/graph/collapse_children/user123",
            "collapse_children",
            "user123",
        ),
        (
            "/api/v1/graph/collapse_spouse/user123",
            "collapse_spouse",
            "user123",
        ),
        (
            "/api/v1/graph/collapse_inlaws/user123",
            "collapse_inlaws",
            "user123",
        ),
    ],
)
def test_unimplemented_endpoints(endpoint, operation, user, client):
    """Tests that all expand/collapse endpoints return 501 Not Implemented."""
    response_template = f"Unsupported operation '{operation}'. Feature '{operation} for user {user}' is not implemented."
    response = client.get(endpoint)
    json_response = response.json()
    assert response.status_code == 501
    assert json_response["status"] == "ERROR"
    assert json_response["message"] == response_template

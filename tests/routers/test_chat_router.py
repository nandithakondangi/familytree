import pytest
from fastapi.testclient import TestClient

from familytree.family_tree_webapp import app


@pytest.fixture
def client():
    return TestClient(app)


def test_send_message_not_implemented(client):
    """Tests that the /chat/send_message endpoint returns 501 Not Implemented."""
    response = client.post("/api/v1/chat/send_message")
    json_response = response.json()
    assert response.status_code == 501
    assert json_response["status"] == "ERROR"
    assert (
        json_response["message"]
        == "Unsupported operation 'send_message'. Feature 'chatbot' is not implemented."
    )

from unittest.mock import AsyncMock

from familytree.models.chat_model import ChatRequest


def test_send_message_success(client_with_mock_handler, mock_family_tree_handler):
    """Tests the /chat/ask endpoint for a successful response."""
    # Arrange
    mock_family_tree_handler.ask_about_family = AsyncMock(
        return_value=("conv_123", "This is a test response.")
    )
    request_data = ChatRequest(query="Hello?", conversation_id="conv_123")

    # Act
    response = client_with_mock_handler.post(
        "/api/v1/chat/ask", json=request_data.model_dump()
    )

    # Assert
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == "OK"
    assert json_response["message"] == "Response generated successfully"
    assert json_response["response"] == "This is a test response."
    assert json_response["conversation_id"] == "conv_123"
    mock_family_tree_handler.ask_about_family.assert_awaited_once_with(
        "Hello?", "conv_123"
    )


def test_send_message_empty_query(client_with_mock_handler):
    """Tests that sending an empty query to /chat/ask returns a 400 error."""
    # Arrange
    request_data = ChatRequest(query="", conversation_id="conv_456")

    # Act
    response = client_with_mock_handler.post(
        "/api/v1/chat/ask", json=request_data.model_dump()
    )

    # Assert
    assert response.status_code == 400
    json_response = response.json()
    assert json_response["detail"] == "Query cannot be empty."


def test_send_message_handler_exception(
    client_with_mock_handler, mock_family_tree_handler
):
    """Tests the /chat/ask endpoint when the handler raises an exception."""
    # Arrange
    mock_family_tree_handler.ask_about_family = AsyncMock(
        side_effect=Exception("AI error")
    )
    request_data = ChatRequest(query="What's wrong?", conversation_id="conv_789")

    # Act
    response = client_with_mock_handler.post(
        "/api/v1/chat/ask", json=request_data.model_dump()
    )

    # Assert
    assert response.status_code == 500
    json_response = response.json()
    assert json_response["status"] == "ERROR"
    assert "An unexpected internal server error occurred" in json_response["message"]
    assert "AI error" in json_response["message"]

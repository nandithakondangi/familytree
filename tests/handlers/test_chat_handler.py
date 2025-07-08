from unittest.mock import patch

from google.adk.agents.run_config import RunConfig, StreamingMode

from familytree.ai import family_tree_assistant
from familytree.handlers.chat_handler import ChatHandler


@patch("familytree.handlers.chat_handler.Runner")
@patch("familytree.handlers.chat_handler.InMemorySessionService")
def test_chat_handler_init(mock_session_service, mock_runner):
    """Tests that the ChatHandler initializes correctly."""
    # Arrange
    mock_session_service_instance = mock_session_service.return_value
    mock_runner_instance = mock_runner.return_value

    # Act
    handler = ChatHandler()

    # Assert
    assert handler.app_name == "Family Genie"
    assert handler.user_id == "user"
    assert handler.family_tree_assistant is family_tree_assistant

    # Check that SessionService and Runner were initialized correctly
    mock_session_service.assert_called_once()
    assert handler.session_service is mock_session_service_instance

    mock_runner.assert_called_once_with(
        app_name="Family Genie",
        agent=family_tree_assistant,
        session_service=mock_session_service_instance,
    )
    assert handler.runner is mock_runner_instance

    # Check RunConfig
    assert isinstance(handler.run_config, RunConfig)
    assert handler.run_config.streaming_mode == StreamingMode.SSE
    assert handler.run_config.max_llm_calls == 10

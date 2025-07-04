import logging

from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.sessions.session import Session
from google.genai import types

from familytree.ai import family_tree_assistant
from familytree.exceptions import OperationError
from familytree.utils import id_utils

logger = logging.getLogger(__name__)


class ChatHandler:
    """
    Handler class for GenAI model and the chatbot.
    """

    def __init__(self):
        """
        Initializes the ChatHandler.
        """
        self.app_name = "Family Genie"
        self.user_id = "user"
        self.family_tree_assistant = family_tree_assistant
        self.session_service = InMemorySessionService()
        self.runner = Runner(
            app_name=self.app_name,
            agent=self.family_tree_assistant,
            session_service=self.session_service,
        )
        self.run_config = RunConfig(streaming_mode=StreamingMode.SSE, max_llm_calls=10)

    def _get_or_create_session(
        self, conversation_id: str | None
    ) -> tuple[str, Session]:
        """
        Gets or creates a session.

        Args:
            conversation_id (str, optional): The conversation ID.

        Returns:
            str: The session ID.
        """
        if conversation_id is None:
            conversation_id = id_utils.generate_family_conversation_id()
            session = await self.session_service.create_session(
                app_name=self.app_name, session_id=conversation_id, user_id=self.user_id
            )
        else:
            try:
                session = await self.session_service.get_session(
                    app_name=self.app_name,
                    session_id=conversation_id,
                    user_id=self.user_id,
                )
                assert session
            except AssertionError:
                logger.error("ADK Session not found")
                raise OperationError(
                    operation="Fetch ADK session", reason="ADK Session not found."
                )
        return conversation_id, session

    async def call_agent_aync(
        self, query: str, conversation_id: str | None
    ) -> tuple[str, str]:
        """
        Sends a query to the agent team and returns the final response.

        Args:
            query (str): The query to be sent to the agent team.
            conversation_id (str, optional): The conversation ID. Defaults to None.

        Returns:
            str: The final response from the agent team.
        """
        conversation_id, session = self._get_or_create_session(conversation_id)

        content = types.Content(
            role="user",  # pyrefly: ignore
            parts=[types.Part(text=query)],
        )
        final_response_text = "Genie was unable to generate a response"

        async for event in self.runner.run_async(
            user_id=self.user_id,
            session_id=conversation_id,
            new_message=content,
            run_config=self.run_config,
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    # Assuming text response in the first part
                    try:
                        final_response_text = event.content.parts[0].text
                        assert final_response_text
                    except AssertionError:
                        logger.error("Final response not found")
                        raise OperationError(
                            operation="Agent response",
                            reason="Final response not found.",
                        )
                elif event.actions and event.actions.escalate:
                    final_response_text += (
                        f": {event.error_message or 'No specific message.'}"
                    )
                break

        return conversation_id, final_response_text

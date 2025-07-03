import logging

from familytree.ai import create_agent_team
from familytree.utils import id_utils

logger = logging.getLogger(__name__)


class ChatHandler:
    """
    Handler class for GenAI model and the chatbot.
    """

    def __init__(self):
        """
        Initializes the ChatHandler.

        Attributes:
            system_prompt_path (str): Path to the system prompt file.
            api_key (str): API key for the Gemini service.
        """
        self.system_prompt_path = ""
        self.api_key = ""
        self.agent_team = create_agent_team()
        self.session_store: dict[str, list[str]] = {}

    def send_query_to_agent_team(
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
        conversation_id, history = self._retrieve_history(conversation_id)
        final_output = await self.agent_team.run({"query": query, "history": history})
        response_text = final_output.get(
            "final_response", "Sorry, I could not generate a response."
        )
        self._update_history(conversation_id, query, response_text)
        return conversation_id, response_text

    def _retrieve_history(self, conversation_id: str | None) -> tuple[str, list[str]]:
        """
        Retrieves the conversation history for a given conversation ID.

        If no conversation ID is provided or it's not found in the session store,
        a new conversation ID is generated and an empty history is initialized.

        Args:
            conversation_id: The ID of the conversation to retrieve.

        Returns:
            A tuple containing the conversation ID and its history (list of strings).
        """

        if conversation_id and conversation_id in self.session_store:
            # Existing conversation
            history = self.session_store[conversation_id]
        else:
            # New conversation
            conversation_id = id_utils.generate_family_conversation_id()
            history: list[str] = []
            self.session_store[conversation_id] = history
        return conversation_id, history

    def _update_history(self, conversation_id: str, query: str, response: str) -> None:
        """
        Updates the conversation history for a given conversation ID.

        Appends the user's query and the agent's response to the history.

        Args:
            conversation_id: The ID of the conversation to update.
            query: The user's query.
            response: The agent's response.
        """

        _, history = self._retrieve_history(conversation_id)
        history.append(f"User: {query}")
        history.append(f"Family Genie: {response}")
        self.session_store[conversation_id] = history

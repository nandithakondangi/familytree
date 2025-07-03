import logging

from familytree.ai import create_agent_team

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

    def send_query_to_agent_team(self, query: str) -> str:
        final_output = await self.agent_team.run({"query": query})
        return final_output.get(
            "final_response", "Sorry, I could not generate a response."
        )

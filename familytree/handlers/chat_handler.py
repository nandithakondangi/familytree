import logging

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

    def initialize_gemini_2_5_flash(self):
        """
        Initializes the Gemini 2.5 Flash model.

        Note: This method is not yet implemented.
        """
        pass

    def get_gemini_response(self, message: str):
        """
        Gets a response from the Gemini model for a given message.

        Args:
            message (str): The user's message to send to the model.

        Note: This method is not yet implemented.
        """
        pass

    def _load_system_prompt(self):
        """
        Loads the system prompt from the specified file path.

        Note: This method is not yet implemented.
        """
        pass

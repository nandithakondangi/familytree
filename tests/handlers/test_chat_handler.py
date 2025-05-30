from familytree.handlers.chat_handler import ChatHandler


class TestChatHandler:
    def test_init(self):
        """
        Tests that the ChatHandler initializes with default empty attributes.
        """
        handler = ChatHandler()
        assert handler.system_prompt_path == "", "system_prompt_path should be empty"
        assert handler.api_key == "", "api_key should be empty"

    # Methods initialize_gemini_2_5_flash, get_gemini_response,
    # and _load_system_prompt are not implemented (pass), so no tests for them.

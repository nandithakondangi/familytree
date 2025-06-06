import html
import logging
import os

from google import genai
from google.genai import types
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from utils_legacy import ResourceUtility

# Get a logger instance for this module
logger = logging.getLogger(__name__)


class ChatbotLogic:
    def __init__(self, family_tree_handler):
        self.family_tree_handler = family_tree_handler
        self.client = None

    def get_api_key(self) -> str | None:
        """Retrieves the Google API key from environment variables."""
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            QMessageBox.warning(
                self,  # Parent is now ChatbotBox (a QWidget)
                "API Key Missing",
                "The GOOGLE_API_KEY environment variable is not set.\n"
                "Please set it to your Google AI Studio API key to use the chatbot.",
            )
            return None
        return api_key

    def _get_prompt(self, user_query: str) -> str:
        graph_context = self.family_tree_handler.get_context_about_this_family()
        system_prompt_file = ResourceUtility.get_resource("system_prompt.txt")
        system_prompt = ""
        with open(system_prompt_file, "r") as f:
            system_prompt = f.read()

        full_prompt = (
            f"{system_prompt}\n\n{graph_context}\n\nUser question: {user_query}"
        )
        logger.debug(full_prompt)
        return full_prompt

    def get_response_chunks(self, prompt: str, gemini_api_key: str):
        self.client = genai.Client(api_key=gemini_api_key)

        # model = "gemma-3-1b-it"
        model = "gemini-2.0-flash"
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=self._get_prompt(prompt)),
                ],
            )
        ]
        generate_content_config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(
                thinking_budget=0,
            ),
            safety_settings=[
                types.SafetySetting(
                    category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    threshold="BLOCK_LOW_AND_ABOVE",  # Block most
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_DANGEROUS_CONTENT",
                    threshold="BLOCK_ONLY_HIGH",  # Block few
                ),
            ],
            response_mime_type="text/plain",
        )
        return self.client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        )


class ChatbotBox(QWidget):
    def __init__(self, family_tree_handler, parent=None):
        super().__init__(parent)
        self.chatbot_logic = ChatbotLogic(family_tree_handler)
        # UI Elements (will be created in init_ui)
        self.chat_history = None
        self.chat_input = None
        self.send_button = None

        self.init_ui()

    def init_ui(self):
        """Sets up the UI elements within the ChatbotBox widget."""
        chatbot_layout = QVBoxLayout(self)  # Set layout directly on self
        chatbot_layout.setContentsMargins(5, 5, 5, 5)

        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setStyleSheet(
            "background-color: #282c34; color: #abb2bf;"
        )  # Darker theme
        chatbot_layout.addWidget(self.chat_history)

        input_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Ask about the family tree...")
        self.chat_input.returnPressed.connect(self._on_send_button_clicked)
        input_layout.addWidget(self.chat_input)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self._on_send_button_clicked)
        input_layout.addWidget(self.send_button)

        chatbot_layout.addLayout(input_layout)

    # --- Methods moved from FamilyTreeGUI ---

    def _add_message_to_chat(self, sender: str, message: str):
        """Appends a formatted message to the chat history."""
        # Basic HTML for formatting
        formatted_message = f"<p><b>{sender}:</b> {message.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')}</p>"
        self.chat_history.append(formatted_message)
        # Scroll to the bottom
        self.chat_history.verticalScrollBar().setValue(
            self.chat_history.verticalScrollBar().maximum()
        )

    def _on_send_button_clicked(self):
        """Handles sending the user's query to the chatbot."""
        user_query = self.chat_input.text().strip()
        if not user_query:
            return

        self._add_message_to_chat("You", user_query)
        self.chat_input.clear()
        self.send_button.setEnabled(False)
        self.chat_input.setEnabled(False)
        self._start_bot_message()

        self.generate(user_query)

    def _start_bot_message(self):
        """Appends the initial 'Bot: ' HTML structure, ready for streaming."""
        # Append the starting HTML, including a space after the colon.
        # IMPORTANT: Do NOT add the closing </p> tag here.
        self.chat_history.append("<p><b>Bot:</b> ")
        # Ensure the view scrolls down to show the start of the bot's turn
        self.chat_history.ensureCursorVisible()

    def _handle_no_api_key(self):
        # If API key is missing, we still need to close the paragraph started and re-enable controls.
        try:
            cursor = self.chat_history.textCursor()
            cursor.movePosition(QTextCursor.End)
            cursor.insertHtml(
                "API Key not configured.</p>"
            )  # Add message and close tag
        except Exception as e_cursor:
            logger.error(f"Error finalizing message after API key check: {e_cursor}")
        finally:
            self.send_button.setEnabled(True)
            self.chat_input.setEnabled(True)
        return

    def generate(self, prompt: str) -> str:
        gemini_api_key = self.chatbot_logic.get_api_key()
        if gemini_api_key is None:
            self._handle_no_api_key()
            return
        self.stream_content_in_chatbox(prompt, gemini_api_key)

    def stream_content_in_chatbox(self, prompt: str, gemini_api_key: str):
        try:
            # Stream the content
            for chunk in self.chatbot_logic.get_response_chunks(prompt, gemini_api_key):
                stream_successful = True  # Mark that we received at least one chunk
                print(chunk.text, end="")  # Keep console log

                # --- Prepare chunk text for HTML insertion ---
                html_chunk = html.escape(chunk.text)
                # --- Use QTextCursor to append ---
                cursor = self.chat_history.textCursor()
                cursor.movePosition(QTextCursor.End)  # Go to the end of the document
                cursor.insertHtml(html_chunk)  # Insert the prepared HTML chunk
                self.chat_history.ensureCursorVisible()  # Keep scrolled to bottom
                # --- End Use QTextCursor ---
        except Exception as e:
            # Handle potential API errors
            logger.exception("Error during Gemini API call:")
            # Append error message within the current bot paragraph if possible
            try:
                cursor = self.chat_history.textCursor()
                cursor.movePosition(QTextCursor.End)
                error_html = f"<br><i>Error: {str(e).replace('<', '&lt;').replace('>', '&gt;')}</i>"
                cursor.insertHtml(error_html)
                self.chat_history.ensureCursorVisible()
            except Exception as e_cursor:
                logger.error(f"Error inserting error message into chat: {e_cursor}")
        finally:
            # --- Ensure the Bot's paragraph is closed ---
            try:
                cursor = self.chat_history.textCursor()
                cursor.movePosition(QTextCursor.End)
                # Add closing tag only if we actually started streaming or if an error occurred mid-stream
                # If the API call failed before any chunk, the initial "<p><b>Bot:</b> " is still open.
                cursor.insertHtml("</p>")
            except Exception as e_cursor:
                logger.error(f"Error adding closing paragraph tag: {e_cursor}")
            # --- Re-enable controls ---
            self.send_button.setEnabled(True)
            self.chat_input.setEnabled(True)
            # --- End Re-enable controls ---

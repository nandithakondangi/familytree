import logging
import os

from add_person import AddPersonDialog
from chatbot import ChatbotBox
from export import ExportWidget
from family_tree_handler import FamilyTreeHandler
from import_from_file import ImportFromFileForm  # noqa F401
from PySide6.QtCore import QObject, Qt, QTimer, QUrl, Signal, Slot  # Added QTimer
from PySide6.QtGui import QAction, QCursor  # Added QAction, QCursor
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QLabel,
    QMainWindow,
    QMenu,  # Added QMenu
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QStatusBar,  # Added QStatusBar
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from utils import ResourceUtility

# Get a logger instance for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# --- Add JavaScript Interface Class ---
class JavaScriptInterface(QObject):
    """Object exposed to JavaScript for communication."""

    # Signal to request editing a node, carrying the node ID (member_id)
    edit_node_requested = Signal(str)
    node_right_clicked = Signal(str, int, int)  # New signal for right-click

    def __init__(self, parent=None):
        super().__init__(parent)

    @Slot(str)  # Decorator exposes this method to JavaScript via QWebChannel
    def handleNodeDoubleClick(self, node_id):
        """Receives the node ID from JavaScript when a node is double-clicked."""
        # Ensure node_id is treated as a string, especially if it could be numeric
        s_node_id = str(node_id) if node_id is not None else None
        logger.debug(
            f"Received nodeDoubleClick signal from JS for node: {s_node_id} (original: {node_id})"
        )
        if s_node_id is not None:
            self.edit_node_requested.emit(s_node_id)  # Emit signal for GUI to handle

    @Slot(str, int, int)  # New slot for right-click
    def handleNodeRightClick(self, node_id, x, y):
        """Receives node ID and click coordinates from JS on right-click."""
        # Ensure node_id is treated as a string
        s_node_id = str(node_id) if node_id is not None else None
        logger.debug(
            f"Received nodeRightClick signal from JS for node: {s_node_id} (original: {node_id}) at ({x},{y})"
        )
        if s_node_id is not None:
            self.node_right_clicked.emit(s_node_id, x, y)


class FamilyTreeGUI(QMainWindow):
    # Accept temp_dir_path in constructor
    def __init__(self, temp_dir_path):
        super().__init__()
        self.temp_dir_path = temp_dir_path
        self.setWindowTitle("Family Tree Viewer")
        self.setGeometry(100, 100, 1200, 800)

        self.family_tree_handler = FamilyTreeHandler(temp_dir_path=self.temp_dir_path)
        self.is_indian_culture = True  # Default to Indian culture enabled

        # --- WebChannel Setup ---
        self.js_interface = JavaScriptInterface(self)  # Create the interface object
        self.channel = QWebChannel(self)  # Create the channel
        # Register the Python object with the name expected by JavaScript ("pythonInterface")
        self.channel.registerObject("pythonInterface", self.js_interface)
        # Connect the signal from the interface to the GUI's handler method
        self.js_interface.edit_node_requested.connect(self.open_edit_person_dialog)
        self.js_interface.node_right_clicked.connect(
            self.show_node_context_menu
        )  # Connect new signal
        # --- End WebChannel Setup ---

        # UI Elements (Specific to main GUI)
        self.pyvis_view = None
        self.chatbot_box = None
        self.culture_checkbox = None
        self.import_from_file_form = None
        self.add_person_button = None
        self.export_widget = None
        self.status_label = None  # For custom status messages

        self.init_ui()

    def init_ui(self):
        # Main Splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)  # Use Orientation enum
        main_splitter.setChildrenCollapsible(False)
        self.setCentralWidget(main_splitter)

        # Sidebar (Left)
        sidebar = self.create_sidebar()
        main_splitter.addWidget(sidebar)

        # Main Content Area (Right)
        content_area = self.create_content_area()  # This now sets up the web channel
        main_splitter.addWidget(content_area)

        # Set initial splitter sizes (adjust as needed)
        main_splitter.setSizes([350, 850])  # Adjusted sizes slightly

        # Add a status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        # Add a permanent label "Status: "
        status_prefix_label = QLabel("Status: ")
        self.status_bar.addWidget(status_prefix_label)
        # Create and add a QLabel for rich text status messages
        self.status_label = QLabel()
        # self.status_label.setTextFormat(Qt.RichText) # QLabel often infers for simple HTML
        self.status_bar.addWidget(
            self.status_label, 1
        )  # Stretch factor 1 to take available space

        self.show_status_message("Ready.", 5000)  # Initial message
        self.update_add_person_button_state()  # Initial check for button state

    def create_sidebar(self):
        sidebar_wrapper = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_wrapper)
        sidebar_layout.setContentsMargins(5, 5, 5, 5)  # Add some margins
        sidebar_wrapper.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding
        )  # Adjust policy

        sidebar = QTabWidget()
        sidebar.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        # Manage Tree Tab
        manage_tree_tab = QWidget()
        manage_tree_layout = QVBoxLayout(manage_tree_tab)
        manage_tree_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )  # Align widgets to top

        # --- Culture Checkbox ---
        self.culture_checkbox = QCheckBox("Culture: Indian")
        self.culture_checkbox.setChecked(self.is_indian_culture)
        self.culture_checkbox.setToolTip(
            "Enable to show fields for traditional Indian dates (Tamil Month/Star/Paksham/Thithi)."
        )
        self.culture_checkbox.stateChanged.connect(self.update_culture_setting)
        manage_tree_layout.addWidget(self.culture_checkbox)
        # --- End Culture Checkbox ---

        # Import from file Form
        self.import_from_file_form = ImportFromFileForm(self.family_tree_handler, self)
        manage_tree_layout.addWidget(self.import_from_file_form)

        # Add Person Button
        self.add_person_button = QPushButton("➕ Add New Person")  # Added icon
        self.add_person_button.clicked.connect(self.open_add_person_dialog)
        manage_tree_layout.addWidget(self.add_person_button)

        # Edit instructions
        edit_instructions_label = QLabel(
            "✏️ <b>Edit Person:</b>\nDouble-click a node\nin the graph."
        )
        # Or AlignCenter
        edit_instructions_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        edit_instructions_label.setWordWrap(True)  # Ensure text wraps if needed
        # Optional styling to make it look less prominent than buttons
        edit_instructions_label.setStyleSheet(
            "margin-top: 10px; margin-bottom: 5px;"
            # "color: #ccc;"
        )
        manage_tree_layout.addWidget(edit_instructions_label)

        # Export Widget
        self.export_widget = ExportWidget(self.family_tree_handler, self)
        manage_tree_layout.addWidget(self.export_widget)

        # Re-render Button
        re_render_button = QPushButton("🔄 Re-render Graph")  # Added icon
        re_render_button.clicked.connect(self.re_render_tree)
        manage_tree_layout.addWidget(re_render_button)

        manage_tree_layout.addStretch()  # Add stretch to push widgets up

        sidebar.addTab(manage_tree_tab, "🌳 Manage Tree")  # Added icon

        # About Tab
        about_tab = QWidget()
        sidebar.addTab(about_tab, "ℹ️ About")  # Added icon
        self.publish_content_to_about_tab(about_tab)

        sidebar_layout.addWidget(sidebar)
        return sidebar_wrapper

    def update_culture_setting(self, state):
        """Updates the culture flag based on the checkbox state."""
        self.is_indian_culture = state == Qt.CheckState.Checked.value
        logger.info(f"Indian culture setting updated: {self.is_indian_culture}")
        # Future: Could potentially trigger updates elsewhere if needed

    def open_add_person_dialog(self):
        # Pass the handler, self (GUI), and the current culture setting to the dialog, and indicate it's for ADDING (member_id=None)
        dialog = AddPersonDialog(self.family_tree_handler, self, self.is_indian_culture)
        dialog = AddPersonDialog(
            family_tree_handler=self.family_tree_handler,
            family_tree_gui=self,
            is_indian_culture=self.is_indian_culture,
            member_id_to_edit=None,  # Explicitly None for adding
        )
        # exec() is blocking, use open() for non-blocking if needed later
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:  # Check if dialog was accepted
            logger.info("Add Person dialog accepted. Re-rendering tree.")
            self.re_render_tree()  # Re-render to show the new person
        else:
            logger.info("Add Person dialog cancelled.")

    def open_edit_person_dialog(self, member_id):
        """Opens the dialog in edit mode for the given member ID."""
        logger.debug(f"Opening edit dialog for member ID: {member_id}")

        # Pass handler, self, culture setting, and the member_id to edit
        dialog = AddPersonDialog(
            family_tree_handler=self.family_tree_handler,
            family_tree_gui=self,
            is_indian_culture=self.is_indian_culture,
            member_id_to_edit=member_id,  # Pass the ID for editing
        )
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            logger.info(
                f"Edit Person dialog accepted for {member_id}. Re-rendering tree."
            )
            self.re_render_tree()  # Re-render to show updated details
        else:
            logger.info(f"Edit Person dialog cancelled for {member_id}.")

    @Slot(str, int, int)
    def show_node_context_menu(self, node_id: str, x: int, y: int):
        """Displays a context menu for the given node ID at the cursor's position."""
        logger.debug(f"Showing context menu for node: {node_id}")
        context_menu = QMenu(self)

        add_spouse_action = QAction("Add Spouse", self)
        # Use lambda to pass additional arguments (node_id, relationship_type)
        add_spouse_action.triggered.connect(
            lambda: self.handle_add_relationship_via_dialog(node_id, "spouse")
        )
        context_menu.addAction(add_spouse_action)

        add_child_action = QAction("Add Child", self)
        add_child_action.triggered.connect(
            lambda: self.handle_add_relationship_via_dialog(node_id, "child")
        )
        context_menu.addAction(add_child_action)

        add_parent_action = QAction("Add Parent", self)
        add_parent_action.triggered.connect(
            lambda: self.handle_add_relationship_via_dialog(node_id, "parent")
        )
        context_menu.addAction(add_parent_action)

        context_menu.addSeparator()

        delete_member_action = QAction("🗑️ Delete Member", self)  # Added icon
        delete_member_action.triggered.connect(
            lambda: self.handle_delete_member(node_id)
        )
        context_menu.addAction(delete_member_action)

        # Show the menu at the current global cursor position
        context_menu.popup(QCursor.pos())

    def handle_delete_member(self, member_id_to_delete: str):
        """Handles the deletion of a member after confirmation."""
        member_name = self.family_tree_handler.get_member_name_by_id(
            member_id_to_delete
        )
        if not member_name:
            QMessageBox.critical(
                self,
                "Error",
                f"Could not find member with ID: {member_id_to_delete} to delete.",
            )
            return

        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete '{member_name}' (ID: {member_id_to_delete}) and all their relationships?\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            logger.info(
                f"Attempting to delete member: {member_name} ({member_id_to_delete})"
            )
            success, message = self.family_tree_handler.delete_member(
                member_id_to_delete
            )
            self.show_status_message(message, 7000)
            if success:
                logger.info(message)
                self.re_render_tree()  # Re-render the graph to reflect the deletion
            else:
                logger.error(message)
                QMessageBox.warning(
                    self, "Deletion Failed", message
                )  # Show a more prominent warning for deletion failure

    def handle_add_relationship_via_dialog(
        self, origin_node_id: str, relationship_type: str
    ):
        """Opens AddPersonDialog to create a new person, then establishes a relationship."""
        logger.info(f"Attempting to add {relationship_type} for node {origin_node_id}")

        dialog = AddPersonDialog(
            family_tree_handler=self.family_tree_handler,
            family_tree_gui=self,
            is_indian_culture=self.is_indian_culture,
            member_id_to_edit=None,  # Always for a new person
        )
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            new_member_id = str(getattr(dialog, "newly_created_member_id", None))
            if new_member_id:
                logger.info(
                    f"New person created (ID: {new_member_id}). Establishing {relationship_type} with {origin_node_id}."
                )
                try:
                    print(f"origin_node_id: {origin_node_id}")
                    print(f"new_member_id: {new_member_id}")
                    print(f"relationship_type: {relationship_type}")
                    success, message = self.family_tree_handler.add_relations(
                        origin_node_id, new_member_id, relationship_type
                    )
                    if success:
                        status_msg = f"Relationship established: {message}"
                        logger.info(status_msg)
                        self.show_status_message(status_msg, 7000)
                    else:
                        status_msg = f"Failed to add relationship: {message}"
                        logger.warning(status_msg)
                        # This might still be a good candidate for a QMessageBox if it's a significant failure
                        self.show_status_message(status_msg, 7000)
                        # QMessageBox.warning(self, "Error", status_msg) # Kept for consideration
                except Exception as e:
                    logger.exception(f"Error establishing relationship: {e}")
                    QMessageBox.critical(
                        self, "Error", f"Failed to add relationship: {str(e)}"
                    )
                self.re_render_tree()  # Re-render even on error to show current state
            else:
                logger.warning("AddPersonDialog accepted, but new_member_id not found.")
                self.show_status_message(
                    "New person created, but ID not retrieved for relationship.", 7000
                )

        else:
            logger.info("AddPersonDialog cancelled. No relationship added.")

    def publish_content_to_about_tab(self, about_tab):
        about_layout = QVBoxLayout(about_tab)
        # Using QTextEdit for better rendering and potential scrollbars
        about_text_edit = QTextEdit()
        about_text_edit.setReadOnly(True)

        try:
            content = ResourceUtility.get_info_about_this_software(
                temp_dir_path=self.temp_dir_path
            )

        except Exception as e:
            logger.exception(f"Error loading about tab content: {e}")
            content = ""

        # Use setHtml for rich text
        about_text_edit.setHtml(content)
        about_layout.addWidget(about_text_edit)

    def create_content_area(self):
        content_area = QSplitter(Qt.Orientation.Vertical)
        content_area.setChildrenCollapsible(False)

        # Pyvis Output (Top)
        self.pyvis_view = QWebEngineView()
        # --- Set the WebChannel on the page ---
        self.pyvis_view.page().setWebChannel(self.channel)
        # Optional: Configure settings if needed (e.g., for local file access, JS)
        # settings = self.pyvis_view.settings()
        # settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        # settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        # settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        content_area.addWidget(self.pyvis_view)

        # --- Chatbot (Bottom) - Instantiate ChatbotBox ---
        # Pass the handler instance to the ChatbotBox
        self.chatbot_box = ChatbotBox(self.family_tree_handler)
        content_area.addWidget(self.chatbot_box)
        # --- End Chatbot ---

        # Set initial splitter sizes
        content_area.setSizes([650, 150])

        return content_area

    def re_render_tree(self):
        """Re-generates the pyvis graph and reloads it in the view."""
        logger.debug("Re-rendering tree...")
        try:
            # Ensure the handler has data before trying to display
            if not self.family_tree_handler.get_member_ids():
                logger.info("No data loaded, clearing view.")
                self.clear_pyvis_view()
                # Optionally show a message in the view
                self.pyvis_view.setHtml(
                    "<p style='color: white; text-align: center; margin-top: 50px;'>Load data or add a person to see the tree.</p>"
                )
                return
            self.family_tree_handler.display_tree()
            if self.load_pyvis_html():  # load_pyvis_html will now return bool
                logger.debug("Tree re-rendered successfully.")
                self.show_status_message("Graph re-rendered.", 3000)
            self.update_add_person_button_state()  # Update button state after render
        except Exception as e:
            error_msg = f"Failed to re-render the tree: {e}"
            logger.error(f"Error during re-rendering: {error_msg}")
            QMessageBox.critical(
                self, "Render Error", error_msg
            )  # Keep critical for major render failures
            self.update_add_person_button_state()  # Also update on error

    def load_pyvis_html(self):
        """Loads the generated HTML file into the QWebEngineView."""
        output_html_file = self.family_tree_handler.get_output_html_file
        if os.path.exists(output_html_file):
            try:
                # Using file:/// prefix is important for local files
                local_url = QUrl.fromLocalFile(os.path.abspath(output_html_file))
                logger.debug(f"local_url: {local_url}")
                logger.debug(f"Loading HTML from: {local_url.toString()}")
                self.pyvis_view.setUrl(local_url)
                return True
            except Exception as e:
                error_msg = f"Could not load the HTML file: {e}"
                logger.error(f"Error loading HTML into QWebEngineView: {error_msg}")
                self.show_status_message(f"Error loading graph: {error_msg}", 7000)
                self.clear_pyvis_view()
                return False
        else:
            logger.info(f"Output file not found: {output_html_file}")
            self.clear_pyvis_view()
            self.pyvis_view.setHtml(
                "<p style='color: white; text-align: center; margin-top: 50px;'>HTML file not generated yet.</p>"
            )
            return False

    def clear_pyvis_view(self):
        """Clears the content of the Pyvis view."""
        logger.info("Clearing Pyvis view.")
        self.pyvis_view.setUrl(QUrl("about:blank"))  # Load a blank page

    def load_from_protobuf(self):
        """Loads data using the handler and triggers a re-render."""
        try:
            # Clear existing graph data in handler before loading new file
            self.family_tree_handler.clear()
            self.family_tree_handler.load_from_text_file()
            # Re-render the tree after successful load
            self.re_render_tree()
            self.show_status_message("Data loaded successfully!", 5000)
        except FileNotFoundError:  # This is a critical error for loading
            QMessageBox.critical(
                self,
                "Error",
                f"File not found:\n{self.family_tree_handler.get_input_text_file}",
            )
            self.clear_pyvis_view()  # Clear view on error
        except Exception as e:
            logger.error(f"Failed to load data: {e}")  # Log detailed error
            QMessageBox.critical(
                self,
                "Load Error",
                f"Failed to load data from file:\n{e}",  # Keep critical
            )
            self.clear_pyvis_view()  # Clear view on error

    def show_status_message(self, message: str, timeout: int = 5000):
        """Displays a message in the status bar for a specified duration."""
        if self.status_label:
            self.status_label.setText(f"<b>{message}</b>")
            if timeout > 0:
                QTimer.singleShot(timeout, self.clear_status_message)
        logger.debug(f"Status: {message}")

    def clear_status_message(self):
        """Clears the text of the status label."""
        if self.status_label:
            self.status_label.clear()

    def update_add_person_button_state(self):
        """Enables or disables the 'Add New Person' button based on tree content."""
        if self.add_person_button:  # Ensure button exists
            if self.family_tree_handler and self.family_tree_handler.get_member_ids():
                self.add_person_button.setEnabled(False)
                self.add_person_button.setToolTip(
                    "Add members via right-click on existing nodes once the tree has people."
                )
            else:
                self.add_person_button.setEnabled(True)
                self.add_person_button.setToolTip(
                    "Add the first person to the family tree."
                )

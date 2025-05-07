import logging
import os

from add_person import AddPersonDialog
from chatbot import ChatbotBox
from export import ExportWidget
from family_tree_handler import FamilyTreeHandler
from import_from_file import ImportFromFileForm
from PySide6.QtCore import QObject, Qt, QUrl, Signal, Slot
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSplitter,
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

    def __init__(self, parent=None):
        super().__init__(parent)

    @Slot(str)  # Decorator exposes this method to JavaScript via QWebChannel
    def handleNodeDoubleClick(self, node_id):
        """Receives the node ID from JavaScript when a node is double-clicked."""
        logger.info(f"Received nodeDoubleClick signal from JS for node: {node_id}")
        if node_id:
            self.edit_node_requested.emit(node_id)  # Emit signal for GUI to handle


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
        # --- End WebChannel Setup ---

        # UI Elements (Specific to main GUI)
        self.pyvis_view = None
        self.chatbot_box = None
        self.culture_checkbox = None
        self.import_from_file_form = None
        self.add_person_button = None
        self.export_widget = None

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
            "color: #ccc; margin-top: 10px; margin-bottom: 5px;"
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

        if result == QDialog.DialogCode.Accepted:
            logger.info("Add/Edit Person dialog accepted.")
            # Re-rendering is handled within the dialog's save method
        else:
            logger.info("Add/Edit Person dialog cancelled.")

    def open_edit_person_dialog(self, member_id):
        """Opens the dialog in edit mode for the given member ID."""
        logger.info(f"Opening edit dialog for member ID: {member_id}")

        # Pass handler, self, culture setting, and the member_id to edit
        dialog = AddPersonDialog(
            family_tree_handler=self.family_tree_handler,
            family_tree_gui=self,
            is_indian_culture=self.is_indian_culture,
            member_id_to_edit=member_id,  # Pass the ID for editing
        )
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            logger.info(f"Edit Person dialog accepted for {member_id}.")
            # Re-rendering is handled within the dialog's save method
        else:
            logger.info(f"Edit Person dialog cancelled for {member_id}.")

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
        logger.info("Re-rendering tree...")
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
            self.load_pyvis_html()
            logger.info("Tree re-rendered successfully.")
        except Exception as e:
            logger.error(f"Error during re-rendering: {e}")
            QMessageBox.critical(
                self, "Render Error", f"Failed to re-render the tree:\n{e}"
            )

    def load_pyvis_html(self):
        """Loads the generated HTML file into the QWebEngineView."""
        output_html_file = self.family_tree_handler.get_output_html_file
        if os.path.exists(output_html_file):
            try:
                # Using file:/// prefix is important for local files
                local_url = QUrl.fromLocalFile(os.path.abspath(output_html_file))
                logger.info(f"local_url: {local_url}")
                logger.info(f"Loading HTML from: {local_url.toString()}")
                self.pyvis_view.setUrl(local_url)
                # self.pyvis_view.reload() # Force reload if needed
            except Exception as e:
                logger.error(f"Error loading HTML into QWebEngineView: {e}")
                QMessageBox.critical(
                    self, "Load Error", f"Could not load the HTML file:\n{e}"
                )
                self.clear_pyvis_view()
        else:
            logger.info(f"Output file not found: {output_html_file}")
            self.clear_pyvis_view()
            self.pyvis_view.setHtml(
                "<p style='color: white; text-align: center; margin-top: 50px;'>HTML file not generated yet.</p>"
            )

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
            # FIXME: (Bug) This message comes in even if there was an error in the previous step
            # When OS module was not included in graph_handler.py, this success message was still displayed
            QMessageBox.information(self, "Success", "Data loaded successfully!")
        except FileNotFoundError:
            QMessageBox.critical(
                self,
                "Error",
                f"File not found:\n{self.family_tree_handler.get_input_text_file}",
            )
            self.clear_pyvis_view()  # Clear view on error
        except Exception as e:
            logger.error(f"Failed to load data: {e}")  # Log detailed error
            QMessageBox.critical(
                self, "Load Error", f"Failed to load data from file:\n{e}"
            )
            self.clear_pyvis_view()  # Clear view on error

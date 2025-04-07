import os
from PySide6.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QSplitter,
    QWidget,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QFileDialog,
    QMessageBox,
    QSizePolicy,
    QDialog,
    QHBoxLayout,
    QSpinBox,
    QDateEdit,
)
from PySide6.QtCore import Qt, QDate
from family_tree_handler import FamilyTreeHandler
from family_tree_pb2 import FamilyMember
from utils_pb2 import Gender
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import Qt, QUrl
from family_tree_handler import FamilyTreeHandler

from PySide6.QtWebEngineCore import QWebEngineSettings
import markdown


class FamilyTreeGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Family Tree Viewer")
        self.setGeometry(100, 100, 1200, 800)

        self.family_tree_handler = FamilyTreeHandler()

        self.init_ui()

    def init_ui(self):
        # Main Splitter
        main_splitter = QSplitter(Qt.Horizontal)
        # Set the splitter to be movable
        main_splitter.setChildrenCollapsible(False)
        self.setCentralWidget(main_splitter)

        # Sidebar (Left)
        sidebar = self.create_sidebar()
        main_splitter.addWidget(sidebar)

        # Main Content Area (Right)
        content_area = self.create_content_area()
        main_splitter.addWidget(content_area)

        # Set initial splitter sizes (adjust as needed)
        main_splitter.setSizes([300, 900])

    def create_sidebar(self):
        # Create a wrapper widget
        sidebar_wrapper = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_wrapper)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        # Set size policy for the wrapper
        sidebar_wrapper.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        sidebar = QTabWidget()
        # Set size policy for the QTabWidget
        sidebar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Manage Tree Tab
        manage_tree_tab = QWidget()
        manage_tree_layout = QVBoxLayout(manage_tree_tab)

        # Import from file Form
        self.import_from_file_form = ImportFromFileForm(self.family_tree_handler, self)
        manage_tree_layout.addWidget(self.import_from_file_form)

        # Add Person Form
        self.add_person_button = QPushButton("Add Person")
        self.add_person_button.clicked.connect(self.open_add_person_dialog)
        manage_tree_layout.addWidget(self.add_person_button)

        # Edit Details Form
        self.edit_details_form = EditDetailsForm(self.family_tree_handler)
        manage_tree_layout.addWidget(self.edit_details_form)

        # Export Widget
        self.export_widget = ExportWidget(self.family_tree_handler, self)
        manage_tree_layout.addWidget(self.export_widget)

        # Re-render Button
        re_render_button = QPushButton("Re-render")
        re_render_button.clicked.connect(self.re_render_tree)
        manage_tree_layout.addWidget(re_render_button)

        sidebar.addTab(manage_tree_tab, "Manage Tree")

        # About Tab (Future) - FIXME: Clean this
        about_tab = QWidget()
        sidebar.addTab(about_tab, "About")
        self.publish_content_to_about_tab(about_tab)

        # Add the QTabWidget to the wrapper
        sidebar_layout.addWidget(sidebar)

        return sidebar_wrapper

    def open_add_person_dialog(self):
        dialog = AddPersonDialog(self.family_tree_handler, self)
        dialog.exec()

    # FIXME: Clean this
    def publish_content_to_about_tab(self, about_tab):
        about_layout = QVBoxLayout(about_tab)
        content = """
        # About Family Tree App

        This is a simple family tree application built using Python and PySide6.

        ## Features

        -   View family tree data in a graphical format.
        -   Import family tree data from a file.
        -   Add new members to the family tree.
        -   Edit existing member details.
        -   Export family tree data and graph to files.

        ## Future Enhancements

        -   Chatbot integration for interactive queries.
        -   More advanced search and filtering options.
        -   Support for different data formats.
        """
        html_content = markdown.markdown(content)
        about_label = QLabel(html_content)
        about_label.setOpenExternalLinks(True)
        about_label.setTextFormat(Qt.RichText)
        # Set the size policy to Ignored
        about_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        about_label.setWordWrap(True)
        about_layout.addWidget(about_label)

    def create_content_area(self):
        content_area = QSplitter(Qt.Vertical)

        # Pyvis Output (Top)
        self.pyvis_view = QWebEngineView()
        content_area.addWidget(self.pyvis_view)

        # Enable local file access (less secure)
        # settings = self.pyvis_view.settings()
        # settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        # settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)

        # Chatbot Placeholder (Bottom)
        self.chatbot_placeholder = ChatbotPlaceholder()
        content_area.addWidget(self.chatbot_placeholder)

        # Set initial splitter sizes (adjust as needed)
        content_area.setSizes([600, 200])

        return content_area

    def re_render_tree(self):
        # Re-render the tree and update the QWebEngineView
        self.family_tree_handler.display_family_tree()
        self.load_pyvis_html()

    def load_pyvis_html(self):
        # Load the pyvis HTML into the QWebEngineView
        if os.path.exists(self.family_tree_handler.output_file):
            print("Loading pyvis HTML...")
            local_url = QUrl.fromLocalFile(self.family_tree_handler.output_file)
            print(f"Local URL: {local_url}")
            self.pyvis_view.setUrl(local_url)
        else:
            QMessageBox.warning(self, "Error", "Output file not found.")

    def clear_pyvis_view(self):
        """Clears the content of the Pyvis view."""
        self.pyvis_view.setHtml("")

    def load_from_protobuf(self):
        try:
            self.family_tree_handler.load_from_protobuf()
            self.re_render_tree()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load data: {e}")


class AddPersonDialog(QDialog):
    def __init__(self, family_tree_handler, family_tree_gui):
        super().__init__()
        self.family_tree_handler = family_tree_handler
        self.family_tree_gui = family_tree_gui
        self.user_input_values = {}
        self.setWindowTitle("Enter a new family member")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.user_input_fields = {}

        # Name
        name_label = QLabel("Name:")
        self.user_input_fields["name"] = QLineEdit()
        layout.addWidget(name_label)
        layout.addWidget(self.user_input_fields["name"])

        # Date of Birth
        self.user_input_fields["day"] = QSpinBox()
        self.user_input_fields["day"].setRange(1, 31)
        self.user_input_fields["month"] = QSpinBox()
        self.user_input_fields["month"].setRange(1, 12)
        self.user_input_fields["year"] = QSpinBox()
        self.user_input_fields["year"].setRange(1700, QDate.currentDate().year())
        self.user_input_fields["year"].setValue(QDate.currentDate().year())
        dob_layout = QHBoxLayout()

        dob_layout.addWidget(QLabel("Day:"))
        dob_layout.addWidget(self.user_input_fields["day"])
        dob_layout.addWidget(QLabel("Month:"))
        dob_layout.addWidget(self.user_input_fields["month"])
        dob_layout.addWidget(QLabel("Year:"))
        dob_layout.addWidget(self.user_input_fields["year"])
        layout.addLayout(dob_layout)

        # Save Button
        save_button = QPushButton("Save New Member")
        save_button.clicked.connect(self.save_new_member)
        layout.addWidget(save_button)

    def save_new_member(self):
        self.user_input_values.clear()
        self.user_input_values["name"] = self.user_input_fields["name"].text()
        self.user_input_values["dob_day"] = self.user_input_fields["day"].value()
        self.user_input_values["dob_month"] = self.user_input_fields["month"].value()
        self.user_input_values["dob_year"] = self.user_input_fields["year"].value()
        if not self.user_input_values["name"]:
            QMessageBox.warning(self, "Warning", "Name cannot be empty.")
            return

        self.family_tree_handler.create_node(self.user_input_values)
        self.family_tree_gui.re_render_tree()
        QMessageBox.information(self, "Success", "New member added!")
        self.accept()


class AddPersonForm(QWidget):
    def __init__(self, family_tree_handler):
        super().__init__()
        self.family_tree_handler = family_tree_handler
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout(self)
        pass
        self.name_input = QLineEdit()
        self.birth_year_input = QLineEdit()
        self.parents_input = QLineEdit()
        self.spouse_input = QLineEdit()
        self.children_input = QLineEdit()

        layout.addRow(QLabel("Name:"), self.name_input)
        layout.addRow(QLabel("Birth Year:"), self.birth_year_input)
        layout.addRow(QLabel("Parents (IDs, comma-separated):"), self.parents_input)
        layout.addRow(QLabel("Spouse (ID):"), self.spouse_input)
        layout.addRow(QLabel("Children (IDs, comma-separated):"), self.children_input)

        save_button = QPushButton("Save New Member")
        save_button.clicked.connect(self.save_new_member)
        layout.addRow(save_button)

    def save_new_member(self):
        # Implement logic to add a new member to the family tree
        # using self.family_tree_handler
        QMessageBox.information(self, "Success", "New member added!")


class EditDetailsForm(QWidget):
    def __init__(self, family_tree_handler):
        super().__init__()
        self.family_tree_handler = family_tree_handler
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        label = QLabel("Edit Details Form (Placeholder)")
        layout.addWidget(label)


class ExportWidget(QWidget):
    def __init__(self, family_tree_handler, family_tree_gui):
        super().__init__()
        self.family_tree_handler = family_tree_handler
        self.family_tree_gui = family_tree_gui
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Export Buttons
        export_data_button = QPushButton("Export data to File")
        export_data_button.clicked.connect(self.export_data_to_file)
        layout.addWidget(export_data_button)

        export_graph_button = QPushButton("Export graph to File")
        export_graph_button.clicked.connect(self.export_graph_to_file)
        layout.addWidget(export_graph_button)

    def export_data_to_file(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save Family Tree File", "", "Protobuf Files (*.txtpb)"
        )
        print(file_name)
        if file_name:
            self.family_tree_handler.update_output_data_file(file_name)
            self.family_tree_handler.save_to_protobuf()
            QMessageBox.information(
                self, "Success", f"Data exported successfully to {file_name}!"
            )

    def export_graph_to_file(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save Family Tree File", "", "HTML Files (*.html)"
        )
        if file_name:
            self.family_tree_handler.update_output_html_file(file_name)
            self.family_tree_gui.re_render_tree()
            QMessageBox.information(
                self, "Success", f"Family tree exported successfully to {file_name}!"
            )


class ChatbotPlaceholder(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        label = QLabel("Chatbot Placeholder")
        layout.addWidget(label)


class ImportFromFileForm(QWidget):
    def __init__(self, family_tree_handler, family_tree_gui):
        super().__init__()
        self.family_tree_handler = family_tree_handler
        self.family_tree_gui = family_tree_gui
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout(self)
        self.file_path_input = QLineEdit()
        self.file_path_input.setReadOnly(True)  # Make it read-only

        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_file)

        load_button = QPushButton("Load file")
        load_button.clicked.connect(self.load_from_file)

        layout.addRow(QLabel("File Path:"), self.file_path_input)
        layout.addRow(browse_button, load_button)

    def browse_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open Family Tree File", "", "Protobuf Files (*.txtpb)"
        )
        if file_name:
            self.file_path_input.setText(file_name)

    def load_from_file(self):
        file_name = self.file_path_input.text()
        if not file_name:
            QMessageBox.warning(self, "Warning", "Please select a file.")
            return

        if not os.path.exists(file_name):
            QMessageBox.critical(self, "Error", "File not found.")
            return
        # Clear the pyvis view before loading new data
        self.family_tree_gui.clear_pyvis_view()

        try:
            self.family_tree_handler.update_data_source(file_name)
            self.family_tree_gui.load_from_protobuf()
            QMessageBox.information(self, "Success", "Data loaded successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load data: {e}")

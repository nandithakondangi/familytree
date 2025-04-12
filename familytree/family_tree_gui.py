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
    QCheckBox,
    QComboBox,  # Import QComboBox
)
from PySide6.QtCore import Qt, QDate
from family_tree_handler import FamilyTreeHandler
import proto.utils_pb2 as utils_pb2
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import Qt, QUrl
from family_tree_handler import FamilyTreeHandler
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
        self.user_input_fields = {}
        # Add widgets for DoD fields to be accessible later
        self.dod_fields_widget = None
        self.dod_label = None
        # Add widget and label for DOB fields
        self.dob_fields_widget = None
        self.dob_label = None
        self.setWindowTitle("Enter a new family member")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()  # Use QFormLayout for label-widget pairs

        self.display_name_field(form_layout)
        self.display_nicknames_field(form_layout)
        self.display_gender_field(form_layout)
        self.display_dob_field(form_layout)
        self.display_traditional_date_of_birth_field(form_layout)
        self.display_is_alive_field(form_layout)
        self.display_dod_field(form_layout)

        # Add the entire form layout to the main vertical layout
        layout.addLayout(form_layout)

        # Save Button
        save_button = QPushButton("Save New Member")
        save_button.clicked.connect(self.save_new_member)
        layout.addWidget(save_button)

        self.toggle_dod_fields()  # Call initially to set correct visibility

    def display_name_field(self, form_layout: QFormLayout):
        # Name
        self.user_input_fields["name"] = QLineEdit()
        form_layout.addRow(QLabel("Name:"), self.user_input_fields["name"])

    def display_nicknames_field(self, form_layout: QFormLayout):
        # Nicknames
        self.user_input_fields["nicknames"] = QLineEdit()
        self.user_input_fields["nicknames"].setPlaceholderText("Comma-separated")
        form_layout.addRow(QLabel("Nicknames:"), self.user_input_fields["nicknames"])

    def display_gender_field(self, form_layout: QFormLayout):
        # Gender Dropdown
        gender_label = QLabel("Gender:")
        self.user_input_fields["gender"] = QComboBox()
        valid_genders = self.family_tree_handler.get_enum_values_from_proto_schema(
            "Gender", proto_module=utils_pb2
        )  # Pass the module
        if valid_genders:
            self.user_input_fields["gender"].addItems(valid_genders)
        else:
            # Handle case where genders couldn't be loaded
            self.user_input_fields["gender"].addItem("Error loading genders")
            self.user_input_fields["gender"].setEnabled(False)
        form_layout.addRow(gender_label, self.user_input_fields["gender"])

    def display_traditional_date_of_birth_field(self, form_layout: QFormLayout):
        valid_traditional_months = (
            self.family_tree_handler.get_enum_values_from_proto_schema("TamilMonth")
        )
        valid_traditional_stars = (
            self.family_tree_handler.get_enum_values_from_proto_schema("TamilStar")
        )
        # --- Start: Added Tamil Month and Star Dropdowns ---
        # Create a horizontal layout for Tamil Month and Star
        traditional_info_widget = QWidget()  # Use a widget to hold the QHBoxLayout
        traditional_info_layout = QHBoxLayout(traditional_info_widget)
        # Remove margins for tighter packing
        traditional_info_layout.setContentsMargins(0, 0, 0, 0)

        # Tamil Month Dropdown
        self.user_input_fields["dob_traditional_month"] = QComboBox()
        self.user_input_fields["dob_traditional_month"].addItems(
            valid_traditional_months
        )

        # Tamil Star Dropdown
        self.user_input_fields["dob_traditional_star"] = QComboBox()
        self.user_input_fields["dob_traditional_star"].addItems(valid_traditional_stars)

        # Add labels and dropdowns to the horizontal layout
        traditional_info_layout.addWidget(QLabel("DOB - Tamil Month:"))
        traditional_info_layout.addWidget(
            self.user_input_fields["dob_traditional_month"]
        )
        traditional_info_layout.addSpacing(10)  # Add some space between the two
        traditional_info_layout.addWidget(QLabel("DOB - Tamil Star:"))
        traditional_info_layout.addWidget(
            self.user_input_fields["dob_traditional_star"]
        )

        # --- End: Added Tamil Month and Star Dropdowns ---
        # Add the horizontal layout widget as a single row in the form layout
        # Use an empty label for the first column if you want it aligned like other rows
        form_layout.addRow(traditional_info_widget)
        # OR, if you want a label spanning the first column:
        # form_layout.addRow(QLabel("Traditional DOB:"), traditional_info_widget)

    def display_dob_field(self, form_layout: QFormLayout):
        # Date of Birth Checkbox
        self.dob_checkbox = QCheckBox("Date of Birth is not known")
        self.dob_checkbox.setChecked(False)  # Initially unchecked
        self.dob_checkbox.stateChanged.connect(self.toggle_dob_fields)
        # Add checkbox spanning both columns or with an empty label
        form_layout.addRow(self.dob_checkbox)

        # Date of Birth Fields (initially hidden)
        self.dob_fields_widget = QWidget()  # Create a widget to hold DOB fields
        self.dob_fields_layout = QHBoxLayout(self.dob_fields_widget)
        self.dob_fields_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        self.user_input_fields["date"] = QSpinBox()
        self.user_input_fields["date"].setRange(1, 31)
        self.user_input_fields["month"] = QSpinBox()
        self.user_input_fields["month"].setRange(1, 12)
        self.user_input_fields["year"] = QSpinBox()
        self.user_input_fields["year"].setRange(1700, QDate.currentDate().year())
        self.user_input_fields["year"].setValue(QDate.currentDate().year())

        self.dob_fields_layout.addWidget(QLabel("Date:"))
        self.dob_fields_layout.addWidget(self.user_input_fields["date"])
        self.dob_fields_layout.addWidget(QLabel("Month:"))
        self.dob_fields_layout.addWidget(self.user_input_fields["month"])
        self.dob_fields_layout.addWidget(QLabel("Year:"))
        self.dob_fields_layout.addWidget(self.user_input_fields["year"])

        # Create and store the DOB label
        self.dob_label = QLabel("DOB (D/M/Y):")
        # Add the stored label and the DOB fields widget as a row
        form_layout.addRow(self.dob_label, self.dob_fields_widget)

        # Initially hide the DOB fields widget
        self.toggle_dob_fields()

    def display_is_alive_field(self, form_layout: QFormLayout):
        self.user_input_fields["IsAlive"] = QCheckBox("Is the person alive?")
        form_layout.addRow(self.user_input_fields["IsAlive"])
        self.user_input_fields["IsAlive"].setChecked(True)  # Default to alive
        self.user_input_fields["IsAlive"].stateChanged.connect(self.toggle_dod_fields)

    def display_dod_field(self, form_layout: QFormLayout):
        """Adds the Date of Death fields (Gregorian and Traditional, initially hidden) to the form."""
        # Create a main widget to hold ALL DoD fields (Gregorian + Traditional)
        self.dod_fields_widget = QWidget()
        # Use a QVBoxLayout to stack Gregorian and Traditional horizontally
        main_dod_layout = QVBoxLayout(self.dod_fields_widget)
        main_dod_layout.setContentsMargins(0, 0, 0, 0)  # Remove outer margins

        # --- Gregorian DoD Fields ---
        gregorian_dod_widget = QWidget()  # Widget for horizontal layout
        gregorian_dod_layout = QHBoxLayout(gregorian_dod_widget)
        gregorian_dod_layout.setContentsMargins(0, 0, 0, 0)  # Remove inner margins

        # Create SpinBoxes for Gregorian DoD
        self.user_input_fields["dod_date"] = QSpinBox()
        self.user_input_fields["dod_date"].setRange(1, 31)
        self.user_input_fields["dod_month"] = QSpinBox()
        self.user_input_fields["dod_month"].setRange(1, 12)
        self.user_input_fields["dod_year"] = QSpinBox()
        self.user_input_fields["dod_year"].setRange(1700, QDate.currentDate().year())
        self.user_input_fields["dod_year"].setValue(QDate.currentDate().year())

        # Add labels and SpinBoxes to the horizontal layout
        gregorian_dod_layout.addWidget(QLabel("Date:"))
        gregorian_dod_layout.addWidget(self.user_input_fields["dod_date"])
        gregorian_dod_layout.addWidget(QLabel("Month:"))
        gregorian_dod_layout.addWidget(self.user_input_fields["dod_month"])
        gregorian_dod_layout.addWidget(QLabel("Year:"))
        gregorian_dod_layout.addWidget(self.user_input_fields["dod_year"])

        # Add the Gregorian DoD widget to the main vertical layout
        main_dod_layout.addWidget(gregorian_dod_widget)
        # --- End Gregorian DoD Fields ---

        # --- Traditional DoD Fields ---
        traditional_dod_widget = QWidget()  # Widget for horizontal layout
        traditional_dod_layout = QHBoxLayout(traditional_dod_widget)
        traditional_dod_layout.setContentsMargins(0, 0, 0, 0)  # Remove inner margins

        # Get enum values
        valid_traditional_months = (
            self.family_tree_handler.get_enum_values_from_proto_schema(
                "TamilMonth", proto_module=utils_pb2
            )
        )
        valid_traditional_paksham = (
            self.family_tree_handler.get_enum_values_from_proto_schema(
                "Paksham", proto_module=utils_pb2
            )
        )
        valid_traditional_thithi = (
            self.family_tree_handler.get_enum_values_from_proto_schema(
                "Thithi", proto_module=utils_pb2
            )
        )

        # Create ComboBoxes for Traditional DoD
        self.user_input_fields["dod_traditional_month"] = QComboBox()
        self.user_input_fields["dod_traditional_month"].addItems(
            valid_traditional_months
        )

        self.user_input_fields["dod_traditional_paksham"] = QComboBox()
        self.user_input_fields["dod_traditional_paksham"].addItems(
            valid_traditional_paksham
        )

        self.user_input_fields["dod_traditional_thithi"] = QComboBox()
        self.user_input_fields["dod_traditional_thithi"].addItems(
            valid_traditional_thithi
        )
        # Add labels and ComboBoxes to the horizontal layout
        traditional_dod_layout.addWidget(QLabel("Month:"))
        traditional_dod_layout.addWidget(
            self.user_input_fields["dod_traditional_month"]
        )
        traditional_dod_layout.addSpacing(10)
        traditional_dod_layout.addWidget(QLabel("Paksham:"))
        traditional_dod_layout.addWidget(
            self.user_input_fields["dod_traditional_paksham"]
        )
        traditional_dod_layout.addSpacing(10)
        traditional_dod_layout.addWidget(QLabel("Thithi:"))
        traditional_dod_layout.addWidget(
            self.user_input_fields["dod_traditional_thithi"]
        )

        # Add the Traditional DoD widget to the main vertical layout
        main_dod_layout.addWidget(traditional_dod_widget)
        # --- End Traditional DoD Fields ---

        # Create and store the label
        self.dod_label = QLabel("Date of Death:")  # <-- Store the label

        # Add the stored label and the main DoD fields widget as a single row in the form layout
        form_layout.addRow(self.dod_label, self.dod_fields_widget)

        # Initial visibility is handled by toggle_dod_fields called in init_ui

    def toggle_dod_fields(self):
        """Shows or hides the Date of Death fields based on the 'Is Alive' checkbox."""
        # Ensure both the label and the widget exist before toggling
        if self.dod_label and self.dod_fields_widget:
            is_alive_checked = self.user_input_fields["IsAlive"].isChecked()
            # Calculate desired visibility (False if alive, True if not)
            visible = not is_alive_checked
            # Toggle visibility for BOTH the label and the widget
            self.dod_label.setVisible(visible)
            self.dod_fields_widget.setVisible(visible)

    def toggle_dob_fields(self):
        """Shows or hides the Date of Birth label and fields based on the checkbox state."""
        # Ensure both the label and the widget exist before toggling
        if self.dob_label and self.dob_fields_widget:
            is_checked = self.dob_checkbox.isChecked()
            # Calculate desired visibility (True if NOT checked, False if checked)
            visible = not is_checked
            # Toggle visibility for BOTH the label and the widget
            self.dob_label.setVisible(visible)  # <-- Toggle label visibility
            self.dob_fields_widget.setVisible(visible)  # <-- Toggle widget visibility

    def save_new_member(self):
        self.user_input_values.clear()
        self.user_input_values["name"] = self.user_input_fields["name"].text()
        if not self.user_input_values["name"]:
            QMessageBox.warning(self, "Warning", "Name cannot be empty.")
            return
        self.user_input_values["nicknames"] = self.user_input_fields["nicknames"].text()
        self.user_input_values["gender"] = self.user_input_fields[
            "gender"
        ].currentText()

        # Get DOB only if checkbox is unchecked
        if not self.dob_checkbox.isChecked():
            self.user_input_values["dob_date"] = self.user_input_fields["date"].value()
            self.user_input_values["dob_month"] = self.user_input_fields[
                "month"
            ].value()
            self.user_input_values["dob_year"] = self.user_input_fields["year"].value()

        self.user_input_values["dob_traditional_month"] = self.user_input_fields[
            "dob_traditional_month"
        ].currentText()
        self.user_input_values["dob_traditional_star"] = self.user_input_fields[
            "dob_traditional_star"
        ].currentText()

        # --- Get IsAlive status ---
        is_alive = self.user_input_fields["IsAlive"].isChecked()
        self.user_input_values["IsAlive"] = is_alive
        # --- End Get IsAlive status ---
        # --- Get DoD only if 'Is Alive' is unchecked ---
        if not is_alive:
            # Gregorian DoD
            self.user_input_values["dod_date"] = self.user_input_fields[
                "dod_date"
            ].value()
            self.user_input_values["dod_month"] = self.user_input_fields[
                "dod_month"
            ].value()
            self.user_input_values["dod_year"] = self.user_input_fields[
                "dod_year"
            ].value()
            # Traditional DoD
            self.user_input_values["dod_traditional_month"] = self.user_input_fields[
                "dod_traditional_month"
            ].currentText()
            self.user_input_values["dod_traditional_paksham"] = self.user_input_fields[
                "dod_traditional_paksham"
            ].currentText()
            self.user_input_values["dod_traditional_thithi"] = self.user_input_fields[
                "dod_traditional_thithi"
            ].currentText()
        # --- End Get DoD ---

        self.family_tree_handler.create_node(self.user_input_values)
        self.family_tree_gui.re_render_tree()
        QMessageBox.information(self, "Success", "New member added!")
        self.accept()


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

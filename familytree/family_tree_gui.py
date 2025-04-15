import os

from family_tree_handler import FamilyTreeHandler
from PySide6.QtCore import QDate, Qt, QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

import proto.utils_pb2 as utils_pb2


class FamilyTreeGUI(QMainWindow):
    # Accept temp_dir_path in constructor
    def __init__(self, temp_dir_path):
        super().__init__()
        self.temp_dir_path = temp_dir_path  # Store the path
        self.setWindowTitle("Family Tree Viewer")
        self.setGeometry(100, 100, 1200, 800)

        # Pass the temp_dir_path to the handler
        self.family_tree_handler = FamilyTreeHandler(temp_dir_path=self.temp_dir_path)

        self.init_ui()
        # Load initial empty state or default file if desired
        # self.load_pyvis_html() # Load initial view (might be empty)

    def init_ui(self):
        # Main Splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)  # Use Orientation enum
        main_splitter.setChildrenCollapsible(False)
        self.setCentralWidget(main_splitter)

        # Sidebar (Left)
        sidebar = self.create_sidebar()
        main_splitter.addWidget(sidebar)

        # Main Content Area (Right)
        content_area = self.create_content_area()
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

        # Import from file Form
        self.import_from_file_form = ImportFromFileForm(self.family_tree_handler, self)
        manage_tree_layout.addWidget(self.import_from_file_form)

        # Add Person Button
        self.add_person_button = QPushButton("➕ Add New Person")  # Added icon
        self.add_person_button.clicked.connect(self.open_add_person_dialog)
        manage_tree_layout.addWidget(self.add_person_button)

        # Edit Details Form (Placeholder)
        # self.edit_details_form = EditDetailsForm(self.family_tree_handler)
        # manage_tree_layout.addWidget(self.edit_details_form)
        edit_placeholder = QLabel("<i>Edit functionality coming soon...</i>")
        edit_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        manage_tree_layout.addWidget(edit_placeholder)

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

    def open_add_person_dialog(self):
        # Pass the handler and self (GUI) to the dialog
        dialog = AddPersonDialog(self.family_tree_handler, self)
        # exec() is blocking, use open() for non-blocking if needed later
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            print("Add Person dialog accepted.")
            # Re-rendering is handled within the dialog's save method now
        else:
            print("Add Person dialog cancelled.")

    def publish_content_to_about_tab(self, about_tab):
        about_layout = QVBoxLayout(about_tab)
        # Using QTextEdit for better rendering and potential scrollbars
        about_text_edit = QTextEdit()
        about_text_edit.setReadOnly(True)

        # Content can be loaded from a file or kept as a string
        content = """
        <h2>About Family Tree App</h2>

        <p>This application allows you to visualize and manage family tree data.</p>
        <p>Built using Python, PySide6, Protobuf, and Pyvis.</p>

        <h3>Features:</h3>
        <ul>
            <li>Load family tree data from <code>.txtpb</code> files.</li>
            <li>Visualize the tree interactively.</li>
            <li>Add new family members.</li>
            <li>Export the data back to <code>.txtpb</code>.</li>
            <li>Export the interactive graph as an HTML file.</li>
        </ul>

        <h3>Future Enhancements:</h3>
        <ul>
            <li>Editing existing member details.</li>
            <li>Adding/Editing relationships (spouse, children).</li>
            <li>Chatbot integration for queries.</li>
            <li>More robust error handling and user feedback.</li>
            <li>Support for different data formats.</li>
        </ul>
        <hr>
        <p>Temporary files are stored in: <code>{temp_dir}</code></p>
        """.format(temp_dir=self.temp_dir_path)  # Show the temp dir path

        # Use setHtml for rich text
        about_text_edit.setHtml(content)
        about_layout.addWidget(about_text_edit)

    def create_content_area(self):
        content_area = QSplitter(Qt.Orientation.Vertical)
        content_area.setChildrenCollapsible(False)

        # Pyvis Output (Top)
        self.pyvis_view = QWebEngineView()
        # Optional: Configure settings if needed (e.g., for local file access, JS)
        # settings = self.pyvis_view.settings()
        # settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        # settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        # settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        content_area.addWidget(self.pyvis_view)

        # Chatbot Placeholder (Bottom) - Keep simple for now
        self.chatbot_placeholder = ChatbotPlaceholder()
        content_area.addWidget(self.chatbot_placeholder)

        # Set initial splitter sizes
        content_area.setSizes([650, 150])

        return content_area

    def re_render_tree(self):
        """Re-generates the pyvis graph and reloads it in the view."""
        print("Re-rendering tree...")
        try:
            # Ensure the handler has data before trying to display
            if not self.family_tree_handler.family_tree.members:
                print("No data loaded, clearing view.")
                self.clear_pyvis_view()
                # Optionally show a message in the view
                self.pyvis_view.setHtml(
                    "<p style='color: white; text-align: center; margin-top: 50px;'>Load data or add a person to see the tree.</p>"
                )
                return

            self.family_tree_handler.display_family_tree()
            self.load_pyvis_html()
            print("Tree re-rendered successfully.")
        except Exception as e:
            print(f"Error during re-rendering: {e}")
            QMessageBox.critical(
                self, "Render Error", f"Failed to re-render the tree:\n{e}"
            )

    def load_pyvis_html(self):
        """Loads the generated HTML file into the QWebEngineView."""
        output_html_file = self.family_tree_handler.output_file
        if os.path.exists(output_html_file):
            try:
                # Using file:/// prefix is important for local files
                local_url = QUrl.fromLocalFile(os.path.abspath(output_html_file))
                print(f"Loading HTML from: {local_url.toString()}")
                self.pyvis_view.setUrl(local_url)
                # self.pyvis_view.reload() # Force reload if needed
            except Exception as e:
                print(f"Error loading HTML into QWebEngineView: {e}")
                QMessageBox.critical(
                    self, "Load Error", f"Could not load the HTML file:\n{e}"
                )
                self.clear_pyvis_view()
        else:
            print(f"Output file not found: {output_html_file}")
            self.clear_pyvis_view()
            self.pyvis_view.setHtml(
                "<p style='color: white; text-align: center; margin-top: 50px;'>HTML file not generated yet.</p>"
            )

    def clear_pyvis_view(self):
        """Clears the content of the Pyvis view."""
        print("Clearing Pyvis view.")
        self.pyvis_view.setUrl(QUrl("about:blank"))  # Load a blank page

    def load_from_protobuf(self):
        """Loads data using the handler and triggers a re-render."""
        try:
            # Clear existing graph data in handler before loading new file
            self.family_tree_handler.family_tree.Clear()
            self.family_tree_handler.nx_graph.clear()
            self.family_tree_handler.load_from_protobuf()
            # Re-render the tree after successful load
            self.re_render_tree()
            QMessageBox.information(self, "Success", "Data loaded successfully!")
        except FileNotFoundError:
            QMessageBox.critical(
                self, "Error", f"File not found:\n{self.family_tree_handler.input_file}"
            )
            self.clear_pyvis_view()  # Clear view on error
        except Exception as e:
            print(f"Failed to load data: {e}")  # Log detailed error
            QMessageBox.critical(
                self, "Load Error", f"Failed to load data from file:\n{e}"
            )
            self.clear_pyvis_view()  # Clear view on error


# --- AddDetailsForm ---
class AddPersonDialog(QDialog):
    def __init__(self, family_tree_handler, family_tree_gui):
        super().__init__()
        self.family_tree_handler = family_tree_handler
        self.family_tree_gui = family_tree_gui  # Keep reference to main GUI
        self.user_input_fields = {}  # Store input widgets

        # Widgets that need state toggling
        self.dod_fields_widget = None
        self.dod_label = None
        self.dob_fields_widget = None
        self.dob_label = None
        self.dob_checkbox = None  # Keep reference to checkbox

        self.setWindowTitle("➕ Add New Family Member")
        self.setMinimumWidth(500)  # Set a minimum width
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.setRowWrapPolicy(
            QFormLayout.RowWrapPolicy.WrapLongRows
        )  # Wrap long rows

        # --- Create Fields ---
        self.display_name_field(form_layout)
        self.display_nicknames_field(form_layout)
        self.display_gender_field(form_layout)
        self.display_dob_field(form_layout)  # Includes checkbox and fields
        self.display_traditional_date_of_birth_field(form_layout)
        self.display_is_alive_field(form_layout)
        self.display_dod_field(form_layout)  # Includes Gregorian and Traditional

        main_layout.addLayout(form_layout)

        # --- Buttons ---
        button_layout = QHBoxLayout()
        button_layout.addStretch()  # Push buttons to the right

        save_button = QPushButton("💾 Save Member")
        save_button.clicked.connect(self.save_new_member)
        save_button.setDefault(True)  # Allow Enter key to trigger save

        cancel_button = QPushButton("❌ Cancel")
        cancel_button.clicked.connect(self.reject)  # Close dialog without saving

        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        main_layout.addLayout(button_layout)

        # --- Initial State ---
        self.toggle_dob_fields()  # Set initial visibility based on checkbox
        self.toggle_dod_fields()  # Set initial visibility based on 'IsAlive'

    # --- Field Creation Methods (Helper functions for init_ui) ---

    def display_name_field(self, form_layout: QFormLayout):
        self.user_input_fields["name"] = QLineEdit()
        self.user_input_fields["name"].setPlaceholderText("Full legal name")
        form_layout.addRow(
            QLabel("<b>Name:</b>*"), self.user_input_fields["name"]
        )  # Bold label, add asterisk

    def display_nicknames_field(self, form_layout: QFormLayout):
        self.user_input_fields["nicknames"] = QLineEdit()
        self.user_input_fields["nicknames"].setPlaceholderText(
            "e.g., Johnny, Beth (comma-separated)"
        )
        form_layout.addRow(QLabel("Nicknames:"), self.user_input_fields["nicknames"])

    def display_gender_field(self, form_layout: QFormLayout):
        gender_label = QLabel("Gender:")
        self.user_input_fields["gender"] = QComboBox()
        # Fetch enum values safely
        valid_genders = self.family_tree_handler.get_enum_values_from_proto_schema(
            "Gender", proto_module=utils_pb2
        )
        if valid_genders:
            self.user_input_fields["gender"].addItems(valid_genders)
            # Optionally set a default, e.g., GENDER_UNKNOWN
            try:
                default_index = valid_genders.index("GENDER_UNKNOWN")
                self.user_input_fields["gender"].setCurrentIndex(default_index)
            except ValueError:
                pass  # GENDER_UNKNOWN not found or list empty
        else:
            self.user_input_fields["gender"].addItem("Error loading")
            self.user_input_fields["gender"].setEnabled(False)
        form_layout.addRow(gender_label, self.user_input_fields["gender"])

    def display_dob_field(self, form_layout: QFormLayout):
        # Checkbox first
        self.dob_checkbox = QCheckBox("Date of Birth is not known")
        self.dob_checkbox.setChecked(False)
        self.dob_checkbox.stateChanged.connect(self.toggle_dob_fields)
        form_layout.addRow(self.dob_checkbox)  # Add checkbox spanning row

        # Container for DOB fields
        self.dob_fields_widget = QWidget()
        dob_fields_layout = QHBoxLayout(self.dob_fields_widget)
        dob_fields_layout.setContentsMargins(0, 0, 0, 0)

        self.user_input_fields["dob_date"] = QSpinBox()
        self.user_input_fields["dob_date"].setRange(1, 31)
        self.user_input_fields["dob_month"] = QSpinBox()
        self.user_input_fields["dob_month"].setRange(1, 12)
        self.user_input_fields["dob_year"] = QSpinBox()
        current_year = QDate.currentDate().year()
        self.user_input_fields["dob_year"].setRange(1700, current_year)
        self.user_input_fields["dob_year"].setValue(
            current_year - 30
        )  # Default to reasonable year

        dob_fields_layout.addWidget(QLabel("Date:"))
        dob_fields_layout.addWidget(self.user_input_fields["dob_date"])
        dob_fields_layout.addWidget(QLabel("Month:"))
        dob_fields_layout.addWidget(self.user_input_fields["dob_month"])
        dob_fields_layout.addWidget(QLabel("Year:"))
        dob_fields_layout.addWidget(self.user_input_fields["dob_year"])
        dob_fields_layout.addStretch()  # Push fields together

        self.dob_label = QLabel("DOB (D/M/Y):")
        form_layout.addRow(self.dob_label, self.dob_fields_widget)

    def display_traditional_date_of_birth_field(self, form_layout: QFormLayout):
        # Fetch enum values
        valid_months = self.family_tree_handler.get_enum_values_from_proto_schema(
            "TamilMonth"
        )
        valid_stars = self.family_tree_handler.get_enum_values_from_proto_schema(
            "TamilStar"
        )

        # Container widget
        traditional_info_widget = QWidget()
        traditional_info_layout = QHBoxLayout(traditional_info_widget)
        traditional_info_layout.setContentsMargins(0, 0, 0, 0)

        # Month Dropdown
        self.user_input_fields["dob_traditional_month"] = QComboBox()
        if valid_months:
            self.user_input_fields["dob_traditional_month"].addItems(valid_months)
        else:
            self.user_input_fields["dob_traditional_month"].addItem("Error")
            self.user_input_fields["dob_traditional_month"].setEnabled(False)

        # Star Dropdown
        self.user_input_fields["dob_traditional_star"] = QComboBox()
        if valid_stars:
            self.user_input_fields["dob_traditional_star"].addItems(valid_stars)
        else:
            self.user_input_fields["dob_traditional_star"].addItem("Error")
            self.user_input_fields["dob_traditional_star"].setEnabled(False)

        traditional_info_layout.addWidget(QLabel("Tamil Month:"))
        traditional_info_layout.addWidget(
            self.user_input_fields["dob_traditional_month"]
        )
        traditional_info_layout.addSpacing(15)
        traditional_info_layout.addWidget(QLabel("Tamil Star:"))
        traditional_info_layout.addWidget(
            self.user_input_fields["dob_traditional_star"]
        )
        traditional_info_layout.addStretch()

        # Add the container widget to the form
        form_layout.addRow(QLabel("Traditional DOB:"), traditional_info_widget)

    def display_is_alive_field(self, form_layout: QFormLayout):
        self.user_input_fields["IsAlive"] = QCheckBox("This person is alive")
        self.user_input_fields["IsAlive"].setChecked(True)  # Default to alive
        self.user_input_fields["IsAlive"].stateChanged.connect(self.toggle_dod_fields)
        form_layout.addRow(self.user_input_fields["IsAlive"])  # Checkbox spans row

    def display_dod_field(self, form_layout: QFormLayout):
        # Main container for all DoD fields
        self.dod_fields_widget = QWidget()
        main_dod_layout = QVBoxLayout(self.dod_fields_widget)
        main_dod_layout.setContentsMargins(0, 0, 0, 0)

        # --- Gregorian DoD ---
        gregorian_dod_widget = QWidget()
        gregorian_dod_layout = QHBoxLayout(gregorian_dod_widget)
        gregorian_dod_layout.setContentsMargins(0, 0, 0, 0)

        self.user_input_fields["dod_date"] = QSpinBox()
        self.user_input_fields["dod_date"].setRange(1, 31)
        self.user_input_fields["dod_month"] = QSpinBox()
        self.user_input_fields["dod_month"].setRange(1, 12)
        self.user_input_fields["dod_year"] = QSpinBox()
        current_year = QDate.currentDate().year()
        self.user_input_fields["dod_year"].setRange(1700, current_year)
        self.user_input_fields["dod_year"].setValue(current_year)

        gregorian_dod_layout.addWidget(QLabel("Date:"))
        gregorian_dod_layout.addWidget(self.user_input_fields["dod_date"])
        gregorian_dod_layout.addWidget(QLabel("Month:"))
        gregorian_dod_layout.addWidget(self.user_input_fields["dod_month"])
        gregorian_dod_layout.addWidget(QLabel("Year:"))
        gregorian_dod_layout.addWidget(self.user_input_fields["dod_year"])
        gregorian_dod_layout.addStretch()
        main_dod_layout.addWidget(QLabel("Gregorian DoD:"))  # Add sub-label
        main_dod_layout.addWidget(gregorian_dod_widget)
        # --- End Gregorian DoD ---

        main_dod_layout.addSpacing(10)  # Space between Gregorian and Traditional

        # --- Traditional DoD ---
        traditional_dod_widget = QWidget()
        traditional_dod_layout = QHBoxLayout(traditional_dod_widget)
        traditional_dod_layout.setContentsMargins(0, 0, 0, 0)

        valid_months = self.family_tree_handler.get_enum_values_from_proto_schema(
            "TamilMonth"
        )
        valid_paksham = self.family_tree_handler.get_enum_values_from_proto_schema(
            "Paksham"
        )
        valid_thithi = self.family_tree_handler.get_enum_values_from_proto_schema(
            "Thithi"
        )

        self.user_input_fields["dod_traditional_month"] = QComboBox()
        if valid_months:
            self.user_input_fields["dod_traditional_month"].addItems(valid_months)
        else:
            self.user_input_fields["dod_traditional_month"].setEnabled(False)

        self.user_input_fields["dod_traditional_paksham"] = QComboBox()
        if valid_paksham:
            self.user_input_fields["dod_traditional_paksham"].addItems(valid_paksham)
        else:
            self.user_input_fields["dod_traditional_paksham"].setEnabled(False)

        self.user_input_fields["dod_traditional_thithi"] = QComboBox()
        if valid_thithi:
            self.user_input_fields["dod_traditional_thithi"].addItems(valid_thithi)
        else:
            self.user_input_fields["dod_traditional_thithi"].setEnabled(False)

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
        traditional_dod_layout.addStretch()
        main_dod_layout.addWidget(QLabel("Traditional DoD:"))  # Add sub-label
        main_dod_layout.addWidget(traditional_dod_widget)
        # --- End Traditional DoD ---

        self.dod_label = QLabel(
            "<b>Date of Death Details:</b>"
        )  # Main label for the section
        form_layout.addRow(self.dod_label, self.dod_fields_widget)

    # --- Toggle Visibility Methods ---

    def toggle_dod_fields(self):
        """Shows/hides DoD fields based on 'Is Alive' checkbox."""
        if self.dod_label and self.dod_fields_widget:
            is_alive = self.user_input_fields["IsAlive"].isChecked()
            visible = not is_alive  # Show if NOT alive
            self.dod_label.setVisible(visible)
            self.dod_fields_widget.setVisible(visible)

    def toggle_dob_fields(self):
        """Shows/hides DOB fields based on 'DOB not known' checkbox."""
        if self.dob_label and self.dob_fields_widget and self.dob_checkbox:
            is_unknown = self.dob_checkbox.isChecked()
            visible = not is_unknown  # Show if NOT unknown
            self.dob_label.setVisible(visible)
            self.dob_fields_widget.setVisible(visible)

    # --- Save Action ---

    def save_new_member(self):
        """Gathers data from fields, validates, calls handler, and closes."""
        user_input_values = {}

        # --- Gather Data ---
        user_input_values["name"] = self.user_input_fields["name"].text().strip()
        if not user_input_values["name"]:
            QMessageBox.warning(
                self, "Input Required", "The 'Name' field cannot be empty."
            )
            self.user_input_fields["name"].setFocus()  # Focus the field
            return  # Stop processing

        user_input_values["nicknames"] = (
            self.user_input_fields["nicknames"].text().strip()
        )
        user_input_values["gender"] = self.user_input_fields["gender"].currentText()

        # DOB (only if known)
        if not self.dob_checkbox.isChecked():
            user_input_values["dob_date"] = self.user_input_fields["dob_date"].value()
            user_input_values["dob_month"] = self.user_input_fields["dob_month"].value()
            user_input_values["dob_year"] = self.user_input_fields["dob_year"].value()
            # Basic validation (e.g., prevent future dates?) - More complex validation possible
            dob = QDate(
                user_input_values["dob_year"],
                user_input_values["dob_month"],
                user_input_values["dob_date"],
            )
            if not dob.isValid() or dob > QDate.currentDate():
                QMessageBox.warning(
                    self,
                    "Invalid Date",
                    "Please enter a valid Date of Birth that is not in the future.",
                )
                return

        # Traditional DOB
        user_input_values["dob_traditional_month"] = self.user_input_fields[
            "dob_traditional_month"
        ].currentText()
        user_input_values["dob_traditional_star"] = self.user_input_fields[
            "dob_traditional_star"
        ].currentText()

        # IsAlive status
        is_alive = self.user_input_fields["IsAlive"].isChecked()
        user_input_values["IsAlive"] = is_alive

        # DoD (only if not alive)
        if not is_alive:
            user_input_values["dod_date"] = self.user_input_fields["dod_date"].value()
            user_input_values["dod_month"] = self.user_input_fields["dod_month"].value()
            user_input_values["dod_year"] = self.user_input_fields["dod_year"].value()
            # Basic validation
            dod = QDate(
                user_input_values["dod_year"],
                user_input_values["dod_month"],
                user_input_values["dod_date"],
            )
            if not dod.isValid() or dod > QDate.currentDate():
                QMessageBox.warning(
                    self,
                    "Invalid Date",
                    "Please enter a valid Date of Death that is not in the future.",
                )
                return
            # Check if DoD is after DOB if both are provided
            if "dob" in locals() and dod < dob:
                QMessageBox.warning(
                    self,
                    "Invalid Date",
                    "Date of Death cannot be before Date of Birth.",
                )
                return

            user_input_values["dod_traditional_month"] = self.user_input_fields[
                "dod_traditional_month"
            ].currentText()
            user_input_values["dod_traditional_paksham"] = self.user_input_fields[
                "dod_traditional_paksham"
            ].currentText()
            user_input_values["dod_traditional_thithi"] = self.user_input_fields[
                "dod_traditional_thithi"
            ].currentText()

        # --- Call Handler ---
        try:
            print("Saving new member with data:", user_input_values)
            self.family_tree_handler.create_node(user_input_values)
            # Trigger re-render in the main GUI
            self.family_tree_gui.re_render_tree()
            QMessageBox.information(
                self,
                "Success",
                f"Member '{user_input_values['name']}' added successfully!",
            )
            self.accept()  # Close the dialog successfully
        except Exception as e:
            print(f"Error creating node: {e}")
            QMessageBox.critical(
                self, "Save Error", f"Failed to save the new member:\n{e}"
            )
            # Don't close the dialog on error


# --- EditDetailsForm (Placeholder) ---
class EditDetailsForm(QWidget):
    def __init__(self, family_tree_handler):
        super().__init__()
        self.family_tree_handler = family_tree_handler
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        label = QLabel("<i>Edit Details Form (Placeholder)</i>")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        # TODO: Implement member selection (e.g., dropdown, list) and form population


# --- ExportWidget ---
class ExportWidget(QWidget):
    def __init__(self, family_tree_handler, family_tree_gui):
        super().__init__()
        self.family_tree_handler = family_tree_handler
        self.family_tree_gui = family_tree_gui
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 0)  # Add top margin

        export_data_button = QPushButton("💾 Export Data (.txtpb)")
        export_data_button.setToolTip(
            "Save the raw family tree data in Protobuf Text Format."
        )
        export_data_button.clicked.connect(self.export_data_to_file)
        layout.addWidget(export_data_button)

        export_graph_button = QPushButton("🌐 Export Graph (.html)")
        export_graph_button.setToolTip(
            "Save the interactive graph visualization as an HTML file."
        )
        export_graph_button.clicked.connect(self.export_graph_to_file)
        layout.addWidget(export_graph_button)

    def export_data_to_file(self):
        # Suggest a filename based on input or default
        suggested_name = "family_tree_export.txtpb"
        # Use handler's default data file path's directory as starting point if possible
        default_dir = os.path.dirname(self.family_tree_handler.output_proto_data_file)

        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save Family Tree Data",
            os.path.join(default_dir, suggested_name),  # Suggest path and name
            "Protobuf Text Files (*.txtpb);;All Files (*)",
        )
        if file_name:
            try:
                self.family_tree_handler.update_output_data_file(
                    file_name
                )  # Update handler's target
                self.family_tree_handler.save_to_protobuf()  # Call save method
                QMessageBox.information(
                    self,
                    "Export Successful",
                    f"Data exported successfully to:\n{file_name}",
                )
            except Exception as e:
                print(f"Error exporting data: {e}")
                QMessageBox.critical(
                    self, "Export Error", f"Failed to export data:\n{e}"
                )

    def export_graph_to_file(self):
        # Suggest a filename based on input or default
        suggested_name = "family_tree_graph.html"
        # Use handler's default html file path's directory as starting point
        default_dir = os.path.dirname(self.family_tree_handler.output_file)

        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save Family Tree Graph",
            os.path.join(default_dir, suggested_name),  # Suggest path and name
            "HTML Files (*.html);;All Files (*)",
        )
        if file_name:
            try:
                # Update the handler's target HTML file path *before* re-rendering
                self.family_tree_handler.update_output_html_file(file_name)
                # Re-render the tree to generate the file at the new location
                self.family_tree_gui.re_render_tree()
                # Check if file was actually created after re-render
                if os.path.exists(file_name):
                    QMessageBox.information(
                        self,
                        "Export Successful",
                        f"Graph exported successfully to:\n{file_name}",
                    )
                else:
                    # This might happen if display_family_tree fails silently
                    QMessageBox.warning(
                        self,
                        "Export Warning",
                        f"Graph rendering completed, but the file was not found at:\n{file_name}",
                    )
            except Exception as e:
                print(f"Error exporting graph: {e}")
                QMessageBox.critical(
                    self, "Export Error", f"Failed to export graph:\n{e}"
                )


# --- ChatbotPlaceholder ---
class ChatbotPlaceholder(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        label = QLabel("🤖 Chatbot / Query Area (Future Feature)")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: #aaa;")  # Dim the text
        layout.addWidget(label)
        # Add a simple text input and button later
        # query_input = QLineEdit()
        # query_input.setPlaceholderText("Ask about the family...")
        # send_button = QPushButton("Send")
        # layout.addWidget(query_input)
        # layout.addWidget(send_button)


# --- ImportFromFileForm ---
class ImportFromFileForm(QWidget):
    def __init__(self, family_tree_handler, family_tree_gui):
        super().__init__()
        self.family_tree_handler = family_tree_handler
        self.family_tree_gui = family_tree_gui
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout(self)
        layout.setContentsMargins(0, 0, 0, 10)  # Add bottom margin

        self.file_path_input = QLineEdit()
        self.file_path_input.setPlaceholderText("Click Browse to select a .txtpb file")
        self.file_path_input.setReadOnly(True)

        browse_button = QPushButton("📂 Browse...")
        browse_button.clicked.connect(self.browse_file)

        load_button = QPushButton("📥 Load File")
        load_button.clicked.connect(self.load_from_file)
        # Disable load button initially until a file is selected
        self.load_button = load_button  # Store reference
        self.load_button.setEnabled(False)

        # Arrange buttons side-by-side
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.addWidget(browse_button)
        button_layout.addWidget(load_button)

        layout.addRow(QLabel("Data File:"), self.file_path_input)
        layout.addRow(button_container)  # Add the button container widget

    def browse_file(self):
        # Start browsing in the user's home directory or last used directory
        start_dir = os.path.expanduser("~")
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open Family Tree Data File",
            start_dir,
            "Protobuf Text Files (*.txtpb);;All Files (*)",
        )
        if file_name:
            self.file_path_input.setText(file_name)
            self.load_button.setEnabled(True)  # Enable load button
            print(f"File selected: {file_name}")
        else:
            self.load_button.setEnabled(False)  # Disable if no file selected

    def load_from_file(self):
        file_name = self.file_path_input.text()
        if not file_name:
            QMessageBox.warning(
                self, "No File Selected", "Please browse and select a data file first."
            )
            return

        if not os.path.exists(file_name):
            QMessageBox.critical(
                self,
                "File Not Found",
                f"The selected file does not exist:\n{file_name}",
            )
            self.file_path_input.clear()  # Clear the invalid path
            self.load_button.setEnabled(False)
            return

        # Confirmation before overwriting existing data (optional but good practice)
        if self.family_tree_handler.family_tree.members:  # Check if handler has data
            reply = QMessageBox.question(
                self,
                "Confirm Load",
                "Loading a new file will clear the current family tree data. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )  # Default to No
            if reply == QMessageBox.StandardButton.No:
                return  # User cancelled

        # Clear the pyvis view *before* loading new data
        self.family_tree_gui.clear_pyvis_view()

        try:
            # Update the data source in the handler
            self.family_tree_handler.update_data_source(file_name)
            # Call the main GUI's load method which handles errors and re-rendering
            self.family_tree_gui.load_from_protobuf()
            # Success message is handled in family_tree_gui.load_from_protobuf
        except Exception as e:
            # Error message is handled in family_tree_gui.load_from_protobuf
            print(f"Error during file load initiation: {e}")  # Log error here too
            self.load_button.setEnabled(
                False
            )  # Disable button on error? Or allow retry?

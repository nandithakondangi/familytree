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

        # --- Culture Setting ---
        self.is_indian_culture = True  # Default to Indian culture enabled

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

    def update_culture_setting(self, state):
        """Updates the culture flag based on the checkbox state."""
        self.is_indian_culture = state == Qt.CheckState.Checked.value
        print(f"Indian culture setting updated: {self.is_indian_culture}")
        # Future: Could potentially trigger updates elsewhere if needed

    def open_add_person_dialog(self):
        # Pass the handler, self (GUI), and the current culture setting to the dialog
        dialog = AddPersonDialog(self.family_tree_handler, self, self.is_indian_culture)
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
            <li>Add new family members (with optional traditional Indian dates).</li>
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
            <li>More culture-specific settings.</li>
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
    # Modified constructor to accept culture setting
    def __init__(self, family_tree_handler, family_tree_gui, is_indian_culture):
        super().__init__()
        self.family_tree_handler = family_tree_handler
        self.family_tree_gui = family_tree_gui  # Keep reference to main GUI
        self.show_traditional_dates = is_indian_culture  # Store culture flag
        self.user_input_fields = {}  # Store input widgets

        # Widgets that need state toggling
        self.dod_fields_widget = None
        self.dod_label = None
        self.dob_details_widget = None
        self.dob_details_label = None
        self.dob_known_checkbox = None

        # Widgets for traditional dates (to toggle visibility)
        self.traditional_dob_widget = None
        self.traditional_dob_label = None
        self.traditional_dod_widget = None
        self.traditional_dod_label = None

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
        self.display_dob_section(form_layout)
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
        self.toggle_dob_details()  # Set initial visibility based on checkbox
        self.toggle_dod_fields()  # Set initial visibility based on 'IsAlive'
        # Set initial visibility for traditional fields based on culture flag
        self.toggle_traditional_dob_visibility()
        self.toggle_traditional_dod_visibility()

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

    # Helper to create Gregorian DOB widget
    def _create_gregorian_dob_widget(self) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

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

        layout.addWidget(QLabel("Date:"))
        layout.addWidget(self.user_input_fields["dob_date"])
        layout.addWidget(QLabel("Month:"))
        layout.addWidget(self.user_input_fields["dob_month"])
        layout.addWidget(QLabel("Year:"))
        layout.addWidget(self.user_input_fields["dob_year"])
        layout.addStretch()
        return widget

    # Helper to create Traditional DOB widget
    def _create_traditional_dob_widget(self) -> QWidget:
        # Store the widget reference
        self.traditional_dob_widget = QWidget()
        layout = QHBoxLayout(self.traditional_dob_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        valid_months = self.family_tree_handler.get_enum_values_from_proto_schema(
            "TamilMonth"
        )
        valid_stars = self.family_tree_handler.get_enum_values_from_proto_schema(
            "TamilStar"
        )

        self.user_input_fields["dob_traditional_month"] = QComboBox()
        if valid_months:
            self.user_input_fields["dob_traditional_month"].addItems(valid_months)
        else:
            self.user_input_fields["dob_traditional_month"].addItem("Error")
            self.user_input_fields["dob_traditional_month"].setEnabled(False)

        self.user_input_fields["dob_traditional_star"] = QComboBox()
        if valid_stars:
            self.user_input_fields["dob_traditional_star"].addItems(valid_stars)
        else:
            self.user_input_fields["dob_traditional_star"].addItem("Error")
            self.user_input_fields["dob_traditional_star"].setEnabled(False)

        layout.addWidget(QLabel("Tamil Month:"))
        layout.addWidget(self.user_input_fields["dob_traditional_month"])
        layout.addSpacing(15)
        layout.addWidget(QLabel("Tamil Star:"))
        layout.addWidget(self.user_input_fields["dob_traditional_star"])
        layout.addStretch()
        return self.traditional_dob_widget  # Return the stored widget

    def display_dob_section(self, form_layout: QFormLayout):
        # Checkbox first
        self.dob_known_checkbox = QCheckBox("Is Date of Birth Known?")
        self.dob_known_checkbox.setChecked(False)  # Default to unknown/hidden
        self.dob_known_checkbox.stateChanged.connect(self.toggle_dob_details)
        form_layout.addRow(self.dob_known_checkbox)  # Add checkbox spanning row

        # Main container for all DOB fields
        self.dob_details_widget = QWidget()
        main_dob_layout = QVBoxLayout(self.dob_details_widget)
        main_dob_layout.setContentsMargins(0, 0, 0, 0)

        # --- Gregorian DOB ---
        gregorian_dob_widget = self._create_gregorian_dob_widget()
        main_dob_layout.addWidget(QLabel("Gregorian DOB:"))  # Add sub-label
        main_dob_layout.addWidget(gregorian_dob_widget)
        # --- End Gregorian DOB ---

        main_dob_layout.addSpacing(10)  # Space between Gregorian and Traditional

        # --- Traditional DOB ---
        # Store the label reference
        self.traditional_dob_label = QLabel("Traditional DOB:")
        traditional_dob_widget = (
            self._create_traditional_dob_widget()
        )  # Creates and stores self.traditional_dob_widget
        main_dob_layout.addWidget(self.traditional_dob_label)  # Add sub-label
        main_dob_layout.addWidget(traditional_dob_widget)
        # --- End Traditional DOB ---

        # Main label for the section
        self.dob_details_label = QLabel("<b>Date of Birth Details:</b>")
        form_layout.addRow(self.dob_details_label, self.dob_details_widget)

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
        # Store the widget reference
        self.traditional_dod_widget = QWidget()
        traditional_dod_layout = QHBoxLayout(self.traditional_dod_widget)
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
        # Store the label reference
        self.traditional_dod_label = QLabel("Traditional DoD:")
        main_dod_layout.addWidget(self.traditional_dod_label)  # Add sub-label
        main_dod_layout.addWidget(self.traditional_dod_widget)  # Add the widget itself
        # --- End Traditional DoD ---

        self.dod_label = QLabel(
            "<b>Date of Death Details:</b>"
        )  # Main label for the section
        form_layout.addRow(self.dod_label, self.dod_fields_widget)

    # --- Toggle Visibility Methods ---

    def toggle_dod_fields(self):
        """Shows/hides the entire DoD section based on 'Is Alive' checkbox."""
        if self.dod_label and self.dod_fields_widget:
            is_alive = self.user_input_fields["IsAlive"].isChecked()
            visible = not is_alive  # Show if NOT alive
            self.dod_label.setVisible(visible)
            self.dod_fields_widget.setVisible(visible)
            # Note: Traditional DOD fields are *inside* dod_fields_widget,
            # so they are hidden/shown along with it. Their specific visibility
            # based on culture is set initially and doesn't need to change here.

    def toggle_dob_details(self):
        """Shows/hides DOB fields based on 'DOB known' checkbox."""
        if (
            self.dob_details_label
            and self.dob_details_widget
            and self.dob_known_checkbox
        ):
            is_known = self.dob_known_checkbox.isChecked()
            self.dob_details_label.setVisible(is_known)
            self.dob_details_widget.setVisible(is_known)

    def toggle_traditional_dob_visibility(self):
        """Shows/hides traditional DOB fields based *only* on culture setting."""
        if self.traditional_dob_label and self.traditional_dob_widget:
            self.traditional_dob_label.setVisible(self.show_traditional_dates)
            self.traditional_dob_widget.setVisible(self.show_traditional_dates)

    def toggle_traditional_dod_visibility(self):
        """Shows/hides traditional DOD fields based *only* on culture setting."""
        # Visibility of the parent DOD section is handled by toggle_dod_fields.
        if self.traditional_dod_label and self.traditional_dod_widget:
            self.traditional_dod_label.setVisible(self.show_traditional_dates)
            self.traditional_dod_widget.setVisible(self.show_traditional_dates)

    # --- Save Action ---
    def save_new_member(self):
        """Gathers data from fields, calls handler to validate and create, handles result."""
        user_input_values = {}

        # --- Gather Data (Raw values) ---
        user_input_values["name"] = self.user_input_fields["name"].text().strip()
        # Basic check for name remains here as it's UI-specific feedback
        if not user_input_values["name"]:
            QMessageBox.warning(
                self, "Input Required", "The 'Name' field cannot be empty."
            )
            self.user_input_fields["name"].setFocus()
            return

        user_input_values["nicknames"] = (
            self.user_input_fields["nicknames"].text().strip()
        )
        user_input_values["gender"] = self.user_input_fields["gender"].currentText()

        # DOB gathering based on 'known' checkbox
        if self.dob_known_checkbox.isChecked():
            # Gregorian DOB
            user_input_values["dob_date"] = self.user_input_fields["dob_date"].value()
            user_input_values["dob_month"] = self.user_input_fields["dob_month"].value()
            user_input_values["dob_year"] = self.user_input_fields["dob_year"].value()

            # Traditional DOB (only if culture enabled and fields were visible)
            if self.show_traditional_dates:
                user_input_values["dob_traditional_month"] = self.user_input_fields[
                    "dob_traditional_month"
                ].currentText()
                user_input_values["dob_traditional_star"] = self.user_input_fields[
                    "dob_traditional_star"
                ].currentText()

        # IsAlive status
        is_alive = self.user_input_fields["IsAlive"].isChecked()
        user_input_values["IsAlive"] = is_alive

        # DoD (only if not alive) - Pass raw values
        if not is_alive:
            user_input_values["dod_date"] = self.user_input_fields["dod_date"].value()
            user_input_values["dod_month"] = self.user_input_fields["dod_month"].value()
            user_input_values["dod_year"] = self.user_input_fields["dod_year"].value()

            # Traditional DoD (only if culture enabled and fields were visible)
            if self.show_traditional_dates:
                user_input_values["dod_traditional_month"] = self.user_input_fields[
                    "dod_traditional_month"
                ].currentText()
                user_input_values["dod_traditional_paksham"] = self.user_input_fields[
                    "dod_traditional_paksham"
                ].currentText()
                user_input_values["dod_traditional_thithi"] = self.user_input_fields[
                    "dod_traditional_thithi"
                ].currentText()

        # --- Call Handler to Create and Validate ---
        try:
            print("Attempting to save new member with data:", user_input_values)
            member_id, error_message = self.family_tree_handler.create_node(
                user_input_values
            )

            if error_message:
                # Validation or creation failed, show the error from the handler
                QMessageBox.warning(self, "Validation Error", error_message)
                # Keep the dialog open for correction
            else:
                # Success!
                print(
                    f"Member '{user_input_values['name']}' created with ID: {member_id}"
                )
                # Trigger re-render in the main GUI
                self.family_tree_gui.re_render_tree()
                QMessageBox.information(
                    self,
                    "Success",
                    f"Member '{user_input_values['name']}' added successfully!",
                )
                self.accept()  # Close the dialog successfully

        except Exception as e:
            # Catch unexpected errors during the handler call itself
            print(f"Unexpected error during create_node call: {e}")
            # Ensure logger is available or handle logging appropriately
            # logger.exception("Unexpected error in save_new_member calling create_node")
            QMessageBox.critical(
                self, "Save Error", f"An unexpected error occurred:\n{e}"
            )
            # Don't close the dialog on unexpected error


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

import logging

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)
from utils import ProtoUtility

# Get a logger instance for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# --- AddDetailsForm ---
class AddPersonDialog(QDialog):
    # Modified constructor to accept culture setting
    def __init__(
        self,
        family_tree_handler,
        family_tree_gui,
        is_indian_culture,
        member_id_to_edit=None,
    ):
        super().__init__()
        self.ft_handler = family_tree_handler
        self.family_tree_gui = family_tree_gui  # Keep reference to main GUI
        self.show_traditional_dates = is_indian_culture  # Store culture flag

        self.member_id_to_edit = member_id_to_edit  # Store the ID if editing
        self.is_edit_mode = member_id_to_edit is not None
        self.user_input_fields = {}  # Store input widgets
        self.newly_created_member_id = None  # To store ID of newly created member

        # Widgets that need state toggling
        self.dod_section_widget = None  # Overall container for DoD, toggled by IsAlive
        self.dod_section_label = None  # Label for the overall DoD section
        self.dob_details_widget = None
        self.dob_details_label = None
        self.dob_known_checkbox = None
        self.dod_known_checkbox = None  # New checkbox for DoD known
        self.dod_input_fields_container = None  # Container for actual DoD date inputs

        # Widgets for traditional dates (to toggle visibility)
        self.traditional_dob_widget = None
        self.traditional_dob_label = None
        self.traditional_dod_widget = None
        self.traditional_dod_label = None

        self.save_button = None  # Reference to save button for text change

        # Set title based on mode
        if self.is_edit_mode:
            self.setWindowTitle(f"✏️ Edit Family Member (ID: {self.member_id_to_edit})")
        else:
            self.setWindowTitle("➕ Add New Family Member")

        self.setMinimumWidth(500)  # Set a minimum width
        self.init_ui()

        # If in edit mode, populate fields *after* UI is created
        if self.is_edit_mode:
            self.populate_fields_for_edit()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.setRowWrapPolicy(
            QFormLayout.RowWrapPolicy.WrapLongRows
        )  # Wrap long rows

        # --- Create Fields ---
        self.display_name_field(form_layout)
        # Optionally disable name editing if ID is based on it or for other reasons
        # if self.is_edit_mode:
        #     self.user_input_fields["name"].setReadOnly(True)
        #     self.user_input_fields["name"].setToolTip("Name cannot be changed after creation.")
        self.display_nicknames_field(form_layout)
        self.display_gender_field(form_layout)
        self.display_dob_section(form_layout)
        self.display_is_alive_field(form_layout)
        self.display_dod_field(form_layout)  # Includes Gregorian and Traditional

        main_layout.addLayout(form_layout)

        # --- Buttons ---
        button_layout = QHBoxLayout()
        button_layout.addStretch()  # Push buttons to the right

        # Set text based on mode
        # Create and store reference to save button
        self.save_button = QPushButton()
        self.save_button.setText(
            "💾 Update Member" if self.is_edit_mode else "💾 Save Member"
        )
        self.save_button.clicked.connect(self.save_member_data)
        self.save_button.setDefault(True)  # Allow Enter key to trigger save

        cancel_button = QPushButton("❌ Cancel")
        cancel_button.clicked.connect(self.reject)  # Close dialog without saving

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(cancel_button)
        main_layout.addLayout(button_layout)

        # --- Initial State ---
        # These toggles need to run AFTER potential population in edit mode
        # We call them here and again after populating if editing
        self.toggle_dob_details()
        self.toggle_dod_section_visibility()  # Renamed from toggle_dod_fields
        self.toggle_dod_input_fields_visibility()  # New call for DoD known
        self.toggle_traditional_dob_visibility()
        self.toggle_traditional_dod_visibility()  # For traditional DoD part

    # --- Field Creation Methods (Helper functions for init_ui) ---

    def display_name_field(self, form_layout: QFormLayout):
        self.user_input_fields["name"] = QLineEdit()
        self.user_input_fields["name"].setPlaceholderText("Name")
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
        valid_genders = ProtoUtility.get_enum_values_from_proto_schema("Gender")
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

        valid_months = ProtoUtility.get_enum_values_from_proto_schema("TamilMonth")
        valid_stars = ProtoUtility.get_enum_values_from_proto_schema("TamilStar")

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
        self.user_input_fields["IsAlive"].stateChanged.connect(
            self.toggle_dod_section_visibility
        )
        form_layout.addRow(self.user_input_fields["IsAlive"])  # Checkbox spans row

    def display_dod_field(self, form_layout: QFormLayout):
        # self.dod_section_widget is the main container for the entire DoD section (label + inputs)
        # Its visibility is controlled by the "IsAlive" checkbox.
        self.dod_section_widget = QWidget()
        dod_section_layout = QVBoxLayout(self.dod_section_widget)
        dod_section_layout.setContentsMargins(0, 0, 0, 0)

        # 1. "Is Date of Death Known?" Checkbox
        self.dod_known_checkbox = QCheckBox("Is Date of Death Known?")
        self.dod_known_checkbox.setChecked(False)  # Default to unknown
        self.dod_known_checkbox.stateChanged.connect(
            self.toggle_dod_input_fields_visibility
        )
        dod_section_layout.addWidget(self.dod_known_checkbox)

        # 2. Container for the actual DoD input fields (Gregorian, Traditional)
        # Its visibility is controlled by dod_known_checkbox.
        self.dod_input_fields_container = QWidget()
        dod_input_fields_layout = QVBoxLayout(self.dod_input_fields_container)
        dod_input_fields_layout.setContentsMargins(0, 0, 0, 0)

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
        dod_input_fields_layout.addWidget(QLabel("Gregorian DoD:"))
        dod_input_fields_layout.addWidget(gregorian_dod_widget)
        # --- End Gregorian DoD ---

        # --- Traditional DoD ---
        # Store the widget reference
        self.traditional_dod_widget = QWidget()
        traditional_dod_layout = QHBoxLayout(self.traditional_dod_widget)
        traditional_dod_layout.setContentsMargins(0, 0, 0, 0)

        valid_months = ProtoUtility.get_enum_values_from_proto_schema("TamilMonth")
        valid_paksham = ProtoUtility.get_enum_values_from_proto_schema("Paksham")
        valid_thithi = ProtoUtility.get_enum_values_from_proto_schema("Thithi")

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
        dod_input_fields_layout.addSpacing(
            10
        )  # Space between Gregorian and Traditional
        dod_input_fields_layout.addWidget(self.traditional_dod_label)
        dod_input_fields_layout.addWidget(self.traditional_dod_widget)
        # --- End Traditional DoD ---

        dod_section_layout.addWidget(
            self.dod_input_fields_container
        )  # Add input fields container to section

        self.dod_section_label = QLabel(
            "<b>Date of Death Details:</b>"
        )  # Main label for the section
        form_layout.addRow(self.dod_section_label, self.dod_section_widget)

    # --- Add method to populate fields when editing ---
    def populate_fields_for_edit(self):
        """Populates the form fields with data from the member being edited."""
        if not self.is_edit_mode or not self.member_id_to_edit:
            return  # Should not happen if called correctly

        # Fetch member data
        member = self.ft_handler.query_member(self.member_id_to_edit)
        # FIXME: I dont expect invalid member Id as this will be called from double click only

        # --- Populate Basic Fields ---
        self.user_input_fields["name"].setText(member.name)
        self.user_input_fields["nicknames"].setText(", ".join(member.nicknames))

        # Gender: Find the index corresponding to the enum name
        gender_name = ProtoUtility.get_gender_name(member.gender)
        gender_index = self.user_input_fields["gender"].findText(gender_name)
        if gender_index != -1:
            self.user_input_fields["gender"].setCurrentIndex(gender_index)
        else:
            # Fallback if enum name not found (e.g., GENDER_UNKNOWN)
            unknown_index = self.user_input_fields["gender"].findText("GENDER_UNKNOWN")
            if unknown_index != -1:
                self.user_input_fields["gender"].setCurrentIndex(unknown_index)

        # --- Populate DOB ---
        # Check if Gregorian DOB exists
        if member.HasField("date_of_birth") and member.date_of_birth.year > 0:
            self.dob_known_checkbox.setChecked(True)
            self.user_input_fields["dob_date"].setValue(member.date_of_birth.date)
            self.user_input_fields["dob_month"].setValue(member.date_of_birth.month)
            self.user_input_fields["dob_year"].setValue(member.date_of_birth.year)
        else:
            self.dob_known_checkbox.setChecked(
                False
            )  # Ensure fields are hidden if no DOB

        # Check if Traditional DOB exists (only if culture is enabled)
        if self.show_traditional_dates and member.HasField("traditional_date_of_birth"):
            # Month
            month_name = ProtoUtility.get_month_name(
                member.traditional_date_of_birth.month
            )
            month_index = self.user_input_fields["dob_traditional_month"].findText(
                month_name
            )
            if month_index != -1:
                self.user_input_fields["dob_traditional_month"].setCurrentIndex(
                    month_index
                )
            # Star
            star_name = ProtoUtility.get_star_name(
                member.traditional_date_of_birth.star
            )
            star_index = self.user_input_fields["dob_traditional_star"].findText(
                star_name
            )
            if star_index != -1:
                self.user_input_fields["dob_traditional_star"].setCurrentIndex(
                    star_index
                )

        # --- Populate IsAlive and DOD ---
        self.user_input_fields["IsAlive"].setChecked(member.alive)
        self.toggle_dod_section_visibility()  # Show/hide entire DoD section

        if not member.alive:
            # If person is not alive, check if DoD data actually exists in proto
            dod_data_exists_in_proto = (
                member.HasField("date_of_death") and member.date_of_death.year > 0
            )
            self.dod_known_checkbox.setChecked(dod_data_exists_in_proto)
            self.toggle_dod_input_fields_visibility()  # Show/hide actual input fields

            if dod_data_exists_in_proto:  # Only populate if data exists
                # Populate Gregorian DOD
                self.user_input_fields["dod_date"].setValue(member.date_of_death.date)
                self.user_input_fields["dod_month"].setValue(member.date_of_death.month)
                self.user_input_fields["dod_year"].setValue(member.date_of_death.year)

                # Populate Traditional DOD (only if culture is enabled and data exists)
                if self.show_traditional_dates and member.HasField(
                    "traditional_date_of_death"
                ):
                    # Month
                    month_name = ProtoUtility.get_month_name(
                        member.traditional_date_of_death.month
                    )
                    month_index = self.user_input_fields[
                        "dod_traditional_month"
                    ].findText(month_name)
                    if month_index != -1:
                        self.user_input_fields["dod_traditional_month"].setCurrentIndex(
                            month_index
                        )
                    # Paksham
                    paksham_name = ProtoUtility.get_paksham_name(
                        member.traditional_date_of_death.paksham
                    )
                    paksham_index = self.user_input_fields[
                        "dod_traditional_paksham"
                    ].findText(paksham_name)
                    if paksham_index != -1:
                        self.user_input_fields[
                            "dod_traditional_paksham"
                        ].setCurrentIndex(paksham_index)
                    # Thithi
                    thithi_name = ProtoUtility.get_thithi_name(
                        member.traditional_date_of_death.thithi
                    )
                    thithi_index = self.user_input_fields[
                        "dod_traditional_thithi"
                    ].findText(thithi_name)
                    if thithi_index != -1:
                        self.user_input_fields[
                            "dod_traditional_thithi"
                        ].setCurrentIndex(thithi_index)

        # Ensure visibility toggles are correct after population
        self.toggle_dob_details()
        # toggle_dod_section_visibility was called after setting IsAlive
        # self.toggle_dod_input_fields_visibility() # Called if not alive
        self.toggle_traditional_dob_visibility()
        self.toggle_traditional_dod_visibility()

    # --- Toggle Visibility Methods ---

    def toggle_dod_section_visibility(self):
        """Shows/hides the entire DoD section based on 'Is Alive' checkbox."""
        if self.dod_section_label and self.dod_section_widget:
            is_alive = self.user_input_fields["IsAlive"].isChecked()
            visible = not is_alive  # Show if NOT alive
            self.dod_section_label.setVisible(visible)
            self.dod_section_widget.setVisible(visible)
            if visible:  # If the DoD section is now visible,
                # ensure its sub-components (input fields, traditional part) are correctly set
                self.toggle_dod_input_fields_visibility()

    def toggle_dod_input_fields_visibility(self):
        """Shows/hides the actual DoD input fields based on 'dod_known_checkbox'."""
        if self.dod_input_fields_container and self.dod_known_checkbox:
            # Only proceed if the parent dod_section_widget is itself visible
            if self.dod_section_widget and self.dod_section_widget.isVisible():
                is_known = self.dod_known_checkbox.isChecked()
                self.dod_input_fields_container.setVisible(is_known)
                if is_known:  # If the input fields are now visible,
                    self.toggle_traditional_dod_visibility()  # ensure traditional part is correct
            else:  # If parent section is hidden, hide these too
                self.dod_input_fields_container.setVisible(False)

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
        # Visibility of the parent dod_section_widget is handled by toggle_dod_section_visibility.
        # Visibility of the parent dod_input_fields_container is handled by toggle_dod_input_fields_visibility.
        if self.traditional_dod_label and self.traditional_dod_widget:
            # Only show if culture is enabled AND its direct parent (dod_input_fields_container) is visible
            parent_visible = (
                self.dod_input_fields_container
                and self.dod_input_fields_container.isVisible()
            )
            self.traditional_dod_label.setVisible(
                self.show_traditional_dates and parent_visible
            )
            self.traditional_dod_widget.setVisible(
                self.show_traditional_dates and parent_visible
            )

    def _gather_values_to_save(self):
        user_input_values = {}

        # --- Gather Data (Raw values - same logic as before) ---
        user_input_values["name"] = self.user_input_fields["name"].text().strip()
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

        # DOB gathering
        if self.dob_known_checkbox.isChecked():
            user_input_values["dob_date"] = self.user_input_fields["dob_date"].value()
            user_input_values["dob_month"] = self.user_input_fields["dob_month"].value()
            user_input_values["dob_year"] = self.user_input_fields["dob_year"].value()
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

        # DoD gathering
        if (
            not is_alive and self.dod_known_checkbox.isChecked()
        ):  # Only gather if not alive AND known
            user_input_values["dod_date"] = self.user_input_fields["dod_date"].value()
            user_input_values["dod_month"] = self.user_input_fields["dod_month"].value()
            user_input_values["dod_year"] = self.user_input_fields["dod_year"].value()
            if self.show_traditional_dates:  # And if traditional dates are enabled
                if (
                    self.traditional_dod_widget.isVisible()
                ):  # And if the widget is actually visible
                    user_input_values["dod_traditional_month"] = self.user_input_fields[
                        "dod_traditional_month"
                    ].currentText()
                    user_input_values["dod_traditional_paksham"] = (
                        self.user_input_fields["dod_traditional_paksham"].currentText()
                    )
                    user_input_values["dod_traditional_thithi"] = (
                        self.user_input_fields["dod_traditional_thithi"].currentText()
                    )
        return user_input_values

    # --- Save Action ---
    def save_member_data(self):
        """Gathers data, calls handler to validate and create OR update, handles result."""

        user_input_values = self._gather_values_to_save()
        if not user_input_values:  # Validation in _gather_values_to_save failed
            return
        action_verb = "updation" if self.is_edit_mode else "creation"
        member_name = user_input_values.get("name", "NAME_NOT_AVAILABLE")
        self.newly_created_member_id = None  # Reset
        try:
            if self.is_edit_mode:
                # --- UPDATE ---
                logger.info(
                    f"Attempting to update member {self.member_id_to_edit} with data:",
                    user_input_values,
                )
                success = self.ft_handler.update_member(
                    self.member_id_to_edit, user_input_values
                )
                if success:  # update_member returns bool
                    self.newly_created_member_id = (
                        self.member_id_to_edit
                    )  # For consistency if GUI needs it
            else:
                # --- CREATE ---
                logger.info(
                    f"Attempting to save new member with data: {user_input_values}"
                )
                # create_member now returns the ID or None
                created_id = self.ft_handler.create_member(user_input_values)
                if created_id:
                    self.newly_created_member_id = created_id
                    success = True
                else:
                    success = False

            if success:
                # Success message is now handled by the main GUI's status bar after dialog closes.
                self.accept()  # Close the dialog successfully

            # If not success, an exception might have been raised by the handler, or create_member returned None

        except Exception as e:
            logger.exception(f"Unexpected error during member {action_verb}: {e}")
            QMessageBox.critical(
                self,
                f"{action_verb.capitalize()} Error",
                f"An unexpected error occurred:\n{str(e)}",
            )
            # Don't close the dialog on unexpected error

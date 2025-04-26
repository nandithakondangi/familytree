import os

from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QWidget,
)


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
        # Start browsing in the user's home directory or current directory
        # start_dir = os.path.expanduser("~")
        start_dir = os.getcwd()
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

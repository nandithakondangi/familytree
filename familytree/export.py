import os

from PySide6.QtWidgets import (
    QFileDialog,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from utils_legacy import ResourceUtility


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
        output_file = self.family_tree_handler.get_output_data_file
        if output_file:
            output_dir = os.path.dirname(output_file)
        else:
            output_dir = os.path.dirname(ResourceUtility.get_resource())

        default_dir = os.path.dirname(output_dir)

        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save Family Tree Data",
            os.path.join(default_dir, suggested_name),  # Suggest path and name
            "Protobuf Text Files (*.txtpb);;All Files (*)",
        )
        if file_name:
            try:
                self.family_tree_handler.update_output_data_file(file_name)
                self.family_tree_handler.save_data_to_file()
                self.family_tree_gui.show_status_message(
                    f"Data exported to: {file_name}", 7000
                )
            except Exception as e:
                print(f"Error exporting data: {e}")
                QMessageBox.critical(
                    self, "Export Error", f"Failed to export data:\n{e}"
                )

    def export_graph_to_file(self):
        # Suggest a filename based on input or default
        suggested_name = "family_tree_graph.html"
        # Use handler's default html file path's directory as starting point. Corrected property access.
        default_dir = os.path.dirname(self.family_tree_handler.get_output_html_file)

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
                    self.family_tree_gui.show_status_message(
                        f"Graph exported to: {file_name}", 7000
                    )
                else:
                    # This might happen if display_family_tree fails silently
                    self.family_tree_gui.show_status_message(
                        f"Graph rendered, but file not found: {file_name}", 7000
                    )
            except Exception as e:
                print(f"Error exporting graph: {e}")
                QMessageBox.critical(
                    self, "Export Error", f"Failed to export graph:\n{e}"
                )

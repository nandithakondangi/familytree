import os
import sys

# FIXME: As PySide6 is not getting resolved properly with Bazel
proto_binary_path = f"{os.path.realpath(os.path.dirname(__file__))}/../bazel-bin"
sys.path.append(proto_binary_path)

from family_tree_gui import FamilyTreeGUI
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("DejaVu Sans", 12)
    app.setFont(font)
    app.setStyle("Fusion")
    gui = FamilyTreeGUI()
    gui.show()
    sys.exit(app.exec())

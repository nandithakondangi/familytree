import sys
import time
from family_tree_gui import FamilyTreeGUI
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

if __name__ == "__main__":
    orig_time = time.time()
    app = QApplication(sys.argv)
    print(f"QApplication created in {time.time() - orig_time:.4f} seconds")
    font = QFont("DejaVu Sans", 12)
    app.setFont(font)
    app.setStyle("Fusion")

    start_time = time.time()
    gui = FamilyTreeGUI()
    print(f"FamilyTreeGUI created in {time.time() - start_time:.4f} seconds")
    gui.show()
    print(f"GUI shown in {time.time() - start_time:.4f} seconds")
    sys.exit(app.exec())

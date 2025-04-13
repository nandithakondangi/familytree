import sys
import time
import tempfile
import atexit
import shutil
import os

from family_tree_gui import FamilyTreeGUI
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

# Global variable to hold the temporary directory path
TEMP_DIR_PATH = None


def cleanup_temp_dir():
    """Function to remove the temporary directory."""
    global TEMP_DIR_PATH
    if TEMP_DIR_PATH and os.path.exists(TEMP_DIR_PATH):
        try:
            print(f"Cleaning up temporary directory: {TEMP_DIR_PATH}")
            shutil.rmtree(TEMP_DIR_PATH)
            print("Temporary directory removed successfully.")
        except OSError as e:
            # Handle potential errors during cleanup (e.g., permissions)
            print(
                f"Error removing temporary directory {TEMP_DIR_PATH}: {e}",
                file=sys.stderr,
            )
    else:
        print("Temporary directory already removed or not created.")


def main():
    """Main application function."""
    global TEMP_DIR_PATH

    orig_time = time.time()

    # --- Temporary Directory Setup ---
    try:
        # Create a unique temporary directory
        TEMP_DIR_PATH = tempfile.mkdtemp(prefix="familytree_app_")
        print(f"Created temporary directory: {TEMP_DIR_PATH}")
        # Register the cleanup function to be called on normal program exit
        atexit.register(cleanup_temp_dir)
    except Exception as e:
        print(f"Error creating temporary directory: {e}", file=sys.stderr)
        # Decide how to handle this - exit? proceed without temp dir?
        # For now, let's exit if we can't create the temp dir, as it's needed.
        sys.exit(f"Fatal Error: Could not create temporary directory. {e}")
    # --- End Temporary Directory Setup ---

    app = QApplication(sys.argv)
    print(f"QApplication created in {time.time() - orig_time:.4f} seconds")

    # --- Font and Style ---
    try:
        # Try setting a specific font, fall back if not available
        font = QFont("DejaVu Sans", 11)  # Slightly smaller default size
        if font.family() != "DejaVu Sans":
            print("Warning: DejaVu Sans font not found, using default.")
            font = QFont()  # Use system default
            font.setPointSize(11)
        app.setFont(font)
    except Exception as e:
        print(f"Warning: Could not set application font: {e}")

    # Set style (Fusion is generally good for cross-platform)
    app.setStyle("Fusion")
    # --- End Font and Style ---

    start_time = time.time()
    # Pass the temporary directory path to the GUI
    gui = FamilyTreeGUI(temp_dir_path=TEMP_DIR_PATH)
    print(f"FamilyTreeGUI created in {time.time() - start_time:.4f} seconds")

    gui.show()
    print(f"GUI shown in {time.time() - start_time:.4f} seconds")

    # Start the Qt event loop
    exit_code = app.exec()
    print("Application event loop finished.")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

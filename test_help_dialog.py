"""
Test the Help dialog to make sure it displays correctly
"""
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton
from PySide6.QtCore import Qt

# Import the help dialog code
from src.gui.pyside6_main_window import PySide6MainWindow
from src.database.database_manager import DatabaseManager

def test_help_dialog():
    """Test opening the help dialog"""
    app = QApplication(sys.argv)
    
    # Create main window
    db_manager = DatabaseManager()
    window = PySide6MainWindow(db_manager)
    
    # Show window
    window.show()
    
    # Programmatically trigger help dialog after a short delay
    from PySide6.QtCore import QTimer
    QTimer.singleShot(500, window.show_help_dialog)
    
    print("✓ Application started")
    print("✓ Help dialog should appear in 500ms")
    print("  Click the Close button or press ESC to close the help dialog")
    print("  Then close the main window to exit")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    test_help_dialog()

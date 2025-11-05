#!/usr/bin/env python3
"""
NextAstroTarget - Modern PySide6 Application Entry Point
Astrophotography Target Selection Application with Modern UI

This is the main entry point for the NextAstroTarget application using PySide6.
It handles application initialization, database setup, and modern GUI launching.
"""

import os
import sys
import logging
from pathlib import Path

# Qt imports
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon

# Add src directory to Python path for imports
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

# Import application modules
try:
    from src.utils.logger import setup_logging
    from src.database.database_manager import DatabaseManager
    from src.gui.pyside6_main_window import ModernMainWindow
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)


class NextAstroTargetApp:
    """Main application class for NextAstroTarget with PySide6."""
    
    def __init__(self):
        self.logger = None
        self.db_manager = None
        self.app = None
        self.main_window = None
        
    def initialize(self):
        """Initialize the application."""
        try:
            # Setup logging
            setup_logging()
            self.logger = logging.getLogger(__name__)
            self.logger.info("Starting NextAstroTarget application (PySide6)...")
            
            # Enable high DPI scaling BEFORE creating QApplication
            from PySide6.QtCore import Qt
            from PySide6.QtWidgets import QApplication
            QApplication.setHighDpiScaleFactorRoundingPolicy(
                Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
            )
            
            # Initialize database manager
            self.db_manager = DatabaseManager()
            
            # Initialize Qt Application
            self.app = QApplication(sys.argv)
            self.app.setApplicationName("NextAstroTarget")
            self.app.setOrganizationName("AstroTarget")
            self.app.setApplicationDisplayName("NextAstroTarget - Enhanced Astrophotography Target Selector")
            
            # Set application style
            self.app.setStyle("Fusion")  # Modern cross-platform style
            
            # Windows-specific: Set AppUserModelID for proper taskbar icon grouping
            if sys.platform == 'win32':
                try:
                    import ctypes
                    myappid = 'AstroTarget.NextAstroTarget.App.1.0'  # arbitrary string
                    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
                except Exception as e:
                    self.logger.warning(f"Could not set Windows AppUserModelID: {e}")
            
            # Set window icon if available
            icon_path = "assets/icon.ico"
            if os.path.exists(icon_path):
                try:
                    self.app.setWindowIcon(QIcon(icon_path))
                except Exception as e:
                    self.logger.warning(f"Could not load icon: {e}")
            
            # Create modern main window
            self.main_window = ModernMainWindow(self.db_manager)
            
            # Configure window
            self.main_window.setWindowTitle("NextAstroTarget - Enhanced Astrophotography Target Selector")
            
            # Set initial size and center
            self._setup_window_geometry()
            
            # Show window
            self.main_window.show()
            
            # Bring to front
            self.main_window.raise_()
            self.main_window.activateWindow()
            
            self.logger.info("Application initialized successfully")
            return True
            
        except Exception as e:
            error_msg = f"Failed to initialize application: {e}"
            if self.logger:
                self.logger.error(error_msg)
            else:
                print(error_msg)
            
            # Show error dialog if possible
            try:
                QMessageBox.critical(None, "Initialization Error", error_msg)
            except:
                pass
            
            return False
    
    def _setup_window_geometry(self):
        """Setup window size and position."""
        # Get available screen geometry
        screen = self.app.primaryScreen()
        screen_geometry = screen.availableGeometry()
        
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        
        # Calculate optimal window dimensions (85% of screen size)
        # Increased width by 20%: 1800 * 1.2 = 2160
        window_width = min(int(screen_width * 0.85), 2160)
        window_height = min(int(screen_height * 0.90), 1200)
        
        # Set minimum size
        self.main_window.setMinimumSize(1400, 900)
        
        # Resize window
        self.main_window.resize(window_width, window_height)
        
        # Center on screen
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.main_window.move(x, y)
        
        self.logger.info(
            f"Window sized for screen {screen_width}x{screen_height}: "
            f"Window {window_width}x{window_height} at ({x}, {y})"
        )
    
    def run(self):
        """Run the application main loop."""
        if not self.initialize():
            return False
        
        try:
            self.logger.info("Starting Qt application event loop...")
            exit_code = self.app.exec()
            
            self.logger.info(f"Application exited with code {exit_code}")
            return exit_code == 0
            
        except KeyboardInterrupt:
            self.logger.info("Application interrupted by user")
            return True
            
        except Exception as e:
            error_msg = f"Error during application execution: {e}"
            self.logger.error(error_msg)
            QMessageBox.critical(None, "Application Error", error_msg)
            return False
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources before application exit."""
        try:
            if self.logger:
                self.logger.info("Cleaning up application resources...")
            
            # Close main window
            if self.main_window:
                self.main_window.close()
            
            # Close database connections
            if self.db_manager:
                # Add any cleanup needed for database manager
                pass
            
            if self.logger:
                self.logger.info("Application cleanup completed")
                
        except Exception as e:
            print(f"Error during cleanup: {e}")


def main():
    """Main function - application entry point."""
    try:
        # Change to application directory
        app_dir = Path(__file__).parent
        os.chdir(app_dir)
        
        # Check for test startup parameter
        if len(sys.argv) > 1 and sys.argv[1] == '--test-startup':
            # Test mode - just check if we can initialize without GUI
            try:
                setup_logging()
                from src.database.database_manager import DatabaseManager
                db_manager = DatabaseManager()
                print("Startup test passed (PySide6)")
                sys.exit(0)
            except Exception as e:
                print(f"Startup test failed: {e}")
                sys.exit(1)
        
        # Create and run application
        app = NextAstroTargetApp()
        success = app.run()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        try:
            QMessageBox.critical(None, "Fatal Error", f"A fatal error occurred:\n\n{e}")
        except:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()

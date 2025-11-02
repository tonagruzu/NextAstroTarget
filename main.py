#!/usr/bin/env python3
"""
NextAstroTarget - Main Application Entry Point
Astrophotography Target Selection Application

This is the main entry point for the NextAstroTarget application.
It handles application initialization, database setup, and GUI launching.
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox
import logging
from pathlib import Path

# Add src directory to Python path for imports
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

# Import application modules
try:
    from src.utils.logger import setup_logging
    from src.database.database_manager import DatabaseManager
    from src.gui.enhanced_main_window import EnhancedMainWindow
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)


class NextAstroTargetApp:
    """Main application class for NextAstroTarget."""
    
    def __init__(self):
        self.logger = None
        self.db_manager = None
        self.root = None
        self.main_window = None
        
    def initialize(self):
        """Initialize the application."""
        try:
            # Setup logging
            setup_logging()
            self.logger = logging.getLogger(__name__)
            self.logger.info("Starting NextAstroTarget application...")
            
            # Initialize database manager
            self.db_manager = DatabaseManager()
            
            # Initialize GUI
            self.root = tk.Tk()
            self.root.title("NextAstroTarget - Enhanced Astrophotography Target Selector")
            self.root.geometry("1800x1200")
            self.root.minsize(1400, 900)
            
            # Set window state to ensure proper visibility
            self.root.state('normal')  # Ensure window is not minimized
            
            # Option to start maximized for better visibility (uncomment next line if desired)
            # self.root.state('zoomed')  # Start maximized on Windows
            
            # Set window icon if available
            icon_path = "assets/icon.ico"
            if os.path.exists(icon_path):
                try:
                    self.root.iconbitmap(icon_path)
                except Exception as e:
                    self.logger.warning(f"Could not load icon: {e}")
            
            # Center window on screen
            self._center_window()
            
            # Ensure window is brought to front
            self.root.lift()
            self.root.focus_force()
            
            # Create enhanced main window
            self.main_window = EnhancedMainWindow(self.root, self.db_manager)
            
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
                messagebox.showerror("Initialization Error", error_msg)
            except:
                pass
            
            return False
    
    def _center_window(self):
        """Center the main window on the screen with responsive sizing."""
        self.root.update_idletasks()
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate optimal window dimensions based on screen size
        # Use 85% of screen width and 90% of screen height, but with reasonable limits
        optimal_width = min(max(int(screen_width * 0.85), 1400), 2000)
        optimal_height = min(max(int(screen_height * 0.90), 900), 1400)
        
        # Override with fixed size if we set it specifically for larger screens
        window_width = 1800 if screen_width >= 1800 else optimal_width
        window_height = 1200 if screen_height >= 1200 else optimal_height
        
        # Calculate position to center the window
        x = max(0, (screen_width - window_width) // 2)
        y = max(0, (screen_height - window_height) // 2)
        
        # Set window position and size
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        if self.logger:
            self.logger.info(f"Window sized for screen {screen_width}x{screen_height}: "
                            f"Window {window_width}x{window_height} at ({x}, {y})")
    
    def run(self):
        """Run the application main loop."""
        if not self.initialize():
            return False
        
        try:
            self.logger.info("Starting GUI main loop...")
            self.root.mainloop()
            return True
            
        except KeyboardInterrupt:
            self.logger.info("Application interrupted by user")
            return True
            
        except Exception as e:
            error_msg = f"Error during application execution: {e}"
            self.logger.error(error_msg)
            messagebox.showerror("Application Error", error_msg)
            return False
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources before application exit."""
        try:
            if self.logger:
                self.logger.info("Cleaning up application resources...")
            
            # Close database connections
            if self.db_manager:
                # Add any cleanup needed for database manager
                pass
            
            # Destroy GUI
            if self.root:
                self.root.quit()
                self.root.destroy()
            
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
                print("Startup test passed")
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
        try:
            messagebox.showerror("Fatal Error", f"A fatal error occurred:\n\n{e}")
        except:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()
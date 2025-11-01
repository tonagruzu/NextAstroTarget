"""
Main GUI window for NextAstroTarget application.
Handles navigation between different application screens.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Optional

from src.database.database_manager import DatabaseManager
from src.gui.database_init_gui import DatabaseInitGUI
from src.gui.target_selection_gui import TargetSelectionGUI


class MainWindow:
    """Main application window with navigation between different screens."""
    
    def __init__(self, root: tk.Tk, db_manager: DatabaseManager):
        self.root = root
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        
        # Current screen tracking
        self.current_screen = None
        self.screens = {}
        
        # Setup GUI
        self.setup_gui()
        self.check_database_and_navigate()
    
    def setup_gui(self):
        """Set up the main GUI structure."""
        # Configure root window
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        
        # Create header frame
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Application title
        title_label = ttk.Label(
            self.header_frame,
            text="NextAstroTarget",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # Subtitle
        subtitle_label = ttk.Label(
            self.header_frame,
            text="Astrophotography Target Selection",
            font=("Arial", 10)
        )
        subtitle_label.grid(row=1, column=0, sticky=tk.W)
        
        # Menu frame
        self.menu_frame = ttk.Frame(self.header_frame)
        self.menu_frame.grid(row=0, column=1, sticky=tk.E)
        
        # Menu buttons
        self.create_menu_buttons()
        
        # Content frame for different screens
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(0, weight=1)
        
        # Status bar
        self.status_bar = ttk.Label(
            self.main_frame,
            text="Ready",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def create_menu_buttons(self):
        """Create menu buttons for navigation."""
        # Database Init button
        self.db_init_button = ttk.Button(
            self.menu_frame,
            text="Database Init",
            command=self.show_database_init
        )
        self.db_init_button.grid(row=0, column=0, padx=(0, 5))
        
        # Target Selection button
        self.target_selection_button = ttk.Button(
            self.menu_frame,
            text="Target Selection",
            command=self.show_target_selection
        )
        self.target_selection_button.grid(row=0, column=1, padx=5)
        
        # Refresh Database button
        self.refresh_button = ttk.Button(
            self.menu_frame,
            text="Refresh DB",
            command=self.refresh_database
        )
        self.refresh_button.grid(row=0, column=2, padx=(5, 0))
    
    def check_database_and_navigate(self):
        """Check if database exists and navigate to appropriate screen."""
        if self.db_manager.database_exists():
            self.logger.info("Database exists, navigating to target selection")
            self.update_status("Database ready - Select your next astrophotography target")
            self.show_target_selection()
        else:
            self.logger.info("Database not found, navigating to initialization screen")
            self.update_status("Database not found - Please initialize the database first")
            self.show_database_init()
    
    def show_database_init(self):
        """Show the database initialization screen."""
        self.logger.info("Showing database initialization screen")
        
        if 'db_init' not in self.screens:
            self.screens['db_init'] = DatabaseInitGUI(
                self.content_frame,
                self.db_manager,
                self.on_database_initialized
            )
        
        self._switch_screen('db_init')
        self.update_status("Database Initialization")
    
    def show_target_selection(self):
        """Show the target selection screen."""
        if not self.db_manager.database_exists():
            messagebox.showwarning(
                "Database Required",
                "Please initialize the database first before selecting targets."
            )
            self.show_database_init()
            return
        
        self.logger.info("Showing target selection screen")
        
        if 'target_selection' not in self.screens:
            self.screens['target_selection'] = TargetSelectionGUI(
                self.content_frame,
                self.db_manager
            )
        
        self._switch_screen('target_selection')
        self.update_status("Target Selection - Find your next astrophotography target")
    
    def refresh_database(self):
        """Refresh/reinitialize the database."""
        result = messagebox.askyesno(
            "Refresh Database",
            "This will reinitialize the database with fresh data from the Excel file.\n"
            "All existing data will be replaced.\n\n"
            "Are you sure you want to continue?"
        )
        
        if result:
            self.logger.info("User requested database refresh")
            # Clear existing screens to force recreation
            if 'target_selection' in self.screens:
                self.screens['target_selection'].destroy()
                del self.screens['target_selection']
            
            # Show database init screen
            self.show_database_init()
    
    def _switch_screen(self, screen_name: str):
        """Switch to a different screen."""
        # Hide current screen
        if self.current_screen and self.current_screen in self.screens:
            self.screens[self.current_screen].hide()
        
        # Show new screen
        if screen_name in self.screens:
            self.screens[screen_name].show()
            self.current_screen = screen_name
    
    def on_database_initialized(self, success: bool):
        """Callback when database initialization is completed."""
        if success:
            self.logger.info("Database initialization successful")
            messagebox.showinfo(
                "Database Initialized",
                "Database has been successfully initialized!\n"
                "You can now proceed to target selection."
            )
            self.update_status("Database initialized successfully")
            
            # Clear target selection screen to force reload
            if 'target_selection' in self.screens:
                self.screens['target_selection'].destroy()
                del self.screens['target_selection']
            
            # Navigate to target selection
            self.show_target_selection()
        else:
            self.logger.error("Database initialization failed")
            self.update_status("Database initialization failed")
            messagebox.showerror(
                "Initialization Failed",
                "Database initialization failed. Please check the logs for details."
            )
    
    def update_status(self, message: str):
        """Update the status bar message."""
        self.status_bar.config(text=message)
        self.root.update_idletasks()
    
    def on_closing(self):
        """Handle application closing event."""
        self.logger.info("Application closing requested")
        
        # Ask for confirmation if needed
        result = messagebox.askyesno(
            "Exit Application",
            "Are you sure you want to exit NextAstroTarget?"
        )
        
        if result:
            self.logger.info("Application closing confirmed")
            self.root.quit()



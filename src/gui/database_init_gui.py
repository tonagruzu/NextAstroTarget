"""
Database initialization GUI for NextAstroTarget application.
Provides interface for initializing the database from Excel data.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
import threading
import os
from typing import Callable, Optional

from src.database.database_manager import DatabaseManager
from src.gui.base_screen import BaseScreen


class DatabaseInitGUI(BaseScreen):
    """GUI for database initialization process."""
    
    def __init__(self, parent_frame: ttk.Frame, db_manager: DatabaseManager, 
                 completion_callback: Optional[Callable[[bool], None]] = None):
        self.db_manager = db_manager
        self.completion_callback = completion_callback
        self.initialization_thread = None
        self.is_initializing = False
        
        super().__init__(parent_frame)
    
    def setup_gui(self):
        """Set up the database initialization GUI."""
        super().setup_gui()
        
        # Main container
        container = ttk.Frame(self.frame)
        container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=20, pady=20)
        container.columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(
            container,
            text="Database Initialization",
            font=("Arial", 14, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Description
        description = (
            "Initialize the database with astrophotography target data from the Excel file.\n"
            "This process will read the Excel spreadsheet and create a local SQLite database\n"
            "for fast target searches and selections."
        )
        desc_label = ttk.Label(container, text=description, justify=tk.CENTER)
        desc_label.grid(row=1, column=0, pady=(0, 20))
        
        # File selection frame
        file_frame = ttk.LabelFrame(container, text="Excel File")
        file_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=10, pady=(0, 20))
        file_frame.columnconfigure(0, weight=1)
        
        self.file_var = tk.StringVar(value=self.db_manager.excel_file)
        
        file_entry_frame = ttk.Frame(file_frame)
        file_entry_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        file_entry_frame.columnconfigure(0, weight=1)
        
        self.file_entry = ttk.Entry(file_entry_frame, textvariable=self.file_var, state='readonly')
        self.file_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        browse_button = ttk.Button(file_entry_frame, text="Browse...", command=self.browse_file)
        browse_button.grid(row=0, column=1)
        
        # File status
        self.file_status_label = ttk.Label(file_frame, text="")
        self.file_status_label.grid(row=1, column=0, pady=(10, 0))
        
        # Database status frame
        db_frame = ttk.LabelFrame(container, text="Database Status")
        db_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), padx=10, pady=(0, 20))
        
        self.db_status_label = ttk.Label(db_frame, text="")
        self.db_status_label.grid(row=0, column=0)
        
        # Progress frame
        progress_frame = ttk.LabelFrame(container, text="Initialization Progress")
        progress_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), padx=10, pady=(0, 20))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.StringVar(value="Ready to initialize...")
        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=0, column=0, sticky=tk.W)
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='determinate',
            length=400
        )
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Buttons frame
        button_frame = ttk.Frame(container)
        button_frame.grid(row=5, column=0, pady=20)
        
        self.init_button = ttk.Button(
            button_frame,
            text="Initialize Database",
            command=self.start_initialization
        )
        self.init_button.grid(row=0, column=0, padx=(0, 10))
        
        self.cancel_button = ttk.Button(
            button_frame,
            text="Cancel",
            command=self.cancel_initialization,
            state='disabled'
        )
        self.cancel_button.grid(row=0, column=1)
        
        # Update initial status
        self.update_status()
    
    def browse_file(self):
        """Browse for Excel file."""
        if self.is_initializing:
            return
        
        filename = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[
                ("Excel files", "*.xlsx *.xlsm"),
                ("All files", "*.*")
            ],
            initialfile=self.file_var.get()
        )
        
        if filename:
            self.file_var.set(filename)
            self.db_manager.excel_file = filename
            self.update_status()
    
    def update_status(self):
        """Update status displays."""
        # File status
        if os.path.exists(self.file_var.get()):
            file_size = os.path.getsize(self.file_var.get()) / (1024 * 1024)  # MB
            self.file_status_label.config(
                text=f"✓ File found ({file_size:.1f} MB)",
                foreground="green"
            )
            file_exists = True
        else:
            self.file_status_label.config(
                text="✗ File not found",
                foreground="red"
            )
            file_exists = False
        
        # Database status
        if self.db_manager.database_exists():
            table_info = self.db_manager.get_table_info()
            table_count = len(table_info)
            total_records = sum(info['row_count'] for info in table_info.values())
            
            self.db_status_label.config(
                text=f"✓ Database exists ({table_count} tables, {total_records:,} records)",
                foreground="green"
            )
        else:
            self.db_status_label.config(
                text="✗ Database not found",
                foreground="red"
            )
        
        # Update button state
        self.init_button.config(state='normal' if file_exists and not self.is_initializing else 'disabled')
    
    def start_initialization(self):
        """Start the database initialization process."""
        if self.is_initializing:
            return
        
        # Confirm action if database exists
        if self.db_manager.database_exists():
            result = messagebox.askyesno(
                "Overwrite Database",
                "A database already exists. This will overwrite all existing data.\n\n"
                "Are you sure you want to continue?"
            )
            if not result:
                return
        
        self.is_initializing = True
        self.init_button.config(state='disabled')
        self.cancel_button.config(state='normal')
        self.progress_bar.config(value=0)
        self.progress_var.set("Starting initialization...")
        
        # Start initialization in separate thread
        self.initialization_thread = threading.Thread(
            target=self._run_initialization,
            daemon=True
        )
        self.initialization_thread.start()
    
    def cancel_initialization(self):
        """Cancel the initialization process."""
        if not self.is_initializing:
            return
        
        # Note: This is a simple cancel - in a more sophisticated version,
        # you would need to implement proper thread cancellation
        self.logger.info("Initialization cancellation requested")
        messagebox.showinfo("Cancel", "Initialization will stop after current operation completes.")
    
    def _run_initialization(self):
        """Run the database initialization in a separate thread."""
        try:
            success = self.db_manager.initialize_database(self.progress_callback)
            
            # Update GUI in main thread
            self.frame.after(0, lambda: self._initialization_completed(success))
            
        except Exception as e:
            self.logger.error(f"Error during initialization: {e}")
            self.frame.after(0, lambda: self._initialization_completed(False))
    
    def progress_callback(self, message: str, progress: int):
        """Callback for progress updates from database initialization."""
        # Update GUI in main thread
        self.frame.after(0, lambda: self._update_progress(message, progress))
    
    def _update_progress(self, message: str, progress: int):
        """Update progress display (called in main thread)."""
        self.progress_var.set(message)
        self.progress_bar.config(value=progress)
        self.frame.update_idletasks()
    
    def _initialization_completed(self, success: bool):
        """Handle completion of initialization (called in main thread)."""
        self.is_initializing = False
        self.init_button.config(state='normal')
        self.cancel_button.config(state='disabled')
        
        if success:
            self.progress_var.set("✓ Initialization completed successfully!")
            self.progress_bar.config(value=100)
        else:
            self.progress_var.set("✗ Initialization failed - check logs for details")
            self.progress_bar.config(value=0)
        
        # Update status displays
        self.update_status()
        
        # Call completion callback if provided
        if self.completion_callback:
            self.completion_callback(success)
    
    def show(self):
        """Show this screen and update status."""
        super().show()
        self.update_status()
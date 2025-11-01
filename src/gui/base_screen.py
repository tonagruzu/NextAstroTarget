"""
Base classes for GUI screens in NextAstroTarget application.
"""

import tkinter as tk
from tkinter import ttk
import logging


class BaseScreen:
    """Base class for application screens."""
    
    def __init__(self, parent_frame: ttk.Frame):
        self.parent_frame = parent_frame
        self.frame = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.setup_gui()
    
    def setup_gui(self):
        """Set up the screen GUI. Override in subclasses."""
        self.frame = ttk.Frame(self.parent_frame)
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
    
    def show(self):
        """Show this screen."""
        if self.frame:
            self.frame.tkraise()
    
    def hide(self):
        """Hide this screen."""
        # Note: We don't actually hide frames in tkinter, just raise others
        pass
    
    def destroy(self):
        """Destroy this screen."""
        if self.frame:
            self.frame.destroy()
            self.frame = None
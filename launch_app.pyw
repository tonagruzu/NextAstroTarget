"""
NextAstroTarget GUI Launcher (No Console)
This .pyw file launches the application without showing a console window.
Simply double-click this file to run the application.
"""

if __name__ == "__main__":
    import sys
    import os
    
    # Ensure we're in the correct directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Import and run the main application
    from src.gui.pyside6_main_window import main
    
    sys.exit(main())

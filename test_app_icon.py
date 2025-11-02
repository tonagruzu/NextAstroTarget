#!/usr/bin/env python3
"""
Test the NextAstroTarget application icon
Verifies that the icon file is properly formatted and loads correctly.
"""

import os
import tkinter as tk
from PIL import Image
import sys

def test_icon():
    """Test the application icon."""
    print("🔍 Testing NextAstroTarget Application Icon...")
    
    icon_path = "assets/icon.ico"
    
    # Check if file exists
    if not os.path.exists(icon_path):
        print(f"❌ Icon file not found: {icon_path}")
        return False
    
    print(f"✅ Icon file exists: {icon_path}")
    
    # Check file size
    file_size = os.path.getsize(icon_path)
    print(f"📏 File size: {file_size:,} bytes")
    
    # Test with PIL
    try:
        with Image.open(icon_path) as img:
            print(f"🎨 PIL can read the icon: {img.format}")
            print(f"   Size: {img.size}")
            print(f"   Mode: {img.mode}")
    except Exception as e:
        print(f"❌ PIL error: {e}")
        return False
    
    # Test with tkinter
    try:
        root = tk.Tk()
        root.title("NextAstroTarget Icon Test")
        root.geometry("300x200")
        
        # Try to set the icon
        root.iconbitmap(icon_path)
        print("✅ Tkinter can load the icon")
        
        # Add a label to show the test is working
        label = tk.Label(root, 
                        text="NextAstroTarget Icon Test\n\nCheck the window title bar\nfor the custom icon!",
                        font=("Arial", 12),
                        justify="center")
        label.pack(expand=True)
        
        # Center the window
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (300 // 2)
        y = (root.winfo_screenheight() // 2) - (200 // 2)
        root.geometry(f"300x200+{x}+{y}")
        
        print("🪟 Test window opened - check the title bar icon!")
        print("   Close the window to continue...")
        
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Tkinter error: {e}")
        return False
    
    print("🌟 Icon test completed successfully!")
    return True

if __name__ == "__main__":
    if test_icon():
        print("\n✅ The icon is ready for use in NextAstroTarget!")
    else:
        print("\n❌ Icon test failed - please check the errors above.")
        sys.exit(1)
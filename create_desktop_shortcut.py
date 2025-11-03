"""
Create a desktop shortcut for NextAstroTarget application.
Windows-specific script using pywin32 or fallback to VBScript.
"""

import os
import sys
from pathlib import Path

def create_shortcut_vbscript():
    """Create desktop shortcut using VBScript (no dependencies needed)."""
    
    # Get paths
    script_dir = Path(__file__).parent.absolute()
    python_exe = sys.executable
    main_script = script_dir / "main_pyside6.py"
    icon_path = script_dir / "assets" / "icon.ico"
    desktop = Path.home() / "Desktop"
    shortcut_path = desktop / "NextAstroTarget.lnk"
    
    print("=" * 70)
    print("Creating Desktop Shortcut for NextAstroTarget")
    print("=" * 70)
    print(f"\nPython executable: {python_exe}")
    print(f"Main script: {main_script}")
    print(f"Icon: {icon_path}")
    print(f"Desktop: {desktop}")
    print(f"Shortcut will be: {shortcut_path}\n")
    
    # Create VBScript to generate shortcut
    vbs_script = f'''
Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{str(shortcut_path)}"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{str(python_exe)}"
oLink.Arguments = """{str(main_script)}"""
oLink.WorkingDirectory = "{str(script_dir)}"
oLink.IconLocation = "{str(icon_path)}"
oLink.Description = "NextAstroTarget - Astronomy Planning Application"
oLink.WindowStyle = 1
oLink.Save
'''
    
    # Write VBScript to temp file
    vbs_path = script_dir / "create_shortcut.vbs"
    with open(vbs_path, 'w') as f:
        f.write(vbs_script)
    
    print("Creating shortcut...")
    
    # Execute VBScript
    import subprocess
    try:
        result = subprocess.run(['cscript', '//Nologo', str(vbs_path)], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✓ Desktop shortcut created successfully!\n")
            print(f"You can now launch NextAstroTarget from:")
            print(f"  {shortcut_path}\n")
        else:
            print(f"✗ Error creating shortcut: {result.stderr}\n")
            return False
    except Exception as e:
        print(f"✗ Error: {e}\n")
        return False
    finally:
        # Clean up VBS file
        if vbs_path.exists():
            vbs_path.unlink()
    
    print("=" * 70)
    return True


def create_shortcut_pywin32():
    """Create desktop shortcut using pywin32 (if available)."""
    try:
        from win32com.client import Dispatch
        
        # Get paths
        script_dir = Path(__file__).parent.absolute()
        python_exe = sys.executable
        main_script = script_dir / "main_pyside6.py"
        icon_path = script_dir / "assets" / "icon.ico"
        desktop = Path.home() / "Desktop"
        shortcut_path = desktop / "NextAstroTarget.lnk"
        
        print("=" * 70)
        print("Creating Desktop Shortcut for NextAstroTarget (using pywin32)")
        print("=" * 70)
        print(f"\nShortcut location: {shortcut_path}\n")
        
        # Create shortcut
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(str(shortcut_path))
        shortcut.TargetPath = str(python_exe)
        shortcut.Arguments = f'"{str(main_script)}"'
        shortcut.WorkingDirectory = str(script_dir)
        shortcut.IconLocation = str(icon_path)
        shortcut.Description = "NextAstroTarget - Astronomy Planning Application"
        shortcut.save()
        
        print("✓ Desktop shortcut created successfully!\n")
        print("=" * 70)
        return True
        
    except ImportError:
        return False
    except Exception as e:
        print(f"✗ Error with pywin32: {e}")
        return False


def main():
    """Create desktop shortcut using available method."""
    
    # Verify we're on Windows
    if os.name != 'nt':
        print("This script is for Windows only.")
        return
    
    # Try pywin32 first, fallback to VBScript
    if not create_shortcut_pywin32():
        print("pywin32 not available, using VBScript method...\n")
        create_shortcut_vbscript()


if __name__ == "__main__":
    main()

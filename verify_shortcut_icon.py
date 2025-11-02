#!/usr/bin/env python3
"""
Verify NextAstroTarget Desktop Shortcut Icon
Checks if the desktop shortcut is properly configured with the new icon.
"""

import os
from pathlib import Path
import subprocess

def verify_shortcut_icon():
    """Verify the desktop shortcut icon configuration."""
    print("🔍 Verifying NextAstroTarget Desktop Shortcut Icon...")
    
    # Check paths
    desktop_path = Path.home() / "Desktop"
    shortcut_path = desktop_path / "NextAstroTarget.lnk"
    icon_path = Path(__file__).parent / "assets" / "icon.ico"
    
    print(f"📁 Desktop: {desktop_path}")
    print(f"🔗 Shortcut: {shortcut_path}")
    print(f"🎨 Icon: {icon_path}")
    
    # Check if files exist
    if not shortcut_path.exists():
        print("❌ Desktop shortcut not found!")
        return False
    
    if not icon_path.exists():
        print("❌ Icon file not found!")
        return False
    
    print("✅ Both shortcut and icon files exist")
    
    # Use PowerShell to check shortcut properties
    ps_command = f"""
    $shortcut = (New-Object -ComObject WScript.Shell).CreateShortcut('{shortcut_path}')
    Write-Host "Target: $($shortcut.TargetPath)"
    Write-Host "WorkingDirectory: $($shortcut.WorkingDirectory)"
    Write-Host "IconLocation: $($shortcut.IconLocation)"
    Write-Host "Arguments: $($shortcut.Arguments)"
    """
    
    try:
        result = subprocess.run([
            'powershell', '-Command', ps_command
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("📋 Shortcut Properties:")
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    print(f"   {line.strip()}")
            
            # Check if icon is properly set
            if str(icon_path) in result.stdout or "icon.ico" in result.stdout:
                print("✅ Shortcut icon is properly configured!")
                return True
            else:
                print("⚠️  Shortcut exists but icon may not be set correctly")
                return False
        else:
            print(f"❌ Error checking shortcut: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Timeout checking shortcut properties")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def provide_manual_steps():
    """Provide manual steps to fix the icon if needed."""
    print("\n🛠️  Manual Fix Steps (if icon still not showing):")
    print("1. Right-click on the NextAstroTarget desktop shortcut")
    print("2. Select 'Properties'")
    print("3. Click 'Change Icon...'")
    print("4. Browse to: D:\\REPOS\\NextAstroTarget\\assets\\icon.ico")
    print("5. Select the icon and click OK")
    print("6. Click OK to close Properties")
    print("7. Right-click desktop and select 'Refresh' or press F5")

if __name__ == "__main__":
    success = verify_shortcut_icon()
    
    if success:
        print("\n🌟 Desktop shortcut icon verification PASSED!")
        print("   The new astronomical targeting icon should be visible.")
    else:
        print("\n⚠️  Desktop shortcut needs manual attention.")
        provide_manual_steps()
    
    print("\n💡 Tips:")
    print("   - If icon doesn't appear immediately, try pressing F5 on desktop")
    print("   - Icon cache refresh can take a few moments")
    print("   - The icon shows crosshairs with stars on a dark blue background")
#!/usr/bin/env python3
"""
Fix NextAstroTarget Desktop Shortcut Icon
Updates the existing desktop shortcut to use the new application icon.
"""

import os
import sys
from pathlib import Path

def fix_desktop_shortcut():
    """Fix the desktop shortcut to use the new icon."""
    print("🔧 Fixing NextAstroTarget Desktop Shortcut Icon...")
    
    # Get paths
    desktop_path = Path.home() / "Desktop"
    shortcut_path = desktop_path / "NextAstroTarget.lnk"
    app_dir = Path(__file__).parent.absolute()
    icon_path = app_dir / "assets" / "icon.ico"
    
    print(f"📁 Desktop path: {desktop_path}")
    print(f"🔗 Shortcut path: {shortcut_path}")
    print(f"🎨 Icon path: {icon_path}")
    
    # Check if shortcut exists
    if not shortcut_path.exists():
        print(f"❌ Shortcut not found: {shortcut_path}")
        print("   Please run the installer first to create the shortcut")
        return False
    
    # Check if icon exists
    if not icon_path.exists():
        print(f"❌ Icon not found: {icon_path}")
        print("   Please run create_app_icon.py first")
        return False
    
    print("✅ Both shortcut and icon exist")
    
    # Create PowerShell script to update the shortcut
    ps_script = f"""
# Update NextAstroTarget shortcut icon
$shortcutPath = "{shortcut_path}"
$iconPath = "{icon_path}"

Write-Host "🔧 Updating shortcut icon..."
Write-Host "   Shortcut: $shortcutPath"
Write-Host "   Icon: $iconPath"

try {{
    # Load COM object
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($shortcutPath)
    
    Write-Host "📋 Current shortcut properties:"
    Write-Host "   Target: $($shortcut.TargetPath)"
    Write-Host "   Working Directory: $($shortcut.WorkingDirectory)"
    Write-Host "   Icon Location: $($shortcut.IconLocation)"
    
    # Update the icon
    $shortcut.IconLocation = $iconPath
    $shortcut.Save()
    
    Write-Host "✅ Shortcut icon updated successfully!"
    Write-Host "   New icon location: $($shortcut.IconLocation)"
    
    # Force icon cache refresh
    Write-Host "🔄 Refreshing icon cache..."
    
    # Method 1: Touch the shortcut to trigger refresh
    $shortcut.Save()
    
    # Method 2: Use ie4uinit to refresh icon cache
    Start-Process -FilePath "ie4uinit.exe" -ArgumentList "-show" -Wait -NoNewWindow
    
    Write-Host "🌟 Desktop shortcut icon fix completed!"
    Write-Host "   The new icon should appear shortly."
    Write-Host "   If not visible immediately, try:"
    Write-Host "   - Right-click desktop → Refresh"
    Write-Host "   - Or restart Windows Explorer"
    
}} catch {{
    Write-Host "❌ Error updating shortcut: $($_.Exception.Message)"
    exit 1
}}
"""
    
    # Write PowerShell script to temp file
    ps_file = app_dir / "fix_shortcut_temp.ps1"
    with open(ps_file, 'w', encoding='utf-8') as f:
        f.write(ps_script)
    
    print(f"📝 Created PowerShell script: {ps_file}")
    return ps_file

if __name__ == "__main__":
    ps_file = fix_desktop_shortcut()
    if ps_file:
        print(f"\n🚀 Run this command to fix the shortcut:")
        print(f'   powershell -ExecutionPolicy Bypass -File "{ps_file}"')
        print("\nOr use the provided batch file for easier execution.")
    else:
        sys.exit(1)
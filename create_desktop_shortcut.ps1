# Create Desktop Shortcut for NextAstroTarget
# This script creates a shortcut on your desktop that launches the app without console

$WshShell = New-Object -ComObject WScript.Shell
$DesktopPath = [System.Environment]::GetFolderPath('Desktop')
$ShortcutPath = Join-Path $DesktopPath "NextAstroTarget.lnk"

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = Join-Path $PSScriptRoot "launch_app.bat"
$Shortcut.WorkingDirectory = $PSScriptRoot
$Shortcut.Description = "NextAstroTarget - Astronomy Target Planning"
$Shortcut.IconLocation = Join-Path $PSScriptRoot "assets\icon.ico"
$Shortcut.Save()

Write-Host "Desktop shortcut created successfully at: $ShortcutPath" -ForegroundColor Green
Write-Host "You can now launch NextAstroTarget from your desktop without the console window." -ForegroundColor Green

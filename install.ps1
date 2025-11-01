# NextAstroTarget PowerShell Installer
# This script installs the NextAstroTarget application on Windows systems

param(
    [switch]$Silent = $false,
    [switch]$NoShortcuts = $false
)

# Set error action preference
$ErrorActionPreference = "Continue"

# Colors for output
$InfoColor = "Green"
$WarningColor = "Yellow"
$ErrorColor = "Red"

function Write-Info {
    param($Message)
    Write-Host $Message -ForegroundColor $InfoColor
}

function Write-Warning {
    param($Message)
    Write-Host "WARNING: $Message" -ForegroundColor $WarningColor
}

function Write-Error {
    param($Message)
    Write-Host "ERROR: $Message" -ForegroundColor $ErrorColor
}

function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Header
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "    NextAstroTarget Installation Script" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check administrator privileges
if (-not (Test-Administrator)) {
    Write-Warning "Not running as administrator. Some features may require elevated privileges."
    Write-Host ""
}

# Get application directory
$AppDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Write-Info "Application directory: $AppDir"
Write-Host ""

# Step 1: Check Python installation
Write-Info "[1/7] Checking Python installation..."
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
    Write-Info "Python found: $pythonVersion"
} catch {
    Write-Error "Python is not installed or not in PATH."
    Write-Host "Please install Python 3.8 or higher from https://www.python.org/"
    Write-Host "Make sure to check 'Add Python to PATH' during installation."
    
    if (-not $Silent) {
        Read-Host "Press Enter to exit"
    }
    exit 1
}

# Step 2: Check pip availability
Write-Info "[2/7] Checking pip availability..."
try {
    $pipVersion = python -m pip --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "pip not found"
    }
    Write-Info "pip is available"
} catch {
    Write-Error "pip is not available. Please reinstall Python with pip included."
    if (-not $Silent) {
        Read-Host "Press Enter to exit"
    }
    exit 1
}

# Step 3: Install required packages
Write-Info "[3/7] Installing required Python packages..."
Write-Host "This may take a few minutes..." -ForegroundColor Yellow
Write-Host ""

try {
    # Upgrade pip
    Write-Host "Upgrading pip..." -ForegroundColor Gray
    python -m pip install --upgrade pip | Out-Host
    
    # Install requirements
    $requirementsFile = Join-Path $AppDir "requirements.txt"
    if (Test-Path $requirementsFile) {
        Write-Host "Installing packages from requirements.txt..." -ForegroundColor Gray
        python -m pip install -r $requirementsFile | Out-Host
        
        if ($LASTEXITCODE -ne 0) {
            throw "Package installation failed"
        }
        Write-Info "Required packages installed successfully"
    } else {
        Write-Warning "requirements.txt not found, skipping package installation"
    }
} catch {
    Write-Error "Failed to install required packages."
    Write-Host "Please check your internet connection and try again."
    Write-Host "You may need to run this installer as administrator."
    
    if (-not $Silent) {
        Read-Host "Press Enter to exit"
    }
    exit 1
}

# Step 4: Create directories
Write-Info "[4/7] Creating application directories..."
$directories = @("data", "logs", "config")
foreach ($dir in $directories) {
    $dirPath = Join-Path $AppDir $dir
    if (-not (Test-Path $dirPath)) {
        New-Item -ItemType Directory -Path $dirPath -Force | Out-Null
    }
}
Write-Info "Directories created"

# Step 5: Check for Excel file
Write-Info "[5/7] Checking for required data files..."
$excelFile = Join-Path $AppDir "Imm Deep Sky Compendium - 2023 - rev4g.xlsm"
if (-not (Test-Path $excelFile)) {
    Write-Warning "Excel data file not found:"
    Write-Warning $excelFile
    Write-Host ""
    Write-Host "Please ensure this file is in the application directory"
    Write-Host "before running the application for the first time."
    Write-Host ""
}

# Step 6: Test application startup
Write-Info "[6/7] Testing application startup..."
try {
    Set-Location $AppDir
    $testOutput = python main.py --test-startup 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Info "Application startup test passed"
    } else {
        Write-Warning "Application startup test failed: $testOutput"
        Write-Warning "The application may still work, but there might be configuration issues."
    }
} catch {
    Write-Warning "Could not run startup test: $_"
}

# Step 7: Create shortcuts
if (-not $NoShortcuts) {
    Write-Info "[7/7] Creating shortcuts..."
    
    # Desktop shortcut
    try {
        $desktopPath = [Environment]::GetFolderPath("Desktop")
        $shortcutPath = Join-Path $desktopPath "NextAstroTarget.lnk"
        
        $WshShell = New-Object -comObject WScript.Shell
        $shortcut = $WshShell.CreateShortcut($shortcutPath)
        $shortcut.TargetPath = "python.exe"
        $shortcut.Arguments = "`"$AppDir\main.py`""
        $shortcut.WorkingDirectory = $AppDir
        $shortcut.Description = "NextAstroTarget - Astrophotography Target Selector"
        
        # Try to set icon if available
        $iconPath = Join-Path $AppDir "assets\icon.ico"
        if (Test-Path $iconPath) {
            $shortcut.IconLocation = $iconPath
        }
        
        $shortcut.Save()
        Write-Info "Desktop shortcut created"
        
        # Start Menu shortcut
        try {
            $startMenuPath = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs"
            $startShortcutPath = Join-Path $startMenuPath "NextAstroTarget.lnk"
            Copy-Item $shortcutPath $startShortcutPath -Force
            Write-Info "Start Menu entry created"
        } catch {
            Write-Warning "Could not create Start Menu entry: $_"
        }
        
    } catch {
        Write-Warning "Could not create shortcuts: $_"
        Write-Host "You can create a shortcut manually:"
        Write-Host "  Target: python.exe `"$AppDir\main.py`""
        Write-Host "  Start in: $AppDir"
    }
} else {
    Write-Info "[7/7] Skipping shortcut creation (NoShortcuts flag set)"
}

# Installation complete
Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "         Installation Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""

Write-Info "NextAstroTarget has been successfully installed."
Write-Host ""
Write-Host "To start the application:"
if (-not $NoShortcuts) {
    Write-Host "  1. Use the desktop shortcut 'NextAstroTarget'"
    Write-Host "  2. Or run: python `"$AppDir\main.py`""
} else {
    Write-Host "  Run: python `"$AppDir\main.py`""
}
Write-Host ""
Write-Host "First-time setup:"
Write-Host "  1. Ensure the Excel data file is in the application directory"
Write-Host "  2. Run the application and initialize the database"
Write-Host "  3. Start selecting your astrophotography targets!"
Write-Host ""
Write-Host "For troubleshooting, check the README.md file"
Write-Host "and the logs in the 'logs' directory."
Write-Host ""

# Ask to launch application
if (-not $Silent) {
    $launch = Read-Host "Would you like to launch NextAstroTarget now? (y/n)"
    if ($launch -eq "y" -or $launch -eq "Y") {
        Write-Host ""
        Write-Info "Starting NextAstroTarget..."
        try {
            Start-Process python -ArgumentList "`"$AppDir\main.py`"" -WorkingDirectory $AppDir
        } catch {
            Write-Warning "Could not start application: $_"
            Write-Host "Please run it manually from the desktop shortcut or command line."
        }
    }
}

Write-Host ""
Write-Info "Thank you for installing NextAstroTarget!"

if (-not $Silent) {
    Read-Host "Press Enter to exit"
}
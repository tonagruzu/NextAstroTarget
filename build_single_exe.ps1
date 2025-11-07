# Build NextAstroTarget as single executable
# Usage: .\build_single_exe.ps1

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "NextAstroTarget - Build Single .EXE" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run setup script first." -ForegroundColor Yellow
    exit 1
}

# Check if PyInstaller is installed
Write-Host "Checking PyInstaller..." -ForegroundColor Yellow
$pyinstallerCheck = & .venv\Scripts\pip.exe show pyinstaller 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "PyInstaller not installed. Installing..." -ForegroundColor Yellow
    & .venv\Scripts\pip.exe install pyinstaller
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install PyInstaller!" -ForegroundColor Red
        exit 1
    }
    Write-Host "PyInstaller installed successfully!" -ForegroundColor Green
} else {
    Write-Host "PyInstaller already installed." -ForegroundColor Green
}

# Check if database exists
if (-not (Test-Path "targets.db")) {
    Write-Host "WARNING: targets.db not found!" -ForegroundColor Yellow
    Write-Host "The executable will be built but won't have the database." -ForegroundColor Yellow
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y") {
        Write-Host "Build cancelled." -ForegroundColor Yellow
        exit 0
    }
}

# Clean previous builds
Write-Host ""
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "build") {
    Remove-Item -Path "build" -Recurse -Force
    Write-Host "  - Removed build directory" -ForegroundColor Gray
}
if (Test-Path "dist\NextAstroTarget.exe") {
    Remove-Item -Path "dist\NextAstroTarget.exe" -Force
    Write-Host "  - Removed previous executable" -ForegroundColor Gray
}

# Build executable
Write-Host ""
Write-Host "Building executable..." -ForegroundColor Yellow
Write-Host "This may take 5-10 minutes on first build..." -ForegroundColor Gray
Write-Host ""

& .venv\Scripts\pyinstaller.exe build_exe.spec --clean

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Build failed!" -ForegroundColor Red
    exit 1
}

# Check if executable was created
if (Test-Path "dist\NextAstroTarget.exe") {
    Write-Host ""
    Write-Host "======================================" -ForegroundColor Green
    Write-Host "Build completed successfully!" -ForegroundColor Green
    Write-Host "======================================" -ForegroundColor Green
    Write-Host ""
    
    $exeSize = (Get-Item "dist\NextAstroTarget.exe").Length / 1MB
    Write-Host "Executable created: dist\NextAstroTarget.exe" -ForegroundColor Cyan
    Write-Host "File size: $([math]::Round($exeSize, 2)) MB" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "You can now distribute this single .exe file!" -ForegroundColor Green
    Write-Host ""
    
    # Ask if user wants to test
    $test = Read-Host "Do you want to test the executable now? (y/n)"
    if ($test -eq "y") {
        Write-Host "Launching executable..." -ForegroundColor Yellow
        Start-Process "dist\NextAstroTarget.exe"
    }
} else {
    Write-Host ""
    Write-Host "ERROR: Executable not found after build!" -ForegroundColor Red
    exit 1
}

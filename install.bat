@echo off
setlocal enabledelayedexpansion

:: NextAstroTarget Windows Installer
:: This script installs the NextAstroTarget application on Windows systems

echo ============================================
echo    NextAstroTarget Installation Script
echo ============================================
echo.

:: Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Warning: Not running as administrator.
    echo Some features may require elevated privileges.
    echo.
)

:: Get current directory
set "APP_DIR=%~dp0"
set "APP_DIR=%APP_DIR:~0,-1%"
echo Application directory: %APP_DIR%
echo.

:: Check Python installation
echo [1/7] Checking Python installation...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

:: Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Python %PYTHON_VERSION% found.

:: Check if pip is available
echo [2/7] Checking pip availability...
python -m pip --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: pip is not available.
    echo Please reinstall Python with pip included.
    echo.
    pause
    exit /b 1
)
echo pip is available.

:: Install required packages
echo [3/7] Installing required Python packages...
echo This may take a few minutes...
echo.

python -m pip install --upgrade pip
if %errorLevel% neq 0 (
    echo Warning: Could not upgrade pip.
)

python -m pip install -r "%APP_DIR%\requirements.txt"
if %errorLevel% neq 0 (
    echo ERROR: Failed to install required packages.
    echo Please check your internet connection and try again.
    echo You may need to run this installer as administrator.
    echo.
    pause
    exit /b 1
)
echo Required packages installed successfully.

:: Create directories
echo [4/7] Creating application directories...
if not exist "%APP_DIR%\data" mkdir "%APP_DIR%\data"
if not exist "%APP_DIR%\logs" mkdir "%APP_DIR%\logs"
if not exist "%APP_DIR%\config" mkdir "%APP_DIR%\config"
echo Directories created.

:: Check for Excel file
echo [5/7] Checking for required data files...
set "EXCEL_FILE=%APP_DIR%\Imm Deep Sky Compendium - 2023 - rev4g.xlsm"
if not exist "!EXCEL_FILE!" (
    echo Warning: Excel data file not found:
    echo "!EXCEL_FILE!"
    echo.
    echo Please ensure this file is in the application directory
    echo before running the application for the first time.
    echo.
)

:: Test application startup
echo [6/7] Testing application startup...
cd /d "%APP_DIR%"
python main.py --test-startup >nul 2>&1
if %errorLevel% neq 0 (
    echo Warning: Application startup test failed.
    echo The application may still work, but there might be configuration issues.
    echo Check the logs directory for error details.
    echo.
) else (
    echo Application startup test passed.
)

:: Create desktop shortcut
echo [7/7] Creating desktop shortcut...
set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT=%DESKTOP%\NextAstroTarget.lnk"

:: Create VBS script for shortcut creation
set "VBS_FILE=%TEMP%\create_shortcut.vbs"
(
    echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
    echo sLinkFile = "%SHORTCUT%"
    echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
    echo oLink.TargetPath = "python.exe"
    echo oLink.Arguments = """%APP_DIR%\main.py"""
    echo oLink.WorkingDirectory = "%APP_DIR%"
    echo oLink.IconLocation = "%APP_DIR%\assets\icon.ico"
    echo oLink.Description = "NextAstroTarget - Astrophotography Target Selector"
    echo oLink.Save
) > "%VBS_FILE%"

cscript //nologo "%VBS_FILE%" >nul 2>&1
if %errorLevel% neq 0 (
    echo Warning: Could not create desktop shortcut automatically.
    echo You can create a shortcut manually:
    echo   Target: python.exe "%APP_DIR%\main.py"
    echo   Start in: %APP_DIR%
    echo.
) else (
    echo Desktop shortcut created successfully.
)

:: Cleanup
del "%VBS_FILE%" >nul 2>&1

:: Create Start Menu entry (optional)
set "START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs"
if exist "%START_MENU%" (
    set "START_SHORTCUT=%START_MENU%\NextAstroTarget.lnk"
    copy "%SHORTCUT%" "!START_SHORTCUT!" >nul 2>&1
    if !errorLevel! equ 0 (
        echo Start Menu entry created.
    )
)

echo.
echo ============================================
echo         Installation Complete!
echo ============================================
echo.
echo NextAstroTarget has been successfully installed.
echo.
echo To start the application:
echo   1. Use the desktop shortcut "NextAstroTarget"
echo   2. Or run: python "%APP_DIR%\main.py"
echo.
echo First-time setup:
echo   1. Ensure the Excel data file is in the application directory
echo   2. Run the application and initialize the database
echo   3. Start selecting your astrophotography targets!
echo.
echo For troubleshooting, check the README.md file
echo and the logs in the 'logs' directory.
echo.

:: Ask if user wants to launch the application
set /p LAUNCH="Would you like to launch NextAstroTarget now? (y/n): "
if /i "!LAUNCH!"=="y" (
    echo.
    echo Starting NextAstroTarget...
    start "" python "%APP_DIR%\main.py"
)

echo.
echo Thank you for installing NextAstroTarget!
pause
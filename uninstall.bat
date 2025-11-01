@echo off
setlocal enabledelayedexpansion

:: NextAstroTarget Uninstaller
:: This script removes NextAstroTarget from the system

echo ============================================
echo    NextAstroTarget Uninstaller
echo ============================================
echo.

:: Get current directory
set "APP_DIR=%~dp0"
set "APP_DIR=%APP_DIR:~0,-1%"
echo Application directory: %APP_DIR%
echo.

:: Confirm uninstallation
echo This will remove NextAstroTarget from your system.
echo The following will be deleted:
echo   - Desktop shortcut
echo   - Start Menu entry
echo   - Application data and logs
echo.
echo The main application files will remain for manual removal.
echo.

set /p CONFIRM="Are you sure you want to continue? (y/n): "
if /i not "!CONFIRM!"=="y" (
    echo Uninstallation cancelled.
    pause
    exit /b 0
)

echo.
echo Starting uninstallation...
echo.

:: Remove desktop shortcut
echo [1/4] Removing desktop shortcut...
set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT=%DESKTOP%\NextAstroTarget.lnk"
if exist "!SHORTCUT!" (
    del "!SHORTCUT!" >nul 2>&1
    if !errorLevel! equ 0 (
        echo Desktop shortcut removed.
    ) else (
        echo Warning: Could not remove desktop shortcut.
    )
) else (
    echo Desktop shortcut not found.
)

:: Remove Start Menu entry
echo [2/4] Removing Start Menu entry...
set "START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs"
set "START_SHORTCUT=%START_MENU%\NextAstroTarget.lnk"
if exist "!START_SHORTCUT!" (
    del "!START_SHORTCUT!" >nul 2>&1
    if !errorLevel! equ 0 (
        echo Start Menu entry removed.
    ) else (
        echo Warning: Could not remove Start Menu entry.
    )
) else (
    echo Start Menu entry not found.
)

:: Clean application data
echo [3/4] Cleaning application data...

:: Remove database files
if exist "%APP_DIR%\data" (
    echo Removing database files...
    rmdir /s /q "%APP_DIR%\data" >nul 2>&1
    if !errorLevel! equ 0 (
        echo Database files removed.
    ) else (
        echo Warning: Could not remove all database files.
    )
)

:: Remove log files
if exist "%APP_DIR%\logs" (
    echo Removing log files...
    rmdir /s /q "%APP_DIR%\logs" >nul 2>&1
    if !errorLevel! equ 0 (
        echo Log files removed.
    ) else (
        echo Warning: Could not remove all log files.
    )
)

:: Reset configuration (optional)
set /p RESET_CONFIG="Remove configuration files? (y/n): "
if /i "!RESET_CONFIG!"=="y" (
    if exist "%APP_DIR%\config" (
        echo Removing configuration files...
        rmdir /s /q "%APP_DIR%\config" >nul 2>&1
        if !errorLevel! equ 0 (
            echo Configuration files removed.
        ) else (
            echo Warning: Could not remove all configuration files.
        )
    )
)

:: Optional: Uninstall Python packages
echo [4/4] Python package cleanup...
set /p REMOVE_PACKAGES="Remove Python packages installed for NextAstroTarget? (y/n): "
if /i "!REMOVE_PACKAGES!"=="y" (
    echo.
    echo Note: This will only remove packages if they are not used by other applications.
    echo Removing packages...
    
    :: Read requirements and try to uninstall
    if exist "%APP_DIR%\requirements.txt" (
        for /f "tokens=1 delims=>=<" %%a in (%APP_DIR%\requirements.txt) do (
            if not "%%a"=="" (
                if not "%%a"=="sqlite3" (
                    if not "%%a"=="tkinter" (
                        echo Uninstalling %%a...
                        python -m pip uninstall -y "%%a" >nul 2>&1
                    )
                )
            )
        )
        echo Package cleanup completed.
    )
)

echo.
echo ============================================
echo       Uninstallation Complete!
echo ============================================
echo.
echo NextAstroTarget has been removed from your system.
echo.
echo Note: The main application files remain in:
echo %APP_DIR%
echo.
echo You can safely delete this directory if you no longer need
echo the application or want to keep the source files for reference.
echo.

:: Ask about removing the application directory
set /p REMOVE_DIR="Remove the entire application directory? (y/n): "
if /i "!REMOVE_DIR!"=="y" (
    echo.
    echo Warning: This will delete all application files including source code.
    set /p FINAL_CONFIRM="Are you absolutely sure? (y/n): "
    if /i "!FINAL_CONFIRM!"=="y" (
        echo.
        echo Removing application directory...
        cd /d "%TEMP%"
        rmdir /s /q "%APP_DIR%" >nul 2>&1
        if !errorLevel! equ 0 (
            echo Application directory removed completely.
            echo.
            echo NextAstroTarget has been completely uninstalled.
        ) else (
            echo Warning: Could not remove application directory.
            echo You may need to remove it manually.
        )
    )
)

echo.
echo Thank you for using NextAstroTarget!
pause
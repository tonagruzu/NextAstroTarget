@echo off
REM Build NextAstroTarget as single executable

echo ======================================
echo NextAstroTarget - Build Single .EXE
echo ======================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    echo Please run setup script first.
    pause
    exit /b 1
)

REM Install PyInstaller if needed
echo Checking PyInstaller...
.venv\Scripts\pip.exe show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    .venv\Scripts\pip.exe install pyinstaller
)

REM Clean previous builds
echo.
echo Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist\NextAstroTarget.exe" del /q "dist\NextAstroTarget.exe"

REM Build executable
echo.
echo Building executable...
echo This may take 5-10 minutes on first build...
echo.

.venv\Scripts\pyinstaller.exe build_exe.spec --clean

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

REM Check result
if exist "dist\NextAstroTarget.exe" (
    echo.
    echo ======================================
    echo Build completed successfully!
    echo ======================================
    echo.
    echo Executable created: dist\NextAstroTarget.exe
    echo.
    echo You can now distribute this single .exe file!
    echo.
) else (
    echo.
    echo ERROR: Executable not found after build!
    pause
    exit /b 1
)

pause

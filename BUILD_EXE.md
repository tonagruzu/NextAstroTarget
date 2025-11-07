# Build Single Executable for NextAstroTarget

## Prerequisites

Install PyInstaller:
```powershell
.venv\Scripts\pip.exe install pyinstaller
```

## Build Instructions

### Option 1: Using the spec file (Recommended)
```powershell
.venv\Scripts\pyinstaller.exe build_exe.spec
```

### Option 2: Direct command (one-liner)
```powershell
.venv\Scripts\pyinstaller.exe --onefile --windowed --name NextAstroTarget --icon icons/app_icon.ico --add-data "targets.db;." --add-data "config;config" --add-data "src;src" main_pyside6.py
```

## Output

The executable will be created in:
```
dist/NextAstroTarget.exe
```

## File Size

The single .exe file will be approximately:
- **50-80 MB** (compressed with UPX)
- **100-150 MB** (without UPX compression)

This includes:
- Python interpreter
- PySide6 (Qt6) libraries
- All dependencies (requests, PIL, sqlite3, etc.)
- Your application code
- Database and config files

## Testing

After building, test the executable:
```powershell
.\dist\NextAstroTarget.exe
```

## Distribution

You can distribute just the single `NextAstroTarget.exe` file. Users don't need:
- Python installed
- Virtual environment
- Any dependencies
- Configuration files (bundled inside)

## Troubleshooting

### Missing modules error
If you get "ModuleNotFoundError", add the module to `hiddenimports` in `build_exe.spec`

### Database not found
Make sure `targets.db` exists before building

### Icon not found
Create an icon file at `icons/app_icon.ico` or remove the `--icon` parameter

### File too large
- Use UPX compression (enabled by default in spec file)
- Exclude unnecessary modules in the `excludes` list

## Advanced: Installer (Optional)

To create a proper Windows installer (.msi), you can use:
- **Inno Setup** (free): Create `setup.iss` script
- **NSIS** (free): Create installer wizard
- **WiX Toolset** (free): Professional MSI installer

## Notes

- First build takes 5-10 minutes
- Subsequent builds are faster (2-3 minutes)
- The .exe runs standalone but extracts to temp folder at runtime
- Startup is slightly slower than running with Python directly
- Antivirus may flag the .exe initially (false positive - add exception)

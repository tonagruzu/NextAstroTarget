# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for NextAstroTarget
Builds a single executable with all dependencies bundled.
"""

import sys
from pathlib import Path

block_cipher = None

# Get the project root directory
project_root = Path('.').absolute()

a = Analysis(
    ['main_pyside6.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        # Include the database file
        ('targets.db', '.'),
        # Include config directory
        ('config', 'config'),
        # Include icons if they exist
        ('icons', 'icons') if Path('icons').exists() else None,
        # Include src package
        ('src', 'src'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'sqlite3',
        'logging',
        'requests',
        'PIL',
        'io',
        'configparser',
        'datetime',
        'math',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',  # Exclude old Tkinter version
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Remove None entries from datas
a.datas = [d for d in a.datas if d is not None]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='NextAstroTarget',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window (GUI app)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icons/app_icon.ico' if Path('icons/app_icon.ico').exists() else None,
)

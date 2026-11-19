"""Path resolution for the application.

Single source of truth for where runtime data lives, in both source and packaged
builds. Every component that writes files should ask these functions instead of
computing paths from ``__file__`` or relying on the current working directory.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


def _source_root() -> Path:
    """Project root when running from source (this file lives in ``src/``)."""
    return Path(__file__).resolve().parents[1]


def app_home() -> Path:
    """Directory the application writes runtime data into.

    Packaged: the folder containing the executable. Source: the project root.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return _source_root()


def bundle_root() -> Path:
    """Directory holding the files bundled with the application.

    Packaged: the PyInstaller extraction directory. Source: the project root.
    """
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            return Path(meipass)
        return Path(sys.executable).resolve().parent
    return _source_root()


def data_dir() -> Path:
    """Data directory under the application home."""
    return app_home() / "data"


def ensure_writable() -> Path:
    """Create the data directory under the application home.

    Raises ``OSError`` naming the path if it cannot be created, so the caller can
    report the failure instead of continuing with silent data loss.
    """
    target = data_dir()
    try:
        target.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise OSError(f"Application data directory is not writable: {target}") from exc
    return target


def seed_runtime_files() -> None:
    """Copy required bundled files into the application home if absent.

    Existing files are never overwritten. Today the required files are the
    configuration file and the catalogue database.
    """
    src_root = bundle_root()
    home = app_home()

    config_src = src_root / "config" / "config.ini"
    config_dst = home / "config" / "config.ini"
    if config_src.exists() and not config_dst.exists():
        config_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(config_src, config_dst)

    db_src = src_root / "data" / "astro_targets.db"
    db_dst = home / "data" / "astro_targets.db"
    if db_src.exists() and not db_dst.exists():
        db_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(db_src, db_dst)

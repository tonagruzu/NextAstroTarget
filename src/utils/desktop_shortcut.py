"""Create, inspect and repair the Windows desktop shortcut for the application.

Uses ``WScript.Shell`` through a generated VBScript, the same mechanism the
repository's development shortcut script already relies on, so no third-party
dependencies are required.

The desktop directory is injectable so tests can target a temporary folder
instead of the user's real desktop.
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

from src.paths import app_home

logger = logging.getLogger(__name__)

SHORTCUT_NAME = "NextAstroTarget.lnk"
_DESCRIPTION = "NextAstroTarget - Astronomy Planning Application"


def is_windows() -> bool:
    """Whether shortcut management is supported on this platform."""
    return sys.platform == "win32"


def is_frozen() -> bool:
    """Whether the application is running from a packaged executable."""
    return bool(getattr(sys, "frozen", False))


def default_desktop_dir() -> Path:
    """The desktop directory, overridable via ``NEXTASTROTARGET_DESKTOP`` for tests."""
    override = os.environ.get("NEXTASTROTARGET_DESKTOP")
    if override:
        return Path(override)
    return Path.home() / "Desktop"


def shortcut_path(desktop_dir: Optional[Path] = None) -> Path:
    return (desktop_dir or default_desktop_dir()) / SHORTCUT_NAME


def current_target() -> str:
    """The path the shortcut should launch: the running executable."""
    return str(Path(sys.executable).resolve())


def _console_encoding() -> str:
    """The codepage ``cscript`` writes to a pipe, which is the console OEM codepage."""
    if sys.platform == "win32":
        try:
            import ctypes

            return f"cp{ctypes.windll.kernel32.GetOEMCP()}"
        except Exception:
            pass
    return "utf-8"


def _run_vbs(script: str) -> Optional[str]:
    """Write ``script`` to a temporary ``.vbs`` file, run it, return its output.

    Returns ``None`` rather than raising on any failure, so a blocked or missing
    script host never aborts application startup.
    """
    if not is_windows():
        return None
    handle, vbs_path = tempfile.mkstemp(suffix=".vbs")
    encoding = _console_encoding()
    try:
        with open(handle, "w", encoding="utf-8") as f:
            f.write(script)
        result = subprocess.run(
            ["cscript", "//nologo", vbs_path],
            capture_output=True,
            timeout=15,
        )
        stdout = (result.stdout or b"").decode(encoding, errors="replace")
        stderr = (result.stderr or b"").decode(encoding, errors="replace")
        if result.returncode != 0:
            logger.warning("Shortcut script failed: %s", stderr.strip())
            return None
        return stdout.strip()
    except Exception as e:
        logger.warning("Shortcut operation failed: %s", e)
        return None
    finally:
        try:
            Path(vbs_path).unlink(missing_ok=True)
        except OSError:
            pass


def _write_shortcut(desktop_dir: Optional[Path] = None) -> bool:
    """Create or overwrite the shortcut to point at the running executable."""
    target = current_target()
    lnk = shortcut_path(desktop_dir)
    workdir = str(app_home())
    script = (
        'Set oWS = WScript.CreateObject("WScript.Shell")\n'
        f'Set oLink = oWS.CreateShortcut("{lnk}")\n'
        f'oLink.TargetPath = "{target}"\n'
        f'oLink.WorkingDirectory = "{workdir}"\n'
        f'oLink.IconLocation = "{target},0"\n'
        f'oLink.Description = "{_DESCRIPTION}"\n'
        "oLink.Save\n"
    )
    return _run_vbs(script) is not None


def read_target(desktop_dir: Optional[Path] = None) -> Optional[str]:
    """Return the target path of the existing shortcut, or ``None``."""
    lnk = shortcut_path(desktop_dir)
    if not lnk.exists():
        return None
    script = (
        'Set oWS = WScript.CreateObject("WScript.Shell")\n'
        f'Set oLink = oWS.CreateShortcut("{lnk}")\n'
        "WScript.Echo oLink.TargetPath\n"
    )
    out = _run_vbs(script)
    return out or None


def is_stale(desktop_dir: Optional[Path] = None) -> bool:
    """Whether the existing shortcut points somewhere other than this executable."""
    target = read_target(desktop_dir)
    return target is not None and target != current_target()


def decide(setting: Optional[str], lnk_stale: bool) -> str:
    """Return the shortcut action for the given state: ``offer``, ``repair`` or ``none``."""
    if setting is None:
        return "offer"
    if setting == "yes":
        return "repair" if lnk_stale else "none"
    return "none"


def create(desktop_dir: Optional[Path] = None) -> bool:
    """Create the shortcut. Returns ``True`` on success."""
    return _write_shortcut(desktop_dir)


def repair(desktop_dir: Optional[Path] = None) -> bool:
    """Point an existing shortcut at the current executable. Returns ``True`` on success."""
    return _write_shortcut(desktop_dir)

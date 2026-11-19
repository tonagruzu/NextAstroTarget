# Proposal

## Why

The application is portable: it runs from whatever folder the executable is dropped into. But
the only desktop-shortcut helper in the repository (`create_desktop_shortcut.py`) targets a
development setup — `python.exe` plus `main_pyside6.py` — and is not bundled, so a packaged build
has no way to create a launcher on the user's desktop. Project requirement 14 asks for a desktop
shortcut, and a portable app still needs one stable, findable way to start.

## What Changes

- On first run the application offers (opt-in) to create a desktop shortcut that launches the
  running executable directly, with its working directory set to the executable's folder and its
  icon taken from the executable itself.
- On later starts the application verifies the shortcut still points at the current executable and
  repairs it when the folder has moved.
- The shortcut target is the executable, never `python.exe` or a script path, so it works in both
  packaged and source runtimes.

Explicitly out of scope: the existing development-oriented shortcut scripts at the repository
root, and any installer-style placement of the shortcut.

## Capabilities

### New Capabilities

- `desktop-shortcut`: creating and keeping current a desktop shortcut that launches the
  application regardless of where it has been placed.

### Modified Capabilities

None.

## Impact

- New `src/utils/desktop_shortcut.py` — Windows `.lnk` creation and inspection.
- `main_pyside6.py` — first-run prompt and periodic verify/repair hook.
- `src/database/database_manager.py` — persisted opt-in decision (reuses `app_settings`).
- `RECOVERY.md` — note already references the repair behaviour; confirm wording.

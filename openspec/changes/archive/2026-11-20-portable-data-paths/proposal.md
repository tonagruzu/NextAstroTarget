# Proposal

## Why

The packaged application resolves its home directory from `__file__`, which inside a
PyInstaller one-file build points into the temporary extraction directory (`_MEIPASS`).
`main_pyside6.py` then calls `os.chdir()` on that path, so the temporary directory becomes
the application's home. Everything written at runtime — logs, image and moon caches, the
SQLite database, and the observatory configuration — dies with the process.

This blocks shipping any 2.0.x release: a user cannot keep their observatory location, and
there is nothing to back up or restore if their disk fails.

## What Changes

- Application home directory is derived from the running executable (`sys.executable`) when
  frozen, and from `__file__` when running from source. Development behaviour is unchanged.
- On startup, missing runtime files are seeded from the bundle into the application folder:
  `config/config.ini` and `data/astro_targets.db`. Existing files are never overwritten.
- Logs, image cache and moon cache are written next to the executable instead of the
  PyInstaller temporary directory.
- The image cache path stops using its own `__file__`-relative computation and resolves
  through the same application home as everything else.
- Observatory settings persisted at exit survive a restart of the packaged executable.
- A `RECOVERY.md` documents the restore procedure for a lost machine.

Explicitly out of scope: creating or repairing the desktop shortcut (separate change), and
moving `config/config.ini` out of version control.

## Capabilities

### New Capabilities

- `data-persistence`: where the application stores runtime data, how the application home is
  resolved in source and frozen builds, first-run seeding of bundled files, and the guarantees
  that runtime state survives a restart.

### Modified Capabilities

None. The project has no existing specifications.

## Impact

- `main_pyside6.py` — application home resolution and working directory.
- `src/utils/image_service.py` — default cache directory.
- `src/utils/logger.py` — log directory creation.
- `src/database/database_manager.py` — data directory resolution.
- `src/gui/pyside6_main_window.py` — observatory configuration read/write path.
- `build_exe.spec` — verify bundled seed sources are present.
- New `RECOVERY.md`.
- Verification uses the existing `--test-startup` entry point plus a launch from a directory
  other than the executable's own.

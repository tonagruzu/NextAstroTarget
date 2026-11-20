# Design

## Context

Motivation is in `proposal.md`. The constraints that shape the approach are in the code:

- `main_pyside6.py` resolves the working directory from `__file__` and calls `os.chdir()`. In a
  PyInstaller one-file build `__file__` points inside `_MEIPASS`, so the temporary extraction
  directory becomes the application home.
- Two path conventions already coexist: `src/utils/image_service.py` computes its cache from
  `__file__` with three `dirname` calls, while `src/database/database_manager.py` derives its
  path from `config/config.ini` (`Paths.data_dir`). Both are relative to the process working
  directory at the moment they run.
- User settings are split. Observatory location is written to `config/config.ini`
  (`[Observatory]`) by `pyside6_main_window.py`; filter ranges and transit window are written to
  the `app_settings` table inside the same SQLite file as the catalogue.
- `build_exe.spec` already bundles `src`, `config`, `assets` and `data/astro_targets.db`, so the
  seed sources are present inside the executable.
- `main_pyside6.py` already supports `--test-startup`, which initialises logging and the database
  manager without opening the GUI. It is a ready-made verification hook.

## Goals / Non-Goals

**Goals:**

- One authoritative notion of the application home, shared by every component that writes files.
- Behaviour identical in source and packaged builds from the user's point of view.
- No silent data loss: a location that cannot be written is reported.

**Non-Goals:**

- Reworking every path in the codebase into absolute paths.
- Desktop shortcut creation or repair (separate change).
- Moving `config/config.ini` out of version control.
- Migrating data from previous packaged builds (that data only ever existed in temp directories).

## Decisions

**Home resolution reads the executable when frozen.** `sys.frozen` selects `sys.executable`,
otherwise `__file__`. Both are resolved to `parent`, then made absolute. *Alternative rejected:*
resolving from the bundle root (`_MEIPASS`) — that is precisely the location that is discarded.

**Keep `os.chdir(home)` instead of rewriting path call sites.** Every existing relative path
(`data`, `logs`, `config/config.ini`) then lands in the right place with no changes to components
that already work. *Alternative rejected:* converting each component to build absolute paths from
an injected home. It is cleaner in the long run but touches every module, and a missed call site
fails silently — the exact failure mode this change removes.

**A single path helper owns the home and seed logic.** `image_service` stops computing its own
default cache directory and asks the helper instead, so the two conventions collapse into one.
The helper is the only place that knows about `sys.frozen`.

**Seeding runs once, before logging and database setup.** For each required file (`config/config.ini`,
`data/astro_targets.db`) the helper copies from the bundle only when the destination is absent.
Existing files are never replaced. Assets are not seeded: they are read-only and continue to be
read from the bundle.

**An unwritable home fails fast.** The helper verifies it can create the data directory at startup.
On failure the application shows an error naming the path and exits, rather than degrading into a
run that loses its state.

## Risks / Trade-offs

- **A newer executable does not refresh an existing catalogue.** Seeding only fills gaps, so a user
  who already has `data/astro_targets.db` keeps it, with their settings, but does not receive
  catalogue updates. → Document in `RECOVERY.md` that deleting the database triggers a reseed from
  the current build, and that a spreadsheet re-import is the supported path for data refresh.
- **Same applies to `config/config.ini` defaults.** A shipped default change will not reach an
  existing installation. → Acceptable; the file is edited by the user anyway.
- **`os.chdir` is process-global.** Any code that assumed the original working directory changes
  behaviour. → Call it once, as the first action in `main()`, before logging and database setup.
- **Two instances started from the same folder share one SQLite file.** → Accepted; SQLite locking
  makes this a slow operation rather than corruption, and the application is single-user.
- **Seeded files are copies, so disk usage doubles on first run** (bundle copy plus extracted
  files). → About 1.3 MB; the one-file executable already extracts far more.

## Migration Plan

No migration is required. Source runs keep the project layout. Packaged builds produced before
this change stored their state in a temporary directory that no longer exists after exit, so there
is nothing to carry forward.

Rollback is a revert of the change: the previous behaviour resolves paths from `__file__` again.

## Open Questions

- Whether the user's observatory coordinates belong in a version-controlled `config/config.ini` at
  all. It affects portability and privacy of the repository, not the approach chosen here, and can
  be decided separately.

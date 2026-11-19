# Recovery

How to restore NextAstroTarget after a lost machine or disk. The application is
portable: everything that matters lives next to the executable, and the code is in Git.

## What to back up

Only two files hold state that cannot be regenerated:

| File | Size | What it holds |
| --- | --- | --- |
| `data/astro_targets.db` | ~1.3 MB | catalogue (3143 objects) + user settings (`app_settings`) |
| `config/config.ini` | ~1 KB | observatory location and ranges |

Together these are about 1.3 MB. Everything else — the executable, logs, image and moon
caches — is rebuildable or disposable:

- The executable is built from `main_pyside6.py` + `build_exe.spec`.
- Logs, `data/image_cache`, and `data/moon_cache` regenerate on their own.

The spreadsheet source of the catalogue is `*.xlsm` and is **not** tracked in Git; the
database file above replaces it for recovery purposes.

## How to restore on a new machine

1. Clone the repository.
2. Drop the two backed-up files into place:
   - `<repo>/data/astro_targets.db`
   - `<repo>/config/config.ini`
3. Build the executable (see `BUILD_EXE.md`):
   ```powershell
   .venv\Scripts\pyinstaller.exe build_exe.spec --clean --noconfirm
   ```
4. Run `dist/NextAstroTarget.exe`. It starts with your catalogue and settings.

If you placed the executable (and its folder) anywhere you like instead of building, just
restore the two files beside it and run.

## Refreshing the catalogue from a newer build

The application seeds `data/astro_targets.db` from the copy bundled inside the executable
**only when the file does not exist**. To pick up a catalogue shipped with a newer executable,
delete `data/astro_targets.db`, then run the application once; it reseeds from that build.
Your settings in `app_settings` are part of the seeded file, so set them again afterwards.

The supported way to refresh catalogue data without losing settings is to re-import the
spreadsheet from inside the application; the import rebuilds the catalogue tables and leaves
`app_settings` intact.

## If the desktop shortcut stops working

The shortcut stores an absolute path. If the folder moved or the drive letter changed, run
`NextAstroTarget.exe` directly from its folder; the application will repair the shortcut per
the desktop-shortcut change.

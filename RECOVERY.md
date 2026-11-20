# Recovery

How to restore NextAstroTarget after a lost machine or disk. The application is
portable: everything that matters lives next to the executable, and the code is in Git.

## What to back up

Three items hold state that cannot be regenerated:

| Item | Size | What it holds |
| --- | --- | --- |
| `data/astro_targets.db` | ~1.3 MB | catalogue + user settings (`app_settings`) + object media references |
| `config/config.ini` | ~1 KB | observatory location and ranges |
| `*.xlsm` (the spreadsheet) | ~35 MB | the catalogue source, including the embedded preview photographs |

Together these are about 36 MB. Everything else — the executable, logs, and the generated
`data/object_images/`, `data/image_cache`, and `data/moon_cache` — is rebuildable or disposable:

- The executable is built from `main_pyside6.py` + `build_exe.spec`.
- `data/object_images/` regenerates when the import runs (it extracts the previews from the
  spreadsheet).
- Logs, `data/image_cache`, and `data/moon_cache` regenerate on their own.

The spreadsheet is in `.gitignore` and lives only on disk, so it is part of the backup set rather
than relying on Git.

## How to restore on a new machine

1. Clone the repository.
2. Drop the three backed-up items into place:
   - `<repo>/data/astro_targets.db`
   - `<repo>/config/config.ini`
   - the `<...>.xlsm` spreadsheet file (the path from `config.ini` → `[Database] excel_file`)
3. Build the executable (see `BUILD_EXE.md`):
   ```powershell
   .venv\Scripts\pyinstaller.exe build_exe.spec --clean --noconfirm
   ```
4. Run `dist/NextAstroTarget.exe`. It starts with your catalogue and settings, and shows the
   survey image for objects until you re-run the import.
5. Re-run the import once to regenerate the object preview images and Astrobin links.

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
`NextAstroTarget.exe` directly from its folder once; on startup the application re-points the
shortcut at the current location. This applies only when the shortcut was previously created
through the application's first-run prompt.

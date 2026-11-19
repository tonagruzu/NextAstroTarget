# Tasks

## 1. Application home

- [ ] 1.1 Add a single path helper exposing the application home: `sys.executable` parent when `sys.frozen` is set, otherwise `__file__` parent, resolved absolute. Verify by running a one-line import that prints the home in source mode and confirming it equals the project root.
- [ ] 1.2 Replace the working-directory resolution in `main_pyside6.py` with the helper, called as the first action in `main()` before logging setup. Verify `python main_pyside6.py --test-startup` still prints "Startup test passed".
- [ ] 1.3 Add the startup writability check: create the data directory under the home, and on failure report the failing path and exit non-zero instead of continuing. Verify by running `--test-startup` from a folder with the write permission removed (or by pointing the helper at a read-only path) and confirming the message names the path.

## 2. First-run seeding

- [ ] 2.1 Seed `config/config.ini` from the bundle when absent (bundle root `sys._MEIPASS` when frozen, project root otherwise). Verify that deleting `config/config.ini` and running `--test-startup` recreates it with the same contents.
- [ ] 2.2 Seed `data/astro_targets.db` from the bundle when absent. Verify that deleting `data/` and running `--test-startup` recreates the database and that `SELECT COUNT(*) FROM Main` returns 3143.
- [ ] 2.3 Confirm seeding never overwrites: modify a value in the existing database, run `--test-startup`, and verify the modification survives.

## 3. Unified cache and log paths

- [ ] 3.1 Point `src/utils/image_service.py` `DEFAULT_CACHE_DIR` at the helper instead of its own `__file__` arithmetic. Verify the printed default resolves under the application home in source mode.
- [ ] 3.2 Confirm the logger and database manager resolve through the home as well, and remove any remaining `__file__`-based path arithmetic in `src/`. Verify by searching `src/` for `dirname` path construction and finding none.

## 4. Observatory settings persistence

- [ ] 4.1 Make the observatory configuration write to the home's `config/config.ini` and confirm the read path uses the same location. Verify that changing the location, closing and reopening the application in source mode shows the new value.

## 5. Documentation

- [ ] 5.1 Write `RECOVERY.md`: what to back up (`data/astro_targets.db`, `config/config.ini`, about 1.3 MB), how to restore on a new machine (clone, restore the two files, rebuild the executable), and the note that deleting `data/astro_targets.db` triggers a reseed from the current build. Verify by following the procedure on a fresh clone and reaching a working launch.

## 6. Packaged verification

- [ ] 6.1 Rebuild the executable and run it from a folder other than the repository. Verify that `data/`, `logs/` and `config/` appear next to the executable and that the object list loads 3139 objects.
- [ ] 6.2 Restart the same executable after changing the observatory location. Verify the change is present, the log file contains entries from both sessions, and no new `_MEI` directory is left holding application data.
- [ ] 6.3 Repeat the launch from a copy of the folder at a different path. Verify the application starts with its data intact and that nothing depends on the original path.

## Workflow follow-up

- Archive the change after the verification above passes.

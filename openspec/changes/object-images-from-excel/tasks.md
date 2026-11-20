# Tasks

## 1. Extractor module

- [x] 1.1 Create `src/utils/object_media_extractor.py` that parses the comment VML drawing and the `xl/media` ZIP entries to produce a mapping from object name to embedded image, plus reads the column-A hyperlink per object. Verify against the configured 2023 workbook that it yields ~3100 mapped images and that sampled names match their spreadsheet rows.
- [x] 1.2 Copy each mapped image into `data/object_images/<sanitized-name>.jpg` and return the relative path. Verify a fresh extraction produces files and that a name-collision is skipped with a log line rather than overwriting.

## 2. Database schema and import

- [x] 2.1 Add an `object_media(object_name, image_path, astrobin_url)` table created during initialization alongside the sheet tables. Verify the table exists and is empty before a first import.
- [x] 2.2 Integrate the extractor and hyperlink reading into `initialize_database`, populating `object_media` after the sheet tables. Verify a fresh import of the configured workbook stores image paths and Astrobin URLs for objects that have them.

## 3. Display with fallback

- [x] 3.1 Point the object image-loading path at `object_media` first and `ImageService` (`hips2fits`) second. Verify in source mode that selecting an object with a preview shows it, and one without shows the survey image.
- [x] 3.2 Make a missing preview file on disk fall back to the survey image without an error. Verify by temporarily removing an object's image file and confirming the view still renders.

## 4. Open Astrobin action

- [x] 4.1 Add an "open on Astrobin" action that calls `QDesktopServices.openUrl` with the object's stored URL. Verify that triggering it resolves the URL for a known object (and that a missing URL disables the action).

## 5. Documentation and housekeeping

- [x] 5.1 Add `data/object_images/` to `.gitignore`. Verify `git check-ignore` reports it ignored.
- [x] 5.2 Update `RECOVERY.md`: the backup set is now `data/astro_targets.db`, `config/config.ini` and the spreadsheet file (~36 MB), and a restore must re-run the import to regenerate images. Verify the documented steps match the implemented import behaviour.

## 6. Packaged verification

- [x] 6.1 Rebuild and run the packaged executable; verify the object list loads and previews render for objects that have them (survey image otherwise), without requiring network for the previews.

## Workflow follow-up

- Archive the change after the verification above passes.

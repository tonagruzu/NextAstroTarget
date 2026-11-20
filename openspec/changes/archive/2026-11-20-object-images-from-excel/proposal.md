# Proposal

## Why

The application shows sky-survey images fetched by coordinate (`hips2fits`), not the author's own
photographs. Its Astrobin integration is broken: the value mapped as `astrobin_id` (`Unnamed: 48`)
contains misaligned data, so the object links do not resolve. The new `Imm Deep Sky Compendium -
2026 - rev6c.xlsm` ships, for every object, both an embedded preview photograph and a hyperlink to
the author's full image on Astrobin. These are the images a user actually wants to see.

## What Changes

- Import extracts the embedded per-object preview photographs from the workbook and stores them
  beside the database, mapped to each object.
- Import reads the Astrobin page hyperlink from the spreadsheet and stores it per object.
- The object view displays the author's preview photograph, falling back to the existing
  `hips2fits` survey image when no preview is present.
- An action opens the object's Astrobin page in the default browser.
- Images and links are extracted from the spreadsheet the configuration points at (currently the
  2023 workbook, which already embeds 3232 preview images), keyed by object name so they match the
  existing database exactly.

Explicitly out of scope: downloading full-resolution Astrobin images inside the application
(Astrobin blocks non-browser clients), and any catalogue migration to the 2026 workbook including
its added columns, header-layout changes or renamed objects.

## Capabilities

### New Capabilities

- `object-images`: per-object preview images sourced from the spreadsheet, display with
  survey-image fallback, and opening the author's Astrobin page from the application.

### Modified Capabilities

None.

## Impact

- `src/database/database_manager.py` — importer: value import via `pandas`, plus a new pass that
  reads hyperlinks with `openpyxl` and extracts embedded images from the workbook package.
- `src/gui/pyside6_target_selection.py` and `src/gui/pyside6_main_window.py` — image display and
  the "open on Astrobin" action.
- `src/utils/image_service.py` — remains as the fallback image source (unchanged behaviour).
- `data/object_images/` — new generated image store (gitignored).
- `RECOVERY.md` — backup set grows from two files to include the spreadsheet source.
- `.gitignore` — ignore `data/object_images/`.

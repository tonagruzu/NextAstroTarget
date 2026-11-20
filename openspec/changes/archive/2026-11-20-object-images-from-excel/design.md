# Design

## Context

Refer to `proposal.md` for motivation. Verified facts about the spreadsheets (the configuration
points at the 2023 workbook today, and both editions embed the same artefacts):

- Column A carries the **hyperlink** to the author's Astrobin page, one per object.
- The preview photographs are embedded in `xl/media/` (3232 files in the 2023 workbook) and wired
  into the sheet through the comment VML drawing `xl/drawings/vmlDrawing1.vml`: each comment shape's
  `<v:fill o:relid>` references an image, and `<x:Anchor>` gives the row. The anchor row matches
  column A of the object (verified against the 2026 file: `Barnard 007`, `IC 1396`, …).
- Previews are 260×260 px, ~10 KB each.
- The 2026 workbook renames a handful of objects and adds columns; it is out of scope here, so
  extraction stays keyed to the file the configuration points at.
- The current importer uses `pandas.read_excel` with default header detection, which drops
  hyperlinks and images and stores the title row and label rows as data — the `astrobin_id`
  mapping (`Unnamed: 48`) is therefore garbage.
- `src/utils/image_service.py` fetches survey images from `hips2fits`; `pyside6_target_selection`
  already shows images through it.

## Goals / Non-Goals

**Goals:**

- Import the embedded preview and the Astrobin link for each object, keyed by object name.
- Show the preview with `hips2fits` as fallback, and open the Astrobin page from the UI.

**Non-Goals:**

- Downloading full-resolution Astrobin images inside the app (blocked by Astrobin).
- Editing catalogue data beyond what the spreadsheet contains.

## Decisions

**Two sources, two pass rules.** Values keep coming through `pandas`; hyperlinks come through
`openpyxl` (`cell.hyperlink.target`), and images come straight from the workbook ZIP by parsing the
VML drawing and reading `xl/media/`. Pandas cannot see either, so these are separate passes.

**Images are keyed by object name in a dedicated table.** A new table
`object_media(object_name TEXT PRIMARY KEY, image_path TEXT, astrobin_url TEXT)` avoids touching the
pandas-generated `Main` table (which is rebuilt on every import). The object name is the stable key
across imports.

**Image files land in `data/object_images/<sanitized-name>.jpg`.** The filename is the object name
with non-alphanumeric characters replaced by underscores. Names are unique per the publication
(one row per object).

**Row mapping drives extraction.** For every `<v:fill o:relid>` in the comment drawing, the
`<x:Anchor>` row is resolved to the object name in column A; the rels file maps the id to a
`xl/media/` file, which is copied to the image store. The same pass records the column-A hyperlink
target as `astrobin_url`.

**Display prefers the preview, then the survey.** The image-loading path in
`pyside6_target_selection` checks `object_media` first and falls back to `ImageService`
(`hips2fits`) — also covering the restored-DB-without-images state, where the reference exists but
the file does not.

**"Open on Astrobin" uses the desktop URL handler.** `QDesktopServices.openUrl` launches the
default browser with the stored URL, exactly as the spreadsheet does.

## Risks / Trade-offs

- **Previews are low-resolution.** 260×260 is fine for a list thumbnail or tooltip; the full image
  lives on Astrobin and opens in the browser. → Accepted.
- **Import becomes heavier.** Parsing a 5 MB VML and copying 3144 files adds time and ~31 MB to
  `data/`. → Progress callbacks are reused; the cost is one-off per import.
- **Sanitized filenames could collide** if two distinct names map to the same sanitized string. →
  Names are unique by construction; a collision is detected and skipped with a log line rather
  than overwriting silently.
- **Astrobin is an external page.** Opening it depends on the user having a browser and network. →
  Out of scope concerns; the action is best-effort.

## Migration Plan

No catalogue migration. `object_media` is populated by the existing import against the configured
spreadsheet (2023 today), which also regenerates `data/object_images/`. Existing `app_settings`
survive because the import only replaces sheet tables. Rollback is a revert; the generated image
directory is ignored by git and can be deleted freely.

## Open Questions

None that change the approach or task breakdown.

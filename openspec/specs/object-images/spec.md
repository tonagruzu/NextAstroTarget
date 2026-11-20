# object-images Specification

## Purpose
Displays the spreadsheet's own per-object preview photographs in the application, uses the survey
image as a fallback, and lets the user open the author's full image on Astrobin.

## Requirements

### Requirement: Import extracts per-object images

When the database is initialized or re-imported from the spreadsheet, the application SHALL extract
the embedded preview image for each object and store it so it can be shown for that object.

#### Scenario: Import produces an image per object
- **WHEN** a spreadsheet that embeds preview images is imported
- **THEN** a preview image is available on disk for every object that has one, mapped by object

### Requirement: Import records the Astrobin link

When importing, the application SHALL store the Astrobin page hyperlink associated with each object.

#### Scenario: Link is stored per object
- **WHEN** an object has an Astrobin hyperlink in the spreadsheet
- **THEN** the object's stored Astrobin URL points at that hyperlink

### Requirement: Object view shows the preview with survey fallback

The object view SHALL display the object's preview photograph when present, and the sky-survey
image otherwise.

#### Scenario: Preview is shown when available
- **WHEN** the selected object has a stored preview image
- **THEN** the preview image is displayed

#### Scenario: Survey image shown otherwise
- **WHEN** the selected object has no stored preview image
- **THEN** the sky-survey image is displayed instead

### Requirement: Open Astrobin from the application

The application SHALL provide an action that opens the object's Astrobin page in the default
browser.

#### Scenario: Action opens the page
- **WHEN** the user triggers the "open on Astrobin" action for an object with a stored URL
- **THEN** the default browser opens the object's Astrobin page

### Requirement: Missing images do not break the view

The object view SHALL degrade gracefully when a stored image is missing from disk, such as after a
restore that has not yet re-run the import.

#### Scenario: Restored database without extracted images
- **WHEN** an object references a preview file that does not exist on disk
- **THEN** the view falls back to the survey image without showing an error

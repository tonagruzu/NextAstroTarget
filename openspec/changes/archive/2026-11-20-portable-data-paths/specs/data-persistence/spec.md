# Spec Delta

## Purpose

Defines where the application keeps its runtime data in both source and packaged builds, how
that location is resolved, and which guarantees ensure that state survives a restart.

## ADDED Requirements

### Requirement: Runtime data lives beside the executable

When the application runs from a packaged executable, runtime data SHALL be stored in the
directory that contains that executable. When it runs from source, the project directory SHALL
be used. Runtime data SHALL NOT be stored in a temporary extraction directory.

#### Scenario: Packaged launch writes beside the executable
- **WHEN** the packaged application is started from a folder
- **THEN** the log file, caches and database are created in that folder

#### Scenario: Packaged launch does not write to a temporary directory
- **WHEN** the packaged application has been running and is then closed
- **THEN** the data written during the session is still present in the executable's folder

#### Scenario: Source launch keeps the project layout
- **WHEN** the application is started from source in the project
- **THEN** runtime data is created under the project directory

### Requirement: Runtime state survives a restart

Data written during a session SHALL still be available the next time the application starts.

#### Scenario: Observatory location is remembered
- **WHEN** the user changes the observatory location and closes the application
- **THEN** the next start shows the changed location without any manual step

#### Scenario: Logs accumulate across runs
- **WHEN** the application is started a second time
- **THEN** the log file contains entries from both sessions

### Requirement: Bundled files are seeded on first run

When a required runtime file is missing, the application SHALL create it by copying the version
shipped inside the executable. An existing file SHALL NOT be overwritten.

#### Scenario: First run creates the catalogue
- **WHEN** the application starts in a folder that has no data directory
- **THEN** the catalogue database is created from the bundled copy and the object list loads

#### Scenario: Existing data is preserved
- **WHEN** the catalogue database already exists next to the executable
- **THEN** startup leaves that file unchanged

### Requirement: Catalogue refresh preserves user settings

Refreshing catalogue contents from the spreadsheet SHALL NOT remove user settings.

#### Scenario: Import after a settings change
- **WHEN** the user imports the spreadsheet while custom filter settings are stored
- **THEN** the import completes and the stored settings are unchanged

### Requirement: Unwritable location is reported

If runtime data cannot be written next to the executable, the application SHALL report the
failure instead of continuing with silent data loss.

#### Scenario: Read-only folder
- **WHEN** the application starts in a folder where it cannot create its data directory
- **THEN** the user is told which path could not be written

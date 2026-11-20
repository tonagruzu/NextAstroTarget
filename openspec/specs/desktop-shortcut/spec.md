# desktop-shortcut Specification

## Purpose
Keeps a working desktop shortcut to the application, created on the user's request and repaired
when the application is moved, so a portable install always has one predictable way to launch.

## Requirements

### Requirement: Shortcut can be created on first run

On first launch the application SHALL offer to create a desktop shortcut pointing at the
running executable, and create it when the user accepts, whether or not a shortcut from an
earlier build already exists.

#### Scenario: User accepts the offer
- **WHEN** the application starts for the first time and the user accepts the shortcut offer
- **THEN** a desktop shortcut is created whose target is the running executable

#### Scenario: User declines the offer
- **WHEN** the application offers a shortcut and the user declines
- **THEN** no shortcut is created and the choice is remembered

### Requirement: Shortcut launches the current executable

The shortcut SHALL point at the executable itself, with its working directory set to the folder
containing the executable, rather than at a script or interpreter.

#### Scenario: Shortcut launches the packaged build
- **WHEN** the user starts the application from the shortcut of a packaged build
- **THEN** the packaged executable runs with runtime data beside it

### Requirement: Shortcut is repaired after the application moves

On startup the application SHALL detect a shortcut whose target no longer matches the running
executable and update it to the current location.

#### Scenario: Folder moved after creation
- **WHEN** the application is started from a new folder via the executable itself
- **THEN** the existing desktop shortcut is updated to point at the new location

### Requirement: Shortcut uses the application icon

The shortcut SHALL use the icon embedded in the executable rather than an external icon file.

#### Scenario: No external icon file is required
- **WHEN** the shortcut is created or repaired
- **THEN** it renders the application icon without relying on a separate `.ico` beside the executable

### Requirement: Repair does not overwrite a user-removed shortcut

The application SHALL NOT recreate a shortcut the user deleted unless they ask for it again.

#### Scenario: User deletes the shortcut
- **WHEN** the user removes the desktop shortcut and starts the application again
- **THEN** the application does not silently recreate it

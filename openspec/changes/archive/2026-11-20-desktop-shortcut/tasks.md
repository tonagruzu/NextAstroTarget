# Tasks

## 1. Shortcut module

- [x] 1.1 Create `src/utils/desktop_shortcut.py` exposing create, read and repair of a Windows `.lnk` through `WScript.Shell`/VBScript, with the desktop directory injectable (default `Path.home() / "Desktop"`), icon location `<exe>,0`, and working directory set to the executable's folder. Verify by calling it from source with a temporary desktop directory and asserting the created `.lnk` target reads back as the running executable.
- [x] 1.2 Guard the module so it is a no-op off Windows, and wrap VBScript failures so they log a warning and never abort startup. Verify the guard evaluates true on this Windows machine and that a forced script failure returns a logged error rather than raising.

## 2. Opt-in persistence

- [x] 2.1 Store the shortcut choice in `app_settings` (`shortcut_enabled` with values `yes`/`no`, absent until asked), reusing the database manager's setting helpers. Verify setting a value and reconnecting the database returns the same value.

## 3. Startup hook

- [x] 3.1 Add the first-run/startup flow to the main window after the database is ready: when the setting is unset and no shortcut exists, offer to create one and record the answer; when `yes` and an existing shortcut target is stale, repair it; otherwise do nothing. Verify with a temporary desktop directory that accepting writes the setting and creates the shortcut.
- [x] 3.2 Verify the repair branch: with a fabricated `.lnk` whose target points elsewhere and the setting `yes`, running the flow updates the target to the current executable and leaves the user's desktop otherwise untouched.

## 4. Documentation

- [x] 4.1 Confirm `RECOVERY.md` documents that a stale shortcut is repaired by launching the executable directly once, and note the opt-in behaviour where launch instructions are described. Verify the written steps match the implemented behaviour.

## 5. Packaged verification

- [x] 5.1 Build the executable and run it from a staging folder with a pre-seeded `shortcut_enabled=yes` and a stale `.lnk`; verify the shortcut target is updated to the staging executable. Verify the `.lnk` icon resolves to the executable and its working directory is the staging folder.
- [x] 5.2 Move the staging folder to a different path and run again; verify the shortcut now points at the moved location.

## Workflow follow-up

- Archive the change after the verification above passes.

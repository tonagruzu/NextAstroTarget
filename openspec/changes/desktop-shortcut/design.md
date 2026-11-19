# Design

## Context

The application is portable after the `portable-data-paths` change: runtime data lives beside the
executable. A shortcut is the one thing a portable install still needs to be findable. The only
shortcut code today (`create_desktop_shortcut.py`) is a development helper: it targets
`sys.executable` plus `main_pyside6.py`, points the icon at a repository `assets/icon.ico`, and is
not bundled into the executable. Windows `.lnk` files store an absolute target, so a shortcut goes
stale when the folder moves or a removable drive changes letter.

The desktop location is resolved from the user's home, and the packaged build runs with no console
(`build_exe.spec` sets `console=False`).

## Goals / Non-Goals

**Goals:**

- A one-click, self-repairing desktop shortcut for a portable install.
- No new third-party dependencies; work within the Python standard library and Windows shell.
- Respect the user's desktop: create nothing without consent and never silently recreate a
  shortcut they deleted.

**Non-Goals:**

- An installer or Start Menu placement.
- Reworking the repository-root development shortcut scripts.

## Decisions

**Create and inspect `.lnk` through `WScript.Shell`, driven by a generated VBScript.** This is the
same mechanism the existing development script already uses, needs no external packages, and can
both write a shortcut and read an existing one's target. *Alternative rejected:* ctypes against the
`IShellLink` COM interface removes the subprocess but adds a large amount of fragile structure
definition for no functional gain.

**The shortcut target is the executable itself, with `IconLocation` set to `<exe>,0`.** PyInstaller
embeds the icon, so the shortcut never depends on a loose `.ico` beside the executable. The working
directory is set to the executable's folder as a belt-and-braces measure behind `app_home()`.

**A persisted opt-in beats a silent create.** A setting (`shortcut_enabled`, stored in
`app_settings`) tracks the user's choice so the question is asked at most once. On startup after the
database is ready the application follows:

```
        setting is None                setting = "yes"            setting = "no"
        --------------                -----------------          --------------
   .lnk absent -> prompt          .lnk present + stale ->    do nothing
   accept   -> create + "yes"         repair
   decline  -> "no"               .lnk present + current
                                      -> do nothing
                                  .lnk absent -> do nothing
```

The `.lnk absent` branch under `"yes"` intentionally does nothing: the user may have deleted the
shortcut, and requirement 5 forbids silently recreating it. A moved folder still repairs correctly
because in that case the `.lnk` exists and is merely stale.

**The prompt is a single modal question on the first relevant startup.** It is one-time and the
least intrusive option that still satisfies "offer to create". In a windowed build the question is
shown with `QMessageBox`.

**The shortcut is looked up at `Path.home() / "Desktop"`.** This matches the existing script and is
correct for the common layout.

## Risks / Trade-offs

- **VBScript execution can be blocked** by policy or antivirus. → The operation is wrapped so a
  failure logs a warning and never aborts startup.
- **OneDrive can redirect the Desktop**, so `Path.home()/Desktop` would point at the wrong place. →
  Accepted for now; recorded as an open question. Resolving the real desktop via the Windows known
  folder API would need shell folder code and is not required for the common case.
- **The shortcut cannot self-repair when it is the only way to launch.** If a drive letter changes,
  the stale shortcut must be bypassed by running the executable directly once. → Documented in
  `RECOVERY.md`; the shortcut is repaired on that next direct launch.
- **Two copies of the app in different folders fight over one desktop shortcut.** → The most
  recently started copy "wins"; accepted trade-off for a single-user portable app.

## Migration Plan

No migration. Before this change a packaged build had no shortcut at all. Rollback is a revert:
remove the hook and the module, leaving any created `.lnk` as an inert file the user can delete.

## Open Questions

- Whether to resolve the desktop through the Windows known-folder API instead of
  `Path.home()/Desktop`, to handle OneDrive redirection. It changes only where the shortcut lands,
  not the approach or task breakdown.

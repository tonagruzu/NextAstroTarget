# kitty-specs — historical record (frozen)

This directory holds the completed **001-better-astro-photos** mission produced by
the Spec Kitty workflow. All work packages (WP01–WP05) reached `approved`.

## Status: FROZEN

As of 2026-11-19 this project uses **OpenSpec** for spec-driven development.
Nothing in this directory is maintained, and no new missions are added here.

- Do not edit these files.
- Do not create new `0NN-*` mission directories.
- Do not treat `status.json` / `lanes.json` as current project state.

## Current workflow

| Path / command | Purpose |
| --- | --- |
| `openspec/specs/` | Specifications — the source of truth |
| `openspec/changes/` | Change proposals in flight |
| `openspec/changes/archive/` | Completed, archived changes |
| `/opsx-propose` | Create a change with proposal, design and tasks |
| `/opsx-apply` | Implement the tasks of a change |
| `/opsx-archive` | Close a change and update the main specs |
| `/opsx-explore` | Think through a problem before proposing |

CLI equivalents: `openspec list`, `openspec show <change>`,
`openspec validate --all`, `openspec status`.

This directory is kept as an audit trail of how the image-service work was
planned and sequenced. Delete it in a single commit whenever that history stops
being useful.

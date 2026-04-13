---
work_package_id: WP05
title: Testing and Validation
dependencies:
- WP01
- WP02
- WP03
- WP04
requirement_refs:
- FR-1
- FR-2
- FR-3
- FR-4
- FR-5
- FR-6
- FR-7
- FR-8
planning_base_branch: main
merge_target_branch: main
branch_strategy: Planning artifacts for this feature were generated on main. During /spec-kitty.implement this WP may branch from a dependency-specific base, but completed changes must merge back into main unless the human explicitly redirects the landing branch.
subtasks:
- 'T001: Test survey fallback chain'
- 'T002: Test disk cache persistence and eviction'
- 'T003: Test adaptive FOV for various object sizes'
- 'T004: Visual quality comparison'
- 'T005: UI responsiveness verification'
phase: Phase 5 - Testing
assignee: ''
agent: ''
history:
- timestamp: '2026-04-13T18:00:00Z'
  agent: system
  action: Prompt generated via /spec-kitty.tasks
authoritative_surface: test_image_service.py
execution_mode: code_change
owned_files:
- test_image_service.py
tags: []
---

# Work Package Prompt: WP05 – Testing and Validation

## Objective

Validate the complete image service integration across both UI backends, ensuring image quality improvement, fallback reliability, cache correctness, and UI responsiveness.

## Requirements

### T001: Test Survey Fallback Chain

Create `test_image_service.py` with tests:

1. **Northern sky object** (M31: RA=10.685, Dec=41.269) — should return PanSTARRS image
2. **Southern sky object** (NGC 104/47 Tuc: RA=6.024, Dec=-72.081) — should fall back to DSS2 (below PanSTARRS dec limit)
3. **SDSS coverage area** (M51: RA=202.47, Dec=47.195) — should return PanSTARRS or SDSS9
4. **Invalid coordinates** (RA=999, Dec=999) — should return None gracefully
5. **Verify source labels** — returned source label matches expected survey

### T002: Test Disk Cache

1. Fetch an image → verify file exists in `data/image_cache/`
2. Fetch same object again → verify no network request (mock or timing check)
3. Verify `.cache_index.json` contains the entry
4. Simulate cache over 500 MB → verify eviction reduces to ~400 MB
5. Restart (new `DiskImageCache` instance) → verify cache still works

### T003: Test Adaptive FOV

Verify FOV calculation for various inputs:

| Input (arcmin) | Expected FOV (deg) |
|---|---|
| `None` | 0.25 |
| `0` | 0.25 |
| `5.0` | 0.167 |
| `30.0` | 1.0 |
| `120.0` | 2.0 (clamped) |
| `0.5` | 0.05 (clamped min) |

### T004: Visual Quality Comparison

Manual test — compare side by side:
1. Open the app, search for M42 (Orion Nebula)
2. Verify detail dialog shows a **color** image (not grayscale)
3. Compare with old DSS image quality
4. Check that the image is properly framed (object centered, reasonable zoom)

Objects to test:
- M42 (large nebula, ~85 arcmin)
- M31 (large galaxy, ~190 arcmin)
- NGC 7331 (small galaxy, ~10 arcmin)
- M57 (tiny planetary nebula, ~1.4 arcmin)
- Abell 39 (faint planetary nebula)

### T005: UI Responsiveness

1. Open Quick Search, browse objects rapidly
2. Verify tooltips appear without lag
3. Verify detail dialog opens quickly (image may load async)
4. Verify the table remains scrollable while images load
5. Check no UI freeze during first-time fetches (cache empty)

## Acceptance Criteria

- [ ] All survey fallback paths produce valid images
- [ ] Disk cache works across app restarts
- [ ] Cache eviction correctly removes oldest entries
- [ ] Color images visible for M42, M31, M51 (major objects)
- [ ] Source label correctly identifies the survey
- [ ] No UI blocking or freezing during image operations

## Files to Create

- **CREATE**: `test_image_service.py` (automated tests for T001-T003)

## Dependencies

- **WP01** through **WP04** — all implementation must be complete.

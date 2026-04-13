---
work_package_id: WP03
title: PySide6 UI Integration
dependencies:
- WP01
- WP02
requirement_refs:
- FR-4
- FR-5
- FR-6
- FR-8
planning_base_branch: main
merge_target_branch: main
branch_strategy: Planning artifacts for this feature were generated on main. During /spec-kitty.implement this WP may branch from a dependency-specific base, but completed changes must merge back into main unless the human explicitly redirects the landing branch.
subtasks:
- 'T001: Replace image fetch methods with ImageService'
- 'T002: Increase detail dialog image to 600×600'
- 'T003: Add survey source label to detail dialog'
- 'T004: Update tooltip to use cached images'
phase: Phase 3 - PySide6 UI
assignee: ''
agent: ''
history:
- timestamp: '2026-04-13T18:00:00Z'
  agent: system
  action: Prompt generated via /spec-kitty.tasks
authoritative_surface: src/gui/pyside6_target_selection.py
execution_mode: code_change
owned_files:
- src/gui/pyside6_target_selection.py
tags: []
---

# Work Package Prompt: WP03 – PySide6 UI Integration

## Objective

Update the PySide6 UI (`src/gui/pyside6_target_selection.py`) to use the new `ImageService` for fetching astronomical images, replacing the existing SDSS/DSS fetch methods.

## Context

The PySide6 target selection GUI currently has its own image fetching logic:
- `load_dss_image()` at ~line 775 — orchestrates loading
- `_try_load_sdss()` at ~line 810 — SDSS cutout API
- `_try_load_dss()` at ~line 856 — DSS via STScI with RGB composite
- Pseudo-color fallback at ~line 956

The detail dialog is at `show_object_detail_dialog()` ~line 1020 with a 400×400 image area.

In-memory cache at `self.image_cache = {}` stores `(QPixmap, source_name)` tuples.

## Requirements

### T001: Replace Image Fetch Methods

1. Import `ImageService` at the top of the file:
   ```python
   from src.utils.image_service import ImageService
   ```

2. Initialize a shared `ImageService` instance in the class `__init__`:
   ```python
   self._image_service = ImageService()
   ```

3. Replace the body of `load_dss_image()` to call `ImageService.fetch_object_image()`:
   ```python
   def load_dss_image(self, ra_deg, dec_deg, object_name=None, astrobin_id=None, diameter_arcmin=None):
       cache_key = f"img_{ra_deg:.3f}_{dec_deg:.3f}"
       if cache_key in self.image_cache:
           return self.image_cache[cache_key]
       
       result = self._image_service.fetch_object_image(
           ra_deg=ra_deg,
           dec_deg=dec_deg,
           diameter_arcmin=diameter_arcmin,
           width=600,
           height=600,
       )
       
       if result:
           image_bytes, source_label = result
           pixmap = QPixmap()
           pixmap.loadFromData(image_bytes)
           self.image_cache[cache_key] = (pixmap, source_label)
           return (pixmap, source_label)
       
       self.image_cache[cache_key] = None
       return None
   ```

4. Remove or deprecate `_try_load_sdss()`, `_try_load_dss()`, and the pseudo-color fallback methods since they are no longer needed.

### T002: Increase Detail Dialog Image to 600×600

In `show_object_detail_dialog()`:
- Change the image label size from 400×400 to 600×600
- Adjust the dialog layout to accommodate the larger image
- Ensure the pixmap is scaled to 600×600 with `Qt.KeepAspectRatio` and `Qt.SmoothTransformation`

### T003: Add Survey Source Label

In the detail dialog, add a small label below the image showing the survey source:
```python
source_label = QLabel(f"Image: {source_name}")
source_label.setAlignment(Qt.AlignCenter)
source_label.setStyleSheet("color: #888; font-size: 10px;")
```

### T004: Update Tooltip to Use Cached Images

The hover tooltip should also benefit from the new image service:
- When generating tooltip content, use `ImageService` (which checks disk cache first)
- Downscale the 600×600 image to fit the 300×250 tooltip area
- The tooltip already runs image loading in a background thread — preserve this

## Acceptance Criteria

- [ ] Right-clicking an object shows the detail dialog with a color image from hips2fits
- [ ] Detail dialog shows 600×600 image (increased from 400×400)
- [ ] Survey source name is displayed below the image
- [ ] Tooltip hover shows a downscaled preview of the same image
- [ ] No UI freezing — image loading remains in background thread
- [ ] In-memory cache still works for the current session
- [ ] Old SDSS/DSS fetch methods are removed or deprecated

## Files to Modify

- **MODIFY**: `src/gui/pyside6_target_selection.py`

## Dependencies

- **WP01** — ImageService module
- **WP02** — DiskImageCache for persistent caching

## Activity Log

- 2026-04-13T18:16:23Z – unknown – Moved to in_progress

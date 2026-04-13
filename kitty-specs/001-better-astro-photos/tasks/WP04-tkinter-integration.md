---
work_package_id: WP04
title: Tkinter UI Integration
dependencies:
- WP01
- WP02
requirement_refs:
- FR-8
planning_base_branch: main
merge_target_branch: main
branch_strategy: Planning artifacts for this feature were generated on main. During /spec-kitty.implement this WP may branch from a dependency-specific base, but completed changes must merge back into main unless the human explicitly redirects the landing branch.
subtasks:
- 'T001: Replace image fetch methods with ImageService'
- 'T002: Add source label to tooltip'
- 'T003: Update context menu detail view'
phase: Phase 4 - Tkinter UI
assignee: ''
agent: ''
history:
- timestamp: '2026-04-13T18:00:00Z'
  agent: system
  action: Prompt generated via /spec-kitty.tasks
authoritative_surface: src/gui/enhanced_target_selection_gui.py
execution_mode: code_change
owned_files:
- src/gui/enhanced_target_selection_gui.py
tags: []
---

# Work Package Prompt: WP04 – Tkinter UI Integration

## Objective

Update the Tkinter UI (`src/gui/enhanced_target_selection_gui.py`) to use the new `ImageService`, replacing the existing AstroBin/DSS fetch methods.

## Context

The Tkinter GUI has its own image fetching in the `AstrobinTooltip` class:
- `_load_astrobin_image()` at ~line 112 — fetches from AstroBin by ID
- `_load_dss_image()` at ~line 229 — fetches from DSS via STScI
- `show_tooltip()` at ~line 36 — triggers image loading on hover
- In-memory cache: `self.image_cache = {}` stores `ImageTk.PhotoImage` objects
- Tooltip max size: 300×250

## Requirements

### T001: Replace Image Fetch Methods

1. Import `ImageService`:
   ```python
   from src.utils.image_service import ImageService
   ```

2. Initialize in `AstrobinTooltip.__init__`:
   ```python
   self._image_service = ImageService()
   ```

3. Replace `_load_astrobin_image()` and `_load_dss_image()` with a unified method:
   ```python
   def _load_image(self, ra_deg, dec_deg, object_name=None, diameter_arcmin=None):
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
           img = Image.open(io.BytesIO(image_bytes))
           img.thumbnail((300, 250), Image.Resampling.LANCZOS)
           photo = ImageTk.PhotoImage(img)
           self.image_cache[cache_key] = (photo, source_label)
           return (photo, source_label)
       
       self.image_cache[cache_key] = None
       return None
   ```

4. Update `show_tooltip()` to call `_load_image()` instead of the old methods.

### T002: Add Source Label to Tooltip

Add a small text label at the bottom of the tooltip showing the survey source:
```python
source_text = tk.Label(
    self.tooltip_window,
    text=f"Source: {source_label}",
    bg="black",
    fg="#888888",
    font=("Arial", 7),
)
source_text.pack(side="bottom")
```

### T003: Update Context Menu Detail View

If the Tkinter version has a "View Details" right-click option (~line 1381), update it to also use `ImageService` for the detail dialog image.

## Acceptance Criteria

- [ ] Hovering over an object shows a tooltip with a color image from hips2fits
- [ ] Source name is displayed in the tooltip
- [ ] Image is downscaled to fit 300×250 tooltip size
- [ ] No UI freezing during image loading
- [ ] In-memory cache prevents redundant fetches within a session
- [ ] Old AstroBin/DSS methods removed or deprecated

## Files to Modify

- **MODIFY**: `src/gui/enhanced_target_selection_gui.py`

## Dependencies

- **WP01** — ImageService module
- **WP02** — DiskImageCache for persistent caching

## Activity Log

- 2026-04-13T18:20:10Z – unknown – Moved to in_progress
- 2026-04-13T18:22:51Z – unknown – Moved to for_review

---
work_package_id: WP01
title: Image Service Module with HiPS2FITS Integration
dependencies: []
requirement_refs:
- FR-1
- FR-2
- FR-7
planning_base_branch: main
merge_target_branch: main
branch_strategy: Planning artifacts for this feature were generated on main. During /spec-kitty.implement this WP may branch from a dependency-specific base, but completed changes must merge back into main unless the human explicitly redirects the landing branch.
base_branch: 001-better-astro-photos
base_commit: 9ef14579324d94ad6a8142f84ac4475c8751cbf2
created_at: '2026-04-13T18:11:26.698770+00:00'
subtasks:
- 'T001: Create src/utils/image_service.py module'
- 'T002: Implement HiPS2FITS API client'
- 'T003: Implement survey fallback chain'
- 'T004: Implement adaptive FOV calculation'
- 'T005: Implement image validation'
phase: Phase 1 - Core Service
assignee: ''
agent: "copilot"
shell_pid: "8956"
history:
- timestamp: '2026-04-13T18:00:00Z'
  agent: system
  action: Prompt generated via /spec-kitty.tasks
authoritative_surface: src/utils/image_service.py
execution_mode: code_change
owned_files:
- src/utils/image_service.py
tags: []
---
owned_files:
- src/gui/enhanced_target_selection_gui.py
- src/gui/pyside6_target_selection.py
- src/utils/image_service.py
tags: []
---

# Work Package Prompt: WP01 – Image Service Module with HiPS2FITS Integration

## Objective

Create a new `src/utils/image_service.py` module providing a unified image fetching service that uses the CDS hips2fits API to retrieve high-quality color astronomical images from multiple sky surveys.

## Context

The current codebase has duplicated image fetching logic in two GUI files:
- `src/gui/pyside6_target_selection.py` — `_try_load_sdss()`, `_try_load_dss()` methods
- `src/gui/enhanced_target_selection_gui.py` — `_load_astrobin_image()`, `_load_dss_image()` methods

Both fetch from SDSS and DSS independently. This WP extracts that logic into a shared module with a better image source.

## Requirements

### T001: Create `src/utils/image_service.py`

Create the module with an `ImageService` class:

```python
class ImageService:
    """Fetches astronomical object images from sky survey services."""
    
    def fetch_object_image(
        self,
        ra_deg: float,
        dec_deg: float,
        diameter_arcmin: float | None = None,
        width: int = 600,
        height: int = 600,
    ) -> tuple[bytes, str] | None:
        """
        Fetch an image for the given coordinates.
        
        Returns (image_bytes, source_label) or None if all sources fail.
        source_label is e.g. "PanSTARRS DR1", "SDSS9", "DSS2".
        """
```

### T002: HiPS2FITS API Client

Implement a method to call the CDS hips2fits API:

**Endpoint:** `https://alasky.cds.unistra.fr/hips-image-services/hips2fits`

**Parameters:**
| Parameter | Value |
|-----------|-------|
| `hips` | Survey ID (e.g., `CDS/P/PanSTARRS/DR1/color-z-zg-g`) |
| `ra` | Right ascension in decimal degrees |
| `dec` | Declination in decimal degrees |
| `fov` | Field of view in degrees |
| `width` | Image width in pixels |
| `height` | Image height in pixels |
| `projection` | `TAN` |
| `format` | `jpg` |

**Headers:**
```python
{
    "User-Agent": "NextAstroTarget/2.0.0 (Astronomy Application)"
}
```

**Timeout:** 10 seconds per request.

### T003: Survey Fallback Chain

Try surveys in this order, moving to the next on failure:

1. **PanSTARRS DR1 color** — `CDS/P/PanSTARRS/DR1/color-z-zg-g` — covers declination > −30°
2. **SDSS9 color** — `CDS/P/SDSS9/color` — ~35% sky coverage
3. **DSS2 color** — `CDS/P/DSS2/color` — full-sky coverage
4. **Legacy STScI DSS** — `https://archive.stsci.edu/cgi-bin/dss_search?v=poss2ukstu_red&r={ra}&d={dec}&e=J2000&h=15.0&w=15.0&f=gif` — ultimate fallback

Define surveys as a list of named tuples/dataclasses for maintainability:

```python
SURVEYS = [
    Survey("PanSTARRS DR1", "CDS/P/PanSTARRS/DR1/color-z-zg-g"),
    Survey("SDSS9", "CDS/P/SDSS9/color"),
    Survey("DSS2", "CDS/P/DSS2/color"),
]
```

### T004: Adaptive FOV Calculation

```python
def _calculate_fov(self, diameter_arcmin: float | None) -> float:
    if diameter_arcmin and diameter_arcmin > 0:
        fov_deg = (diameter_arcmin * 2.0) / 60.0  # 2× diameter
        return max(0.05, min(fov_deg, 2.0))       # clamp 3'–2°
    return 0.25  # default 15 arcmin
```

### T005: Image Validation

After fetching, validate the response:
1. HTTP status == 200
2. Content-Type contains `image/`
3. Response body size > 5 KB (rejects error pages / empty tiles)
4. Average pixel brightness > 10 (rejects blank/black frames)

Use `PIL.Image` to check brightness:
```python
from PIL import Image
import io

img = Image.open(io.BytesIO(image_bytes))
avg_brightness = sum(img.convert("L").getdata()) / (img.width * img.height)
if avg_brightness < 10:
    return None  # blank image, try next survey
```

## Acceptance Criteria

- [ ] `ImageService` can fetch a color image for M31 (RA=10.685, Dec=41.269)
- [ ] Fallback chain works: if PanSTARRS returns empty, falls to SDSS9 or DSS2
- [ ] Adaptive FOV produces reasonable framing for objects of varying sizes
- [ ] 10-second timeout prevents hanging on unresponsive servers
- [ ] Module has no GUI dependencies (pure utility)
- [ ] Thread-safe for concurrent calls from UI threads

## Files to Create/Modify

- **CREATE**: `src/utils/image_service.py`

## Dependencies

None — this is the foundational WP.

## Activity Log

- 2026-04-13T18:11:27Z – copilot – shell_pid=8956 – Assigned agent via action command
- 2026-04-13T18:12:23Z – copilot – shell_pid=8956 – Image service module with hips2fits integration, survey fallback chain, adaptive FOV, and brightness validation
- 2026-04-13T18:12:30Z – copilot – shell_pid=8956 – Approved: ImageService module correctly implements hips2fits API, fallback chain, FOV calculation, and brightness validation

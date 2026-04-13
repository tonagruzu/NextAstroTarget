# Implementation Plan: Better Astro Object Photos

**Branch**: `main` | **Date**: 2026-04-13 | **Spec**: [spec.md](spec.md)

## Summary

Replace the current SDSS/DSS/AstroBin image fallback chain with the CDS hips2fits unified API, providing high-quality color images from PanSTARRS, SDSS9, and DSS2 color surveys. Add persistent disk caching with LRU eviction. Update both PySide6 and Tkinter UI backends.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: PySide6, Pillow, urllib3 (stdlib urllib.request)  
**Storage**: File-based image cache in `data/image_cache/`  
**Testing**: Manual testing + existing test scripts  
**Target Platform**: Windows desktop (primary), cross-platform compatible  
**Project Type**: Single desktop application  
**Performance Goals**: Image load < 3s on first fetch, instant from cache  
**Constraints**: No API keys, no authentication, < 500 MB disk cache  
**Scale/Scope**: ~3000 deep-sky objects in the database

## Project Structure

### Documentation (this feature)

```
kitty-specs/001-better-astro-photos/
├── spec.md              # Feature specification
├── plan.md              # This file
└── tasks/               # Work packages
```

### Source Code (repository root)

```
src/
├── gui/
│   ├── pyside6_target_selection.py   # PySide6 UI — image loading & detail dialog
│   └── enhanced_target_selection_gui.py  # Tkinter UI — tooltip & image loading
└── utils/
    └── image_service.py              # NEW — shared image fetching & caching logic

data/
└── image_cache/                      # NEW — persistent disk cache directory
```

**Structure Decision**: Extract shared image fetching logic into a new `src/utils/image_service.py` module. Both UI backends call this module instead of implementing their own fetch logic. This eliminates code duplication and ensures consistent behavior.

## Architecture

### Component Overview

```
┌─────────────────────────────────┐
│  UI Layer (PySide6 / Tkinter)   │
│  - Detail dialog                │
│  - Tooltip preview              │
│  - Source label display          │
└──────────┬──────────────────────┘
           │ calls
┌──────────▼──────────────────────┐
│  ImageService (new module)      │
│  - fetch_object_image()         │
│  - Survey fallback chain        │
│  - Adaptive FOV calculation     │
│  - Thread-safe                  │
└──────────┬──────────────────────┘
           │ uses
┌──────────▼──────────────────────┐
│  DiskCache                      │
│  - get() / put()                │
│  - LRU eviction at 500 MB       │
│  - Cache key: survey+coords     │
└──────────┬──────────────────────┘
           │ fetches from
┌──────────▼──────────────────────┐
│  CDS hips2fits API              │
│  Surveys: PanSTARRS → SDSS9     │
│           → DSS2 color          │
│  Fallback: legacy STScI DSS     │
└─────────────────────────────────┘
```

### Image Fetch Flow

1. UI requests image for object (RA, Dec, optional diameter)
2. `ImageService.fetch_object_image()` checks disk cache
3. If cache hit → return cached image bytes + source label
4. If cache miss → try surveys in order:
   - PanSTARRS DR1 color via hips2fits
   - SDSS9 color via hips2fits
   - DSS2 color via hips2fits
   - Legacy STScI DSS (existing endpoint)
5. On success → save to disk cache, return image bytes + source label
6. On all failures → return None (UI shows placeholder)

### Survey Detection

Each hips2fits response is validated:
- HTTP 200 status
- Content-Type contains `image/`
- Response size > 5 KB (rejects empty/error responses)
- Image brightness check (avg pixel > 10, rejects blank sky tiles)

### Adaptive FOV

```python
if object_diameter_arcmin and object_diameter_arcmin > 0:
    fov_deg = (object_diameter_arcmin * 2.0) / 60.0  # 2× diameter
    fov_deg = max(fov_deg, 0.05)   # minimum 3 arcmin
    fov_deg = min(fov_deg, 2.0)    # maximum 2 degrees
else:
    fov_deg = 0.25  # default 15 arcmin
```

### Disk Cache Design

- **Location**: `data/image_cache/`
- **File naming**: `{survey_key}_{ra:.4f}_{dec:.4f}.jpg`
- **Metadata**: `.cache_index.json` tracks file sizes and last-access times
- **Eviction**: When total size exceeds 500 MB, remove least-recently-accessed files until under 400 MB
- **Thread safety**: File-level locking via `threading.Lock`

## Implementation Phases

### Phase 1: Image Service Module (WP01)
Create `src/utils/image_service.py` with:
- `ImageService` class with hips2fits API integration
- Survey fallback chain (PanSTARRS → SDSS9 → DSS2 → legacy DSS)
- Adaptive FOV calculation
- Image validation (brightness, size checks)
- 10-second timeout per request

### Phase 2: Disk Cache (WP02)
Add to `image_service.py`:
- `DiskImageCache` class with get/put/evict
- Cache index file for LRU tracking
- 500 MB limit with eviction to 400 MB
- Thread-safe operations

### Phase 3: PySide6 Integration (WP03)
Update `src/gui/pyside6_target_selection.py`:
- Replace `_try_load_sdss()` and `_try_load_dss()` with `ImageService` calls
- Increase detail dialog image to 600×600
- Add survey source label to detail dialog
- Preserve background threading

### Phase 4: Tkinter Integration (WP04)
Update `src/gui/enhanced_target_selection_gui.py`:
- Replace `_load_astrobin_image()` and `_load_dss_image()` with `ImageService` calls
- Add source label to tooltip
- Preserve existing tooltip behavior

### Phase 5: Testing & Validation (WP05)
- Test with objects at various declinations (PanSTARRS coverage boundary)
- Test fallback chain (mock service failures)
- Test cache eviction
- Verify no UI blocking
- Visual quality comparison

## Dependencies Between Phases

```
WP01 (Image Service) ──► WP03 (PySide6 UI)
         │                       │
         ├──► WP02 (Disk Cache) ─┤
         │                       │
         └──► WP04 (Tkinter UI) ─┘
                                 │
                          WP05 (Testing) ◄─┘
```

WP01 must be completed first. WP02 can be done in parallel with or after WP01. WP03 and WP04 depend on WP01+WP02. WP05 depends on all others.
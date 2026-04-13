# Feature: Better Astro Object Photos

## Problem Statement

The NextAstroTarget application displays astronomical object photos in the object card (tooltip on hover and detail dialog on right-click). The current implementation relies on three image sources in a fallback chain:

1. **SDSS** (Sloan Digital Sky Survey) — 512×512 color JPEG, but limited sky coverage (~35% of sky, mostly northern galactic cap)
2. **DSS** (Digitized Sky Survey via STScI) — 12–15 arcmin GIF, grayscale only, low resolution
3. **AstroBin** — requires pre-stored IDs from the Excel database; coverage is sparse

For the majority of deep-sky objects, users see either a grayscale DSS image or a black/empty frame. The user experience is poor compared to what modern astronomical image services can deliver for free.

## Goal

Replace the current image source chain with higher-quality, freely available astronomical image services that provide **color images** with **better resolution** and **broader sky coverage**.

## Current Implementation (As-Is)

### Files Involved
- `src/gui/pyside6_target_selection.py` — PySide6 UI with detail dialog and image loading (`load_dss_image()`, `_try_load_sdss()`, `_try_load_dss()`)
- `src/gui/enhanced_target_selection_gui.py` — Tkinter UI with AstrobinTooltip class (`_load_astrobin_image()`, `_load_dss_image()`)

### Current Fallback Chain (PySide6)
1. SDSS → `http://skyserver.sdss.org/dr17/SkyServerWS/ImgCutout/getjpeg?ra={ra}&dec={dec}&width=512&height=512&scale=0.4`
2. DSS Red+Blue RGB composite → `https://archive.stsci.edu/cgi-bin/dss_search?v=poss2ukstu_red&r={ra}&d={dec}&e=J2000&h=15.0&w=15.0&f=gif`
3. DSS pseudo-color fallback (colormap applied to grayscale)
4. AstroBin (if ID available) → `https://www.astrobin.com/{id}/0/rawthumb/regular/`

### Known Limitations
- SDSS covers only ~35% of the sky
- DSS images are grayscale GIFs from photographic plate scans (1950s–1990s)
- AstroBin coverage depends on pre-populated IDs in the database
- No disk caching — images are re-fetched each session

## Proposed Solution (To-Be)

### New Image Source: CDS HiPS2FITS Service

Replace the primary image source with the **CDS hips2fits** service, which provides access to multiple modern sky surveys through a single unified API.

**API Endpoint:** `https://alasky.cds.unistra.fr/hips-image-services/hips2fits`

**Key advantages:**
- Access to **color survey data** (PanSTARRS DR1 color, DECaLS DR5 color, SDSS9 color, DSS2 color)
- Full-sky coverage through survey fallback (DSS2 covers the entire sky)
- Configurable output: JPEG/PNG format, custom resolution, adjustable contrast
- Single API for all surveys — no need for separate integrations
- Free, no authentication required

### New Fallback Chain

1. **PanSTARRS DR1 color** (`CDS/P/PanSTARRS/DR1/color-z-zg-g`) — best quality, covers declination > −30°
2. **SDSS9 color** (`CDS/P/SDSS9/color`) — excellent quality, ~35% sky coverage
3. **DSS2 color** (`CDS/P/DSS2/color`) — full-sky coverage, reasonable color quality
4. **Legacy DSS** (current STScI endpoint) — ultimate fallback for service outages

### API Parameters

```
GET https://alasky.cds.unistra.fr/hips-image-services/hips2fits?
    hips=CDS/P/PanSTARRS/DR1/color-z-zg-g
    &ra={ra_deg}
    &dec={dec_deg}
    &fov={fov_deg}
    &width=600
    &height=600
    &projection=TAN
    &format=jpg
```

Where `fov` should be adaptive based on the object's angular size (from the database diameter column if available, or a sensible default like 0.25°).

## Functional Requirements

### FR-1: Replace Primary Image Source
Replace the current SDSS/DSS image loading with the CDS hips2fits service using the fallback chain defined above.

### FR-2: Adaptive Field of View
When the object's angular diameter is known (from the database), set the field of view to ~2× the diameter to frame the object nicely. Use a default of 0.25° (~15 arcmin) when diameter is unknown.

### FR-3: Disk Cache
Implement persistent disk caching of downloaded images in `data/image_cache/` to avoid re-fetching images across sessions. Cache key should be based on object coordinates and survey source.

### FR-4: Higher Resolution Display
Increase the detail dialog image display from 400×400 to 600×600 pixels. Request 600×600 from the API.

### FR-5: Tooltip Preview
Keep the tooltip preview at 300×250 but use a downscaled version of the cached higher-resolution image.

### FR-6: Image Source Label
Display the survey name (e.g., "PanSTARRS DR1", "SDSS9", "DSS2") in the detail dialog so users know which source is shown.

### FR-7: Graceful Degradation
If the hips2fits service is unreachable (timeout after 10 seconds), fall back to the current DSS/STScI endpoint. If all services fail, display a placeholder with "No image available".

### FR-8: Both UI Backends
Apply changes to both the PySide6 (`pyside6_target_selection.py`) and Tkinter (`enhanced_target_selection_gui.py`) implementations.

## Non-Functional Requirements

### NFR-1: Performance
Image loading must not block the UI. Loading should happen in a background thread (already implemented).

### NFR-2: Cache Size
Implement a cache size limit (default 500 MB) with LRU eviction policy.

### NFR-3: Network Timeout
Individual image fetch requests must timeout after 10 seconds.

### NFR-4: No Authentication Required
All image sources must be freely available without API keys or authentication.

## Out of Scope

- AstroBin integration removal (keep as optional source if ID is available)
- Moon phase image generation
- Changes to the database schema
- Object name resolution via SIMBAD/NED

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| CDS hips2fits service downtime | No images from primary source | Multi-level fallback chain; legacy DSS as final fallback |
| PanSTARRS coverage gap (dec < −30°) | No PanSTARRS image for southern objects | Automatic fallback to SDSS9 then DSS2 color |
| Rate limiting by CDS | Slow image loading | Disk cache ensures each object is only fetched once |
| Large cache directory | Disk space usage | LRU eviction at 500 MB limit |

## Acceptance Criteria

1. Object card shows a **color image** for at least 95% of objects in the database
2. Image quality is visibly better than the current DSS grayscale for objects covered by PanSTARRS or SDSS
3. Images are cached on disk and load instantly on subsequent views
4. Fallback chain works correctly when a survey has no coverage for a given position
5. Both PySide6 and Tkinter UIs display the improved images
6. No UI freezing during image loading

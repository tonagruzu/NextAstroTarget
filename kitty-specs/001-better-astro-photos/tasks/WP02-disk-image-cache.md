---
work_package_id: WP02
title: Persistent Disk Image Cache
dependencies:
- WP01
requirement_refs:
- FR-3
planning_base_branch: main
merge_target_branch: main
branch_strategy: Planning artifacts for this feature were generated on main. During /spec-kitty.implement this WP may branch from a dependency-specific base, but completed changes must merge back into main unless the human explicitly redirects the landing branch.
subtasks:
- 'T001: Implement DiskImageCache class'
- 'T002: Implement LRU eviction'
- 'T003: Integrate cache into ImageService'
- 'T004: Create cache directory with .gitignore'
phase: Phase 2 - Caching
assignee: ''
agent: "copilot"
shell_pid: "41376"
history:
- timestamp: '2026-04-13T18:00:00Z'
  agent: system
  action: Prompt generated via /spec-kitty.tasks
authoritative_surface: data/image_cache
execution_mode: code_change
owned_files:
- data/image_cache/.gitkeep
tags: []
---

# Work Package Prompt: WP02 – Persistent Disk Image Cache

## Objective

Add persistent disk caching to `ImageService` so that astronomical images are stored locally and served instantly on subsequent views, avoiding redundant network requests across sessions.

## Context

The current implementation uses only in-memory caching (a `dict` per session). Images are re-fetched every time the application restarts. With ~3000 objects in the database, this wastes bandwidth and slows the user experience.

## Requirements

### T001: DiskImageCache Class

Add a `DiskImageCache` class to `src/utils/image_service.py`:

```python
class DiskImageCache:
    """Persistent disk cache for astronomical images with LRU eviction."""
    
    def __init__(self, cache_dir: str = "data/image_cache", max_size_mb: int = 500):
        self.cache_dir = Path(cache_dir)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.index_file = self.cache_dir / ".cache_index.json"
        self._lock = threading.Lock()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._load_index()
    
    def get(self, key: str) -> bytes | None:
        """Return cached image bytes or None. Updates last-access time."""
    
    def put(self, key: str, data: bytes, source: str) -> None:
        """Store image bytes. Triggers eviction if over limit."""
    
    def _evict(self) -> None:
        """Remove least-recently-accessed files until under 80% of max size."""
```

**Cache key format:** `{survey_key}_{ra:.4f}_{dec:.4f}` (e.g., `panstarrs_10.6850_41.2690`)

**File naming:** `{cache_key}.jpg`

### T002: LRU Eviction

The cache index (`.cache_index.json`) tracks:
```json
{
  "panstarrs_10.6850_41.2690": {
    "file": "panstarrs_10.6850_41.2690.jpg",
    "size": 45230,
    "source": "PanSTARRS DR1",
    "last_access": "2026-04-13T18:00:00Z",
    "created": "2026-04-13T18:00:00Z"
  }
}
```

Eviction policy:
- Triggered when total cache size exceeds `max_size_bytes` (500 MB)
- Removes least-recently-accessed entries until total size drops below 80% (400 MB)
- Index file is updated atomically after eviction

### T003: Integrate Cache into ImageService

Modify `ImageService.fetch_object_image()`:
1. Before network requests, check `DiskImageCache.get(key)`
2. If hit, return `(cached_bytes, cached_source_label)`
3. If miss, fetch from network, then `DiskImageCache.put(key, bytes, source)`
4. The cache key should be based on the first survey that produces a valid result (not all surveys attempted)

### T004: Create Cache Directory

- Create `data/image_cache/.gitkeep`
- Add `data/image_cache/*.jpg` and `data/image_cache/.cache_index.json` to `.gitignore`

## Acceptance Criteria

- [ ] First fetch for an object stores the image on disk
- [ ] Second fetch for the same object returns instantly from disk (no network call)
- [ ] Cache index persists across application restarts
- [ ] Eviction kicks in when cache exceeds 500 MB, reduces to ~400 MB
- [ ] Thread-safe: concurrent fetches for different objects don't corrupt the index
- [ ] Cache directory is ignored by git

## Files to Create/Modify

- **MODIFY**: `src/utils/image_service.py` (add DiskImageCache, integrate into ImageService)
- **CREATE**: `data/image_cache/.gitkeep`
- **MODIFY**: `.gitignore` (add cache entries)

## Dependencies

- **WP01** — ImageService module must exist.

## Activity Log

- 2026-04-13T18:12:41Z – copilot – shell_pid=41376 – Started implementation via action command
- 2026-04-13T18:16:07Z – copilot – shell_pid=41376 – Moved to for_review
- 2026-04-13T18:16:13Z – copilot – shell_pid=41376 – Moved to approved

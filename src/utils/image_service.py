"""Astronomical image fetching service using CDS hips2fits API.

Provides high-quality color images from multiple sky surveys with
automatic fallback and adaptive field-of-view calculation.
"""

from __future__ import annotations

import io
import json
import logging
import os
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from PIL import Image

logger = logging.getLogger(__name__)

HIPS2FITS_ENDPOINT = "https://alasky.cds.unistra.fr/hips-image-services/hips2fits"
LEGACY_DSS_ENDPOINT = "https://archive.stsci.edu/cgi-bin/dss_search"

REQUEST_TIMEOUT = 10  # seconds
MIN_IMAGE_SIZE = 5 * 1024  # 5 KB minimum for valid image
MIN_BRIGHTNESS = 10  # minimum average pixel brightness
USER_AGENT = "NextAstroTarget/2.0.0 (Astronomy Application)"
DEFAULT_CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "image_cache")
MAX_CACHE_SIZE_MB = 500
EVICTION_TARGET_RATIO = 0.8  # evict down to 80% of max


@dataclass(frozen=True)
class Survey:
    """A sky survey available via hips2fits."""
    label: str
    hips_id: str


# Ordered by preference: best quality first, broadest coverage last
SURVEYS = [
    Survey("PanSTARRS DR1", "CDS/P/PanSTARRS/DR1/color-z-zg-g"),
    Survey("SDSS9", "CDS/P/SDSS9/color"),
    Survey("DSS2", "CDS/P/DSS2/color"),
]


@dataclass
class ImageResult:
    """Result of an image fetch operation."""
    image_bytes: bytes
    source_label: str
    width: int
    height: int


class DiskImageCache:
    """Persistent disk cache for astronomical images with LRU eviction."""

    def __init__(self, cache_dir: str, max_size_mb: int = MAX_CACHE_SIZE_MB):
        self.cache_dir = Path(cache_dir)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.eviction_target = int(self.max_size_bytes * EVICTION_TARGET_RATIO)
        self.index_file = self.cache_dir / ".cache_index.json"
        self._lock = threading.Lock()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._index: Dict[str, Dict[str, Any]] = self._load_index()

    def _load_index(self) -> Dict[str, Dict[str, Any]]:
        """Load cache index from disk."""
        if self.index_file.exists():
            try:
                return json.loads(self.index_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                logger.warning("Corrupt cache index, starting fresh")
        return {}

    def _save_index(self) -> None:
        """Save cache index to disk atomically."""
        content = json.dumps(self._index, indent=2)
        tmp_path = self.index_file.with_suffix(".tmp")
        tmp_path.write_text(content, encoding="utf-8")
        tmp_path.replace(self.index_file)

    def get(self, key: str) -> Optional[Tuple[bytes, str]]:
        """Return cached image bytes and source label, or None."""
        with self._lock:
            entry = self._index.get(key)
            if entry is None:
                return None

            file_path = self.cache_dir / entry["file"]
            if not file_path.exists():
                del self._index[key]
                self._save_index()
                return None

            # Update last access time
            entry["last_access"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            self._save_index()

            image_bytes = file_path.read_bytes()
            return (image_bytes, entry["source"])

    def put(self, key: str, data: bytes, source: str) -> None:
        """Store image bytes in the cache."""
        with self._lock:
            filename = f"{key}.jpg"
            file_path = self.cache_dir / filename

            file_path.write_bytes(data)

            now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            self._index[key] = {
                "file": filename,
                "size": len(data),
                "source": source,
                "last_access": now,
                "created": now,
            }
            self._save_index()
            self._maybe_evict()

    def _maybe_evict(self) -> None:
        """Evict least-recently-accessed entries if over size limit."""
        total_size = sum(e["size"] for e in self._index.values())
        if total_size <= self.max_size_bytes:
            return

        # Sort by last_access ascending (oldest first)
        sorted_keys = sorted(
            self._index.keys(),
            key=lambda k: self._index[k].get("last_access", ""),
        )

        for key in sorted_keys:
            if total_size <= self.eviction_target:
                break
            entry = self._index[key]
            file_path = self.cache_dir / entry["file"]
            total_size -= entry["size"]
            try:
                file_path.unlink(missing_ok=True)
            except OSError:
                pass
            del self._index[key]

        self._save_index()
        logger.info("Cache eviction complete, new size: %.1f MB", total_size / (1024 * 1024))


class ImageService:
    """Fetches astronomical object images from sky survey services."""

    def __init__(self, cache_dir: Optional[str] = None):
        self._lock = threading.Lock()
        cache_path = cache_dir or DEFAULT_CACHE_DIR
        self._cache = DiskImageCache(cache_path)

    @staticmethod
    def _make_cache_key(ra_deg: float, dec_deg: float) -> str:
        """Create a cache key from coordinates."""
        return f"{ra_deg:.4f}_{dec_deg:.4f}"

    def fetch_object_image(
        self,
        ra_deg: float,
        dec_deg: float,
        diameter_arcmin: Optional[float] = None,
        width: int = 600,
        height: int = 600,
    ) -> Optional[Tuple[bytes, str]]:
        """Fetch an image for the given coordinates.

        Tries surveys in order: PanSTARRS DR1 -> SDSS9 -> DSS2 color -> legacy DSS.

        Args:
            ra_deg: Right ascension in decimal degrees.
            dec_deg: Declination in decimal degrees.
            diameter_arcmin: Object angular diameter in arcminutes (optional).
            width: Requested image width in pixels.
            height: Requested image height in pixels.

        Returns:
            Tuple of (image_bytes, source_label) or None if all sources fail.
        """
        cache_key = self._make_cache_key(ra_deg, dec_deg)

        # Check disk cache first
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        fov_deg = self._calculate_fov(diameter_arcmin)

        # Try hips2fits surveys in order
        for survey in SURVEYS:
            try:
                result = self._fetch_hips2fits(
                    survey, ra_deg, dec_deg, fov_deg, width, height
                )
                if result is not None:
                    self._cache.put(cache_key, result[0], result[1])
                    return result
            except Exception:
                logger.debug(
                    "Survey %s failed for (%.4f, %.4f)",
                    survey.label, ra_deg, dec_deg,
                    exc_info=True,
                )
                continue

        # Ultimate fallback: legacy STScI DSS
        try:
            result = self._fetch_legacy_dss(ra_deg, dec_deg)
            if result is not None:
                self._cache.put(cache_key, result[0], result[1])
                return result
        except Exception:
            logger.debug(
                "Legacy DSS failed for (%.4f, %.4f)",
                ra_deg, dec_deg,
                exc_info=True,
            )

        return None

    @staticmethod
    def _calculate_fov(diameter_arcmin: Optional[float]) -> float:
        """Calculate field of view in degrees based on object diameter.

        Args:
            diameter_arcmin: Object diameter in arcminutes, or None.

        Returns:
            Field of view in degrees, clamped to [0.05, 2.0].
        """
        if diameter_arcmin and diameter_arcmin > 0:
            fov_deg = (diameter_arcmin * 2.0) / 60.0  # 2x diameter
            return max(0.05, min(fov_deg, 2.0))
        return 0.25  # default 15 arcmin

    def _fetch_hips2fits(
        self,
        survey: Survey,
        ra_deg: float,
        dec_deg: float,
        fov_deg: float,
        width: int,
        height: int,
    ) -> Optional[Tuple[bytes, str]]:
        """Fetch an image from the CDS hips2fits service.

        Returns (image_bytes, source_label) or None if the image is invalid.
        """
        params = urllib.parse.urlencode({
            "hips": survey.hips_id,
            "ra": f"{ra_deg:.6f}",
            "dec": f"{dec_deg:.6f}",
            "fov": f"{fov_deg:.6f}",
            "width": str(width),
            "height": str(height),
            "projection": "TAN",
            "format": "jpg",
        })
        url = f"{HIPS2FITS_ENDPOINT}?{params}"

        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "image/jpeg, image/*",
            },
        )

        response = urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT)
        if response.status != 200:
            return None

        content_type = response.headers.get("Content-Type", "")
        if "image" not in content_type.lower():
            return None

        image_bytes = response.read()

        if len(image_bytes) < MIN_IMAGE_SIZE:
            logger.debug(
                "Survey %s returned too-small image (%d bytes) for (%.4f, %.4f)",
                survey.label, len(image_bytes), ra_deg, dec_deg,
            )
            return None

        if not self._validate_brightness(image_bytes):
            logger.debug(
                "Survey %s returned blank image for (%.4f, %.4f)",
                survey.label, ra_deg, dec_deg,
            )
            return None

        logger.info(
            "Fetched image from %s for (%.4f, %.4f), %d bytes",
            survey.label, ra_deg, dec_deg, len(image_bytes),
        )
        return (image_bytes, survey.label)

    def _fetch_legacy_dss(
        self, ra_deg: float, dec_deg: float
    ) -> Optional[Tuple[bytes, str]]:
        """Fetch from the legacy STScI DSS endpoint as ultimate fallback."""
        params = urllib.parse.urlencode({
            "v": "poss2ukstu_red",
            "r": f"{ra_deg:.6f}",
            "d": f"{dec_deg:.6f}",
            "e": "J2000",
            "h": "15.0",
            "w": "15.0",
            "f": "gif",
        })
        url = f"{LEGACY_DSS_ENDPOINT}?{params}"

        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "image/gif, image/*",
            },
        )

        response = urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT)
        if response.status != 200:
            return None

        image_bytes = response.read()

        if len(image_bytes) < MIN_IMAGE_SIZE:
            return None

        if not self._validate_brightness(image_bytes):
            return None

        logger.info(
            "Fetched legacy DSS image for (%.4f, %.4f), %d bytes",
            ra_deg, dec_deg, len(image_bytes),
        )
        return (image_bytes, "DSS (legacy)")

    @staticmethod
    def _validate_brightness(image_bytes: bytes) -> bool:
        """Check that an image is not blank/black.

        Returns True if average brightness exceeds MIN_BRIGHTNESS threshold.
        """
        try:
            img = Image.open(io.BytesIO(image_bytes))
            grayscale = img.convert("L")
            pixels = list(grayscale.getdata())
            if not pixels:
                return False
            avg_brightness = sum(pixels) / len(pixels)
            return avg_brightness >= MIN_BRIGHTNESS
        except Exception:
            logger.debug("Failed to validate image brightness", exc_info=True)
            return False

"""Astronomical image fetching service using CDS hips2fits API.

Provides high-quality color images from multiple sky surveys with
automatic fallback and adaptive field-of-view calculation.
"""

from __future__ import annotations

import io
import logging
import threading
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image

logger = logging.getLogger(__name__)

HIPS2FITS_ENDPOINT = "https://alasky.cds.unistra.fr/hips-image-services/hips2fits"
LEGACY_DSS_ENDPOINT = "https://archive.stsci.edu/cgi-bin/dss_search"

REQUEST_TIMEOUT = 10  # seconds
MIN_IMAGE_SIZE = 5 * 1024  # 5 KB minimum for valid image
MIN_BRIGHTNESS = 10  # minimum average pixel brightness
USER_AGENT = "NextAstroTarget/2.0.0 (Astronomy Application)"


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


class ImageService:
    """Fetches astronomical object images from sky survey services."""

    def __init__(self, cache_dir: Optional[str] = None):
        self._lock = threading.Lock()
        self._cache_dir = Path(cache_dir) if cache_dir else None

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
        fov_deg = self._calculate_fov(diameter_arcmin)

        # Try hips2fits surveys in order
        for survey in SURVEYS:
            try:
                result = self._fetch_hips2fits(
                    survey, ra_deg, dec_deg, fov_deg, width, height
                )
                if result is not None:
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

"""Tests for the ImageService and DiskImageCache (WP05)."""

import json
import os
import shutil
import tempfile
import time
import unittest
from unittest.mock import patch, MagicMock

from src.utils.image_service import (
    DiskImageCache,
    ImageService,
    DEFAULT_CACHE_DIR,
    MAX_CACHE_SIZE_MB,
    EVICTION_TARGET_RATIO,
)


class TestAdaptiveFOV(unittest.TestCase):
    """T003: Test _calculate_fov for various object sizes."""

    def setUp(self):
        self.svc = ImageService.__new__(ImageService)

    def test_none_returns_default(self):
        self.assertAlmostEqual(self.svc._calculate_fov(None), 0.25)

    def test_zero_returns_default(self):
        self.assertAlmostEqual(self.svc._calculate_fov(0), 0.25)

    def test_five_arcmin(self):
        # (5 * 2) / 60 = 0.16667
        self.assertAlmostEqual(self.svc._calculate_fov(5.0), 5.0 * 2 / 60, places=4)

    def test_thirty_arcmin(self):
        self.assertAlmostEqual(self.svc._calculate_fov(30.0), 1.0)

    def test_large_object_clamped_to_max(self):
        self.assertAlmostEqual(self.svc._calculate_fov(120.0), 2.0)

    def test_tiny_object_clamped_to_min(self):
        self.assertAlmostEqual(self.svc._calculate_fov(0.5), 0.05)

    def test_negative_returns_default(self):
        self.assertAlmostEqual(self.svc._calculate_fov(-10), 0.25)


class TestDiskImageCache(unittest.TestCase):
    """T002: Test disk cache persistence and eviction."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.cache = DiskImageCache(self.tmpdir, max_size_mb=1)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_put_and_get(self):
        data = b"\xff\xd8\xff" + b"\x00" * 100
        self.cache.put("m31", data, "PanSTARRS DR1")
        result = self.cache.get("m31")
        self.assertIsNotNone(result)
        self.assertEqual(result[0], data)
        self.assertEqual(result[1], "PanSTARRS DR1")

    def test_get_missing_key(self):
        self.assertIsNone(self.cache.get("nonexistent"))

    def test_cache_file_on_disk(self):
        data = b"\xff" * 50
        self.cache.put("key1", data, "DSS2 color")
        self.assertTrue(os.path.exists(os.path.join(self.tmpdir, "key1.jpg")))

    def test_index_persists(self):
        data = b"\x00" * 50
        self.cache.put("persist_key", data, "SDSS9")
        # Create a new cache instance pointing to same dir
        cache2 = DiskImageCache(self.tmpdir, max_size_mb=1)
        result = cache2.get("persist_key")
        self.assertIsNotNone(result)
        self.assertEqual(result[0], data)
        self.assertEqual(result[1], "SDSS9")

    def test_index_json_written(self):
        self.cache.put("idx_test", b"\xAB" * 10, "test")
        idx_path = os.path.join(self.tmpdir, ".cache_index.json")
        self.assertTrue(os.path.exists(idx_path))
        with open(idx_path, encoding="utf-8") as f:
            index = json.load(f)
        self.assertIn("idx_test", index)

    def test_eviction_reduces_size(self):
        # 1 MB cache limit → fill with 1.2 MB of data
        chunk = b"\xFF" * (200 * 1024)  # 200 KB each
        for i in range(7):  # 7 * 200 KB = 1.4 MB > 1 MB limit
            self.cache.put(f"evict_{i}", chunk, "test")

        # After eviction, total should be <= max_size_bytes
        total = sum(e["size"] for e in self.cache._index.values())
        self.assertLessEqual(total, self.cache.max_size_bytes)

    def test_eviction_removes_oldest(self):
        chunk = b"\xFF" * (300 * 1024)  # 300 KB each
        # Put entries with slight time gap (index tracks timestamps)
        self.cache.put("oldest", chunk, "t")
        self.cache.put("middle", chunk, "t")
        self.cache.put("newest", chunk, "t")
        # After the 3rd entry (900KB < 1MB), trigger eviction by adding another
        self.cache.put("trigger", chunk, "t")
        # The oldest entry should have been evicted first
        self.assertIsNone(self.cache.get("oldest"))

    def test_get_updates_last_access(self):
        self.cache.put("access_test", b"\x00" * 10, "src")
        old_access = self.cache._index["access_test"]["last_access"]
        # Small delay to get a different timestamp
        import time as _t
        _t.sleep(1.1)
        self.cache.get("access_test")
        new_access = self.cache._index["access_test"]["last_access"]
        self.assertNotEqual(old_access, new_access)

    def test_get_handles_missing_file(self):
        self.cache.put("gone", b"\x00" * 10, "src")
        # Delete the file behind cache's back
        os.remove(os.path.join(self.tmpdir, "gone.jpg"))
        self.assertIsNone(self.cache.get("gone"))
        self.assertNotIn("gone", self.cache._index)


class TestImageServiceFallback(unittest.TestCase):
    """T001: Test survey fallback chain with mocked network."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.svc = ImageService(cache_dir=self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    @patch("src.utils.image_service.urllib.request.urlopen")
    def test_invalid_coordinates_returns_none(self, mock_urlopen):
        mock_urlopen.side_effect = Exception("bad coords")
        result = self.svc.fetch_object_image(ra_deg=999, dec_deg=999)
        self.assertIsNone(result)

    @patch("src.utils.image_service.urllib.request.urlopen")
    def test_returns_bytes_and_source(self, mock_urlopen):
        # Create a JPEG large enough to pass MIN_IMAGE_SIZE (5 KB) and brightness
        from PIL import Image
        import io
        import random
        random.seed(42)
        img = Image.new("RGB", (300, 300))
        pixels = img.load()
        for x in range(300):
            for y in range(300):
                pixels[x, y] = (random.randint(80, 200), random.randint(80, 200), random.randint(80, 200))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=95)
        jpeg_bytes = buf.getvalue()

        mock_resp = MagicMock()
        mock_resp.read.return_value = jpeg_bytes
        mock_resp.status = 200
        mock_resp.headers = MagicMock()
        mock_resp.headers.get.return_value = "image/jpeg"
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        result = self.svc.fetch_object_image(ra_deg=10.685, dec_deg=41.269)
        self.assertIsNotNone(result)
        image_bytes, source_label = result
        self.assertIsInstance(image_bytes, bytes)
        self.assertTrue(len(image_bytes) > 0)
        self.assertIsInstance(source_label, str)

    @patch("src.utils.image_service.urllib.request.urlopen")
    def test_all_surveys_fail_returns_none(self, mock_urlopen):
        # Simulate all surveys returning a too-dark image (< brightness threshold)
        mock_urlopen.side_effect = Exception("network error")
        result = self.svc.fetch_object_image(ra_deg=10.0, dec_deg=10.0)
        self.assertIsNone(result)

    def test_make_cache_key(self):
        key = ImageService._make_cache_key(10.685, 41.269)
        self.assertEqual(key, "10.6850_41.2690")

    def test_make_cache_key_precision(self):
        key = ImageService._make_cache_key(10.6854999, 41.2691111)
        self.assertEqual(key, "10.6855_41.2691")


class TestMakeCacheKey(unittest.TestCase):
    """Supplementary tests for cache key generation."""

    def test_negative_coordinates(self):
        key = ImageService._make_cache_key(-72.081, -13.5)
        self.assertEqual(key, "-72.0810_-13.5000")

    def test_zero_coordinates(self):
        key = ImageService._make_cache_key(0.0, 0.0)
        self.assertEqual(key, "0.0000_0.0000")


if __name__ == "__main__":
    unittest.main()

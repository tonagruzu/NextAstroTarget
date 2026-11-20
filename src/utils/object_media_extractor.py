"""Extract per-object preview images and Astrobin links from the spreadsheet.

The workbook embeds one preview photograph per object as the fill image of a
comment shape, wired through ``xl/drawings/vmlDrawing1.vml`` (``<v:fill
o:relid>`` plus an ``<x:Anchor>`` giving the row), with the files themselves in
``xl/media/``. The Astrobin page hyperlink sits in column A of each object row.

None of this is visible to ``pandas``, so it is read directly from the workbook
ZIP, with the object name resolved from column A via ``openpyxl``.
"""

from __future__ import annotations

import logging
import re
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from xml.etree import ElementTree as ET

logger = logging.getLogger(__name__)

_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
_NS = {"m": _MAIN, "r": _R}

_COL_A_HYPERLINK = re.compile(r'<hyperlink ref="(A\d+)" r:id="(rId\d+)"')
_VML_FILL = re.compile(r'<v:fill[^>]*o:relid="(rId\d+)"')
_VML_ANCHOR = re.compile(r"<x:Anchor>\s*(\d+)\s*,\s*\d+\s*,\s*(\d+)")

# Spreadsheet label rows that must not be treated as objects.
_META_LABELS = {"Link", "Object Data", "Object Name & Image", "Astrobin"}


def sanitize_object_name(name: str) -> str:
    """Turn an object name into a safe filesystem base name."""
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", name.strip())
    return cleaned.strip("_") or "object"


class ObjectMediaExtractor:
    """Reads object preview images and Astrobin links from an .xlsm workbook."""

    def __init__(self, excel_path: str, images_dir: Path):
        self.excel_path = str(excel_path)
        self.images_dir = images_dir

    def _column_a_names_indexed(self, ws) -> Dict[int, str]:
        names: Dict[int, str] = {}
        for idx, row in enumerate(ws.iter_rows(min_col=1, max_col=1, values_only=True), start=1):
            if row and row[0] is not None:
                names[idx] = str(row[0]).strip()
        return names

    def _rels(self, z: zipfile.ZipFile, rels_path: str) -> Dict[str, str]:
        if rels_path not in z.namelist():
            return {}
        root = ET.fromstring(z.read(rels_path))
        return {e.get("Id"): e.get("Target") for e in root}

    def _sheet_rels(self, z: zipfile.ZipFile) -> Tuple[str, Dict[str, str]]:
        """Return (sheet_path, rid->Target) for the Main sheet."""
        wbx = ET.fromstring(z.read("xl/workbook.xml"))
        sheets = [
            (s.get("name"), s.get("{%s}id" % _R))
            for s in wbx.findall(".//m:sheets/m:sheet", _NS)
        ]
        rid = next(r for n, r in sheets if n == "Main")
        wbrels = {e.get("Id"): e.get("Target") for e in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
        sheet_path = "xl/" + wbrels[rid]
        srels = self._rels(z, "xl/worksheets/_rels/" + sheet_path.split("/")[-1] + ".rels")
        return sheet_path, srels

    def _astrobin_by_row(self, z, sheet_path, srels) -> Dict[int, str]:
        data = z.read(sheet_path).decode("utf-8", "replace")
        out: Dict[int, str] = {}
        for tag in re.finditer(r"<hyperlink\b[^>]*", data):
            attrs = tag.group(0)
            ref = re.search(r'ref="(A\d+)"', attrs)
            rid = re.search(r'r:id="(rId\d+)"', attrs)
            if not ref or not rid:
                continue
            url = srels.get(rid.group(1), "")
            if url and url.lower().startswith("http"):
                out[int(ref.group(1)[1:])] = url
        return out

    def _image_by_row(self, z) -> Dict[int, str]:
        """Map sheet row -> media target for comment fill images (1-based row)."""
        rels = self._rels(z, "xl/drawings/_rels/vmlDrawing1.vml.rels")
        data = z.read("xl/drawings/vmlDrawing1.vml").decode("utf-8", "replace")
        # Split into shapes to pair a fill relid with its own anchor.
        out: Dict[int, str] = {}
        for shape in data.split("<v:shape ")[1:]:
            mf = _VML_FILL.search(shape)
            ma = _VML_ANCHOR.search(shape)
            if not mf or not ma:
                continue
            target = rels.get(mf.group(1), "")
            if not target:
                continue
            # anchor: col, dx, row, dy (0-based row)
            row0 = int(ma.group(2))
            out[row0 + 1] = target  # 1-based sheet row
        return out

    def extract(self) -> List[Dict[str, str]]:
        """Return one dict per object: {object_name, image_path, astrobin_url}.

        ``image_path`` is relative to the application data directory.
        """
        names = {}
        import openpyxl

        wb = openpyxl.load_workbook(self.excel_path, read_only=True, data_only=True)
        try:
            names = self._column_a_names_indexed(wb["Main"])
        finally:
            wb.close()

        self.images_dir.mkdir(parents=True, exist_ok=True)

        records: List[Dict[str, str]] = []
        written: Dict[str, str] = {}  # sanitized name -> original object name

        with zipfile.ZipFile(self.excel_path) as z:
            sheet_path, srels = self._sheet_rels(z)
            astrobin = self._astrobin_by_row(z, sheet_path, srels)
            image_targets = self._image_by_row(z)

            # Collect the set of image file names actually referenced.
            needed = {tg.split("/")[-1] for tg in image_targets.values()}

            for row, target in image_targets.items():
                media_name = target.split("/")[-1]
                obj = names.get(row)
                if not obj or obj in _META_LABELS:
                    continue

                image_path = None
                if media_name in needed:
                    base = sanitize_object_name(obj)
                    if base in written and written[base] != obj:
                        logger.warning("Image filename collision for %r (existing %r); skipping", obj, written[base])
                        continue
                    rel = f"object_images/{base}.jpg"
                    dest = self.images_dir / f"{base}.jpg"
                    try:
                        dest.write_bytes(z.read(f"xl/media/{media_name}"))
                        written[base] = obj
                        image_path = rel
                    except Exception as e:
                        logger.warning("Failed to extract image for %r: %s", obj, e)

                records.append(
                    {
                        "object_name": obj,
                        "image_path": image_path or "",
                        "astrobin_url": astrobin.get(row, ""),
                    }
                )

        return records

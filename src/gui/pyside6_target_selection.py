"""
Modern PySide6 target selection GUI with professional table view.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QLabel, QLineEdit, QMenu, QMessageBox, QToolTip,
    QDialog, QScrollArea
)
from PySide6.QtCore import Qt, Signal, Slot, QTimer, QPoint
from PySide6.QtGui import QColor, QBrush, QFont, QAction, QPixmap, QCursor
import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from datetime import datetime
import requests
from PIL import Image
from io import BytesIO

from src.database.database_manager import DatabaseManager
from src.utils.astronomical_calculations import AstronomicalCalculator


class PySide6TargetSelectionGUI(QWidget):
    """Modern target selection interface with QTableWidget."""
    
    object_selected = Signal(dict)  # Signal emitted when object is selected
    
    def __init__(self, parent, db_manager: DatabaseManager, observatory: Dict):
        super().__init__(parent)
        
        self.db_manager = db_manager
        self.observatory = observatory
        self.logger = logging.getLogger(__name__)
        self.astro_calc = AstronomicalCalculator()
        
        # Data storage
        self.all_objects = []
        self.filtered_objects = []
        self.current_filters = {}
        
        # Image cache for tooltips
        self.image_cache = {}
        
        # Tooltip state
        self.tooltip_timer = QTimer()
        self.tooltip_timer.setSingleShot(True)
        self.tooltip_timer.timeout.connect(self.show_image_tooltip)
        self.hover_row = -1
        self.hover_data = None
        
        self.setup_ui()
        self.load_objects()
        
    def setup_ui(self):
        """Create modern UI layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("🔍 Quick Search:")
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Type object name, catalog number (M31, NGC2244)...")
        self.search_edit.textChanged.connect(self.on_search_changed)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_edit)
        
        # Clear button
        clear_search_btn = QPushButton("✖ Clear")
        clear_search_btn.setMaximumWidth(80)
        clear_search_btn.clicked.connect(self.clear_search)
        search_layout.addWidget(clear_search_btn)
        
        layout.addLayout(search_layout)
        
        # Object count label
        self.count_label = QLabel("Loading objects...")
        self.count_label.setStyleSheet("color: #4A9EFF; font-weight: bold;")
        layout.addWidget(self.count_label)
        
        # Table widget
        self.table = QTableWidget()
        self.setup_table()
        layout.addWidget(self.table)
        
        # Apply stylesheet
        self.apply_table_stylesheet()
        
    def setup_table(self):
        """Configure table widget."""
        # Columns
        columns = [
            "Object", "Type", "Subtype", "Constellation",
            "RA", "Dec", "Size", "Magnitude", "Rating",
            "Transit", "Altitude", "Nick"
        ]
        
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        
        # Enable sorting
        self.table.setSortingEnabled(True)
        
        # Selection behavior
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        
        # Header styling
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Object name stretches
        
        # Set specific column widths
        self.table.setColumnWidth(8, 120)  # Rating column - wide enough for 5 stars (⭐⭐⭐⭐⭐)
        
        # Context menu
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        # Double-click to view details
        self.table.doubleClicked.connect(self.on_row_double_clicked)
        
        # Hover for image preview
        self.table.setMouseTracking(True)
        self.table.cellEntered.connect(self.on_cell_hover)
        
    def apply_table_stylesheet(self):
        """Apply modern styling to table."""
        stylesheet = """
            QTableWidget {
                background-color: #252525;
                alternate-background-color: #2a2a2a;
                gridline-color: #3a3a3a;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
            }
            
            QTableWidget::item {
                padding: 8px;
                color: #e0e0e0;
            }
            
            QTableWidget::item:selected {
                background-color: #4A9EFF;
                color: #ffffff;
            }
            
            QTableWidget::item:hover {
                background-color: #353535;
            }
            
            QHeaderView::section {
                background-color: #2d2d2d;
                color: #4A9EFF;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #4A9EFF;
                font-weight: bold;
            }
            
            QHeaderView::section:hover {
                background-color: #353535;
            }
        """
        self.table.setStyleSheet(stylesheet)
        
    def load_objects(self):
        """Load objects from database with default size filter for performance."""
        try:
            self.logger.info("Loading objects from database")
            
            query = """
                SELECT 
                    [Imm Deep Sky Compendium -  2023 - 4th Edition] as object_name,
                    [Unnamed: 3] as object_type,
                    [Unnamed: 4] as subtype,
                    [Unnamed: 5] as classification,
                    [Unnamed: 6] as size_arcmin,
                    [Unnamed: 9] as rating,
                    [Sun] as ra_raw,
                    [Unnamed: 12] as ra_degrees,
                    [Moon] as dec_raw,
                    [Unnamed: 14] as dec_degrees,
                    [Unnamed: 15] as constellation,
                    [Unnamed: 16] as nick,
                    [Quick Start Guide] as notes,
                    [Unnamed: 19] as magnitude,
                    [Unnamed: 34] as ngc_designation,
                    [Unnamed: 35] as ic_designation,
                    [Unnamed: 37] as messier_designation,
                    [Unnamed: 48] as astrobin_id
                FROM Main 
                WHERE [Imm Deep Sky Compendium -  2023 - 4th Edition] IS NOT NULL
                ORDER BY [Imm Deep Sky Compendium -  2023 - 4th Edition]
            """
            
            df = pd.read_sql_query(query, self.db_manager.get_connection())
            self.all_objects = df.to_dict('records')
            
            # Apply default size filter from stored settings for performance
            self.filtered_objects = self._apply_default_size_filter(self.all_objects.copy())
            
            self.logger.info(f"Loaded {len(self.all_objects)} objects, filtered to {len(self.filtered_objects)} by default size range")
            self.update_table_display()
            
        except Exception as e:
            self.logger.error(f"Failed to load objects: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load objects: {str(e)}")
    
    def _apply_default_size_filter(self, objects):
        """Apply default size filter from persistent settings."""
        try:
            # Get stored size range from database
            size_min_str = self.db_manager.get_setting('size_min', '0')
            size_max_str = self.db_manager.get_setting('size_max', '9999')
            
            size_min = int(size_min_str)
            size_max = int(size_max_str)
            
            # Only filter if range is not the full range (0-9999)
            if size_min > 0 or size_max < 9999:
                filtered = []
                for obj in objects:
                    size_val = obj.get('size_arcmin')
                    if size_val is not None:
                        try:
                            size_float = float(size_val)
                            if size_min <= size_float <= size_max:
                                filtered.append(obj)
                        except (ValueError, TypeError):
                            # Skip objects with invalid size values
                            pass
                    else:
                        # Include objects without size data if min is 0
                        if size_min == 0:
                            filtered.append(obj)
                self.logger.info(f"Default size filter ({size_min}'-{size_max}'): {len(objects)} -> {len(filtered)} objects")
                return filtered
            
            return objects
            
        except Exception as e:
            self.logger.warning(f"Failed to apply default size filter: {e}")
            return objects
            
    def update_table_display(self):
        """Update table with current filtered objects."""
        self.table.setSortingEnabled(False)  # Disable while updating
        self.table.setRowCount(0)
        
        for obj in self.filtered_objects[:1000]:  # Limit to 1000 for performance
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Populate columns
            self.set_table_item(row, 0, obj.get('object_name', ''))
            self.set_table_item(row, 1, obj.get('object_type', ''))
            self.set_table_item(row, 2, obj.get('subtype', ''))
            self.set_table_item(row, 3, obj.get('constellation', ''))
            self.set_table_item(row, 4, self.format_ra(obj.get('ra_degrees')))
            self.set_table_item(row, 5, self.format_dec(obj.get('dec_degrees')))
            self.set_table_item(row, 6, self.format_size(obj.get('size_arcmin')))
            self.set_table_item(row, 7, obj.get('magnitude', ''))
            self.set_table_item(row, 8, self.format_rating(obj.get('rating')))
            
            # Calculate transit time and altitude
            transit_time, altitude = self.calculate_astronomical_data(obj)
            self.set_table_item(row, 9, transit_time)
            self.set_table_item(row, 10, altitude)
            
            self.set_table_item(row, 11, obj.get('nick', ''))
            
            # Store object data in first column
            item = self.table.item(row, 0)
            if item:
                item.setData(Qt.UserRole, obj)
                
        self.table.setSortingEnabled(True)
        
        # Update count
        total = len(self.filtered_objects)
        shown = min(total, 1000)
        self.count_label.setText(f"📊 Showing {shown} of {total} objects")
        
    def set_table_item(self, row, col, text):
        """Set table item with proper formatting."""
        item = QTableWidgetItem(str(text) if text else "")
        item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.table.setItem(row, col, item)
        
    def format_ra(self, ra_degrees):
        """Format RA for display."""
        try:
            ra = float(ra_degrees)
            hours = int(ra / 15)
            minutes = int((ra / 15 - hours) * 60)
            return f"{hours:02d}h {minutes:02d}m"
        except:
            return ""
            
    def format_dec(self, dec_degrees):
        """Format Dec for display."""
        try:
            dec = float(dec_degrees)
            sign = "+" if dec >= 0 else "-"
            dec = abs(dec)
            degrees = int(dec)
            minutes = int((dec - degrees) * 60)
            return f"{sign}{degrees:02d}° {minutes:02d}'"
        except:
            return ""
            
    def format_size(self, size_arcmin):
        """Format size for display."""
        try:
            size = float(size_arcmin)
            return f"{size:.1f}'"
        except:
            return ""
            
    def format_rating(self, rating):
        """Format rating with stars."""
        try:
            r = float(rating)
            stars = "⭐" * min(int(r), 5)
            return stars if stars else ""
        except:
            return ""
            
    def calculate_astronomical_data(self, obj: Dict) -> tuple:
        """Calculate transit time and altitude for an object."""
        try:
            ra_deg = obj.get('ra_degrees')
            dec_deg = obj.get('dec_degrees')
            
            if ra_deg is None or dec_deg is None:
                return ("--:--", "--°")
                
            ra_deg_float = float(ra_deg)
            dec_deg_float = float(dec_deg)
            
            # Convert RA degrees to hours
            ra_hours = ra_deg_float / 15.0
            
            # Calculate current altitude
            current_time = datetime.now()
            altitude, _ = self.astro_calc.calculate_altitude_azimuth(
                ra_hours, dec_deg_float, current_time,
                self.observatory['latitude'], self.observatory['longitude']
            )
            
            # Calculate transit time
            transit_time = self.astro_calc.calculate_transit_time(
                ra_hours, self.observatory['longitude'], current_time.date()
            )
            
            return (transit_time.strftime('%H:%M'), f"{altitude:.1f}°")
            
        except Exception as e:
            self.logger.debug(f"Error calculating astronomical data: {e}")
            return ("--:--", "--°")
            
    @Slot(str)
    def on_search_changed(self, text):
        """Handle search text changes with fuzzy matching."""
        if not text:
            self.filtered_objects = self.all_objects.copy()
        else:
            self.filtered_objects = self._apply_fuzzy_search(text.strip())
            
        self.update_table_display()
    
    def clear_search(self):
        """Clear search field."""
        self.search_edit.clear()
    
    def _apply_fuzzy_search(self, search_term: str) -> List[Dict]:
        """Apply fuzzy search with multiple matching strategies."""
        import re
        
        search_lower = search_term.lower()
        matches = []
        seen_ids = set()
        
        # Strategy 1: Exact substring match in name, nickname, constellation
        for obj in self.all_objects:
            obj_id = id(obj)
            if obj_id in seen_ids:
                continue
                
            name = str(obj.get('object_name', '')).lower()
            nick = str(obj.get('nick', '')).lower()
            const = str(obj.get('constellation', '')).lower()
            obj_type = str(obj.get('object_type', '')).lower()
            
            if (search_lower in name or search_lower in nick or 
                search_lower in const or search_lower in obj_type):
                matches.append(obj)
                seen_ids.add(obj_id)
        
        # Strategy 2: Catalog number matching (M31, NGC123, IC456)
        catalog_pattern = re.match(r'^([a-z]+)\s*(\d+)$', search_lower.strip())
        if catalog_pattern:
            prefix = catalog_pattern.group(1).upper()
            number = catalog_pattern.group(2)
            number_int = int(number)
            
            # Create search patterns
            patterns = [
                f"{prefix}\\s*0*{number_int}\\b",
                f"{prefix}\\s+0*{number_int}\\b",
            ]
            
            for obj in self.all_objects:
                obj_id = id(obj)
                if obj_id in seen_ids:
                    continue
                    
                name = str(obj.get('object_name', ''))
                
                for pattern in patterns:
                    if re.search(pattern, name, re.IGNORECASE):
                        matches.append(obj)
                        seen_ids.add(obj_id)
                        break
        
        # Strategy 3: Partial word matching (for names like "Horsehead", "Orion")
        if len(search_lower) >= 3 and not catalog_pattern:
            for obj in self.all_objects:
                obj_id = id(obj)
                if obj_id in seen_ids:
                    continue
                    
                name = str(obj.get('object_name', '')).lower()
                nick = str(obj.get('nick', '')).lower()
                
                # Check if any word in name/nick starts with search term
                name_words = name.split()
                nick_words = nick.split()
                
                for word in name_words + nick_words:
                    if word.startswith(search_lower):
                        matches.append(obj)
                        seen_ids.add(obj_id)
                        break
        
        return matches
        
    @Slot(int, int)
    def on_cell_hover(self, row, column):
        """Handle cell hover for image preview."""
        if row >= 0 and row < self.table.rowCount():
            item = self.table.item(row, 0)
            if item:
                obj_data = item.data(Qt.UserRole)
                if obj_data:
                    self.hover_row = row
                    self.hover_data = obj_data
                    # Start timer for tooltip (300ms delay)
                    self.tooltip_timer.start(300)
        
    @Slot()
    def show_image_tooltip(self):
        """Show image tooltip for hovered object."""
        if not self.hover_data:
            return
            
        try:
            object_name = self.hover_data.get('object_name', 'Unknown')
            ra_deg = self.hover_data.get('ra_degrees')
            dec_deg = self.hover_data.get('dec_degrees')
            astrobin_id = self.hover_data.get('astrobin_id')
            
            # Try to get sky survey image first
            if ra_deg is not None and dec_deg is not None:
                try:
                    ra_float = float(ra_deg)
                    dec_float = float(dec_deg)
                    pixmap, source = self.load_dss_image(ra_float, dec_float, object_name)
                    
                    if pixmap:
                        # Create tooltip HTML with image
                        tooltip_html = f"""
                        <div style='background-color: #1e1e1e; padding: 10px; border: 2px solid #4A9EFF;'>
                            <h3 style='color: #4A9EFF; margin: 0 0 10px 0;'>🌌 {object_name}</h3>
                            <p style='color: #b0b0b0; margin: 0;'><img src='data:image/png;base64,{self.pixmap_to_base64(pixmap)}' /></p>
                            <p style='color: #808080; font-size: 8pt; margin: 5px 0 0 0;'>🔭 {source} Survey</p>
                        </div>
                        """
                        # For now, use simple text tooltip
                        # Qt doesn't support rich image tooltips easily, so show text
                        QToolTip.showText(
                            QCursor.pos(),
                            f"🌌 {object_name}\n📍 RA: {ra_float:.2f}° Dec: {dec_float:.2f}°\n🔭 {source} image available",
                            self.table
                        )
                        return
                except (ValueError, TypeError) as e:
                    self.logger.debug(f"Invalid coordinates: {e}")
            
            # Fallback to simple text tooltip
            tooltip_text = f"🌌 {object_name}"
            if self.hover_data.get('object_type'):
                tooltip_text += f"\n📂 Type: {self.hover_data.get('object_type')}"
            if self.hover_data.get('constellation'):
                tooltip_text += f"\n⭐ Constellation: {self.hover_data.get('constellation')}"
                
            QToolTip.showText(QCursor.pos(), tooltip_text, self.table)
            
        except Exception as e:
            self.logger.error(f"Error showing tooltip: {e}")
    
    def _parse_rating(self, rating_value) -> float:
        """Parse rating value which may be '5 - High', '5', or numeric."""
        if not rating_value:
            return 0.0
        
        try:
            # Handle string ratings like "5 - High", "4 - Good", etc.
            if isinstance(rating_value, str):
                # Extract first numeric part before any space or dash
                rating_str = str(rating_value).strip()
                if ' ' in rating_str:
                    rating_str = rating_str.split()[0]
                return float(rating_str)
            else:
                return float(rating_value)
        except (ValueError, AttributeError):
            self.logger.warning(f"Could not parse rating: {rating_value}")
            return 0.0
    
    def _is_transit_in_range(self, obj: Dict, start_time: str, end_time: str) -> bool:
        """Check if object transits between the specified time range."""
        try:
            ra_deg = obj.get('ra_degrees')
            if not ra_deg:
                return False
            
            # Convert RA from degrees to hours
            ra_hours = float(ra_deg) / 15.0
            
            # Calculate transit time
            current_dt = datetime.now()
            transit_time = self.astro_calc.calculate_transit_time(
                ra_hours,
                self.observatory['longitude'],
                current_dt.date()
            )
            
            if not transit_time:
                return False
            
            # Get transit time as HH:MM
            transit_str = transit_time.strftime("%H:%M")
            
            # Parse times to minutes
            start_hour, start_min = map(int, start_time.split(':'))
            end_hour, end_min = map(int, end_time.split(':'))
            transit_hour, transit_min = map(int, transit_str.split(':'))
            
            start_minutes = start_hour * 60 + start_min
            end_minutes = end_hour * 60 + end_min
            transit_minutes = transit_hour * 60 + transit_min
            
            # Handle time range crossing midnight
            if start_minutes > end_minutes:
                return transit_minutes >= start_minutes or transit_minutes <= end_minutes
            else:
                return start_minutes <= transit_minutes <= end_minutes
                
        except Exception as e:
            self.logger.debug(f"Error checking transit time for object: {e}")
            return False
            
    def load_dss_image(self, ra_deg: float, dec_deg: float, object_name: str) -> tuple:
        """Load astronomical image from best available source (SDSS, then DSS fallback).
        Returns: (QPixmap, source_name) where source_name is 'SDSS', 'DSS', or None
        """
        cache_key = f"sky_{ra_deg:.3f}_{dec_deg:.3f}"
        
        # Check cache (stores tuple of (pixmap, source))
        if cache_key in self.image_cache:
            cached = self.image_cache[cache_key]
            if cached is None:
                return None, None
            return cached
        
        # Try SDSS first (better quality, color images)
        pixmap = self._try_load_sdss(ra_deg, dec_deg, object_name)
        if pixmap and not pixmap.isNull():
            result = (pixmap, 'SDSS')
            self.image_cache[cache_key] = result
            return result
        
        # Fallback to DSS if SDSS fails
        pixmap = self._try_load_dss(ra_deg, dec_deg, object_name)
        if pixmap and not pixmap.isNull():
            result = (pixmap, 'DSS')
            self.image_cache[cache_key] = result
            return result
        
        # Cache failure to avoid repeated attempts
        self.image_cache[cache_key] = None
        return None, None
    
    def _try_load_sdss(self, ra_deg: float, dec_deg: float, object_name: str) -> QPixmap:
        """Try to load image from Sloan Digital Sky Survey."""
        try:
            # SDSS SkyServer cutout service - provides color composite images
            # Scale: 0.396 arcsec/pixel, width/height in pixels
            # Using 512x512 pixels = ~3.4 arcmin field of view
            width = 512
            height = 512
            scale = 0.4  # arcsec/pixel
            
            sdss_url = (
                f"http://skyserver.sdss.org/dr17/SkyServerWS/ImgCutout/getjpeg"
                f"?ra={ra_deg:.6f}&dec={dec_deg:.6f}"
                f"&width={width}&height={height}&scale={scale}"
            )
            
            self.logger.info(f"Fetching SDSS image for {object_name}")
            
            headers = {
                'User-Agent': 'NextAstroTarget/2.0.0 (Astronomy Application; PySide6)',
                'Accept': 'image/jpeg,image/*,*/*'
            }
            
            response = requests.get(sdss_url, headers=headers, timeout=8)
            
            if response.status_code == 200 and len(response.content) > 5000:
                # Load image
                img = Image.open(BytesIO(response.content))
                
                # Check if image is not just blank/black (SDSS returns black for no data)
                # Convert to grayscale and check average brightness
                img_gray = img.convert('L')
                img_array = np.array(img_gray)
                avg_brightness = np.mean(img_array)
                
                # If image is mostly black (avg < 10), SDSS has no data for this region
                if avg_brightness < 10:
                    self.logger.info(f"SDSS image too dark for {object_name}, likely no coverage")
                    return None
                
                # Resize if needed
                if img.size[0] > 400 or img.size[1] > 400:
                    img.thumbnail((400, 400), Image.Resampling.LANCZOS)
                
                # Convert to QPixmap
                img_bytes = BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)
                
                pixmap = QPixmap()
                pixmap.loadFromData(img_bytes.read())
                
                self.logger.info(f"Successfully loaded SDSS color image for {object_name}")
                return pixmap
                
        except Exception as e:
            self.logger.debug(f"Failed to load SDSS image: {e}")
            
        return None
    
    def _try_load_dss(self, ra_deg: float, dec_deg: float, object_name: str) -> QPixmap:
        """Fallback: Load color composite image from Digitized Sky Survey.
        Combines Red, Blue, and IR filters to create an RGB color image.
        """
        try:
            # DSS2 has multiple surveys we can combine for color
            # R: poss2ukstu_red (Red filter)
            # G: poss2ukstu_blue (Blue filter) 
            # B: poss2ukstu_ir (Infrared, used as blue channel for deeper sky)
            
            # Try to fetch and combine multiple filters for color
            size = 15.0  # 15 arcmin field of view
            
            self.logger.info(f"Fetching DSS color composite for {object_name}")
            
            headers = {
                'User-Agent': 'NextAstroTarget/2.0.0 (Astronomy Application; PySide6)',
                'Accept': 'image/gif,image/*,*/*;q=0.8'
            }
            
            # Fetch Red channel (brightest, use for luminance)
            red_url = (
                f"https://archive.stsci.edu/cgi-bin/dss_search"
                f"?v=poss2ukstu_red&r={ra_deg:.6f}&d={dec_deg:.6f}"
                f"&e=J2000&h={size}&w={size}&f=gif&c=none&fov=NONE&v3="
            )
            
            red_response = requests.get(red_url, headers=headers, timeout=8)
            
            if red_response.status_code == 200 and len(red_response.content) > 10000:
                red_img = Image.open(BytesIO(red_response.content)).convert('L')
                
                # Try to fetch Blue channel for color
                blue_url = (
                    f"https://archive.stsci.edu/cgi-bin/dss_search"
                    f"?v=poss2ukstu_blue&r={ra_deg:.6f}&d={dec_deg:.6f}"
                    f"&e=J2000&h={size}&w={size}&f=gif&c=none&fov=NONE&v3="
                )
                
                try:
                    blue_response = requests.get(blue_url, headers=headers, timeout=8)
                    if blue_response.status_code == 200 and len(blue_response.content) > 10000:
                        blue_img = Image.open(BytesIO(blue_response.content)).convert('L')
                        
                        # Create RGB composite
                        # Resize to same dimensions if needed
                        if red_img.size != blue_img.size:
                            blue_img = blue_img.resize(red_img.size, Image.Resampling.LANCZOS)
                        
                        # Create color image: R=red, G=(red+blue)/2, B=blue
                        # This creates a natural-looking color image
                        red_array = np.array(red_img)
                        blue_array = np.array(blue_img)
                        green_array = ((red_array.astype(np.float32) + blue_array.astype(np.float32)) / 2).astype(np.uint8)
                        
                        # Stack into RGB
                        rgb_array = np.stack([red_array, green_array, blue_array], axis=2)
                        color_img = Image.fromarray(rgb_array, mode='RGB')
                        
                        self.logger.info(f"Created DSS RGB composite for {object_name}")
                    else:
                        # Blue channel failed, create pseudo-color from red
                        color_img = self._create_pseudocolor(red_img)
                        self.logger.info(f"Created DSS pseudo-color image for {object_name}")
                        
                except Exception as e:
                    # Fallback to pseudo-color if blue channel fails
                    self.logger.debug(f"Blue channel failed, using pseudo-color: {e}")
                    color_img = self._create_pseudocolor(red_img)
                
                # Resize if needed
                if color_img.size[0] > 400 or color_img.size[1] > 400:
                    color_img.thumbnail((400, 400), Image.Resampling.LANCZOS)
                
                # Convert to QPixmap
                img_bytes = BytesIO()
                color_img.save(img_bytes, format='PNG')
                img_bytes.seek(0)
                
                pixmap = QPixmap()
                pixmap.loadFromData(img_bytes.read())
                
                self.logger.info(f"Successfully loaded DSS color image for {object_name}")
                return pixmap
                
        except Exception as e:
            self.logger.debug(f"Failed to load DSS image: {e}")
            
        return None
    
    def _create_pseudocolor(self, grayscale_img: Image.Image) -> Image.Image:
        """Create a pseudo-color image from grayscale using color mapping.
        Maps grayscale to a blue-white-red color scheme typical of astronomy images.
        """
        # Convert to numpy array
        gray_array = np.array(grayscale_img)
        
        # Normalize to 0-1
        gray_norm = gray_array.astype(np.float32) / 255.0
        
        # Create color mapping (blue for dark, white for bright, slight red for very bright)
        # R channel: gradual increase from 0 to 1
        r = np.clip(gray_norm * 1.2, 0, 1)
        
        # G channel: peaks at mid-tones
        g = np.clip(gray_norm * 1.1, 0, 1)
        
        # B channel: strong in dark areas, decreases with brightness
        b = np.clip(0.3 + gray_norm * 0.9, 0, 1)
        
        # Stack and convert back to uint8
        rgb_array = np.stack([
            (r * 255).astype(np.uint8),
            (g * 255).astype(np.uint8),
            (b * 255).astype(np.uint8)
        ], axis=2)
        
        return Image.fromarray(rgb_array, mode='RGB')
        
    def pixmap_to_base64(self, pixmap: QPixmap) -> str:
        """Convert QPixmap to base64 string."""
        from PySide6.QtCore import QBuffer, QIODevice
        import base64
        
        buffer = QBuffer()
        buffer.open(QIODevice.WriteOnly)
        pixmap.save(buffer, "PNG")
        return base64.b64encode(buffer.data()).decode()
        
    @Slot()
    def on_row_double_clicked(self):
        """Handle row double-click - show detail dialog with DSS image."""
        current_row = self.table.currentRow()
        if current_row >= 0:
            item = self.table.item(current_row, 0)
            if item:
                obj_data = item.data(Qt.UserRole)
                if obj_data:
                    self.object_selected.emit(obj_data)
                    self.show_object_detail_dialog(obj_data)
    
    def show_object_detail_dialog(self, obj_data: Dict):
        """Show detailed object information with DSS image preview."""
        try:
            self.logger.info(f"Opening detail dialog for {obj_data.get('object_name', 'Unknown')}")
            
            dialog = QDialog(self)
            dialog.setWindowTitle(f"🌌 {obj_data.get('object_name', 'Object Details')}")
            dialog.setMinimumSize(500, 600)
            
            layout = QVBoxLayout(dialog)
            layout.setSpacing(10)
            layout.setContentsMargins(15, 15, 15, 15)
            
            # Object name header
            name_label = QLabel(f"<h2 style='color: #4A9EFF;'>{obj_data.get('object_name', 'Unknown')}</h2>")
            layout.addWidget(name_label)
            
            # DSS Image section
            ra_deg = obj_data.get('ra_degrees')
            dec_deg = obj_data.get('dec_degrees')
            
            if ra_deg is not None and dec_deg is not None:
                try:
                    ra_float = float(ra_deg)
                    dec_float = float(dec_deg)
                    
                    self.logger.info(f"Loading sky survey image for coordinates: RA={ra_float}, Dec={dec_float}")
                    
                    # Load sky survey image (SDSS or DSS)
                    pixmap, source = self.load_dss_image(ra_float, dec_float, obj_data.get('object_name', ''))
                    
                    if pixmap and not pixmap.isNull():
                        self.logger.info(f"Sky survey image loaded successfully from {source}, size: {pixmap.width()}x{pixmap.height()}")
                        
                        image_label = QLabel()
                        # Scale image to fit dialog while maintaining aspect ratio
                        scaled_pixmap = pixmap.scaled(450, 450, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        image_label.setPixmap(scaled_pixmap)
                        image_label.setAlignment(Qt.AlignCenter)
                        image_label.setStyleSheet("border: 2px solid #4A9EFF; background-color: #000; padding: 5px;")
                        layout.addWidget(image_label)
                        
                        # Show source attribution
                        if source == 'SDSS':
                            caption_text = "🔭 Sloan Digital Sky Survey (SDSS) - Color Composite"
                        else:
                            caption_text = "🔭 Digitized Sky Survey (DSS) - Red Filter"
                        
                        caption = QLabel(caption_text)
                        caption.setAlignment(Qt.AlignCenter)
                        caption.setStyleSheet("color: #808080; font-size: 9pt;")
                        layout.addWidget(caption)
                    else:
                        self.logger.warning(f"Sky survey image not available for {obj_data.get('object_name')}")
                        no_image_label = QLabel("📷 No survey image available")
                        no_image_label.setAlignment(Qt.AlignCenter)
                        no_image_label.setStyleSheet("font-size: 11pt; padding: 20px; color: #808080;")
                        layout.addWidget(no_image_label)
                        
                except (ValueError, TypeError) as e:
                    self.logger.error(f"Error with coordinates: {e}")
                    error_label = QLabel("⚠️ Invalid coordinates")
                    error_label.setAlignment(Qt.AlignCenter)
                    error_label.setStyleSheet("font-size: 11pt; padding: 20px; color: #ff6b6b;")
                    layout.addWidget(error_label)
            else:
                no_coord_label = QLabel("📍 No coordinates available")
                no_coord_label.setAlignment(Qt.AlignCenter)
                no_coord_label.setStyleSheet("font-size: 11pt; padding: 20px; color: #808080;")
                layout.addWidget(no_coord_label)
            
            # Object details
            try:
                # Safely parse rating
                rating_value = obj_data.get('rating', '0')
                if rating_value:
                    rating_num = self._parse_rating(rating_value)
                    rating_stars = '⭐' * int(rating_num) if rating_num > 0 else ''
                else:
                    rating_stars = ''
                    rating_value = 'Unknown'
                
                details_text = f"""
                <div style='font-size: 11pt; line-height: 1.6;'>
                    <p><b>Type:</b> {obj_data.get('object_type', 'Unknown')}</p>
                    <p><b>Constellation:</b> {obj_data.get('constellation', 'Unknown')}</p>
                    <p><b>Size:</b> {obj_data.get('size_arcmin', 'Unknown')}' arcminutes</p>
                    <p><b>Rating:</b> {rating_stars} {rating_value}</p>
                    <p><b>RA:</b> {ra_deg if ra_deg else 'Unknown'} ({obj_data.get('ra_hms', 'Unknown')})</p>
                    <p><b>Dec:</b> {dec_deg if dec_deg else 'Unknown'} ({obj_data.get('dec_dms', 'Unknown')})</p>
                </div>
                """
                
                details_label = QLabel(details_text)
                details_label.setWordWrap(True)
                layout.addWidget(details_label)
            except Exception as e:
                self.logger.error(f"Error formatting details: {e}")
            
            # Close button
            close_btn = QPushButton("Close")
            close_btn.setFixedHeight(32)
            close_btn.setMinimumWidth(100)
            close_btn.clicked.connect(dialog.accept)
            layout.addWidget(close_btn)
            
            self.logger.info("Showing detail dialog")
            dialog.exec_()
            
        except Exception as e:
            self.logger.error(f"Error showing detail dialog: {e}", exc_info=True)
            QMessageBox.warning(self, "Error", f"Could not show object details: {str(e)}")
                    
    @Slot(object)
    def show_context_menu(self, pos):
        """Show context menu on right-click."""
        menu = QMenu(self)
        
        view_action = QAction("📋 View Details", self)
        view_action.triggered.connect(self.on_row_double_clicked)
        menu.addAction(view_action)
        
        menu.addSeparator()
        
        export_action = QAction("💾 Export to CSV", self)
        menu.addAction(export_action)
        
        menu.exec_(self.table.mapToGlobal(pos))
        
    def apply_filters(self, filters: Dict):
        """Apply filters to object list."""
        self.logger.info(f"Applying filters: {filters}")
        self.current_filters = filters
        self.filtered_objects = self.all_objects.copy()
        
        try:
            # Apply rating filter
            if filters.get('rating') and filters['rating'] != "All":
                rating_str = filters['rating']
                # Handle both "5+" and "5" formats
                if '+' in rating_str:
                    min_rating = float(rating_str.replace('+', ''))
                else:
                    min_rating = float(rating_str)
                    
                before_count = len(self.filtered_objects)
                self.filtered_objects = [
                    obj for obj in self.filtered_objects
                    if obj.get('rating') and self._parse_rating(obj['rating']) >= min_rating
                ]
                self.logger.info(f"Rating filter ({rating_str}): {before_count} -> {len(self.filtered_objects)} objects")
                
            # Apply type filter
            if filters.get('type') and filters['type'] != "All":
                filter_type = filters['type']
                before_count = len(self.filtered_objects)
                
                # Map filter names to database type abbreviations
                type_mapping = {
                    'Galaxies': ['gal', 'galaxy'],
                    'Nebulae': ['neb', 'nebula', 'planetary', 'emission', 'reflection'],
                    'Clusters': ['cluster', 'open', 'globular', 'cl'],
                    'Others': []  # Will be handled specially
                }
                
                if filter_type in type_mapping:
                    search_terms = type_mapping[filter_type]
                    if filter_type == 'Others':
                        # Others = anything not in the main categories
                        excluded_terms = ['gal', 'neb', 'cluster', 'cl']
                        self.filtered_objects = [
                            obj for obj in self.filtered_objects
                            if not any(term in str(obj.get('object_type', '')).lower() 
                                      for term in excluded_terms)
                        ]
                    else:
                        self.filtered_objects = [
                            obj for obj in self.filtered_objects
                            if any(term in str(obj.get('object_type', '')).lower() 
                                  for term in search_terms)
                        ]
                self.logger.info(f"Type filter ({filter_type}): {before_count} -> {len(self.filtered_objects)} objects")
                
            # Apply size filter
            size_min = filters.get('size_min', 0)
            size_max = filters.get('size_max', 9999)
            if size_min > 0 or size_max < 9999:
                before_count = len(self.filtered_objects)
                filtered_by_size = []
                for obj in self.filtered_objects:
                    size_val = obj.get('size_arcmin')
                    if size_val is not None:
                        try:
                            size_float = float(size_val)
                            if size_min <= size_float <= size_max:
                                filtered_by_size.append(obj)
                        except (ValueError, TypeError):
                            # Skip objects with invalid size values
                            pass
                self.filtered_objects = filtered_by_size
                self.logger.info(f"Size filter ({size_min}'-{size_max}'): {before_count} -> {len(self.filtered_objects)} objects")
                
            # Apply transit time filter
            transit_start = filters.get('transit_start')
            transit_end = filters.get('transit_end')
            if transit_start and transit_end and (transit_start != "00:00" or transit_end != "23:59"):
                before_count = len(self.filtered_objects)
                
                # Filter objects by transit time
                filtered_by_transit = []
                for obj in self.filtered_objects:
                    if self._is_transit_in_range(obj, transit_start, transit_end):
                        filtered_by_transit.append(obj)
                
                self.filtered_objects = filtered_by_transit
                self.logger.info(f"Transit filter ({transit_start}-{transit_end}): {before_count} -> {len(self.filtered_objects)} objects")
            
            # Apply declination filter
            dec_min = filters.get('dec_min', -90)
            dec_max = filters.get('dec_max', 90)
            if dec_min > -90 or dec_max < 90:
                before_count = len(self.filtered_objects)
                filtered_by_dec = []
                for obj in self.filtered_objects:
                    dec_val = obj.get('dec_degrees')
                    if dec_val is not None:
                        try:
                            dec_float = float(dec_val)
                            if dec_min <= dec_float <= dec_max:
                                filtered_by_dec.append(obj)
                        except (ValueError, TypeError):
                            # Skip objects with invalid declination values
                            pass
                self.filtered_objects = filtered_by_dec
                self.logger.info(f"Declination filter ({dec_min}° to {dec_max}°): {before_count} -> {len(self.filtered_objects)} objects")
                
        except Exception as e:
            self.logger.error(f"Error applying filters: {e}", exc_info=True)
            
        self.update_table_display()
        self.logger.info(f"Filter application complete. Showing {len(self.filtered_objects)} of {len(self.all_objects)} objects")
        
    def update_astronomical_calculations(self):
        """Update astronomical calculations for visible objects."""
        # TODO: Calculate transit times and altitudes
        pass

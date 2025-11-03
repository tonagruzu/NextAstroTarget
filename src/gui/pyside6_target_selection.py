"""
Modern PySide6 target selection GUI with professional table view.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QLabel, QLineEdit, QMenu, QMessageBox, QToolTip
)
from PySide6.QtCore import Qt, Signal, Slot, QTimer, QPoint
from PySide6.QtGui import QColor, QBrush, QFont, QAction, QPixmap, QCursor
import logging
import pandas as pd
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
        self.search_edit.setPlaceholderText("Type object name...")
        self.search_edit.textChanged.connect(self.on_search_changed)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_edit)
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
        """Load objects from database."""
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
            self.filtered_objects = self.all_objects.copy()
            
            self.logger.info(f"Loaded {len(self.all_objects)} objects")
            self.update_table_display()
            
        except Exception as e:
            self.logger.error(f"Failed to load objects: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load objects: {str(e)}")
            
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
        """Handle search text changes."""
        if not text:
            self.filtered_objects = self.all_objects.copy()
        else:
            text_lower = text.lower()
            self.filtered_objects = [
                obj for obj in self.all_objects
                if text_lower in str(obj.get('object_name', '')).lower() or
                   text_lower in str(obj.get('nick', '')).lower()
            ]
            
        self.update_table_display()
        
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
            
            # Try to get DSS image first
            if ra_deg is not None and dec_deg is not None:
                try:
                    ra_float = float(ra_deg)
                    dec_float = float(dec_deg)
                    pixmap = self.load_dss_image(ra_float, dec_float, object_name)
                    
                    if pixmap:
                        # Create tooltip HTML with image
                        tooltip_html = f"""
                        <div style='background-color: #1e1e1e; padding: 10px; border: 2px solid #4A9EFF;'>
                            <h3 style='color: #4A9EFF; margin: 0 0 10px 0;'>🌌 {object_name}</h3>
                            <p style='color: #b0b0b0; margin: 0;'><img src='data:image/png;base64,{self.pixmap_to_base64(pixmap)}' /></p>
                            <p style='color: #808080; font-size: 8pt; margin: 5px 0 0 0;'>🔭 Digitized Sky Survey</p>
                        </div>
                        """
                        # For now, use simple text tooltip
                        # Qt doesn't support rich image tooltips easily, so show text
                        QToolTip.showText(
                            QCursor.pos(),
                            f"🌌 {object_name}\n📍 RA: {ra_float:.2f}° Dec: {dec_float:.2f}°\n🔭 Image available",
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
            
    def load_dss_image(self, ra_deg: float, dec_deg: float, object_name: str) -> QPixmap:
        """Load image from Digitized Sky Survey."""
        cache_key = f"dss_{ra_deg:.3f}_{dec_deg:.3f}"
        
        # Check cache
        if cache_key in self.image_cache:
            return self.image_cache[cache_key]
            
        try:
            # DSS URL with 12 arcmin field of view
            dss_url = f"https://archive.stsci.edu/cgi-bin/dss_search?v=poss2ukstu_red&r={ra_deg:.6f}&d={dec_deg:.6f}&e=J2000&h=12.0&w=12.0&f=gif&c=none&fov=NONE&v3="
            
            self.logger.info(f"Fetching DSS image for {object_name}")
            
            headers = {
                'User-Agent': 'NextAstroTarget/2.0.0 (Astronomy Application; PySide6)',
                'Accept': 'image/gif,image/*,*/*;q=0.8'
            }
            
            response = requests.get(dss_url, headers=headers, timeout=5)
            
            if response.status_code == 200 and len(response.content) > 10000:
                # Load and resize image
                img = Image.open(BytesIO(response.content))
                img.thumbnail((200, 200), Image.Resampling.LANCZOS)
                
                # Convert to QPixmap
                img_bytes = BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)
                
                pixmap = QPixmap()
                pixmap.loadFromData(img_bytes.read())
                
                # Cache the pixmap
                self.image_cache[cache_key] = pixmap
                
                self.logger.info(f"Successfully loaded DSS image for {object_name}")
                return pixmap
                
        except Exception as e:
            self.logger.debug(f"Failed to load DSS image: {e}")
            self.image_cache[cache_key] = None
            
        return None
        
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
        """Handle row double-click."""
        current_row = self.table.currentRow()
        if current_row >= 0:
            item = self.table.item(current_row, 0)
            if item:
                obj_data = item.data(Qt.UserRole)
                if obj_data:
                    self.object_selected.emit(obj_data)
                    QMessageBox.information(
                        self,
                        obj_data.get('object_name', 'Object'),
                        f"Details for {obj_data.get('object_name')}\\n\\n"
                        f"Type: {obj_data.get('object_type')}\\n"
                        f"Constellation: {obj_data.get('constellation')}\\n"
                        f"Size: {obj_data.get('size_arcmin')}'\\n"
                        f"Rating: {obj_data.get('rating')} stars"
                    )
                    
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
                min_rating_str = filters['rating'].replace('+', '')
                try:
                    min_rating = float(min_rating_str)
                    before_count = len(self.filtered_objects)
                    self.filtered_objects = [
                        obj for obj in self.filtered_objects
                        if obj.get('rating') and float(obj['rating']) >= min_rating
                    ]
                    self.logger.info(f"Rating filter ({filters['rating']}): {before_count} → {len(self.filtered_objects)} objects")
                except ValueError:
                    self.logger.error(f"Invalid rating value: {filters['rating']}")
                
            # Apply type filter
            if filters.get('type') and filters['type'] != "All":
                filter_type = filters['type']
                before_count = len(self.filtered_objects)
                
                # Map filter names to database types
                type_mapping = {
                    'Galaxies': ['galaxy', 'galaxies'],
                    'Nebulae': ['nebula', 'nebulae', 'emission', 'reflection', 'planetary'],
                    'Clusters': ['cluster', 'open cluster', 'globular cluster'],
                    'Others': []  # Will be handled specially
                }
                
                if filter_type in type_mapping:
                    search_terms = type_mapping[filter_type]
                    if filter_type == 'Others':
                        # Others = anything not in the main categories
                        excluded_terms = ['galaxy', 'nebula', 'cluster']
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
                self.logger.info(f"Type filter ({filter_type}): {before_count} → {len(self.filtered_objects)} objects")
                
            # Apply size filter
            size_min = filters.get('size_min', 0)
            size_max = filters.get('size_max', 9999)
            if size_min > 0 or size_max < 9999:
                before_count = len(self.filtered_objects)
                self.filtered_objects = [
                    obj for obj in self.filtered_objects
                    if obj.get('size_arcmin') and 
                       size_min <= float(obj['size_arcmin']) <= size_max
                ]
                self.logger.info(f"Size filter ({size_min}'-{size_max}'): {before_count} → {len(self.filtered_objects)} objects")
                
            # Apply transit time filter
            transit_start = filters.get('transit_start')
            transit_end = filters.get('transit_end')
            if transit_start and transit_end and (transit_start != "00:00" or transit_end != "23:59"):
                before_count = len(self.filtered_objects)
                # TODO: Implement transit time filtering
                self.logger.info(f"Transit filter ({transit_start}-{transit_end}): {before_count} → {len(self.filtered_objects)} objects")
                
        except Exception as e:
            self.logger.error(f"Error applying filters: {e}", exc_info=True)
            
        self.update_table_display()
        self.logger.info(f"Filter application complete. Showing {len(self.filtered_objects)} of {len(self.all_objects)} objects")
        
    def update_astronomical_calculations(self):
        """Update astronomical calculations for visible objects."""
        # TODO: Calculate transit times and altitudes
        pass

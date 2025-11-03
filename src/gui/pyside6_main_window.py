"""
Modern PySide6 main window for NextAstroTarget application.
Features professional UI with dark theme, improved layouts, and better UX.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QFrame, QSplitter, QGroupBox, QComboBox,
    QSpinBox, QDoubleSpinBox, QTimeEdit, QScrollArea, QStatusBar,
    QMessageBox, QDockWidget, QLineEdit
)
from PySide6.QtCore import Qt, QTime, QTimer, Signal, Slot
from PySide6.QtGui import QFont, QPalette, QColor, QIcon, QPainter, QBrush, QPen, QPixmap, QImage
from datetime import datetime, timedelta
import logging
from typing import Optional, Dict, Any
from pathlib import Path
import configparser
import os

from src.database.database_manager import DatabaseManager
from src.gui.pyside6_target_selection import PySide6TargetSelectionGUI
from src.gui.pyside6_weather_widget import PySide6WeatherWidget
from src.utils.astronomical_calculations import AstronomicalCalculator
from src.utils.location_service import LocationService


class MoonPhaseWidget(QWidget):
    """Custom widget to display real moon phase images."""
    
    # Class-level cache for moon images
    _moon_cache = {}
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(120, 150)
        self.setMaximumSize(120, 150)
        self.phase_data = None
        self.moon_pixmap = None
        self.logger = logging.getLogger(__name__)
        
        # Ensure cache directory exists
        self.cache_dir = Path('data/moon_cache')
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def set_phase_data(self, phase_data: Dict[str, Any]):
        """Update moon phase data and load corresponding image."""
        self.phase_data = phase_data
        if phase_data:
            self._load_moon_image()
        self.update()
    
    def _load_moon_image(self):
        """Load real moon phase image based on lunar day with caching."""
        try:
            import requests
            
            # Get cycle position (0.0 = new moon, 0.5 = full moon, 1.0 = new moon)
            cycle_position = self.phase_data.get('cycle_position', 0)
            
            # Map cycle_position (0-1) to frame number (1-29)
            # Frame 1 = cycle 0.000 (new moon)
            # Frame 15 = cycle 0.500 (full moon)
            # Frame 29 = cycle 1.000 (back to new moon)
            # Formula: frame = round(cycle * 28) + 1
            frame_num = round(cycle_position * 28) + 1
            frame_num = max(1, min(29, frame_num))  # Clamp to valid range 1-29
            
            # Check memory cache first
            if frame_num in self._moon_cache:
                self.moon_pixmap = self._moon_cache[frame_num]
                self.logger.debug(f"Loaded moon image for frame {frame_num} from memory cache")
                return
            
            # Check disk cache - use existing moon_day_XX.jpg files (frames 1-29)
            cache_file = self.cache_dir / f"moon_day_{frame_num:02d}.jpg"
            if cache_file.exists():
                self.moon_pixmap = QPixmap(str(cache_file))
                if not self.moon_pixmap.isNull():
                    # Scale to larger size (110x110)
                    self.moon_pixmap = self.moon_pixmap.scaled(
                        110, 110,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    self._moon_cache[frame_num] = self.moon_pixmap
                    self.logger.info(f"Loaded moon image for frame {frame_num} from disk cache")
                    return
                else:
                    self.logger.warning(f"Cached file exists but failed to load: {cache_file}")
            else:
                self.logger.warning(f"Moon image file not found: {cache_file}")
            
            # If we get here, file doesn't exist or failed to load - use fallback
            self.logger.info("Using fallback graphic for moon phase")
            self._draw_fallback_graphic()
                
        except Exception as e:
            self.logger.warning(f"Failed to load moon image: {e}")
            # Use fallback on exception
            self.logger.info("Using fallback graphic for moon phase")
            self._draw_fallback_graphic()
    
    def _draw_fallback_graphic(self):
        """Create fallback moon graphic if image loading fails."""
        # Create a pixmap with drawn moon phase
        pixmap = QPixmap(110, 110)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if not self.phase_data:
            return
        
        size = 100
        margin = 5
        illumination = self.phase_data['illumination']
        cycle_position = self.phase_data['cycle_position']
        
        # Draw main moon circle (lit portion)
        painter.setBrush(QBrush(QColor("#F5F5DC")))  # Beige color
        painter.setPen(QPen(QColor("gray"), 1))
        painter.drawEllipse(margin, margin, size, size)
        
        # Draw shadow based on cycle position
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor("#2F2F2F")))  # Dark shadow
        
        if illumination < 1:  # New Moon
            painter.drawEllipse(margin + 1, margin + 1, size - 2, size - 2)
        elif illumination > 99:  # Full Moon
            pass  # No shadow
        else:
            # Partial phases - simplified for fallback
            if cycle_position <= 0.5:
                # Waxing phases
                shadow_coverage = 1.0 - (cycle_position * 2)
                shadow_width = size * shadow_coverage
                if shadow_width > 0:
                    painter.drawEllipse(margin, margin, int(shadow_width), size)
            else:
                # Waning phases
                shadow_coverage = (cycle_position - 0.5) * 2
                shadow_start = size * (1.0 - shadow_coverage)
                painter.drawEllipse(
                    int(margin + shadow_start), margin,
                    int(size - shadow_start), size
                )
        
        # Draw outer circle
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor("gray"), 2))
        painter.drawEllipse(margin, margin, size, size)
        
        painter.end()
        self.moon_pixmap = pixmap
        
    def paintEvent(self, event):
        """Draw moon phase image or graphic."""
        if not self.phase_data:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw moon image if available - centered and moved up
        if self.moon_pixmap:
            # Center the image horizontally, start at y=2 (moved up from y=5)
            x = (120 - self.moon_pixmap.width()) // 2
            y = 2
            painter.drawPixmap(x, y, self.moon_pixmap)
        
        # Draw text below image (moved up to ensure visibility)
        y_offset = 115  # Moved up from 120 to prevent cutoff
        painter.setPen(QColor("white"))
        font = QFont("Arial", 10, QFont.Bold)
        painter.setFont(font)
        illumination = self.phase_data.get('illumination', 0)
        painter.drawText(0, y_offset, 120, 20, Qt.AlignCenter, f"{illumination:.0f}%")
        
        font.setPointSize(8)
        font.setBold(False)
        painter.setFont(font)
        painter.setPen(QColor("gray"))
        phase_name = self.phase_data.get('phase_name', '')
        painter.drawText(0, y_offset + 13, 120, 20, Qt.AlignCenter, phase_name)


class ModernMainWindow(QMainWindow):
    """Modern PySide6 main application window with professional UI."""
    
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        self.astro_calc = AstronomicalCalculator()
        self.location_service = LocationService()
        
        # Current screen tracking
        self.current_screen = None
        self.screens = {}
        
        # Observatory settings
        self.observatory = {
            'latitude': 40.0,
            'longitude': -75.0,
            'elevation': 100.0,
            'timezone': 'EST',
            'gmt_offset': -5.0,
            'dst_active': True
        }
        
        # Active filter tracking
        self.active_filters = {
            'declination': False,
            'size': False,
            'transit': False,
            'rating': None,
            'catalog': None,
            'type': None
        }
        
        # Filter button references
        self.filter_buttons = {}
        
        # Load settings
        self.load_observatory_config()
        
        # Setup modern UI
        self.setup_modern_ui()
        self.apply_modern_stylesheet()
        
        # Load persistent filter settings after UI is set up
        self.load_persistent_settings()
        
        # Update astronomical data
        self.update_astronomical_data()
        
        # Check database and navigate
        self.check_database_and_navigate()
    
    def setup_modern_ui(self):
        """Set up modern PySide6 interface."""
        self.setWindowTitle("NextAstroTarget - Astronomy Target Planning")
        self.setMinimumSize(1400, 900)
        
        # Create central widget with modern layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout with splitter for resizable sections
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create main splitter (vertical)
        main_splitter = QSplitter(Qt.Vertical)
        main_layout.addWidget(main_splitter)
        
        # Top section: Controls and info
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(8, 5, 8, 5)
        top_layout.setSpacing(5)
        
        # Add header
        self.setup_header(top_layout)
        
        # Create horizontal splitter for Observatory and Weather sections
        top_horizontal_splitter = QSplitter(Qt.Horizontal)
        
        # Left side: Observatory (narrowed by 50%)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(5)
        self.setup_timing_location(left_layout)
        self.setup_sun_moon_info_inline(left_layout)
        top_horizontal_splitter.addWidget(left_widget)
        
        # Right side: Weather (taller, using vertical space)
        self.setup_weather_info_inline(top_horizontal_splitter)
        
        # Set splitter proportions: Observatory/Sun+Moon 50%, Weather 50%
        top_horizontal_splitter.setSizes([600, 600])
        
        top_layout.addWidget(top_horizontal_splitter)
        self.setup_filtering_controls(top_layout)
        
        # Add to main splitter
        main_splitter.addWidget(top_widget)
        
        # Bottom section: Object data view
        self.object_data_container = QWidget()
        main_splitter.addWidget(self.object_data_container)
        
        # Set splitter proportions - less space for controls, more for object list
        main_splitter.setSizes([320, 580])
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
    def setup_header(self, parent_layout):
        """Create modern header section."""
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(5, 5, 5, 5)
        
        # App icon and title container
        title_container = QWidget()
        title_container_layout = QHBoxLayout(title_container)
        title_container_layout.setContentsMargins(0, 0, 0, 0)
        title_container_layout.setSpacing(15)
        
        # App icon
        icon_label = QLabel()
        icon_path = Path(__file__).parent.parent.parent / "assets" / "icon_64.png"
        if icon_path.exists():
            icon_pixmap = QPixmap(str(icon_path))
            # Scale icon to balanced size (56x56)
            scaled_icon = icon_pixmap.scaled(56, 56, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(scaled_icon)
        else:
            self.logger.warning(f"App icon not found at {icon_path}")
        title_container_layout.addWidget(icon_label)
        
        # App title with much larger font
        title_label = QLabel("NextAstroTarget")
        title_font = QFont("Segoe UI", 96, QFont.Bold)  # Doubled from 48pt to 96pt
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #4A9EFF;")
        title_container_layout.addWidget(title_label)
        
        header_layout.addWidget(title_container)
        header_layout.addStretch()
        
        # Quick action buttons - reduced height
        self.refresh_btn = QPushButton("🔄 Refresh Data")
        self.settings_btn = QPushButton("⚙️ Settings")
        self.help_btn = QPushButton("❓ Help")
        
        for btn in [self.refresh_btn, self.settings_btn, self.help_btn]:
            btn.setFixedHeight(30)
            btn.setMinimumWidth(110)
            header_layout.addWidget(btn)
        
        parent_layout.addWidget(header_frame)
        
    def setup_timing_location(self, parent_layout):
        """Create timing and location controls."""
        group = QGroupBox("📍 Observatory & Time Settings")
        group.setObjectName("controlGroup")
        # Larger font for section title
        group_font = QFont("Segoe UI", 11, QFont.Bold)
        group.setFont(group_font)
        # No width constraint - expand to fill available space
        layout = QGridLayout(group)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Location
        layout.addWidget(QLabel("Location:"), 0, 0)
        self.location_combo = QComboBox()
        self.location_combo.addItems(["Custom Location", "Load from GPS"])
        self.location_combo.setMinimumWidth(200)
        layout.addWidget(self.location_combo, 0, 1)
        
        # Latitude
        layout.addWidget(QLabel("Latitude:"), 0, 2)
        self.lat_spin = QDoubleSpinBox()
        self.lat_spin.setRange(-90, 90)
        self.lat_spin.setValue(self.observatory['latitude'])
        self.lat_spin.setSuffix("°")
        self.lat_spin.setDecimals(4)
        layout.addWidget(self.lat_spin, 0, 3)
        
        # Longitude
        layout.addWidget(QLabel("Longitude:"), 0, 4)
        self.lon_spin = QDoubleSpinBox()
        self.lon_spin.setRange(-180, 180)
        self.lon_spin.setValue(self.observatory['longitude'])
        self.lon_spin.setSuffix("°")
        self.lon_spin.setDecimals(4)
        layout.addWidget(self.lon_spin, 0, 5)
        
        # Address input (new row)
        layout.addWidget(QLabel("Address:"), 1, 0)
        self.address_edit = QLineEdit()
        self.address_edit.setPlaceholderText("Enter address (e.g., Gdansk, Poland)")
        self.address_edit.setMinimumWidth(300)
        layout.addWidget(self.address_edit, 1, 1, 1, 3)
        
        # Geocode button
        geocode_btn = QPushButton("🔍 Geocode")
        geocode_btn.setFixedHeight(30)
        geocode_btn.setMinimumWidth(100)
        geocode_btn.clicked.connect(self.geocode_address)
        geocode_btn.setToolTip("Convert address to coordinates using OpenStreetMap")
        layout.addWidget(geocode_btn, 1, 4)
        
        # Date/Time
        layout.addWidget(QLabel("Observation Time:"), 2, 0)
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime.currentTime())
        self.time_edit.setDisplayFormat("HH:mm")
        layout.addWidget(self.time_edit, 2, 1)
        
        # Apply button
        apply_btn = QPushButton("Apply Settings")
        apply_btn.setFixedHeight(30)
        apply_btn.setMinimumWidth(120)
        apply_btn.clicked.connect(self.apply_location_settings)
        layout.addWidget(apply_btn, 2, 5)
        
        parent_layout.addWidget(group)
        
    def setup_sun_moon_info(self, parent_splitter):
        """Create sun and moon information display."""
        group = QGroupBox("☀️ Sun & 🌙 Moon")
        group.setObjectName("infoGroup")
        # Larger font for section title
        group_font = QFont("Segoe UI", 11, QFont.Bold)
        group.setFont(group_font)
        # Reduce width by 50%
        group.setMaximumWidth(400)
        layout = QVBoxLayout(group)
        layout.setSpacing(3)
        layout.setContentsMargins(8, 5, 8, 5)
        
        # Sun info - compact display
        self.sun_info_label = QLabel("Calculating sun data...")
        self.sun_info_label.setWordWrap(True)
        self.sun_info_label.setStyleSheet("font-size: 13pt; font-weight: 500;")
        layout.addWidget(self.sun_info_label)
        
        # Moon info with phase graphic
        moon_container = QHBoxLayout()
        moon_container.setSpacing(5)
        
        self.moon_info_label = QLabel("Calculating moon data...")
        self.moon_info_label.setWordWrap(True)
        self.moon_info_label.setStyleSheet("font-size: 13pt; font-weight: 500;")
        moon_container.addWidget(self.moon_info_label, 1)
        
        # Add moon phase widget - smaller size
        self.moon_phase_widget = MoonPhaseWidget()
        self.moon_phase_widget.setMaximumSize(80, 100)
        moon_container.addWidget(self.moon_phase_widget)
        
        layout.addLayout(moon_container)
        
        parent_splitter.addWidget(group)
        
    def setup_weather_info(self, parent_splitter):
        """Create weather forecast display."""
        group = QGroupBox("🌤️ Weather Forecast")
        group.setObjectName("infoGroup")
        # Larger font for section title
        group_font = QFont("Segoe UI", 11, QFont.Bold)
        group.setFont(group_font)
        # Make weather widget taller - double the height
        group.setMinimumHeight(350)
        layout = QVBoxLayout(group)
        layout.setSpacing(5)
        layout.setContentsMargins(8, 8, 8, 8)
        
        try:
            self.weather_widget = PySide6WeatherWidget(group)
            # Update weather location from observatory settings
            self.weather_widget.update_location(
                self.observatory['latitude'],
                self.observatory['longitude']
            )
            layout.addWidget(self.weather_widget)
        except Exception as e:
            self.logger.error(f"Failed to create weather widget: {e}")
            layout.addWidget(QLabel("Weather data unavailable"))
        
        parent_splitter.addWidget(group)
        
    def setup_sun_moon_info_inline(self, parent_layout):
        """Create sun and moon information display (inline for left column)."""
        group = QGroupBox("☀️ Sun & 🌙 Moon")
        group.setObjectName("infoGroup")
        # Larger font for section title
        group_font = QFont("Segoe UI", 11, QFont.Bold)
        group.setFont(group_font)
        # No width constraint - expand to fill available space
        layout = QVBoxLayout(group)
        layout.setSpacing(3)
        layout.setContentsMargins(8, 5, 8, 5)
        
        # Sun info - compact display
        self.sun_info_label = QLabel("Calculating sun data...")
        self.sun_info_label.setWordWrap(True)
        self.sun_info_label.setStyleSheet("font-size: 13pt; font-weight: 500;")
        layout.addWidget(self.sun_info_label)
        
        # Moon info with phase graphic
        moon_container = QHBoxLayout()
        moon_container.setSpacing(5)
        
        self.moon_info_label = QLabel("Calculating moon data...")
        self.moon_info_label.setWordWrap(True)
        self.moon_info_label.setStyleSheet("font-size: 13pt; font-weight: 500;")
        moon_container.addWidget(self.moon_info_label, 1)
        
        # Add moon phase widget - smaller size
        self.moon_phase_widget = MoonPhaseWidget()
        self.moon_phase_widget.setMaximumSize(80, 100)
        moon_container.addWidget(self.moon_phase_widget)
        
        layout.addLayout(moon_container)
        
        parent_layout.addWidget(group)
        
    def setup_weather_info_inline(self, parent_splitter):
        """Create weather forecast display (inline for right column - taller and narrower)."""
        group = QGroupBox("🌤️ Weather Forecast")
        group.setObjectName("infoGroup")
        # Larger font for section title
        group_font = QFont("Segoe UI", 11, QFont.Bold)
        group.setFont(group_font)
        # Narrower but taller - use vertical space
        group.setMaximumWidth(700)
        group.setMinimumHeight(400)
        layout = QVBoxLayout(group)
        layout.setSpacing(5)
        layout.setContentsMargins(8, 8, 8, 8)
        
        try:
            self.weather_widget = PySide6WeatherWidget(group)
            # Update weather location from observatory settings
            self.weather_widget.update_location(
                self.observatory['latitude'],
                self.observatory['longitude']
            )
            layout.addWidget(self.weather_widget)
        except Exception as e:
            self.logger.error(f"Failed to create weather widget: {e}")
            layout.addWidget(QLabel("Weather data unavailable"))
        
        parent_splitter.addWidget(group)
    
    def setup_filtering_controls(self, parent_layout):
        """Create modern filtering controls."""
        group = QGroupBox("🔍 Target Filters")
        group.setObjectName("controlGroup")
        # Larger font for section title
        group_font = QFont("Segoe UI", 11, QFont.Bold)
        group.setFont(group_font)
        layout = QGridLayout(group)
        layout.setSpacing(6)
        layout.setContentsMargins(8, 8, 8, 8)
        
        row = 0
        
        # Rating filter
        layout.addWidget(QLabel("Rating:"), row, 0)
        rating_layout = QHBoxLayout()
        self.rating_buttons = {}
        for rating in ["All", "3+", "4+", "5"]:
            btn = QPushButton(f"⭐ {rating}")
            btn.setCheckable(True)
            btn.setFixedHeight(30)
            btn.setMinimumWidth(70)
            btn.clicked.connect(lambda checked, r=rating: self.filter_by_rating(r))
            self.rating_buttons[rating] = btn
            rating_layout.addWidget(btn)
        self.rating_buttons["All"].setChecked(True)
        layout.addLayout(rating_layout, row, 1, 1, 5)
        row += 1
        
        # Object type filter
        layout.addWidget(QLabel("Type:"), row, 0)
        type_layout = QHBoxLayout()
        self.type_buttons = {}
        for obj_type in ["All", "Galaxies", "Nebulae", "Clusters", "Others"]:
            btn = QPushButton(obj_type)
            btn.setCheckable(True)
            btn.setFixedHeight(30)
            btn.setMinimumWidth(75)
            btn.clicked.connect(lambda checked, t=obj_type: self.filter_by_type(t))
            self.type_buttons[obj_type] = btn
            type_layout.addWidget(btn)
        self.type_buttons["All"].setChecked(True)
        layout.addLayout(type_layout, row, 1, 1, 5)
        row += 1
        
        # Size range
        layout.addWidget(QLabel("Size Range:"), row, 0)
        self.size_min = QSpinBox()
        self.size_min.setRange(0, 9999)
        self.size_min.setSuffix(" '")
        self.size_min.editingFinished.connect(self.apply_all_filters)
        layout.addWidget(self.size_min, row, 1)
        layout.addWidget(QLabel("to"), row, 2)
        self.size_max = QSpinBox()
        self.size_max.setRange(0, 9999)
        self.size_max.setValue(9999)
        self.size_max.setSuffix(" '")
        self.size_max.editingFinished.connect(self.apply_all_filters)
        layout.addWidget(self.size_max, row, 3)
        
        # Transit time
        layout.addWidget(QLabel("Transit Time:"), row, 4)
        self.transit_start = QTimeEdit()
        self.transit_start.setDisplayFormat("HH:mm")
        self.transit_start.setTime(QTime(0, 0))
        self.transit_start.editingFinished.connect(self.apply_all_filters)
        layout.addWidget(self.transit_start, row, 5)
        layout.addWidget(QLabel("to"), row, 6)
        self.transit_end = QTimeEdit()
        self.transit_end.setDisplayFormat("HH:mm")
        self.transit_end.setTime(QTime(23, 59))
        self.transit_end.editingFinished.connect(self.apply_all_filters)
        layout.addWidget(self.transit_end, row, 7)
        row += 1
        
        # Declination range (new filter)
        layout.addWidget(QLabel("Declination Range:"), row, 0)
        self.dec_min = QSpinBox()
        self.dec_min.setRange(-90, 90)
        self.dec_min.setValue(-90)
        self.dec_min.setSuffix("°")
        self.dec_min.editingFinished.connect(self.apply_all_filters)
        layout.addWidget(self.dec_min, row, 1)
        layout.addWidget(QLabel("to"), row, 2)
        self.dec_max = QSpinBox()
        self.dec_max.setRange(-90, 90)
        self.dec_max.setValue(90)
        self.dec_max.setSuffix("°")
        self.dec_max.editingFinished.connect(self.apply_all_filters)
        layout.addWidget(self.dec_max, row, 3)
        row += 1
        
        # Apply filters button
        apply_filters_btn = QPushButton("🔎 Apply Filters")
        apply_filters_btn.setFixedHeight(32)
        apply_filters_btn.setMinimumWidth(200)
        apply_filters_btn.clicked.connect(self.apply_all_filters)
        layout.addWidget(apply_filters_btn, row, 0, 1, 4)
        
        # Clear filters button
        clear_filters_btn = QPushButton("🔄 Clear All Filters")
        clear_filters_btn.setFixedHeight(32)
        clear_filters_btn.setMinimumWidth(150)
        clear_filters_btn.clicked.connect(self.clear_all_filters)
        layout.addWidget(clear_filters_btn, row, 4, 1, 4)
        
        parent_layout.addWidget(group)
        
    def apply_modern_stylesheet(self):
        """Apply modern dark theme stylesheet."""
        stylesheet = """
            QMainWindow {
                background-color: #1e1e1e;
            }
            
            QWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
                font-family: "Segoe UI", Arial, sans-serif;
                font-size: 10pt;
            }
            
            QGroupBox {
                border: 2px solid #3a3a3a;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 15px;
                font-weight: bold;
                color: #4A9EFF;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
            
            QGroupBox#controlGroup {
                background-color: #252525;
            }
            
            QGroupBox#infoGroup {
                background-color: #2a2a2a;
            }
            
            QFrame#headerFrame {
                background-color: #2d2d2d;
                border-radius: 8px;
                padding: 15px;
            }
            
            QPushButton {
                background-color: #3a3a3a;
                color: #e0e0e0;
                border: 1px solid #4a4a4a;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }
            
            QPushButton:hover {
                background-color: #4a4a4a;
                border: 1px solid #5a5a5a;
            }
            
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
            
            QPushButton:checked {
                background-color: #4A9EFF;
                color: #ffffff;
                border: 1px solid #6AB0FF;
            }
            
            QComboBox, QSpinBox, QDoubleSpinBox, QTimeEdit {
                background-color: #2a2a2a;
                color: #e0e0e0;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                padding: 6px;
                min-height: 25px;
            }
            
            QComboBox:hover, QSpinBox:hover, QDoubleSpinBox:hover, QTimeEdit:hover {
                border: 1px solid #4A9EFF;
            }
            
            QComboBox::drop-down {
                border: none;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #e0e0e0;
            }
            
            QLabel {
                background-color: transparent;
                color: #e0e0e0;
            }
            
            QStatusBar {
                background-color: #252525;
                color: #a0a0a0;
                border-top: 1px solid #3a3a3a;
            }
            
            QSplitter::handle {
                background-color: #3a3a3a;
            }
            
            QSplitter::handle:hover {
                background-color: #4A9EFF;
            }
            
            QScrollBar:vertical {
                background-color: #2a2a2a;
                width: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #4a4a4a;
                border-radius: 6px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #5a5a5a;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """
        self.setStyleSheet(stylesheet)
        
    def load_observatory_config(self):
        """Load observatory settings from config file."""
        try:
            config = configparser.ConfigParser()
            config_path = os.path.join('config', 'config.ini')
            
            if os.path.exists(config_path):
                config.read(config_path)
                if 'Observatory' in config:
                    self.observatory.update({
                        'latitude': config.getfloat('Observatory', 'latitude', fallback=40.0),
                        'longitude': config.getfloat('Observatory', 'longitude', fallback=-75.0),
                        'elevation': config.getfloat('Observatory', 'elevation', fallback=100.0),
                        'gmt_offset': config.getfloat('Observatory', 'gmt_offset', fallback=0.0),
                        'dst_active': config.getboolean('Observatory', 'dst_active', fallback=False),
                        'timezone': config.get('Observatory', 'timezone', fallback='UTC')
                    })
                    self.logger.info(f"Loaded observatory config: {self.observatory['latitude']}, {self.observatory['longitude']}, GMT offset: {self.observatory['gmt_offset']}, DST: {self.observatory['dst_active']}")
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            
    def save_observatory_config(self):
        """Save observatory settings to config file."""
        try:
            config = configparser.ConfigParser()
            config_path = os.path.join('config', 'config.ini')
            
            if os.path.exists(config_path):
                config.read(config_path)
                
            if 'Observatory' not in config:
                config['Observatory'] = {}
                
            config['Observatory'].update({
                'latitude': str(self.observatory['latitude']),
                'longitude': str(self.observatory['longitude']),
                'elevation': str(self.observatory['elevation']),
                'gmt_offset': str(self.observatory.get('gmt_offset', 0.0)),
                'dst_active': str(self.observatory.get('dst_active', False)),
                'timezone': str(self.observatory.get('timezone', 'UTC'))
            })
            
            with open(config_path, 'w') as f:
                config.write(f)
                
            self.logger.info("Saved observatory config")
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
    
    def load_persistent_settings(self):
        """Load persistent filter and location settings from database."""
        try:
            # Ensure settings table exists
            self.db_manager.create_settings_table()
            
            # Load size range
            size_min = self.db_manager.get_setting('size_min')
            if size_min is not None:
                self.size_min.setValue(int(size_min))
            
            size_max = self.db_manager.get_setting('size_max')
            if size_max is not None:
                self.size_max.setValue(int(size_max))
            
            # Load declination range
            dec_min = self.db_manager.get_setting('dec_min')
            if dec_min is not None:
                self.dec_min.setValue(int(dec_min))
            
            dec_max = self.db_manager.get_setting('dec_max')
            if dec_max is not None:
                self.dec_max.setValue(int(dec_max))
            
            # Load transit time
            transit_start = self.db_manager.get_setting('transit_start')
            if transit_start is not None:
                time_parts = transit_start.split(':')
                if len(time_parts) == 2:
                    self.transit_start.setTime(QTime(int(time_parts[0]), int(time_parts[1])))
            
            transit_end = self.db_manager.get_setting('transit_end')
            if transit_end is not None:
                time_parts = transit_end.split(':')
                if len(time_parts) == 2:
                    self.transit_end.setTime(QTime(int(time_parts[0]), int(time_parts[1])))
            
            # Load observatory address
            address = self.db_manager.get_setting('observatory_address')
            if address is not None:
                self.address_edit.setText(address)
            
            self.logger.info("Loaded persistent settings from database")
        except Exception as e:
            self.logger.error(f"Failed to load persistent settings: {e}", exc_info=True)
    
    def save_persistent_settings(self):
        """Save persistent filter and location settings to database."""
        try:
            # Save size range
            self.db_manager.save_setting('size_min', str(self.size_min.value()))
            self.db_manager.save_setting('size_max', str(self.size_max.value()))
            
            # Save declination range
            self.db_manager.save_setting('dec_min', str(self.dec_min.value()))
            self.db_manager.save_setting('dec_max', str(self.dec_max.value()))
            
            # Save transit time
            self.db_manager.save_setting('transit_start', self.transit_start.time().toString("HH:mm"))
            self.db_manager.save_setting('transit_end', self.transit_end.time().toString("HH:mm"))
            
            # Save observatory address
            self.db_manager.save_setting('observatory_address', self.address_edit.text())
            
            self.logger.info("Saved persistent settings to database")
        except Exception as e:
            self.logger.error(f"Failed to save persistent settings: {e}", exc_info=True)
            
    def check_database_and_navigate(self):
        """Check database and navigate to appropriate screen."""
        if self.db_manager.database_exists():
            self.logger.info("Database exists, navigating to target selection")
            self.show_target_selection_screen()
        else:
            self.logger.info("Database not found, showing init screen")
            QMessageBox.information(
                self,
                "Database Setup Required",
                "Please import the Excel database file first."
            )
            
    def show_target_selection_screen(self):
        """Show modern target selection screen."""
        if self.current_screen:
            # Clear existing screen
            layout = self.object_data_container.layout()
            if layout:
                while layout.count():
                    child = layout.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
            else:
                layout = QVBoxLayout(self.object_data_container)
                
        else:
            layout = QVBoxLayout(self.object_data_container)
            
        # Create target selection GUI
        try:
            target_gui = PySide6TargetSelectionGUI(
                self.object_data_container,
                self.db_manager,
                self.observatory
            )
            layout.addWidget(target_gui)
            self.current_screen = target_gui
            self.status_bar.showMessage("Target Selection - Use filters to refine results")
        except Exception as e:
            self.logger.error(f"Failed to create target selection screen: {e}")
            error_label = QLabel(f"Error loading target selection: {str(e)}")
            layout.addWidget(error_label)
            
    @Slot()
    def update_astronomical_data(self):
        """Update sun and moon data displays."""
        try:
            from datetime import datetime, timedelta
            current_time = datetime.now()
            
            # Update sun position
            sun_alt, sun_az = self.astro_calc.calculate_sun_position(
                current_time, self.observatory['latitude'], self.observatory['longitude']
            )
            
            # Calculate sun times
            sun_times = self.astro_calc.calculate_sun_times(
                self.observatory['latitude'], self.observatory['longitude'], current_time.date()
            )
            
            # Get GMT offset
            gmt_offset_hours = self.observatory.get('gmt_offset', 0)
            gmt_offset = timedelta(hours=gmt_offset_hours)
            if self.observatory.get('dst_active', False):
                gmt_offset += timedelta(hours=1)
            
            # Convert to local time
            local_sunrise = sun_times['sunrise'] + gmt_offset
            local_sunset = sun_times['sunset'] + gmt_offset
            local_dawn = sun_times['nautical_dawn'] + gmt_offset
            local_dusk = sun_times['nautical_dusk'] + gmt_offset
            
            # Determine sun status
            if sun_alt > 0:
                sun_status = "Above horizon"
            elif sun_alt > -6:
                sun_status = "Civil twilight"
            elif sun_alt > -12:
                sun_status = "Nautical twilight"
            elif sun_alt > -18:
                sun_status = "Astronomical twilight"
            else:
                sun_status = "Night"
            
            # Update sun label - compact format
            # Nautical dark time: from dusk (evening) to dawn (next morning)
            sun_text = f"""<b>☀️ Sun:</b> {sun_alt:.1f}° alt | {sun_az:.1f}° az<br>
↑ {local_sunrise.strftime('%H:%M')} | ↓ {local_sunset.strftime('%H:%M')} | Nautical: {local_dusk.strftime('%H:%M')}-{local_dawn.strftime('%H:%M')}"""
            self.sun_info_label.setText(sun_text)
            
            # Update moon position
            moon_alt, moon_az = self.astro_calc.calculate_moon_position(
                current_time, self.observatory['latitude'], self.observatory['longitude']
            )
            moon_phase_data = self.astro_calc.calculate_moon_phase(current_time)
            
            # Calculate moon times
            moon_times = self.astro_calc.calculate_moon_times(
                self.observatory['latitude'], self.observatory['longitude'], current_time.date()
            )
            
            local_moonrise = moon_times['moonrise'] + gmt_offset
            local_moonset = moon_times.get('moonset', moon_times['moonrise'] + timedelta(hours=12)) + gmt_offset
            
            # Update moon label - compact format
            moon_text = f"""<b>🌙 Moon:</b> {moon_alt:.1f}° alt | {moon_az:.1f}° az<br>
{moon_phase_data['phase_name']} ({moon_phase_data['illumination']:.0f}%) | ↑ {local_moonrise.strftime('%H:%M')} | ↓ {local_moonset.strftime('%H:%M')}"""
            self.moon_info_label.setText(moon_text)
            
            # Update moon phase widget
            self.moon_phase_widget.set_phase_data(moon_phase_data)
            
        except Exception as e:
            self.logger.error(f"Error updating astronomical data: {e}", exc_info=True)
            self.sun_info_label.setText("☀️ Sun: Error calculating data")
            self.moon_info_label.setText("🌙 Moon: Error calculating data")
    
    @Slot()
    def apply_location_settings(self):
        """Apply location and time settings."""
        self.observatory['latitude'] = self.lat_spin.value()
        self.observatory['longitude'] = self.lon_spin.value()
        self.save_observatory_config()
        
        self.status_bar.showMessage(
            f"Updated location: {self.observatory['latitude']:.4f}°, "
            f"{self.observatory['longitude']:.4f}°"
        )
        
        # Update astronomical data with new location
        self.update_astronomical_data()
        
        # Refresh calculations if target screen exists
        if self.current_screen:
            try:
                self.current_screen.update_astronomical_calculations()
            except AttributeError:
                pass
    
    @Slot()
    def geocode_address(self):
        """Geocode address to coordinates using OpenStreetMap Nominatim API."""
        import requests
        
        address = self.address_edit.text().strip()
        if not address:
            QMessageBox.warning(self, "No Address", "Please enter an address to geocode.")
            return
        
        try:
            # Use Nominatim API with proper user agent
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': address,
                'format': 'json',
                'limit': 1
            }
            headers = {
                'User-Agent': 'NextAstroTarget/1.0'
            }
            
            self.status_bar.showMessage("Geocoding address...")
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            results = response.json()
            
            if not results:
                QMessageBox.warning(
                    self, 
                    "Address Not Found", 
                    f"Could not find coordinates for: {address}\n\n"
                    "Try:\n"
                    "- Adding more details (city, country)\n"
                    "- Using different address format\n"
                    "- Checking spelling"
                )
                self.status_bar.showMessage("Geocoding failed - address not found", 5000)
                return
            
            # Get first result
            result = results[0]
            lat = float(result['lat'])
            lon = float(result['lon'])
            display_name = result.get('display_name', address)
            
            # Update spinboxes
            self.lat_spin.setValue(lat)
            self.lon_spin.setValue(lon)
            
            # Show success message
            QMessageBox.information(
                self,
                "Geocoding Successful",
                f"Location: {display_name}\n\n"
                f"Latitude: {lat:.4f}°\n"
                f"Longitude: {lon:.4f}°\n\n"
                "Click 'Apply Settings' to save these coordinates."
            )
            
            self.status_bar.showMessage(f"Geocoded: {display_name}", 5000)
            self.logger.info(f"Geocoded '{address}' to ({lat:.4f}, {lon:.4f})")
            
        except requests.exceptions.Timeout:
            QMessageBox.critical(
                self, 
                "Geocoding Timeout", 
                "The geocoding service took too long to respond.\n"
                "Please check your internet connection and try again."
            )
            self.status_bar.showMessage("Geocoding timed out", 5000)
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(
                self,
                "Geocoding Error",
                f"Failed to connect to geocoding service:\n{str(e)}\n\n"
                "Please check your internet connection."
            )
            self.status_bar.showMessage("Geocoding failed - network error", 5000)
            self.logger.error(f"Geocoding error: {e}")
        except Exception as e:
            QMessageBox.critical(
                self,
                "Geocoding Error",
                f"An unexpected error occurred:\n{str(e)}"
            )
            self.status_bar.showMessage("Geocoding failed", 5000)
            self.logger.error(f"Unexpected geocoding error: {e}", exc_info=True)
                
    @Slot(str)
    def filter_by_rating(self, rating):
        """Filter targets by rating."""
        # Update button states
        for btn_rating, btn in self.rating_buttons.items():
            btn.setChecked(btn_rating == rating)
            
        self.active_filters['rating'] = rating if rating != "All" else None
        self.apply_all_filters()
        
    @Slot(str)
    def filter_by_type(self, obj_type):
        """Filter targets by type."""
        # Update button states
        for btn_type, btn in self.type_buttons.items():
            btn.setChecked(btn_type == obj_type)
            
        self.active_filters['type'] = obj_type if obj_type != "All" else None
        self.apply_all_filters()
        
    @Slot()
    def apply_all_filters(self):
        """Apply all active filters to target list."""
        if self.current_screen and hasattr(self.current_screen, 'apply_filters'):
            filters = {
                'rating': self.active_filters['rating'],
                'type': self.active_filters['type'],
                'size_min': self.size_min.value(),
                'size_max': self.size_max.value(),
                'transit_start': self.transit_start.time().toString("HH:mm"),
                'transit_end': self.transit_end.time().toString("HH:mm"),
                'dec_min': self.dec_min.value(),
                'dec_max': self.dec_max.value()
            }
            self.current_screen.apply_filters(filters)
            
    @Slot()
    def clear_all_filters(self):
        """Clear Rating and Type filters only. Size Range, Declination Range, and Transit Time remain intact."""
        # Reset Rating filter - uncheck all buttons first
        for btn in self.rating_buttons.values():
            btn.setChecked(False)
        self.rating_buttons["All"].setChecked(True)
        
        # Reset Type filter
        for btn in self.type_buttons.values():
            btn.setChecked(False)
        self.type_buttons["All"].setChecked(True)
        
        # DO NOT reset Size Range, Declination Range, or Transit Time
        # These filters remain as configured by the user
        
        # Clear only rating and type in active filters
        self.active_filters['rating'] = None
        self.active_filters['type'] = None
        
        # Apply cleared filters
        self.apply_all_filters()
        
    def closeEvent(self, event):
        """Handle window close event."""
        self.logger.info("Application closing")
        self.save_observatory_config()
        self.save_persistent_settings()
        event.accept()

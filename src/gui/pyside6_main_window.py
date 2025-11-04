"""
Modern PySide6 main window for NextAstroTarget application.
Features professional UI with dark theme, improved layouts, and better UX.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QFrame, QSplitter, QGroupBox, QComboBox,
    QSpinBox, QDoubleSpinBox, QTimeEdit, QDateEdit, QScrollArea, QStatusBar,
    QMessageBox, QDockWidget, QLineEdit
)
from PySide6.QtCore import Qt, QTime, QDate, QTimer, Signal, Slot
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
        
        # Initialize observation datetime to current time
        self.observation_datetime = datetime.now()
        
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
        """Create compact header section with icon, app name, and action buttons."""
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(10, 4, 10, 4)  # Reduced vertical padding from 8 to 4
        header_layout.setSpacing(15)
        
        # App icon
        icon_label = QLabel()
        icon_path = Path(__file__).parent.parent.parent / "assets" / "icon_64.png"
        if icon_path.exists():
            icon_pixmap = QPixmap(str(icon_path))
            # Use 48x48 for a balanced, compact header
            scaled_icon = icon_pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(scaled_icon)
        else:
            self.logger.warning(f"App icon not found at {icon_path}")
        header_layout.addWidget(icon_label)
        
        # App name - large and prominent, taking most of the available space
        title_label = QLabel("Next Astro Target")
        title_label.setObjectName("appTitle")
        title_font = QFont("Segoe UI", 38, QFont.Bold)  # 38pt (20% smaller than 48pt)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #4A9EFF; padding: 0px 20px; font-size: 38pt; font-weight: bold;")
        header_layout.addWidget(title_label, stretch=1)  # stretch=1 makes it take available space
        
        # Quick action buttons
        self.refresh_btn = QPushButton("🔄 Refresh Data")
        self.settings_btn = QPushButton("⚙️ Settings")
        self.help_btn = QPushButton("❓ Help")
        
        for btn in [self.refresh_btn, self.settings_btn, self.help_btn]:
            btn.setFixedHeight(30)
            btn.setMinimumWidth(110)
            header_layout.addWidget(btn)
        
        # Connect help button
        self.help_btn.clicked.connect(self.show_help_dialog)
        
        parent_layout.addWidget(header_frame)
        
    def setup_timing_location(self, parent_layout):
        """Create timing and location controls."""
        group = QGroupBox("📍 Observatory & Time Settings")
        group.setObjectName("controlGroup")
        # Larger font for section title
        group_font = QFont("Segoe UI", 13, QFont.Bold)  # Increased from 11pt to 13pt
        group.setFont(group_font)
        # No width constraint - expand to fill available space
        layout = QGridLayout(group)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)
        # Use 4 columns for better balance: Label, Input, Label, Input
        layout.setColumnMinimumWidth(0, 70)   # Label column
        layout.setColumnMinimumWidth(1, 180)  # Input column
        layout.setColumnMinimumWidth(2, 70)   # Label column
        layout.setColumnMinimumWidth(3, 180)  # Input column
        
        # Row 0: Location and Latitude
        loc_label = QLabel("Location:")
        loc_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(loc_label, 0, 0)
        self.location_combo = QComboBox()
        self.location_combo.addItems(["Custom Location", "Load from GPS"])
        layout.addWidget(self.location_combo, 0, 1)
        
        lat_label = QLabel("Latitude:")
        lat_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(lat_label, 0, 2)
        self.lat_spin = QDoubleSpinBox()
        self.lat_spin.setRange(-90, 90)
        self.lat_spin.setValue(self.observatory['latitude'])
        self.lat_spin.setSuffix("°")
        self.lat_spin.setDecimals(4)
        layout.addWidget(self.lat_spin, 0, 3)
        
        # Row 1: Address and Longitude
        addr_label = QLabel("Address:")
        addr_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(addr_label, 1, 0)
        self.address_edit = QLineEdit()
        self.address_edit.setPlaceholderText("Enter address (e.g., Gdansk, Poland)")
        layout.addWidget(self.address_edit, 1, 1)
        
        lon_label = QLabel("Longitude:")
        lon_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(lon_label, 1, 2)
        self.lon_spin = QDoubleSpinBox()
        self.lon_spin.setRange(-180, 180)
        self.lon_spin.setValue(self.observatory['longitude'])
        self.lon_spin.setSuffix("°")
        self.lon_spin.setDecimals(4)
        layout.addWidget(self.lon_spin, 1, 3)
        
        # Row 2: Date and Geocode button
        date_label = QLabel("Date:")
        date_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(date_label, 2, 0)
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setCalendarPopup(True)
        layout.addWidget(self.date_edit, 2, 1)
        
        # Geocode button in the right side
        geocode_btn = QPushButton("🔍 Geocode Address")
        geocode_btn.setFixedHeight(32)
        geocode_btn.clicked.connect(self.geocode_address)
        geocode_btn.setToolTip("Convert address to coordinates using OpenStreetMap")
        layout.addWidget(geocode_btn, 2, 2, 1, 2)  # Span 2 columns
        
        # Row 3: Time and control buttons
        time_label = QLabel("Time:")
        time_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(time_label, 3, 0)
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime.currentTime())
        self.time_edit.setDisplayFormat("HH:mm")
        layout.addWidget(self.time_edit, 3, 1)
        
        # Time control buttons in a horizontal layout
        time_btn_layout = QHBoxLayout()
        time_btn_layout.setSpacing(8)
        
        now_btn = QPushButton("⏰ Now")
        now_btn.setFixedHeight(32)
        now_btn.clicked.connect(self.set_time_to_now)
        now_btn.setToolTip("Set date and time to current moment")
        time_btn_layout.addWidget(now_btn)
        
        sunset_btn = QPushButton("🌇 Sunset")
        sunset_btn.setFixedHeight(32)
        sunset_btn.clicked.connect(self.set_time_to_sunset)
        sunset_btn.setToolTip("Set time to sunset on selected date")
        time_btn_layout.addWidget(sunset_btn)
        
        layout.addLayout(time_btn_layout, 3, 2, 1, 2)  # Span 2 columns
        
        # Row 4: Apply button (right-aligned)
        apply_btn = QPushButton("Apply Settings")
        apply_btn.setFixedHeight(32)
        apply_btn.setMinimumWidth(140)
        apply_btn.clicked.connect(self.apply_location_settings)
        layout.addWidget(apply_btn, 4, 3, Qt.AlignRight)

        parent_layout.addWidget(group)
        
    def setup_sun_moon_info(self, parent_splitter):
        """Create sun and moon information display."""
        group = QGroupBox("☀️ Sun & 🌙 Moon")
        group.setObjectName("infoGroup")
        # Larger font for section title
        group_font = QFont("Segoe UI", 13, QFont.Bold)  # Increased from 11pt to 13pt
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
        group_font = QFont("Segoe UI", 13, QFont.Bold)  # Increased from 11pt to 13pt
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
        group_font = QFont("Segoe UI", 13, QFont.Bold)  # Increased from 11pt to 13pt
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
        group_font = QFont("Segoe UI", 13, QFont.Bold)  # Increased from 11pt to 13pt
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
        group_font = QFont("Segoe UI", 13, QFont.Bold)  # Increased from 11pt to 13pt
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
                border: 2px solid #5a5a5a;
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
            # Use observation datetime instead of current time
            current_time = self.observation_datetime
            
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
        
        # Get date and time from pickers
        selected_date = self.date_edit.date()
        selected_time = self.time_edit.time()
        
        # Store observation datetime
        self.observation_datetime = datetime(
            selected_date.year(),
            selected_date.month(),
            selected_date.day(),
            selected_time.hour(),
            selected_time.minute()
        )
        
        self.save_observatory_config()
        
        self.status_bar.showMessage(
            f"Updated location: {self.observatory['latitude']:.4f}°, "
            f"{self.observatory['longitude']:.4f}° | "
            f"Time: {self.observation_datetime.strftime('%Y-%m-%d %H:%M')}"
        )
        
        # Update astronomical data with new location and time
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
    
    @Slot()
    def set_time_to_now(self):
        """Set date and time to current moment."""
        self.date_edit.setDate(QDate.currentDate())
        self.time_edit.setTime(QTime.currentTime())
        self.status_bar.showMessage("Date and time set to now", 3000)
        self.logger.info("Observation time set to current date/time")
    
    @Slot()
    def set_time_to_sunset(self):
        """Set time to sunset on the selected date."""
        # Get the selected date
        selected_date = self.date_edit.date()
        year = selected_date.year()
        month = selected_date.month()
        day = selected_date.day()
        
        # Create date object for the selected date
        from datetime import date, timedelta
        target_date = date(year, month, day)
        
        # Calculate sunset for this date
        calculator = AstronomicalCalculator()
        sun_data = calculator.calculate_sun_times(
            self.observatory['latitude'],
            self.observatory['longitude'],
            target_date
        )
        
        if 'sunset' in sun_data and sun_data['sunset']:
            sunset_time = sun_data['sunset']
            
            # Apply GMT offset and DST
            gmt_offset_hours = self.observatory.get('gmt_offset', 0)
            gmt_offset = timedelta(hours=gmt_offset_hours)
            if self.observatory.get('dst_active', False):
                gmt_offset += timedelta(hours=1)
            
            # Adjust sunset time to local time
            local_sunset = sunset_time + gmt_offset
            
            # Set the time edit to local sunset time
            self.time_edit.setTime(QTime(local_sunset.hour, local_sunset.minute))
            
            sunset_str = local_sunset.strftime("%H:%M")
            self.status_bar.showMessage(f"Time set to sunset: {sunset_str}", 3000)
            self.logger.info(f"Observation time set to sunset: {sunset_str} on {selected_date.toString('yyyy-MM-dd')}")
        else:
            QMessageBox.warning(
                self,
                "Sunset Not Available",
                f"Could not calculate sunset for the selected date.\n"
                f"This may occur in polar regions during certain seasons."
            )
            self.status_bar.showMessage("Sunset calculation failed", 3000)
                
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
    
    @Slot()
    def show_help_dialog(self):
        """Show comprehensive help dialog with attractive formatting."""
        from PySide6.QtWidgets import QDialog, QTextBrowser, QVBoxLayout, QDialogButtonBox
        from PySide6.QtCore import QSize
        
        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("NextAstroTarget - User Guide")
        dialog.setMinimumSize(QSize(900, 700))
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create text browser for scrollable rich text content
        browser = QTextBrowser(dialog)
        browser.setOpenExternalLinks(False)
        
        # Set attractive HTML content with comprehensive help
        help_html = """
        <html>
        <head>
            <style>
                body {
                    font-family: 'Segoe UI', Arial, sans-serif;
                    background-color: #1e1e1e;
                    color: #e0e0e0;
                    margin: 20px;
                    line-height: 1.6;
                }
                h1 {
                    color: #4A9EFF;
                    border-bottom: 3px solid #4A9EFF;
                    padding-bottom: 10px;
                    margin-top: 0;
                    font-size: 28px;
                }
                h2 {
                    color: #FF9A3D;
                    margin-top: 25px;
                    margin-bottom: 15px;
                    font-size: 20px;
                    border-left: 4px solid #FF9A3D;
                    padding-left: 10px;
                }
                h3 {
                    color: #66D9EF;
                    margin-top: 15px;
                    margin-bottom: 10px;
                    font-size: 16px;
                }
                p {
                    margin: 10px 0;
                }
                ul {
                    margin: 10px 0;
                    padding-left: 25px;
                }
                li {
                    margin: 5px 0;
                }
                .section {
                    background-color: #252525;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 15px 0;
                    border-left: 4px solid #4A9EFF;
                }
                .tip {
                    background-color: #2a3a2a;
                    padding: 12px;
                    border-radius: 6px;
                    margin: 10px 0;
                    border-left: 4px solid #66D966;
                }
                .warning {
                    background-color: #3a2a2a;
                    padding: 12px;
                    border-radius: 6px;
                    margin: 10px 0;
                    border-left: 4px solid #FF6666;
                }
                .code {
                    background-color: #2d2d2d;
                    padding: 3px 8px;
                    border-radius: 3px;
                    font-family: 'Consolas', monospace;
                    color: #A6E22E;
                }
                table {
                    border-collapse: collapse;
                    width: 100%;
                    margin: 15px 0;
                }
                th {
                    background-color: #2d2d2d;
                    color: #4A9EFF;
                    padding: 10px;
                    text-align: left;
                    border-bottom: 2px solid #4A9EFF;
                }
                td {
                    padding: 8px;
                    border-bottom: 1px solid #3a3a3a;
                }
                tr:hover {
                    background-color: #2a2a2a;
                }
                .emoji {
                    font-size: 20px;
                }
            </style>
        </head>
        <body>
            <h1>🔭 NextAstroTarget User Guide</h1>
            <p>Welcome to NextAstroTarget - your comprehensive tool for planning deep sky imaging sessions!</p>
            
            <div class="section">
                <h2><span class="emoji">📍</span> Observatory & Time Settings</h2>
                <p>Configure your observing location and time to get accurate astronomical data:</p>
                
                <h3>Location Settings</h3>
                <ul>
                    <li><strong>Location:</strong> Select a predefined location or enter custom coordinates</li>
                    <li><strong>Latitude/Longitude:</strong> Enter your precise location (North/East are positive)</li>
                    <li><strong>Address:</strong> Enter an address and click "Geocode Address" to auto-fill coordinates</li>
                    <li><strong>GMT Offset:</strong> Hours offset from UTC (negative for west of Greenwich)</li>
                </ul>
                
                <h3>Date & Time Controls</h3>
                <ul>
                    <li><strong>Date Picker:</strong> Select the observation date</li>
                    <li><strong>Time Picker:</strong> Set the observation time (24-hour format)</li>
                    <li><strong>"Now" Button:</strong> Instantly set to current date and time</li>
                    <li><strong>"Sunset" Button:</strong> Set time to local sunset (accounts for DST)</li>
                </ul>
                
                <div class="tip">
                    <strong>💡 Tip:</strong> Use the "Sunset" button to quickly plan evening sessions!
                </div>
            </div>
            
            <div class="section">
                <h2><span class="emoji">🌙</span> Astronomical Data Display</h2>
                
                <h3>Sun Data</h3>
                <p>View sunrise, sunset, and twilight times for your location and selected date.</p>
                
                <h3>Moon Data</h3>
                <p>See current moon phase, illumination percentage, and a realistic moon phase visualization. 
                The moon phase image accurately represents the current lunar appearance.</p>
                
                <h3>Weather Forecast</h3>
                <p>Astronomical seeing conditions forecast powered by ClearOutside.com showing:</p>
                <ul>
                    <li>Cloud cover predictions</li>
                    <li>Transparency (atmospheric clarity)</li>
                    <li>Seeing quality</li>
                    <li>Wind and temperature</li>
                </ul>
            </div>
            
            <div class="section">
                <h2><span class="emoji">🎯</span> Target Selection & Filtering</h2>
                
                <h3>Filter by Rating</h3>
                <table>
                    <tr><th>Rating</th><th>Description</th></tr>
                    <tr><td>⭐⭐⭐⭐⭐ (5)</td><td>Showcase Objects - Top 2% (Best imaging targets)</td></tr>
                    <tr><td>⭐⭐⭐⭐ (4+)</td><td>Excellent - Top 10%</td></tr>
                    <tr><td>⭐⭐⭐ (3+)</td><td>Good - Top 25%</td></tr>
                    <tr><td>⭐⭐ (2+)</td><td>Average - Majority of objects</td></tr>
                    <tr><td>⭐ (1+)</td><td>All rated objects</td></tr>
                </table>
                
                <h3>Filter by Object Type</h3>
                <ul>
                    <li><strong>Galaxies:</strong> Distant galactic systems</li>
                    <li><strong>Nebulae:</strong> Gas and dust clouds (emission, reflection, planetary, SNR)</li>
                    <li><strong>Clusters:</strong> Star clusters (open and globular)</li>
                    <li><strong>All:</strong> Show all object types</li>
                </ul>
                
                <h3>Size Range Filter</h3>
                <p>Filter objects by apparent size in arc-minutes (useful for matching your telescope's field of view).</p>
                <ul>
                    <li><strong>Min Size:</strong> Minimum apparent size in arcminutes</li>
                    <li><strong>Max Size:</strong> Maximum apparent size in arcminutes</li>
                </ul>
                <div class="tip">
                    <strong>💡 Reference:</strong> Full Moon = 31 arcmin, Jupiter ≈ 0.6 arcmin
                </div>
                
                <h3>Declination Range</h3>
                <p>Limit objects to those within your observable declination range:</p>
                <ul>
                    <li><strong>Min Dec:</strong> Southern limit (based on your latitude and horizon obstructions)</li>
                    <li><strong>Max Dec:</strong> Northern limit (typically +90° for northern observers)</li>
                </ul>
                
                <h3>Transit Time Window</h3>
                <p>Filter objects that transit (reach maximum altitude) within a specific time window during the night.</p>
                <ul>
                    <li><strong>Start Time:</strong> Beginning of imaging window</li>
                    <li><strong>End Time:</strong> End of imaging window</li>
                </ul>
            </div>
            
            <div class="section">
                <h2><span class="emoji">📊</span> Object Information</h2>
                
                <h3>Object Card Details</h3>
                <p>Double-click any object to view comprehensive information:</p>
                <ul>
                    <li><strong>Basic Info:</strong> Name, type, subtype, constellation, nickname</li>
                    <li><strong>Coordinates:</strong> Right Ascension (RA) and Declination (Dec)</li>
                    <li><strong>Physical Data:</strong>
                        <ul>
                            <li>Distance: Galaxies in Mly (millions of light years), others in ly</li>
                            <li>Physical Size: Galaxies in kly (thousands of light years), others in ly</li>
                            <li>Apparent Size: Angular size in arcminutes</li>
                        </ul>
                    </li>
                    <li><strong>Observing Info:</strong> Magnitude, transit altitude, best viewing months</li>
                    <li><strong>Sky Survey Image:</strong> Real astronomical image from SDSS or DSS</li>
                    <li><strong>Notes:</strong> Description and interesting facts about the object</li>
                </ul>
                
                <h3>Understanding Distance & Size</h3>
                <table>
                    <tr><th>Object Type</th><th>Distance Units</th><th>Size Units</th></tr>
                    <tr><td>Galaxies</td><td>Mly (millions of ly)</td><td>kly (thousands of ly)</td></tr>
                    <tr><td>Nebulae & Clusters</td><td>ly (light years)</td><td>ly (light years)</td></tr>
                </table>
                <p><span class="code">u</span> indicates unknown distance/size</p>
            </div>
            
            <div class="section">
                <h2><span class="emoji">⚙️</span> Tips & Best Practices</h2>
                
                <div class="tip">
                    <h3>Planning Your Session</h3>
                    <ul>
                        <li>Set your location accurately for correct rise/set times</li>
                        <li>Use the transit time filter to find objects at their highest altitude</li>
                        <li>Check moon phase and plan narrowband imaging during bright moon</li>
                        <li>Filter by rating to focus on the best targets first</li>
                    </ul>
                </div>
                
                <div class="tip">
                    <h3>Declination Guidelines</h3>
                    <ul>
                        <li>Objects near zenith (directly overhead) have least atmospheric distortion</li>
                        <li>Objects below 30° altitude show significant atmospheric effects</li>
                        <li>Adjust Dec Min based on your southern horizon obstructions</li>
                    </ul>
                </div>
                
                <div class="warning">
                    <h3>⚠️ Important Notes</h3>
                    <ul>
                        <li>DST setting affects sunset and twilight time calculations</li>
                        <li>Transit times assume meridian crossing at midnight (1 AM during DST)</li>
                        <li>Weather data requires internet connection</li>
                    </ul>
                </div>
            </div>
            
            <div class="section">
                <h2><span class="emoji">🔄</span> Button Actions</h2>
                <ul>
                    <li><strong>Apply Settings:</strong> Save location changes and recalculate astronomical data</li>
                    <li><strong>Apply Filters:</strong> Refresh target list with current filter settings</li>
                    <li><strong>Clear Filters:</strong> Reset rating and type filters (size/dec/transit remain)</li>
                    <li><strong>Geocode Address:</strong> Convert address to coordinates automatically</li>
                    <li><strong>Refresh Data:</strong> Reload weather and astronomical information</li>
                </ul>
            </div>
            
            <p style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 2px solid #3a3a3a;">
                <strong>Happy Observing! 🌟</strong><br>
                <span style="color: #808080; font-size: 12px;">
                    Based on the Immersive Deep Sky Compendium database
                </span>
            </p>
        </body>
        </html>
        """
        
        browser.setHtml(help_html)
        layout.addWidget(browser)
        
        # Add close button
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(dialog.close)
        layout.addWidget(button_box)
        
        # Show dialog
        dialog.exec()
        
    def closeEvent(self, event):
        """Handle window close event."""
        self.logger.info("Application closing")
        self.save_observatory_config()
        self.save_persistent_settings()
        event.accept()

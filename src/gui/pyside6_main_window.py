"""
Modern PySide6 main window for NextAstroTarget application.
Features professional UI with dark theme, improved layouts, and better UX.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QFrame, QSplitter, QGroupBox, QComboBox,
    QSpinBox, QDoubleSpinBox, QTimeEdit, QScrollArea, QStatusBar,
    QMessageBox, QDockWidget
)
from PySide6.QtCore import Qt, QTime, QTimer, Signal, Slot
from PySide6.QtGui import QFont, QPalette, QColor, QIcon, QPainter, QBrush, QPen
from datetime import datetime, timedelta
import logging
from typing import Optional, Dict, Any
import configparser
import os

from src.database.database_manager import DatabaseManager
from src.gui.pyside6_target_selection import PySide6TargetSelectionGUI
from src.gui.pyside6_weather_widget import PySide6WeatherWidget
from src.utils.astronomical_calculations import AstronomicalCalculator
from src.utils.location_service import LocationService


class MoonPhaseWidget(QWidget):
    """Custom widget to display moon phase graphic."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(90, 120)
        self.setMaximumSize(90, 120)
        self.phase_data = None
        
    def set_phase_data(self, phase_data: Dict[str, Any]):
        """Update moon phase data and trigger repaint."""
        self.phase_data = phase_data
        self.update()
        
    def paintEvent(self, event):
        """Draw moon phase graphic."""
        if not self.phase_data:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Canvas dimensions
        margin = 5
        size = 70
        center_x = 45
        center_y = 45
        
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
            # Partial phases
            if cycle_position <= 0.5:
                # Waxing phases
                if cycle_position <= 0.25:  # New to First Quarter
                    shadow_coverage = 1.0 - (cycle_position / 0.25)
                    shadow_width = size * shadow_coverage
                    if shadow_width > 0:
                        painter.drawEllipse(margin, margin, int(shadow_width), size)
                else:  # First Quarter to Full
                    progress = (cycle_position - 0.25) / 0.25
                    shadow_offset = (size / 2) * (1.0 - progress)
                    if shadow_offset > 2:
                        painter.drawEllipse(
                            int(margin - shadow_offset), margin,
                            int(shadow_offset * 2), size
                        )
            else:
                # Waning phases
                if cycle_position <= 0.75:  # Full to Last Quarter
                    progress = (cycle_position - 0.5) / 0.25
                    shadow_offset = (size / 2) * progress
                    if shadow_offset > 2:
                        painter.drawEllipse(
                            int(margin + size - shadow_offset), margin,
                            int(shadow_offset * 2), size
                        )
                else:  # Last Quarter to New
                    progress = (cycle_position - 0.75) / 0.25
                    shadow_start = size * (1.0 - progress)
                    painter.drawEllipse(
                        int(margin + shadow_start), margin,
                        int(size - shadow_start), size
                    )
        
        # Draw outer circle for definition
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor("gray"), 2))
        painter.drawEllipse(margin, margin, size, size)
        
        # Draw text
        painter.setPen(QColor("white"))
        font = QFont("Arial", 9, QFont.Bold)
        painter.setFont(font)
        painter.drawText(0, margin + size + 10, 90, 20, Qt.AlignCenter, f"{illumination:.0f}%")
        
        font.setPointSize(8)
        font.setBold(False)
        painter.setFont(font)
        painter.setPen(QColor("gray"))
        painter.drawText(0, margin + size + 25, 90, 20, Qt.AlignCenter, self.phase_data['phase_name'])


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
        
        # Update astronomical data
        self.update_astronomical_data()
        
        # Check database and navigate
        self.check_database_and_navigate()
        
        # Auto-refresh weather widget on startup
        QTimer.singleShot(1000, self.auto_refresh_weather)
        
    def auto_refresh_weather(self):
        """Auto-refresh weather widget after startup."""
        try:
            if hasattr(self, 'weather_widget'):
                self.weather_widget.refresh_forecast()
        except Exception as e:
            self.logger.error(f"Failed to auto-refresh weather: {e}")
    
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
        
        # Add sections
        self.setup_header(top_layout)
        self.setup_timing_location(top_layout)
        
        # Create horizontal splitter for weather and sun/moon
        info_splitter = QSplitter(Qt.Horizontal)
        
        self.setup_sun_moon_info(info_splitter)
        self.setup_weather_info(info_splitter)
        
        top_layout.addWidget(info_splitter)
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
        
        # App title with larger font
        title_label = QLabel("🌌 NextAstroTarget")
        title_font = QFont("Segoe UI", 24, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #4A9EFF;")
        header_layout.addWidget(title_label)
        
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
        
        # Date/Time
        layout.addWidget(QLabel("Observation Time:"), 1, 0)
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime.currentTime())
        self.time_edit.setDisplayFormat("HH:mm")
        layout.addWidget(self.time_edit, 1, 1)
        
        # Apply button
        apply_btn = QPushButton("Apply Settings")
        apply_btn.setFixedHeight(28)
        apply_btn.clicked.connect(self.apply_location_settings)
        layout.addWidget(apply_btn, 1, 5)
        
        parent_layout.addWidget(group)
        
    def setup_sun_moon_info(self, parent_splitter):
        """Create sun and moon information display."""
        group = QGroupBox("☀️ Sun & 🌙 Moon")
        group.setObjectName("infoGroup")
        # Larger font for section title
        group_font = QFont("Segoe UI", 11, QFont.Bold)
        group.setFont(group_font)
        layout = QVBoxLayout(group)
        layout.setSpacing(3)
        layout.setContentsMargins(8, 5, 8, 5)
        
        # Sun info - compact display
        self.sun_info_label = QLabel("Calculating sun data...")
        self.sun_info_label.setWordWrap(True)
        self.sun_info_label.setStyleSheet("font-size: 9pt;")
        layout.addWidget(self.sun_info_label)
        
        # Moon info with phase graphic
        moon_container = QHBoxLayout()
        moon_container.setSpacing(5)
        
        self.moon_info_label = QLabel("Calculating moon data...")
        self.moon_info_label.setWordWrap(True)
        self.moon_info_label.setStyleSheet("font-size: 9pt;")
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
            btn.setFixedHeight(28)
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
            btn.setFixedHeight(28)
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
        
        # Apply filters button
        apply_filters_btn = QPushButton("🔎 Apply Filters")
        apply_filters_btn.setFixedHeight(32)
        apply_filters_btn.setMinimumWidth(200)
        apply_filters_btn.clicked.connect(self.apply_all_filters)
        layout.addWidget(apply_filters_btn, row, 0, 1, 4)
        
        # Clear filters button
        clear_filters_btn = QPushButton("🔄 Clear All Filters")
        clear_filters_btn.setFixedHeight(32)
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
            sun_text = f"""<b>☀️ Sun:</b> {sun_alt:.1f}° alt | {sun_az:.1f}° az<br>
↑ {local_sunrise.strftime('%H:%M')} | ↓ {local_sunset.strftime('%H:%M')} | Nautical: {local_dawn.strftime('%H:%M')}-{local_dusk.strftime('%H:%M')}"""
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
                'transit_end': self.transit_end.time().toString("HH:mm")
            }
            self.current_screen.apply_filters(filters)
            
    @Slot()
    def clear_all_filters(self):
        """Clear all active filters."""
        # Reset UI
        self.rating_buttons["All"].setChecked(True)
        self.type_buttons["All"].setChecked(True)
        self.size_min.setValue(0)
        self.size_max.setValue(9999)
        self.transit_start.setTime(QTime(0, 0))
        self.transit_end.setTime(QTime(23, 59))
        
        # Clear active filters
        self.active_filters = {
            'declination': False,
            'size': False,
            'transit': False,
            'rating': None,
            'catalog': None,
            'type': None
        }
        
        # Apply cleared filters
        self.apply_all_filters()
        
    def closeEvent(self, event):
        """Handle window close event."""
        self.logger.info("Application closing")
        self.save_observatory_config()
        event.accept()

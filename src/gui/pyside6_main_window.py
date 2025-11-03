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
from PySide6.QtGui import QFont, QPalette, QColor, QIcon
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
        top_layout.setContentsMargins(10, 10, 10, 10)
        top_layout.setSpacing(10)
        
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
        
        # Set splitter proportions
        main_splitter.setSizes([400, 500])
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
    def setup_header(self, parent_layout):
        """Create modern header section."""
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QHBoxLayout(header_frame)
        
        # App title
        title_label = QLabel("🌌 NextAstroTarget")
        title_font = QFont("Segoe UI", 20, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #4A9EFF;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Quick action buttons
        self.refresh_btn = QPushButton("🔄 Refresh Data")
        self.settings_btn = QPushButton("⚙️ Settings")
        self.help_btn = QPushButton("❓ Help")
        
        for btn in [self.refresh_btn, self.settings_btn, self.help_btn]:
            btn.setFixedHeight(35)
            btn.setMinimumWidth(120)
            header_layout.addWidget(btn)
        
        parent_layout.addWidget(header_frame)
        
    def setup_timing_location(self, parent_layout):
        """Create timing and location controls."""
        group = QGroupBox("📍 Observatory & Time Settings")
        group.setObjectName("controlGroup")
        layout = QGridLayout(group)
        layout.setSpacing(10)
        
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
        apply_btn.setFixedHeight(35)
        apply_btn.clicked.connect(self.apply_location_settings)
        layout.addWidget(apply_btn, 1, 5)
        
        parent_layout.addWidget(group)
        
    def setup_sun_moon_info(self, parent_splitter):
        """Create sun and moon information display."""
        group = QGroupBox("☀️ Sun & 🌙 Moon")
        group.setObjectName("infoGroup")
        layout = QVBoxLayout(group)
        
        # Sun info
        self.sun_info_label = QLabel("Calculating sun data...")
        self.sun_info_label.setWordWrap(True)
        layout.addWidget(self.sun_info_label)
        
        # Moon info
        self.moon_info_label = QLabel("Calculating moon data...")
        self.moon_info_label.setWordWrap(True)
        layout.addWidget(self.moon_info_label)
        
        layout.addStretch()
        
        parent_splitter.addWidget(group)
        
    def setup_weather_info(self, parent_splitter):
        """Create weather forecast display."""
        group = QGroupBox("🌤️ Weather Forecast")
        group.setObjectName("infoGroup")
        layout = QVBoxLayout(group)
        
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
        layout = QGridLayout(group)
        layout.setSpacing(8)
        
        row = 0
        
        # Rating filter
        layout.addWidget(QLabel("Rating:"), row, 0)
        rating_layout = QHBoxLayout()
        self.rating_buttons = {}
        for rating in ["All", "3+", "4+", "5"]:
            btn = QPushButton(f"⭐ {rating}")
            btn.setCheckable(True)
            btn.setFixedHeight(35)
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
            btn.setFixedHeight(35)
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
        apply_filters_btn.setFixedHeight(40)
        apply_filters_btn.setMinimumWidth(200)
        apply_filters_btn.clicked.connect(self.apply_all_filters)
        layout.addWidget(apply_filters_btn, row, 0, 1, 4)
        
        # Clear filters button
        clear_filters_btn = QPushButton("🔄 Clear All Filters")
        clear_filters_btn.setFixedHeight(40)
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
                        'elevation': config.getfloat('Observatory', 'elevation', fallback=100.0)
                    })
                    self.logger.info(f"Loaded observatory config: {self.observatory['latitude']}, {self.observatory['longitude']}")
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
                'elevation': str(self.observatory['elevation'])
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
    def apply_location_settings(self):
        """Apply location and time settings."""
        self.observatory['latitude'] = self.lat_spin.value()
        self.observatory['longitude'] = self.lon_spin.value()
        self.save_observatory_config()
        
        self.status_bar.showMessage(
            f"Updated location: {self.observatory['latitude']:.4f}°, "
            f"{self.observatory['longitude']:.4f}°"
        )
        
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

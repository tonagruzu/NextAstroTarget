"""
Modern PySide6 weather forecast widget with ClearOutside integration.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton
from PySide6.QtCore import Qt, Signal, Slot, QTimer
from PySide6.QtGui import QFont, QPixmap
import logging
from datetime import datetime
from typing import Dict, Optional
import requests
from io import BytesIO
from PIL import Image
import webbrowser


class PySide6WeatherWidget(QWidget):
    """Modern weather forecast display widget with ClearOutside integration."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.latitude = 40.0
        self.longitude = -75.0
        self.forecast_image = None
        
        self.setup_ui()
        self.apply_stylesheet()
        
    def setup_ui(self):
        """Create weather widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header with controls
        header_layout = QHBoxLayout()
        header_icon = QLabel("🌤️")
        header_icon.setFont(QFont("Segoe UI Emoji", 16))
        header_label = QLabel("Weather Forecast")
        header_label.setStyleSheet("color: #4A9EFF; font-weight: bold; font-size: 14px;")
        header_layout.addWidget(header_icon)
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        
        # Refresh button
        self.refresh_button = QPushButton("↻")
        self.refresh_button.setFixedSize(30, 30)
        self.refresh_button.setToolTip("Refresh weather forecast")
        self.refresh_button.clicked.connect(self.refresh_forecast)
        header_layout.addWidget(self.refresh_button)
        
        # View on website button
        self.view_button = QPushButton("🔗")
        self.view_button.setFixedSize(30, 30)
        self.view_button.setToolTip("Open ClearOutside website")
        self.view_button.clicked.connect(self.open_clearoutside_website)
        header_layout.addWidget(self.view_button)
        
        layout.addLayout(header_layout)
        
        # Location label
        self.location_label = QLabel("Location: Not set")
        self.location_label.setStyleSheet("color: #b0b0b0; font-size: 9pt;")
        layout.addWidget(self.location_label)
        
        # Forecast image display
        self.forecast_image_label = QLabel("Click ↻ to load forecast")
        self.forecast_image_label.setAlignment(Qt.AlignCenter)
        self.forecast_image_label.setMinimumHeight(200)
        self.forecast_image_label.setWordWrap(True)
        self.forecast_image_label.setStyleSheet("""
            QLabel {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                padding: 10px;
                color: #b0b0b0;
            }
        """)
        layout.addWidget(self.forecast_image_label)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #808080; font-size: 8pt;")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
    def apply_stylesheet(self):
        """Apply modern styling."""
        stylesheet = """
            QWidget {
                background-color: #252525;
                border-radius: 6px;
            }
            
            QPushButton {
                background-color: #3a3a3a;
                color: #e0e0e0;
                border: 1px solid #4a4a4a;
                border-radius: 4px;
                font-size: 12pt;
            }
            
            QPushButton:hover {
                background-color: #4a4a4a;
                border: 1px solid #4A9EFF;
            }
            
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
        """
        self.setStyleSheet(stylesheet)
        
    def update_location(self, latitude: float, longitude: float):
        """Update weather location."""
        self.latitude = latitude
        self.longitude = longitude
        self.location_label.setText(f"Location: {latitude:.2f}°N, {longitude:.2f}°E")
        self.logger.info(f"Weather location updated: {latitude}, {longitude}")
        
    @Slot()
    def refresh_forecast(self):
        """Refresh the weather forecast from ClearOutside."""
        self.logger.info("Refreshing astronomical weather forecast")
        
        try:
            # Update status
            self.status_label.setText("Loading forecast image...")
            self.status_label.setStyleSheet("color: #4A9EFF; font-size: 8pt;")
            self.refresh_button.setEnabled(False)
            
            # Get forecast image URL
            lat_rounded = round(self.latitude, 2)
            lon_rounded = round(self.longitude, 2)
            image_url = f"https://clearoutside.com/forecast_image_medium/{lat_rounded}/{lon_rounded}/forecast.png"
            
            self.logger.info(f"Fetching weather from: {image_url}")
            
            # Download forecast image
            headers = {
                'User-Agent': 'NextAstroTarget/2.0.0 (Astronomy Application; PySide6)'
            }
            
            response = requests.get(image_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Verify we got image content
            if response.headers.get('content-type', '').startswith('text/html'):
                raise Exception("ClearOutside returned webpage instead of image")
            
            if not response.content.startswith(b'\x89PNG') and not response.content.startswith(b'\xff\xd8'):
                raise Exception("Invalid image format received")
            
            # Load and display image
            image_data = BytesIO(response.content)
            pil_image = Image.open(image_data)
            
            # Scale image for better visibility
            original_width, original_height = pil_image.size
            self.logger.info(f"Original image size: {original_width}x{original_height}")
            
            # Target size for widget
            target_width = 400
            scale_factor = target_width / original_width
            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)
            
            # Resize with high quality
            pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.logger.info(f"Scaled image to: {new_width}x{new_height}")
            
            # Convert to QPixmap
            pil_image_bytes = BytesIO()
            pil_image.save(pil_image_bytes, format='PNG')
            pil_image_bytes.seek(0)
            
            pixmap = QPixmap()
            pixmap.loadFromData(pil_image_bytes.read())
            
            # Display image
            self.forecast_image_label.setPixmap(pixmap)
            self.forecast_image_label.setScaledContents(False)
            
            # Update status
            self.status_label.setText("✓ Forecast updated - Data from ClearOutside.com")
            self.status_label.setStyleSheet("color: #4CAF50; font-size: 8pt;")
            
            self.logger.info("Weather forecast loaded successfully")
            
        except requests.RequestException as e:
            error_msg = f"Network error loading forecast: {str(e)}"
            self.logger.error(error_msg)
            self.status_label.setText(f"❌ {error_msg}")
            self.status_label.setStyleSheet("color: #f44336; font-size: 8pt;")
            self.forecast_image_label.setText("Failed to load forecast\nCheck internet connection")
            
        except Exception as e:
            error_msg = f"Error loading forecast: {str(e)}"
            self.logger.error(error_msg)
            self.status_label.setText(f"❌ {error_msg}")
            self.status_label.setStyleSheet("color: #f44336; font-size: 8pt;")
            self.forecast_image_label.setText("Failed to load forecast image")
            
        finally:
            self.refresh_button.setEnabled(True)
            
    @Slot()
    def open_clearoutside_website(self):
        """Open ClearOutside website in browser."""
        lat_rounded = round(self.latitude, 2)
        lon_rounded = round(self.longitude, 2)
        url = f"https://clearoutside.com/forecast/{lat_rounded}/{lon_rounded}"
        webbrowser.open(url)
        self.logger.info(f"Opened ClearOutside website: {url}")
        
    @Slot(dict)
    def update_weather(self, weather_data: Dict):
        """Update weather display with new data (compatibility method)."""
        # This method exists for compatibility but we use ClearOutside images
        pass

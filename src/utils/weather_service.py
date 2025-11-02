"""
Weather Service for NextAstroTarget application.
Provides astronomical weather forecasting using ClearOutside service.
"""

import tkinter as tk
from tkinter import ttk
import requests
from PIL import Image, ImageTk
from io import BytesIO
import logging
from typing import Optional, Tuple
import webbrowser


class WeatherForecastWidget:
    """Widget for displaying astronomical weather forecast from ClearOutside."""
    
    def __init__(self, parent_frame: ttk.Frame, latitude: float, longitude: float):
        self.parent_frame = parent_frame
        self.latitude = latitude
        self.longitude = longitude
        self.logger = logging.getLogger(__name__)
        
        # Widget components
        self.weather_frame = None
        self.forecast_image_label = None
        self.status_label = None
        self.refresh_button = None
        self.view_button = None
        
        # Cached image
        self.forecast_image = None
        
        self.setup_widget()
    
    def setup_widget(self):
        """Setup the weather forecast widget."""
        # Use the parent frame directly (no additional LabelFrame)
        self.weather_frame = self.parent_frame
        
        # Compact header with location and controls in one row
        header_frame = ttk.Frame(self.weather_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        header_frame.grid_columnconfigure(2, weight=1)  # Make middle space expandable
        
        # Location label (more compact)
        location_label = ttk.Label(
            header_frame,
            text=f"{self.latitude:.2f}°N, {self.longitude:.2f}°E",
            font=("Arial", 9, "bold")
        )
        location_label.grid(row=0, column=0, sticky=tk.W)
        
        # Control buttons (horizontal layout to save space)
        self.refresh_button = ttk.Button(
            header_frame,
            text="↻",  # Refresh symbol
            command=self.refresh_forecast,
            width=3
        )
        self.refresh_button.grid(row=0, column=3, sticky=tk.E, padx=2)
        
        self.view_button = ttk.Button(
            header_frame,
            text="🔗",  # Link symbol
            command=self.open_clearoutside_website,
            width=3
        )
        self.view_button.grid(row=0, column=4, sticky=tk.E, padx=2)
        
        # Forecast image with better sizing (takes most of the space)
        self.forecast_image_label = ttk.Label(
            self.weather_frame,
            text="Loading weather forecast...",
            font=("Arial", 10),
            anchor="center",
            justify=tk.CENTER
        )
        self.forecast_image_label.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Compact status label
        self.status_label = ttk.Label(
            self.weather_frame,
            text="Click ↻ to load forecast",
            font=("Arial", 8),
            foreground="gray",
            wraplength=200
        )
        self.status_label.grid(row=2, column=0, sticky=tk.W, padx=5, pady=(0, 5))
        
        # Configure weights to make image area expand
        self.weather_frame.grid_columnconfigure(0, weight=1)
        self.weather_frame.grid_rowconfigure(1, weight=1)  # Make image area expandable
        
        # Load initial forecast
        self.refresh_forecast()
    
    def get_clearoutside_urls(self) -> Tuple[str, str]:
        """Get ClearOutside URLs for the current coordinates."""
        # Round coordinates to 2 decimal places for ClearOutside compatibility
        lat_rounded = round(self.latitude, 2)
        lon_rounded = round(self.longitude, 2)
        
        # Use the medium sized image for better visibility
        forecast_image_url = f"https://clearoutside.com/forecast_image_medium/{lat_rounded}/{lon_rounded}/forecast.png"
        website_url = f"https://clearoutside.com/forecast/{lat_rounded}/{lon_rounded}"
        
        return forecast_image_url, website_url
    
    def refresh_forecast(self):
        """Refresh the weather forecast from ClearOutside."""
        self.logger.info("Refreshing astronomical weather forecast")
        
        try:
            # Update status
            self.status_label.config(text="Loading forecast image...", foreground="blue")
            self.refresh_button.config(state='disabled')
            self.parent_frame.update_idletasks()
            
            # Get forecast image URL
            image_url, _ = self.get_clearoutside_urls()
            
            # Download forecast image
            headers = {
                'User-Agent': 'NextAstroTarget/1.1.0 (Astronomy Application)'
            }
            
            response = requests.get(image_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Verify we got image content, not HTML
            if response.headers.get('content-type', '').startswith('text/html'):
                raise Exception("ClearOutside returned webpage instead of image")
            
            if not response.content.startswith(b'\x89PNG') and not response.content.startswith(b'\xff\xd8'):
                raise Exception("Invalid image format received")
            
            # Load and display image
            image_data = BytesIO(response.content)
            pil_image = Image.open(image_data)
            
            # Scale image to make it much more readable (ClearOutside images are very small)
            original_width, original_height = pil_image.size
            self.logger.info(f"Original image size: {original_width}x{original_height}")
            
            # ClearOutside medium images are larger (typically 672x225)
            # They should fit better in the widget with minimal scaling
            
            target_width = 170   # Widget width constraint
            max_height = 250     # Maximum height to fit in widget
            
            # Calculate scale factor based on image size
            if original_height >= 150:  # Medium/large images like the new medium format
                # Scale to fit width primarily, these are already readable
                width_scale = target_width / original_width
                # Don't scale up too much, but ensure readability
                scale_factor = max(width_scale, 0.8)  # Don't scale down too much
                scale_factor = min(scale_factor, 1.5)  # Don't scale up too much
            elif original_height < 80:  # Very thin images (small format fallback)
                # Scale to achieve good readability for thin images
                height_scale = 120 / original_height
                scale_factor = max(height_scale, 2.0)  # Minimum 2x for small images
                scale_factor = min(scale_factor, 4.0)  # Maximum 4x to prevent huge images
            else:
                # Normal sized images - scale to fit width
                scale_factor = target_width / original_width
                scale_factor = max(scale_factor, 1.0)  # Never scale down below original
            
            # Apply scaling
            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)
            
            # Ensure height is within reasonable bounds
            if new_height > max_height:
                height_scale = max_height / new_height
                new_width = int(new_width * height_scale)
                new_height = max_height
            
            # For very wide images, we accept that they'll be wider than the widget
            # The label can scroll or the user can see the important parts
            
            # Resize with high-quality interpolation for crisp text
            pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            self.logger.info(f"Scaled image to: {new_width}x{new_height} (scale factor: {scale_factor:.1f}x)")
            
            # Convert to PhotoImage for Tkinter
            self.forecast_image = ImageTk.PhotoImage(pil_image)
            
            # Update the label with the image
            self.forecast_image_label.config(
                image=self.forecast_image,
                text="",  # Clear text when image is loaded
            )
            
            # Update status
            self.status_label.config(
                text=f"✓ Forecast updated - Data from ClearOutside.com",
                foreground="green"
            )
            
            self.logger.info("Weather forecast loaded successfully")
            
        except requests.RequestException as e:
            self.logger.error(f"Network error loading weather forecast: {e}")
            self.forecast_image_label.config(
                image="",
                text=f"Network error loading forecast\n\n{str(e)[:100]}..."
            )
            self.status_label.config(
                text="✗ Failed to load forecast - Check internet connection",
                foreground="red"
            )
            
        except Exception as e:
            self.logger.error(f"Error loading weather forecast: {e}")
            self.forecast_image_label.config(
                image="",
                text=f"Error loading forecast\n\n{str(e)[:100]}..."
            )
            self.status_label.config(
                text="✗ Error loading forecast",
                foreground="red"
            )
            
        finally:
            self.refresh_button.config(state='normal')
    
    def open_clearoutside_website(self):
        """Open the ClearOutside website for detailed forecast."""
        try:
            _, website_url = self.get_clearoutside_urls()
            self.logger.info(f"Opening ClearOutside website: {website_url}")
            webbrowser.open(website_url)
            
        except Exception as e:
            self.logger.error(f"Error opening ClearOutside website: {e}")
            self.status_label.config(
                text="✗ Error opening website",
                foreground="red"
            )
    
    def update_coordinates(self, latitude: float, longitude: float):
        """Update the coordinates for weather forecast."""
        self.latitude = latitude
        self.longitude = longitude
        
        # Update location label (find the label that contains coordinates)
        for widget in self.weather_frame.winfo_children():
            if isinstance(widget, ttk.Label) and ("°N" in widget.cget("text") or "Location:" in widget.cget("text")):
                widget.config(text=f"{latitude:.2f}°N, {longitude:.2f}°E")
                break
        
        # Refresh forecast with new coordinates
        self.refresh_forecast()
        
        self.logger.info(f"Weather widget coordinates updated: {latitude:.4f}, {longitude:.4f}")
    
    def destroy(self):
        """Clean up the weather widget."""
        if self.weather_frame:
            self.weather_frame.destroy()


class WeatherService:
    """Service for managing weather forecast functionality."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def is_clearoutside_available(self) -> bool:
        """Check if ClearOutside service is available."""
        try:
            response = requests.get("https://clearoutside.com", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def validate_coordinates_for_clearoutside(self, latitude: float, longitude: float) -> bool:
        """Validate that coordinates are suitable for ClearOutside."""
        # ClearOutside works worldwide but is optimized for certain regions
        return (-90 <= latitude <= 90) and (-180 <= longitude <= 180)
    
    def get_forecast_info(self, latitude: float, longitude: float) -> dict:
        """Get forecast information for given coordinates."""
        lat_rounded = round(latitude, 2)
        lon_rounded = round(longitude, 2)
        
        return {
            'latitude': lat_rounded,
            'longitude': lon_rounded,
            'image_url': f"https://clearoutside.com/forecast_image_small/{lat_rounded}/{lon_rounded}/forecast.png",
            'website_url': f"https://clearoutside.com/forecast/{lat_rounded}/{lon_rounded}",
            'service': 'ClearOutside.com'
        }
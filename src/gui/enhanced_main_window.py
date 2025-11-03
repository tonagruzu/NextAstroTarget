"""
Enhanced main window for NextAstroTarget application following UserInterface.md specifications.
Implements comprehensive astrophotography target selection interface with timing, location,
filtering, and detailed object data management.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import logging
from typing import Optional, Dict, Any
import math
import configparser
import os

from src.database.database_manager import DatabaseManager
from src.gui.database_init_gui import DatabaseInitGUI
from src.gui.enhanced_target_selection_gui import EnhancedTargetSelectionGUI
from src.utils.astronomical_calculations import AstronomicalCalculator
from src.utils.location_service import LocationService
from src.utils.weather_service import WeatherForecastWidget


class EnhancedMainWindow:
    """Enhanced main application window implementing UserInterface.md specifications."""
    
    def __init__(self, root: tk.Tk, db_manager: DatabaseManager):
        self.root = root
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        self.astro_calc = AstronomicalCalculator()
        self.location_service = LocationService()
        
        # Current screen tracking
        self.current_screen = None
        self.screens = {}
        
        # Observatory settings (user configurable)
        self.observatory = {
            'latitude': 40.0,      # degrees N
            'longitude': -75.0,    # degrees W (negative for west)
            'elevation': 100.0,    # meters
            'timezone': 'EST',     # timezone name
            'gmt_offset': -5.0,    # hours from GMT
            'dst_active': True     # daylight saving time
        }
        
        # Current time settings
        self.current_time = datetime.now()
        
        # Active filter tracking for visual feedback
        self.active_filters = {
            'declination': False,
            'size': False,
            'transit': False,
            'rating': None,  # Stores the active rating level
            'catalog': None,  # Stores the active catalog
            'type': None     # Stores the active object type
        }
        
        # Filter button references for styling
        self.filter_buttons = {}
        
        # Load observatory settings from config
        self.load_observatory_config()
        
        # Setup GUI
        self.setup_enhanced_gui()
        self.check_database_and_navigate()
    
    def setup_enhanced_gui(self):
        """Set up the enhanced GUI structure following UserInterface.md."""
        # Configure root window
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.configure(bg='#f0f0f0')
        
        # Create main container with sections
        self.setup_main_container()
        self.setup_header_section()
        self.setup_timing_location_section()
        self.setup_sun_moon_section()
        self.setup_weather_section()
        self.setup_filtering_section()
        self.setup_object_data_section()
        self.setup_status_section()
    
    def setup_main_container(self):
        """Create main container structure."""
        # Configure root window grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Main container frame
        main_container = ttk.Frame(self.root)
        main_container.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        
        # Main scrollable frame
        self.main_canvas = tk.Canvas(main_container, bg='#f0f0f0')
        self.scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=self.main_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.main_canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )
        
        self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack main components with proper grid layout
        self.main_canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Configure grid weights
        self.scrollable_frame.columnconfigure(0, weight=1)
        # Give most weight to the object data section (row 4)
        self.scrollable_frame.rowconfigure(4, weight=1)
        
        # Add mouse wheel scrolling
        self.main_canvas.bind("<MouseWheel>", self._on_mousewheel)
        
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def setup_header_section(self):
        """Setup application header with navigation."""
        header_frame = ttk.Frame(self.scrollable_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)
        header_frame.columnconfigure(1, weight=1)
        
        # Application title
        title_label = ttk.Label(
            header_frame,
            text="NextAstroTarget",
            font=("Arial", 20, "bold"),
            foreground="#2c3e50"
        )
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # Navigation buttons
        nav_frame = ttk.Frame(header_frame)
        nav_frame.grid(row=0, column=2, sticky=tk.E)
        
        self.db_init_button = ttk.Button(
            nav_frame,
            text="Database Init",
            command=self.show_database_init,
            style="Navigation.TButton"
        )
        self.db_init_button.pack(side=tk.LEFT, padx=2)
        
        self.target_selection_button = ttk.Button(
            nav_frame,
            text="Target Selection",
            command=self.show_target_selection,
            style="Navigation.TButton"
        )
        self.target_selection_button.pack(side=tk.LEFT, padx=2)
        
        # Subtitle with current status
        self.status_label = ttk.Label(
            header_frame,
            text="Astrophotography Target Selection System",
            font=("Arial", 12),
            foreground="#7f8c8d"
        )
        self.status_label.grid(row=1, column=0, columnspan=3, pady=(0, 10))
    
    def setup_timing_location_section(self):
        """Setup Timing and Location controls."""
        # Timing and Location
        timing_frame = ttk.LabelFrame(
            self.scrollable_frame,
            text="Timing and Location",
            style="Section.TLabelframe"
        )
        timing_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)
        timing_frame.columnconfigure(2, weight=1)
        
        # Date/Time controls
        ttk.Label(timing_frame, text="Date/Time:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        
        # Time control frame
        time_frame = ttk.Frame(timing_frame)
        time_frame.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Current time button
        self.now_button = ttk.Button(
            time_frame,
            text="Now",
            command=self.set_time_now,
            style="Action.TButton"
        )
        self.now_button.pack(side=tk.LEFT, padx=2)
        
        # Sunset button
        self.sunset_button = ttk.Button(
            time_frame,
            text="Sunset",
            command=self.set_time_sunset,
            style="Action.TButton"
        )
        self.sunset_button.pack(side=tk.LEFT, padx=2)
        
        # Date/time spinboxes
        self.setup_datetime_spinboxes(time_frame)
        
        # Location controls
        location_frame = ttk.Frame(timing_frame)
        location_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        self.setup_location_controls(location_frame)
    
    def setup_datetime_spinboxes(self, parent):
        """Setup date/time spinboxes for detailed time control."""
        # Month spinbox
        ttk.Label(parent, text="Month:").pack(side=tk.LEFT, padx=(10, 2))
        self.month_var = tk.StringVar(value=str(self.current_time.month))
        self.month_spin = ttk.Spinbox(
            parent, from_=1, to=12, width=3, textvariable=self.month_var,
            command=self.on_time_changed
        )
        self.month_spin.pack(side=tk.LEFT, padx=2)
        
        # Day spinbox
        ttk.Label(parent, text="Day:").pack(side=tk.LEFT, padx=(10, 2))
        self.day_var = tk.StringVar(value=str(self.current_time.day))
        self.day_spin = ttk.Spinbox(
            parent, from_=1, to=31, width=3, textvariable=self.day_var,
            command=self.on_time_changed
        )
        self.day_spin.pack(side=tk.LEFT, padx=2)
        
        # Year spinbox
        ttk.Label(parent, text="Year:").pack(side=tk.LEFT, padx=(10, 2))
        self.year_var = tk.StringVar(value=str(self.current_time.year))
        self.year_spin = ttk.Spinbox(
            parent, from_=2020, to=2030, width=5, textvariable=self.year_var,
            command=self.on_time_changed
        )
        self.year_spin.pack(side=tk.LEFT, padx=2)
        
        # Hour spinbox
        ttk.Label(parent, text="Hour:").pack(side=tk.LEFT, padx=(10, 2))
        self.hour_var = tk.StringVar(value=str(self.current_time.hour))
        self.hour_spin = ttk.Spinbox(
            parent, from_=0, to=23, width=3, textvariable=self.hour_var,
            command=self.on_time_changed
        )
        self.hour_spin.pack(side=tk.LEFT, padx=2)
        
        # Minute spinbox
        ttk.Label(parent, text="Min:").pack(side=tk.LEFT, padx=(10, 2))
        self.minute_var = tk.StringVar(value=str(self.current_time.minute))
        self.minute_spin = ttk.Spinbox(
            parent, from_=0, to=59, width=3, textvariable=self.minute_var,
            command=self.on_time_changed
        )
        self.minute_spin.pack(side=tk.LEFT, padx=2)
    
    def setup_location_controls(self, parent):
        """Setup observatory location controls with address lookup."""
        # Address lookup row
        ttk.Label(parent, text="Address:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.address_var = tk.StringVar()
        self.address_entry = ttk.Entry(parent, textvariable=self.address_var, width=30)
        self.address_entry.grid(row=0, column=1, columnspan=2, sticky=tk.EW, padx=5, pady=2)
        
        self.lookup_button = ttk.Button(
            parent, text="Lookup Location", 
            command=self.lookup_address,
            style="Action.TButton"
        )
        self.lookup_button.grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)
        
        # Status label for lookup results
        self.location_status_var = tk.StringVar(value="Enter address and click 'Lookup Location'")
        self.location_status_label = ttk.Label(
            parent, textvariable=self.location_status_var,
            foreground="gray", font=("Arial", 9)
        )
        self.location_status_label.grid(row=0, column=4, sticky=tk.W, padx=5, pady=2)
        
        # Coordinates and timezone row
        # Latitude
        ttk.Label(parent, text="Latitude (deg):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.latitude_var = tk.StringVar(value=str(self.observatory['latitude']))
        self.latitude_entry = ttk.Entry(parent, textvariable=self.latitude_var, width=12)
        self.latitude_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        self.latitude_entry.bind('<KeyRelease>', self.on_location_changed)
        
        # Longitude
        ttk.Label(parent, text="Longitude (deg):").grid(row=1, column=2, sticky=tk.W, padx=5, pady=2)
        self.longitude_var = tk.StringVar(value=str(self.observatory['longitude']))
        self.longitude_entry = ttk.Entry(parent, textvariable=self.longitude_var, width=12)
        self.longitude_entry.grid(row=1, column=3, sticky=tk.W, padx=5, pady=2)
        self.longitude_entry.bind('<KeyRelease>', self.on_location_changed)
        
        # GMT Offset and DST row
        ttk.Label(parent, text="GMT Offset (hrs):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.gmt_offset_var = tk.StringVar(value=str(self.observatory['gmt_offset']))
        self.gmt_offset_entry = ttk.Entry(parent, textvariable=self.gmt_offset_var, width=8)
        self.gmt_offset_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        self.gmt_offset_entry.bind('<KeyRelease>', self.on_location_changed)
        
        # DST checkbox
        self.dst_var = tk.BooleanVar(value=self.observatory['dst_active'])
        self.dst_check = ttk.Checkbutton(
            parent, text="DST Active", variable=self.dst_var,
            command=self.on_location_changed
        )
        self.dst_check.grid(row=2, column=2, sticky=tk.W, padx=5, pady=2)
        
        # Configure column weights for better layout
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_columnconfigure(4, weight=1)
    

    
    def setup_sun_moon_section(self):
        """Setup Sun and Moon data display."""
        astro_frame = ttk.LabelFrame(
            self.scrollable_frame,
            text="Sun and Moon Data",
            style="Section.TLabelframe"
        )
        astro_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        # Configure column weights - left side for sun/moon, right side for weather (more space)
        astro_frame.columnconfigure(0, weight=2)  # Sun/Moon area (more space)
        astro_frame.columnconfigure(1, weight=3)  # Weather area (even more space for forecast image)
        astro_frame.rowconfigure(0, weight=1)  # Make row expandable
        
        # Container for sun and moon data (left side) - side-by-side layout
        sun_moon_container = ttk.Frame(astro_frame)
        sun_moon_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        sun_moon_container.columnconfigure(0, weight=1)
        sun_moon_container.columnconfigure(1, weight=1)
        
        # Sun data section (left)
        sun_frame = ttk.Frame(sun_moon_container)
        sun_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        self.setup_sun_data(sun_frame)
        
        # Moon data section (right)
        moon_frame = ttk.Frame(sun_moon_container)
        moon_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        self.setup_moon_data(moon_frame)
    
    def setup_sun_data(self, parent):
        """Setup sun data display with better space utilization."""
        # Header with larger, more prominent text
        ttk.Label(parent, text="☀ Sun Data", font=("Arial", 14, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(5, 10)
        )
        
        # Sun position labels with larger fonts and better spacing
        self.sun_alt_label = ttk.Label(parent, text="Altitude: --°", font=("Arial", 11))
        self.sun_alt_label.grid(row=1, column=0, sticky=tk.W, padx=(10, 5), pady=2)
        
        self.sun_az_label = ttk.Label(parent, text="Azimuth: --°", font=("Arial", 11))
        self.sun_az_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Sun times with larger fonts
        self.sunrise_label = ttk.Label(parent, text="Sunrise: --:--", font=("Arial", 11))
        self.sunrise_label.grid(row=2, column=0, sticky=tk.W, padx=(10, 5), pady=2)
        
        self.sunset_label = ttk.Label(parent, text="Sunset: --:--", font=("Arial", 11))
        self.sunset_label.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Nautical twilight times
        self.nautical_dawn_label = ttk.Label(parent, text="Nautical Dawn: --:--", font=("Arial", 10))
        self.nautical_dawn_label.grid(row=3, column=0, sticky=tk.W, padx=(10, 5), pady=2)
        
        self.nautical_dusk_label = ttk.Label(parent, text="Nautical Dusk: --:--", font=("Arial", 10))
        self.nautical_dusk_label.grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Sun status indicator
        self.sun_status_label = ttk.Label(parent, text="Status: --", font=("Arial", 10, "italic"))
        self.sun_status_label.grid(row=4, column=0, columnspan=2, sticky=tk.W, padx=10, pady=(5, 10))
    
    def setup_moon_data(self, parent):
        """Setup moon data display with better layout and larger moon phase graphic."""
        # Header with moon emoji and larger text
        ttk.Label(parent, text="🌙 Moon Data", font=("Arial", 14, "bold")).grid(
            row=0, column=0, columnspan=3, pady=(5, 10)
        )
        
        # Moon phase canvas (larger and more prominent)
        self.moon_canvas = tk.Canvas(parent, width=80, height=80, bg='black', highlightthickness=1)
        self.moon_canvas.grid(row=1, column=0, rowspan=3, padx=(10, 15), pady=5, sticky=tk.N)
        
        # Moon position and timing data in two columns
        self.moon_alt_label = ttk.Label(parent, text="Altitude: --°", font=("Arial", 11))
        self.moon_alt_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        self.moon_az_label = ttk.Label(parent, text="Azimuth: --°", font=("Arial", 11))
        self.moon_az_label.grid(row=1, column=2, sticky=tk.W, padx=5, pady=2)
        
        self.moon_phase_label = ttk.Label(parent, text="Phase: --%", font=("Arial", 11))
        self.moon_phase_label.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        self.moon_rise_label = ttk.Label(parent, text="Moonrise: --:--", font=("Arial", 11))
        self.moon_rise_label.grid(row=2, column=2, sticky=tk.W, padx=5, pady=2)
        
        # Additional moon info
        self.moon_set_label = ttk.Label(parent, text="Moonset: --:--", font=("Arial", 10))
        self.moon_set_label.grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)
        
        self.moon_distance_label = ttk.Label(parent, text="Distance: -- km", font=("Arial", 10))
        self.moon_distance_label.grid(row=3, column=2, sticky=tk.W, padx=5, pady=2)
        
        # Moon status
        self.moon_status_label = ttk.Label(parent, text="Status: --", font=("Arial", 10, "italic"))
        self.moon_status_label.grid(row=4, column=1, columnspan=2, sticky=tk.W, padx=5, pady=(5, 10))
    
    def setup_weather_section(self):
        """Setup Weather Forecast section using ClearOutside service."""
        # Get the astro_frame from sun/moon section to add weather on the right
        # Find the astro_frame that was created in setup_sun_moon_section
        for child in self.scrollable_frame.winfo_children():
            if isinstance(child, ttk.LabelFrame) and "Sun and Moon Data" in child.cget("text"):
                astro_frame = child
                break
        else:
            # Fallback: create standalone weather frame if astro_frame not found
            astro_frame = self.scrollable_frame
        
        # Create weather frame on the right side (narrower but taller)
        weather_frame = ttk.LabelFrame(
            astro_frame,
            text="Weather Forecast",
            style="Section.TLabelframe"
        )
        weather_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Create weather forecast widget inside the frame
        self.weather_widget = WeatherForecastWidget(
            weather_frame,
            self.observatory['latitude'],
            self.observatory['longitude']
        )
        
        self.logger.info("Weather forecast section initialized")
    
    def setup_filtering_section(self):
        """Setup Filtering buttons."""
        filter_frame = ttk.LabelFrame(
            self.scrollable_frame,
            text="Filtering Controls",
            style="Section.TLabelframe"
        )
        filter_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        # Active filters status indicator
        self.setup_filter_status(filter_frame)
        
        # Create filter button groups
        self.setup_filter_buttons(filter_frame)
    
    def setup_filter_status(self, parent):
        """Setup active filter status display."""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=(5, 10))
        
        ttk.Label(status_frame, text="Active Filters:", font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        
        self.filter_status_label = ttk.Label(
            status_frame, 
            text="None", 
            font=("Arial", 9), 
            foreground="gray"
        )
        self.filter_status_label.pack(side=tk.LEFT, padx=10)
    
    def setup_filter_buttons(self, parent):
        """Setup comprehensive filtering button system."""
        # Declination limits (blue)
        dec_frame = ttk.Frame(parent)
        dec_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=5, pady=2)
        
        ttk.Label(dec_frame, text="Declination Limits:").pack(side=tk.LEFT)
        
        # Use saved values if available, otherwise use defaults
        min_dec_default = "-30"
        max_dec_default = "+90"
        if hasattr(self, 'saved_filter_values') and self.saved_filter_values:
            min_dec_default = self.saved_filter_values['min_dec']
            max_dec_default = self.saved_filter_values['max_dec']
            
        self.min_dec_var = tk.StringVar(value=min_dec_default)
        ttk.Entry(dec_frame, textvariable=self.min_dec_var, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Label(dec_frame, text="to").pack(side=tk.LEFT, padx=2)
        self.max_dec_var = tk.StringVar(value=max_dec_default)
        ttk.Entry(dec_frame, textvariable=self.max_dec_var, width=8).pack(side=tk.LEFT, padx=2)
        
        self.filter_buttons['declination'] = tk.Button(
            dec_frame, text="Apply Dec Filter",
            command=self.apply_declination_filter,
            bg="#f0f8ff", fg="darkblue", font=("Arial", 9),
            relief="raised", borderwidth=1
        )
        self.filter_buttons['declination'].pack(side=tk.LEFT, padx=5)
        
        # Size limits (green)
        size_frame = ttk.Frame(parent)
        size_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=5, pady=2)
        
        ttk.Label(size_frame, text="Size Limits (arcmin):").pack(side=tk.LEFT)
        
        # Use saved values if available, otherwise use defaults
        min_size_default = "0"
        max_size_default = "999"
        if hasattr(self, 'saved_filter_values') and self.saved_filter_values:
            min_size_default = self.saved_filter_values['min_size']
            max_size_default = self.saved_filter_values['max_size']
            
        self.min_size_var = tk.StringVar(value=min_size_default)
        ttk.Entry(size_frame, textvariable=self.min_size_var, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Label(size_frame, text="to").pack(side=tk.LEFT, padx=2)
        self.max_size_var = tk.StringVar(value=max_size_default)
        ttk.Entry(size_frame, textvariable=self.max_size_var, width=8).pack(side=tk.LEFT, padx=2)
        
        self.filter_buttons['size'] = tk.Button(
            size_frame, text="Apply Size Filter",
            command=self.apply_size_filter,
            bg="#f0fff0", fg="darkgreen", font=("Arial", 9),
            relief="raised", borderwidth=1
        )
        self.filter_buttons['size'].pack(side=tk.LEFT, padx=5)
        
        # Transit Time limits (purple)
        transit_frame = ttk.Frame(parent)
        transit_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), padx=5, pady=2)
        
        ttk.Label(transit_frame, text="Transit Time (24h format):").pack(side=tk.LEFT)
        
        # Use saved values if available, otherwise use defaults
        start_time_default = "18:00"
        end_time_default = "06:00"
        if hasattr(self, 'saved_filter_values') and self.saved_filter_values:
            start_time_default = self.saved_filter_values.get('transit_start', "18:00")
            end_time_default = self.saved_filter_values.get('transit_end', "06:00")
            
        self.transit_start_var = tk.StringVar(value=start_time_default)
        ttk.Entry(transit_frame, textvariable=self.transit_start_var, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Label(transit_frame, text="to").pack(side=tk.LEFT, padx=2)
        self.transit_end_var = tk.StringVar(value=end_time_default)
        ttk.Entry(transit_frame, textvariable=self.transit_end_var, width=8).pack(side=tk.LEFT, padx=2)
        
        self.filter_buttons['transit'] = tk.Button(
            transit_frame, text="Apply Transit Filter",
            command=self.apply_transit_filter,
            bg="#f8f0ff", fg="purple", font=("Arial", 9),
            relief="raised", borderwidth=1
        )
        self.filter_buttons['transit'].pack(side=tk.LEFT, padx=5)
        
        # Best targets (red)
        rating_frame = ttk.Frame(parent)
        rating_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), padx=5, pady=2)
        
        ttk.Label(rating_frame, text="Best Targets:").pack(side=tk.LEFT)
        
        for rating, label in [(5, "Showcase (5)"), (4, "Excellent (4+)"), (3, "Good (3+)")]:
            button = tk.Button(
                rating_frame, text=label,
                command=lambda r=rating: self.filter_by_rating(r),
                bg="#fff0f0", fg="darkred", font=("Arial", 9),
                relief="raised", borderwidth=1
            )
            button.pack(side=tk.LEFT, padx=2)
            self.filter_buttons[f'rating_{rating}'] = button
        
        # Catalog filters (blue dropdown style)
        catalog_frame = ttk.Frame(parent)
        catalog_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), padx=5, pady=2)
        
        ttk.Label(catalog_frame, text="Catalogs:").pack(side=tk.LEFT)
        
        self.catalog_var = tk.StringVar()
        self.filter_buttons['catalog'] = ttk.Combobox(
            catalog_frame, textvariable=self.catalog_var,
            values=["All", "Messier", "NGC", "IC", "Caldwell", "Sharpless", "Barnard"],
            width=15, state="readonly"
        )
        self.filter_buttons['catalog'].pack(side=tk.LEFT, padx=5)
        self.filter_buttons['catalog'].bind('<<ComboboxSelected>>', self.on_catalog_filter_changed)
        
        # Object type filters (brown)
        type_frame = ttk.Frame(parent)
        type_frame.grid(row=6, column=0, sticky=(tk.W, tk.E), padx=5, pady=2)
        
        ttk.Label(type_frame, text="Object Types:").pack(side=tk.LEFT)
        
        for obj_type in ["Galaxies", "Nebulae", "Clusters", "Planetary Nebulae"]:
            button = tk.Button(
                type_frame, text=obj_type,
                command=lambda t=obj_type: self.filter_by_type(t),
                bg="#fdf5e6", fg="saddlebrown", font=("Arial", 9),
                relief="raised", borderwidth=1
            )
            button.pack(side=tk.LEFT, padx=2)
            self.filter_buttons[f'type_{obj_type.lower().replace(" ", "_")}'] = button
        
        # Sorting controls (gray)
        sort_frame = ttk.Frame(parent)
        sort_frame.grid(row=7, column=0, sticky=(tk.W, tk.E), padx=5, pady=2)
        
        ttk.Label(sort_frame, text="Sorting:").pack(side=tk.LEFT)
        
        ttk.Button(
            sort_frame, text="Alphabetical Sort",
            command=self.sort_alphabetical,
            style="Sort.TButton"
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            sort_frame, text="Transit Sort",
            command=self.sort_transit,
            style="Sort.TButton"
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            sort_frame, text="Top",
            command=self.scroll_to_top,
            style="Sort.TButton"
        ).pack(side=tk.LEFT, padx=2)
        
        # Add separator and clear buttons to same row for better grouping
        ttk.Separator(sort_frame, orient='vertical').pack(side=tk.LEFT, padx=10, fill='y')
        
        ttk.Button(
            sort_frame, text="Clear Filters (Keep Values)",
            command=self.clear_filters,
            style="Filter.Clear.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            sort_frame, text="Reset Values & Filters",
            command=self.reset_filters,
            style="Filter.Clear.TButton"
        ).pack(side=tk.LEFT, padx=5)
    
    def setup_object_data_section(self):
        """Setup Object data with comprehensive column display."""
        # This will be the main target selection interface
        self.content_frame = ttk.Frame(self.scrollable_frame)
        self.content_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=5)
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(0, weight=1)
        
        # This is where the enhanced target selection GUI will be embedded
    
    def setup_status_section(self):
        """Setup status bar at bottom."""
        self.status_frame = ttk.Frame(self.scrollable_frame)
        self.status_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)
        self.status_frame.columnconfigure(1, weight=1)
        
        # Status indicator
        self.status_indicator = ttk.Label(
            self.status_frame, text="●", foreground="green", font=("Arial", 16)
        )
        self.status_indicator.grid(row=0, column=0, padx=5)
        
        # Status message
        self.status_message = ttk.Label(
            self.status_frame, text="Ready - Select your next astrophotography target"
        )
        self.status_message.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # Current time display
        self.current_time_label = ttk.Label(self.status_frame, text="")
        self.current_time_label.grid(row=0, column=2, padx=5)
        
        # Start time update
        self.update_current_time()
    
    def setup_styles(self):
        """Setup custom styles for the enhanced interface."""
        style = ttk.Style()
        
        # Section label frames
        style.configure("Section.TLabelframe", relief="ridge", borderwidth=2)
        style.configure("Section.TLabelframe.Label", font=("Arial", 10, "bold"))
        
        # Navigation buttons
        style.configure("Navigation.TButton", padding=(10, 5))
        
        # Action buttons
        style.configure("Action.TButton", foreground="blue")
        
        # Sort buttons
        style.configure("Sort.TButton", foreground="darkgreen")
        
        # Filter buttons with different colors - inactive state (lighter, subtle)
        style.configure("Filter.Dec.TButton", 
                       foreground="darkblue", 
                       background="#f0f8ff",  # AliceBlue
                       borderwidth=1,
                       relief="raised")
        style.configure("Filter.Size.TButton", 
                       foreground="darkgreen", 
                       background="#f0fff0",  # Honeydew
                       borderwidth=1,
                       relief="raised") 
        style.configure("Filter.Rating.TButton", 
                       foreground="darkred", 
                       background="#fff0f0",  # Light pink
                       borderwidth=1,
                       relief="raised")
        style.configure("Filter.Type.TButton", 
                       foreground="saddlebrown", 
                       background="#fdf5e6",  # OldLace
                       borderwidth=1,
                       relief="raised")
        style.configure("Filter.Clear.TButton", 
                       foreground="black", 
                       font=("Arial", 9, "bold"))
        
        # Filter buttons - active state (bold, prominent colors with strong borders)
        style.configure("Filter.Dec.Active.TButton", 
                       foreground="white", 
                       background="#0066cc",  # Strong blue
                       font=("Arial", 10, "bold"),
                       borderwidth=3,
                       focuscolor="yellow",
                       relief="raised")
        style.configure("Filter.Size.Active.TButton", 
                       foreground="white", 
                       background="#009900",  # Strong green
                       font=("Arial", 10, "bold"),
                       borderwidth=3,
                       focuscolor="yellow",
                       relief="raised")
        style.configure("Filter.Rating.Active.TButton", 
                       foreground="white", 
                       background="#cc0000",  # Strong red
                       font=("Arial", 10, "bold"),
                       borderwidth=3,
                       focuscolor="yellow",
                       relief="raised")
        style.configure("Filter.Type.Active.TButton", 
                       foreground="white", 
                       background="#8B4513",  # SaddleBrown
                       font=("Arial", 10, "bold"),
                       borderwidth=3,
                       focuscolor="yellow",
                       relief="raised")
        style.configure("Filter.Catalog.Active.TButton", 
                       foreground="white", 
                       background="#003366",  # Dark navy
                       font=("Arial", 10, "bold"),
                       borderwidth=3,
                       focuscolor="yellow",
                       relief="raised")
    
    # Filter state management methods
    def update_filter_button_style(self, filter_type, is_active):
        """Update filter button style and text based on active state."""
        if filter_type not in self.filter_buttons:
            return
        
        button = self.filter_buttons[filter_type]
        
        # Update style and text based on filter type
        if filter_type == 'declination':
            if is_active:
                button.configure(bg="#0066cc", fg="white", font=("Arial", 9, "bold"), text="🔵 Apply Dec Filter")
            else:
                button.configure(bg="#f0f8ff", fg="darkblue", font=("Arial", 9), text="Apply Dec Filter")
        elif filter_type == 'size':
            if is_active:
                button.configure(bg="#009900", fg="white", font=("Arial", 9, "bold"), text="🟢 Apply Size Filter")
            else:
                button.configure(bg="#f0fff0", fg="darkgreen", font=("Arial", 9), text="Apply Size Filter")
        elif filter_type == 'transit':
            if is_active:
                button.configure(bg="#800080", fg="white", font=("Arial", 9, "bold"), text="🟣 Apply Transit Filter")
            else:
                button.configure(bg="#f8f0ff", fg="purple", font=("Arial", 9), text="Apply Transit Filter")
        elif filter_type.startswith('rating_'):
            # Get the original button text and add/remove indicator
            current_text = button.cget('text')
            base_text = current_text.replace('🔴 ', '').replace('● ', '')
            if is_active:
                button.configure(bg="#cc0000", fg="white", font=("Arial", 9, "bold"), text=f"🔴 {base_text}")
            else:
                button.configure(bg="#fff0f0", fg="darkred", font=("Arial", 9), text=base_text)
        elif filter_type.startswith('type_'):
            # Get the original button text and add/remove indicator
            current_text = button.cget('text')
            base_text = current_text.replace('🟤 ', '').replace('● ', '')
            if is_active:
                button.configure(bg="#8B4513", fg="white", font=("Arial", 9, "bold"), text=f"🟤 {base_text}")
            else:
                button.configure(bg="#fdf5e6", fg="saddlebrown", font=("Arial", 9), text=base_text)
        elif filter_type == 'catalog':
            # Special handling for combobox - limited styling options
            try:
                if is_active:
                    button.configure(foreground="white", background="#003366", font=("Arial", 9, "bold"))
                else:
                    button.configure(foreground="black", background="white", font=("Arial", 9))
            except:
                pass  # Some combobox styling might not work on all systems
            return
        else:
            return
    
    def reset_all_filter_styles(self):
        """Reset all filter buttons to inactive state."""
        for filter_type in self.filter_buttons:
            self.update_filter_button_style(filter_type, False)
        
        # Clear active filter tracking
        self.active_filters = {
            'declination': False,
            'size': False,
            'transit': False,
            'rating': None,
            'catalog': None,
            'type': None
        }
        
        # Update status display
        self.update_filter_status_display()
    
    def update_filter_status_display(self):
        """Update the active filters status display."""
        if not hasattr(self, 'filter_status_label'):
            return
            
        active_list = []
        
        if self.active_filters['declination']:
            active_list.append("Declination")
        if self.active_filters['size']:
            active_list.append("Size")
        if self.active_filters['transit']:
            active_list.append("Transit Time")
        if self.active_filters['rating']:
            active_list.append(f"Rating {self.active_filters['rating']}+")
        if self.active_filters['catalog']:
            active_list.append(f"Catalog: {self.active_filters['catalog']}")
        if self.active_filters['type']:
            active_list.append(f"Type: {self.active_filters['type']}")
        
        if active_list:
            status_text = " | ".join(active_list)
            self.filter_status_label.config(text=status_text, foreground="darkgreen")
        else:
            self.filter_status_label.config(text="None", foreground="gray")
    
    # Event handlers and functionality methods
    def set_time_now(self):
        """Set time to current time."""
        self.current_time = datetime.now()
        self.update_time_controls()
        self.update_astronomical_data()
    
    def set_time_sunset(self):
        """Set time to sunset today."""
        # Calculate accurate sunset time
        sunset_time = self.astro_calc.calculate_sunset(
            self.observatory['latitude'], 
            self.observatory['longitude'],
            datetime.now().date()
        )
        
        # Convert to local time
        gmt_offset_hours = self.observatory.get('gmt_offset', 0)
        gmt_offset = timedelta(hours=gmt_offset_hours)
        
        # Apply DST correction if active
        if self.observatory.get('dst_active', False):
            gmt_offset += timedelta(hours=1)
        
        local_sunset = sunset_time + gmt_offset
        
        self.current_time = local_sunset
        self.update_time_controls()
        self.update_astronomical_data()
    
    def on_time_changed(self):
        """Handle time control changes."""
        try:
            self.current_time = datetime(
                int(self.year_var.get()),
                int(self.month_var.get()),
                int(self.day_var.get()),
                int(self.hour_var.get()),
                int(self.minute_var.get())
            )
            self.update_astronomical_data()
        except ValueError:
            pass  # Invalid date/time
    
    def lookup_address(self):
        """Lookup coordinates and timezone for the entered address."""
        address = self.address_var.get().strip()
        if not address:
            messagebox.showwarning("No Address", "Please enter an address to lookup.")
            return
        
        try:
            # Update status to show we're working
            self.location_status_var.set("Looking up location...")
            self.root.update_idletasks()
            
            # Disable the lookup button while processing
            self.lookup_button.config(state='disabled')
            
            # Perform geocoding
            location_data = self.location_service.geocode_address(address)
            
            if location_data:
                # Update the coordinate and timezone fields
                self.latitude_var.set(f"{location_data['latitude']:.6f}")
                self.longitude_var.set(f"{location_data['longitude']:.6f}")
                self.gmt_offset_var.set(f"{location_data['gmt_offset']:.1f}")
                self.dst_var.set(location_data['dst_active'])
                
                # Update the observatory settings
                self.observatory['latitude'] = location_data['latitude']
                self.observatory['longitude'] = location_data['longitude']
                self.observatory['gmt_offset'] = location_data['gmt_offset']
                self.observatory['dst_active'] = location_data['dst_active']
                self.observatory['timezone'] = location_data['timezone']
                
                # Update status with success message
                location_str = self.location_service.format_coordinates(
                    location_data['latitude'], location_data['longitude']
                )
                
                city_info = []
                if location_data.get('city'):
                    city_info.append(location_data['city'])
                if location_data.get('state'):
                    city_info.append(location_data['state'])
                if location_data.get('country'):
                    city_info.append(location_data['country'])
                
                location_name = ", ".join(city_info) if city_info else "Location found"
                
                self.location_status_var.set(
                    f"✓ {location_name} - {location_str} - {location_data['timezone']}"
                )
                self.location_status_label.config(foreground="green")
                
                # Update astronomical calculations
                self.update_astronomical_data()
                
                # Update weather widget coordinates if it exists
                if hasattr(self, 'weather_widget') and self.weather_widget:
                    self.weather_widget.update_coordinates(
                        location_data['latitude'],
                        location_data['longitude']
                    )
                
                # Save configuration with new location
                self.save_observatory_config()
                
                self.logger.info(f"Successfully geocoded address: {address}")
                messagebox.showinfo(
                    "Location Found", 
                    f"Location: {location_name}\n"
                    f"Coordinates: {location_str}\n"
                    f"Timezone: {location_data['timezone']}\n"
                    f"GMT Offset: {location_data['gmt_offset']:+.1f} hours"
                )
                
            else:
                self.location_status_var.set("✗ Address not found. Please try a more specific address.")
                self.location_status_label.config(foreground="red")
                messagebox.showerror(
                    "Location Not Found",
                    f"Could not find coordinates for: {address}\n\n"
                    "Please try:\n"
                    "• A more complete address\n"
                    "• City, State, Country format\n"
                    "• Famous landmarks or places\n"
                    "• ZIP codes or postal codes"
                )
                
        except Exception as e:
            self.location_status_var.set("✗ Error during lookup. Check internet connection.")
            self.location_status_label.config(foreground="red")
            self.logger.error(f"Error during address lookup: {e}")
            messagebox.showerror("Lookup Error", f"Error looking up address: {e}")
            
        finally:
            # Re-enable the lookup button
            self.lookup_button.config(state='normal')

    def on_location_changed(self, event=None):
        """Handle location parameter changes."""
        try:
            self.observatory['dst_active'] = self.dst_var.get()
            self.observatory['gmt_offset'] = float(self.gmt_offset_var.get())
            self.observatory['latitude'] = float(self.latitude_var.get())
            self.observatory['longitude'] = float(self.longitude_var.get())
            self.update_astronomical_data()
            
            # Update weather widget coordinates if it exists
            if hasattr(self, 'weather_widget') and self.weather_widget:
                self.weather_widget.update_coordinates(
                    self.observatory['latitude'],
                    self.observatory['longitude']
                )
            
            # Save configuration when location changes
            self.save_observatory_config()
        except ValueError:
            pass  # Invalid values
    
    def update_time_controls(self):
        """Update time control displays."""
        self.month_var.set(str(self.current_time.month))
        self.day_var.set(str(self.current_time.day))
        self.year_var.set(str(self.current_time.year))
        self.hour_var.set(str(self.current_time.hour))
        self.minute_var.set(str(self.current_time.minute))
    
    def update_astronomical_data(self):
        """Update sun and moon data displays."""
        # Update sun position data
        sun_alt, sun_az = self.astro_calc.calculate_sun_position(
            self.current_time, self.observatory['latitude'], self.observatory['longitude']
        )
        
        self.sun_alt_label.config(text=f"Altitude: {sun_alt:.1f}°")
        self.sun_az_label.config(text=f"Azimuth: {sun_az:.1f}°")
        
        # Calculate and update sun times (sunrise, sunset, twilight)
        sun_times = self.astro_calc.calculate_sun_times(
            self.observatory['latitude'], self.observatory['longitude'], self.current_time.date()
        )
        
        # Convert UTC times to local time using GMT offset
        gmt_offset_hours = self.observatory.get('gmt_offset', 0)
        gmt_offset = timedelta(hours=gmt_offset_hours)
        
        # Apply DST correction if active
        if self.observatory.get('dst_active', False):
            gmt_offset += timedelta(hours=1)
        
        local_sunrise = sun_times['sunrise'] + gmt_offset
        local_sunset = sun_times['sunset'] + gmt_offset
        local_dawn = sun_times['nautical_dawn'] + gmt_offset
        local_dusk = sun_times['nautical_dusk'] + gmt_offset
        
        self.sunrise_label.config(text=f"Sunrise: {local_sunrise.strftime('%H:%M')}")
        self.sunset_label.config(text=f"Sunset: {local_sunset.strftime('%H:%M')}")
        
        # Update individual twilight labels
        self.nautical_dawn_label.config(text=f"Nautical Dawn: {local_dawn.strftime('%H:%M')}")
        self.nautical_dusk_label.config(text=f"Nautical Dusk: {local_dusk.strftime('%H:%M')}")
        
        # Add sun status
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
        
        self.sun_status_label.config(text=f"Status: {sun_status}")
        
        # Update moon position data
        moon_alt, moon_az = self.astro_calc.calculate_moon_position(
            self.current_time, self.observatory['latitude'], self.observatory['longitude']
        )
        moon_phase_data = self.astro_calc.calculate_moon_phase(self.current_time)
        
        self.moon_alt_label.config(text=f"Altitude: {moon_alt:.1f}°")
        self.moon_az_label.config(text=f"Azimuth: {moon_az:.1f}°")
        self.moon_phase_label.config(text=f"Phase: {moon_phase_data['phase_name']} ({moon_phase_data['illumination']:.0f}%)")
        
        # Calculate and update moon times (moonrise/moonset)
        moon_times = self.astro_calc.calculate_moon_times(
            self.observatory['latitude'], self.observatory['longitude'], self.current_time.date()
        )
        
        # Convert to local time
        local_moonrise = moon_times['moonrise'] + gmt_offset
        local_moonset = moon_times.get('moonset', moon_times['moonrise'] + timedelta(hours=12)) + gmt_offset
        
        self.moon_rise_label.config(text=f"Moonrise: {local_moonrise.strftime('%H:%M')}")
        self.moon_set_label.config(text=f"Moonset: {local_moonset.strftime('%H:%M')}")
        
        # Calculate moon distance (approximate)
        moon_distance = 384400  # Average distance in km - could be calculated more precisely
        self.moon_distance_label.config(text=f"Distance: {moon_distance:,} km")
        
        # Add moon status
        if moon_alt > 0:
            moon_status = f"Above horizon ({moon_phase_data['phase_name']})"
        else:
            moon_status = f"Below horizon ({moon_phase_data['phase_name']})"
        
        self.moon_status_label.config(text=f"Status: {moon_status}")
        
        # Update moon phase graphic
        self.draw_moon_phase(moon_phase_data)
    
    def draw_moon_phase(self, phase_data):
        """Draw accurate moon phase graphic based on lunar cycle position."""
        self.moon_canvas.delete("all")
        
        # Canvas dimensions
        margin = 5
        size = 70
        center = 40
        
        illumination = phase_data['illumination']
        cycle_position = phase_data['cycle_position']
        is_waxing = phase_data['is_waxing']
        
        # Draw main moon circle (lit portion)
        self.moon_canvas.create_oval(margin, margin, margin + size, margin + size, 
                                   fill="#F5F5DC", outline="gray", width=1)  # Beige color for moon
        
        # Calculate shadow coverage based on cycle position
        if illumination < 1:  # New Moon
            # Almost completely dark
            self.moon_canvas.create_oval(margin + 1, margin + 1, margin + size - 1, margin + size - 1, 
                                       fill="#2F2F2F", outline="")
        elif illumination > 99:  # Full Moon  
            # Keep the light circle as is
            pass
        else:
            # Partial phases - create accurate shadow
            # Calculate the position of the terminator (day/night boundary)
            
            # Use cycle position for accurate shadow placement
            # cycle_position: 0.0=New, 0.25=First Quarter, 0.5=Full, 0.75=Last Quarter
            
            if cycle_position <= 0.5:
                # Waxing phases (0.0 to 0.5): Shadow starts covering entire moon, gradually reveals from right
                if cycle_position <= 0.25:  # New to First Quarter
                    # Shadow covers left portion, gradually shrinking to reveal right side
                    shadow_coverage = 1.0 - (cycle_position / 0.25)  # 1.0 to 0.0
                    shadow_width = size * shadow_coverage
                    if shadow_width > 0:
                        self.moon_canvas.create_oval(
                            margin, margin,
                            margin + shadow_width, margin + size,
                            fill="#2F2F2F", outline=""
                        )
                else:  # First Quarter to Full (0.25 to 0.5)
                    # Use elliptical shadow that shrinks from left
                    progress = (cycle_position - 0.25) / 0.25  # 0.0 to 1.0
                    shadow_offset = (size / 2) * (1.0 - progress)
                    if shadow_offset > 2:
                        self.moon_canvas.create_oval(
                            margin - shadow_offset, margin,
                            margin + shadow_offset, margin + size,
                            fill="#2F2F2F", outline=""
                        )
            else:
                # Waning phases (0.5 to 1.0): Shadow gradually covers from right
                if cycle_position <= 0.75:  # Full to Last Quarter (0.5 to 0.75)
                    # Use elliptical shadow that grows from right
                    progress = (cycle_position - 0.5) / 0.25  # 0.0 to 1.0
                    shadow_offset = (size / 2) * progress
                    if shadow_offset > 2:
                        self.moon_canvas.create_oval(
                            margin + size - shadow_offset, margin,
                            margin + size + shadow_offset, margin + size,
                            fill="#2F2F2F", outline=""
                        )
                else:  # Last Quarter to New (0.75 to 1.0)
                    # Shadow grows from right, gradually covering left portion
                    progress = (cycle_position - 0.75) / 0.25  # 0.0 to 1.0
                    shadow_start = size * (1.0 - progress)  # size to 0
                    self.moon_canvas.create_oval(
                        margin + shadow_start, margin,
                        margin + size, margin + size,
                        fill="#2F2F2F", outline=""
                    )
        
        # Add outer circle for definition
        self.moon_canvas.create_oval(margin, margin, margin + size, margin + size, 
                                   fill="", outline="gray", width=2)
        
        # Add phase information text
        self.moon_canvas.create_text(center, margin + size + 10, 
                                   text=f"{illumination:.0f}%", 
                                   font=("Arial", 9, "bold"))
        
        # Add phase name
        self.moon_canvas.create_text(center, margin + size + 25, 
                                   text=phase_data['phase_name'], 
                                   font=("Arial", 8), fill="gray")
    
    def update_current_time(self):
        """Update current time display every second."""
        current = datetime.now()
        time_str = current.strftime("%Y-%m-%d %H:%M:%S")
        self.current_time_label.config(text=time_str)
        
        # Schedule next update
        self.root.after(1000, self.update_current_time)
    
    # Sorting methods
    def sort_alphabetical(self):
        """Sort objects alphabetically."""
        if hasattr(self, 'target_selection_gui'):
            self.target_selection_gui.sort_by_column("Object Name")
        self.update_status("Sorted alphabetically by object name")
    
    def sort_transit(self):
        """Sort objects by transit time.""" 
        if hasattr(self, 'target_selection_gui'):
            self.target_selection_gui.sort_by_column("Transit Time")
        self.update_status("Sorted by transit time")
    
    def scroll_to_top(self):
        """Scroll to top of the interface."""
        self.main_canvas.yview_moveto(0)
    
    # Filter methods
    def apply_declination_filter(self):
        """Apply declination range filter."""
        try:
            min_dec = float(self.min_dec_var.get())
            max_dec = float(self.max_dec_var.get())
            if hasattr(self, 'target_selection_gui'):
                self.target_selection_gui.apply_declination_filter(min_dec, max_dec)
            
            # Update visual state
            self.active_filters['declination'] = True
            self.update_filter_button_style('declination', True)
            self.update_filter_status_display()
            
            self.update_status(f"[ACTIVE] Filtered by declination: {min_dec}° to {max_dec}°")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid declination values")
    
    def apply_size_filter(self):
        """Apply size range filter."""
        try:
            min_size = float(self.min_size_var.get())
            max_size = float(self.max_size_var.get())
            if hasattr(self, 'target_selection_gui'):
                self.target_selection_gui.apply_size_filter(min_size, max_size)
            
            # Update visual state
            self.active_filters['size'] = True
            self.update_filter_button_style('size', True)
            self.update_filter_status_display()
            
            self.update_status(f"[ACTIVE] Filtered by size: {min_size}' to {max_size}'")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid size values")
    
    def apply_transit_filter(self):
        """Apply transit time range filter."""
        try:
            start_time = self.transit_start_var.get()
            end_time = self.transit_end_var.get()
            
            # Validate time format (HH:MM)
            import re
            time_pattern = r'^([01]?[0-9]|2[0-3]):([0-5][0-9])$'
            if not re.match(time_pattern, start_time) or not re.match(time_pattern, end_time):
                raise ValueError("Invalid time format")
            
            if hasattr(self, 'target_selection_gui'):
                self.target_selection_gui.apply_transit_filter(start_time, end_time)
            
            # Update visual state
            self.active_filters['transit'] = True
            self.update_filter_button_style('transit', True)
            self.update_filter_status_display()
            
            self.update_status(f"[ACTIVE] Filtered by transit time: {start_time} to {end_time}")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid time values in HH:MM format (24-hour)")
    
    def filter_by_rating(self, min_rating):
        """Filter by minimum rating."""
        if hasattr(self, 'target_selection_gui'):
            self.target_selection_gui.apply_rating_filter(min_rating)
        
        # Update visual state - first reset all rating buttons
        for rating in [3, 4, 5]:
            self.update_filter_button_style(f'rating_{rating}', False)
        
        # Activate the selected rating button
        self.active_filters['rating'] = min_rating
        self.update_filter_button_style(f'rating_{min_rating}', True)
        self.update_filter_status_display()
        
        self.update_status(f"[ACTIVE] Filtered by rating: {min_rating}+ stars")
    
    def on_catalog_filter_changed(self, event=None):
        """Handle catalog filter selection."""
        catalog = self.catalog_var.get()
        if hasattr(self, 'target_selection_gui'):
            self.target_selection_gui.apply_catalog_filter(catalog)
        
        # Update visual state
        is_active = catalog and catalog != "All"
        self.active_filters['catalog'] = catalog if is_active else None
        self.update_filter_button_style('catalog', is_active)
        self.update_filter_status_display()
        
        status = f"[ACTIVE] Filtered by catalog: {catalog}" if is_active else "Catalog filter cleared"
        self.update_status(status)
    
    def filter_by_type(self, obj_type):
        """Filter by object type."""
        if hasattr(self, 'target_selection_gui'):
            self.target_selection_gui.apply_type_filter(obj_type)
        
        # Update visual state - first reset all type buttons
        type_keys = ['galaxies', 'nebulae', 'clusters', 'planetary_nebulae']
        for type_key in type_keys:
            self.update_filter_button_style(f'type_{type_key}', False)
        
        # Activate the selected type button
        type_key = obj_type.lower().replace(" ", "_")
        self.active_filters['type'] = obj_type
        self.update_filter_button_style(f'type_{type_key}', True)
        self.update_filter_status_display()
        
        self.update_status(f"[ACTIVE] Filtered by type: {obj_type}")
    
    def clear_filters(self):
        """Clear all active filters but preserve declination and size input values."""
        if hasattr(self, 'target_selection_gui'):
            self.target_selection_gui.clear_all_filters()
        
        # Reset visual state
        self.reset_all_filter_styles()
        
        # Clear only catalog selection, preserve declination and size values
        self.catalog_var.set("")
        
        self.update_status("[CLEARED] All filters cleared - input values preserved")
    
    def reset_filters(self):
        """Reset all filter values to defaults and clear all active filters."""
        # Reset form values to defaults
        self.min_dec_var.set("-30")
        self.max_dec_var.set("+90")
        self.min_size_var.set("0")
        self.max_size_var.set("999")
        self.catalog_var.set("")
        
        # Clear filters and reset visual state
        if hasattr(self, 'target_selection_gui'):
            self.target_selection_gui.clear_all_filters()
        
        self.reset_all_filter_styles()
        self.update_status("[RESET] All filters and values reset to defaults")
    
    def update_status(self, message):
        """Update status message."""
        self.status_message.config(text=message)
        self.logger.info(f"Status: {message}")
    
    # Navigation methods (adapted from original)
    def check_database_and_navigate(self):
        """Check if database exists and navigate to appropriate screen."""
        # Auto-activate "Now" button to set current time on startup
        self.set_time_now()
        
        if self.db_manager.database_exists():
            self.logger.info("Database exists, navigating to enhanced target selection")
            self.update_status("Database ready - Use controls above to filter and select targets")
            self.show_target_selection()
        else:
            self.logger.info("Database not found, navigating to initialization screen")
            self.update_status("Database not found - Please initialize the database first")
            self.show_database_init()
    
    def show_database_init(self):
        """Show the database initialization screen."""
        self.logger.info("Showing database initialization screen")
        
        if 'db_init' not in self.screens:
            self.screens['db_init'] = DatabaseInitGUI(
                self.content_frame,
                self.db_manager,
                self.on_database_initialized
            )
        
        self._switch_screen('db_init')
        self.update_status("Database Initialization")
    
    def show_target_selection(self):
        """Show the enhanced target selection screen."""
        if not self.db_manager.database_exists():
            messagebox.showwarning(
                "Database Required",
                "Please initialize the database first before selecting targets."
            )
            self.show_database_init()
            return
        
        self.logger.info("Showing enhanced target selection screen")
        
        if 'target_selection' not in self.screens:
            self.screens['target_selection'] = EnhancedTargetSelectionGUI(
                self.content_frame,
                self.db_manager,
                self.observatory,
                self.current_time
            )
            # Store reference for filter methods
            self.target_selection_gui = self.screens['target_selection']
        
        self._switch_screen('target_selection')
        self.update_status("Enhanced Target Selection - Use filtering controls above")
    
    def _switch_screen(self, screen_name: str):
        """Switch to a different screen."""
        # Hide current screen
        if self.current_screen and self.current_screen in self.screens:
            self.screens[self.current_screen].hide()
        
        # Show new screen
        if screen_name in self.screens:
            self.screens[screen_name].show()
            self.current_screen = screen_name
    
    def on_database_initialized(self, success: bool):
        """Callback when database initialization is completed."""
        if success:
            self.logger.info("Database initialization successful")
            messagebox.showinfo(
                "Database Initialized",
                "Database has been successfully initialized!\n"
                "You can now proceed to enhanced target selection."
            )
            self.update_status("Database initialized successfully")
            
            # Clear target selection screen to force reload
            if 'target_selection' in self.screens:
                self.screens['target_selection'].destroy()
                del self.screens['target_selection']
            
            # Navigate to target selection
            self.show_target_selection()
        else:
            self.logger.error("Database initialization failed")
            self.update_status("Database initialization failed")
            messagebox.showerror(
                "Initialization Failed",
                "Database initialization failed. Please check the logs for details."
            )
    
    def load_observatory_config(self):
        """Load observatory configuration from config.ini file."""
        config_path = os.path.join("config", "config.ini")
        
        if not os.path.exists(config_path):
            self.logger.warning(f"Config file not found: {config_path}")
            return
        
        try:
            config = configparser.ConfigParser()
            config.read(config_path)
            
            if 'Observatory' in config:
                obs_config = config['Observatory']
                self.observatory['latitude'] = obs_config.getfloat('latitude', fallback=40.0)
                self.observatory['longitude'] = obs_config.getfloat('longitude', fallback=-75.0)
                self.observatory['elevation'] = obs_config.getfloat('elevation', fallback=100.0)
                self.observatory['timezone'] = obs_config.get('timezone', fallback='EST')
                self.observatory['gmt_offset'] = obs_config.getfloat('gmt_offset', fallback=-5.0)
                self.observatory['dst_active'] = obs_config.getboolean('dst_active', fallback=True)
                
                # Load last address if available
                last_address = obs_config.get('last_address', fallback='')
                if hasattr(self, 'address_var') and last_address:
                    self.address_var.set(last_address)
                
                self.logger.info(f"Loaded observatory config: {self.observatory['latitude']:.4f}, {self.observatory['longitude']:.4f}")
            else:
                self.logger.info("No Observatory section in config, using defaults")
            
            # Load filter settings
            if 'Filters' in config:
                filter_config = config['Filters']
                # Store values to apply after GUI is created
                self.saved_filter_values = {
                    'min_dec': filter_config.get('min_declination', '-30'),
                    'max_dec': filter_config.get('max_declination', '+90'),
                    'min_size': filter_config.get('min_size', '0'),
                    'max_size': filter_config.get('max_size', '999'),
                    'transit_start': filter_config.get('transit_start', '18:00'),
                    'transit_end': filter_config.get('transit_end', '06:00')
                }
                self.logger.info("Loaded saved filter values")
            else:
                self.saved_filter_values = None
                
        except Exception as e:
            self.logger.error(f"Error loading observatory config: {e}")
    
    def save_observatory_config(self):
        """Save observatory configuration to config.ini file."""
        config_path = os.path.join("config", "config.ini")
        
        try:
            config = configparser.ConfigParser()
            
            # Read existing config
            if os.path.exists(config_path):
                config.read(config_path)
            
            # Update Observatory section
            if 'Observatory' not in config:
                config.add_section('Observatory')
            
            obs_config = config['Observatory']
            obs_config['latitude'] = str(self.observatory['latitude'])
            obs_config['longitude'] = str(self.observatory['longitude'])
            obs_config['elevation'] = str(self.observatory['elevation'])
            obs_config['timezone'] = str(self.observatory['timezone'])
            obs_config['gmt_offset'] = str(self.observatory['gmt_offset'])
            obs_config['dst_active'] = str(self.observatory['dst_active']).lower()
            
            # Save last address if available
            if hasattr(self, 'address_var'):
                obs_config['last_address'] = self.address_var.get()
            
            # Save filter settings
            if 'Filters' not in config:
                config.add_section('Filters')
            
            filter_config = config['Filters']
            if hasattr(self, 'min_dec_var'):
                filter_config['min_declination'] = self.min_dec_var.get()
            if hasattr(self, 'max_dec_var'):
                filter_config['max_declination'] = self.max_dec_var.get()
            if hasattr(self, 'min_size_var'):
                filter_config['min_size'] = self.min_size_var.get()
            if hasattr(self, 'max_size_var'):
                filter_config['max_size'] = self.max_size_var.get()
            if hasattr(self, 'transit_start_var'):
                filter_config['transit_start'] = self.transit_start_var.get()
            if hasattr(self, 'transit_end_var'):
                filter_config['transit_end'] = self.transit_end_var.get()
            
            # Write config file
            with open(config_path, 'w') as configfile:
                config.write(configfile)
                
            self.logger.info(f"Saved observatory config and filter values: {self.observatory['latitude']:.4f}, {self.observatory['longitude']:.4f}")
            
        except Exception as e:
            self.logger.error(f"Error saving observatory config: {e}")

    def on_closing(self):
        """Handle application closing event."""
        self.logger.info("Enhanced application closing requested")
        
        result = messagebox.askyesno(
            "Exit NextAstroTarget",
            "Are you sure you want to exit NextAstroTarget?"
        )
        
        if result:
            # Save configuration before closing
            self.save_observatory_config()
            self.logger.info("Enhanced application closing confirmed")
            self.root.quit()
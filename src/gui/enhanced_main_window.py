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

from src.database.database_manager import DatabaseManager
from src.gui.database_init_gui import DatabaseInitGUI
from src.gui.enhanced_target_selection_gui import EnhancedTargetSelectionGUI
from src.utils.astronomical_calculations import AstronomicalCalculator


class EnhancedMainWindow:
    """Enhanced main application window implementing UserInterface.md specifications."""
    
    def __init__(self, root: tk.Tk, db_manager: DatabaseManager):
        self.root = root
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        self.astro_calc = AstronomicalCalculator()
        
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
        self.setup_filtering_section()
        self.setup_object_data_section()
        self.setup_status_section()
    
    def setup_main_container(self):
        """Create main container structure."""
        # Main scrollable frame
        self.main_canvas = tk.Canvas(self.root, bg='#f0f0f0')
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.main_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.main_canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )
        
        self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack main components
        self.main_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Configure grid weights
        self.scrollable_frame.columnconfigure(0, weight=1)
    
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
        """Setup Section 1: Timing and Location controls."""
        # Section 1: Timing and Location
        timing_frame = ttk.LabelFrame(
            self.scrollable_frame,
            text="Section 1: Timing and Location",
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
        
        # Sorting controls
        sort_frame = ttk.Frame(timing_frame)
        sort_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        self.setup_sorting_controls(sort_frame)
    
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
        """Setup observatory location controls."""
        # DST checkbox
        self.dst_var = tk.BooleanVar(value=self.observatory['dst_active'])
        self.dst_check = ttk.Checkbutton(
            parent, text="DST Active", variable=self.dst_var,
            command=self.on_location_changed
        )
        self.dst_check.grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        
        # GMT Offset
        ttk.Label(parent, text="GMT Offset (hrs):").grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        self.gmt_offset_var = tk.StringVar(value=str(self.observatory['gmt_offset']))
        self.gmt_offset_entry = ttk.Entry(parent, textvariable=self.gmt_offset_var, width=8)
        self.gmt_offset_entry.grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.gmt_offset_entry.bind('<KeyRelease>', self.on_location_changed)
        
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
    
    def setup_sorting_controls(self, parent):
        """Setup sorting control buttons."""
        ttk.Button(
            parent, text="Alphabetical Sort",
            command=self.sort_alphabetical,
            style="Sort.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            parent, text="Transit Sort",
            command=self.sort_transit,
            style="Sort.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            parent, text="Top",
            command=self.scroll_to_top,
            style="Sort.TButton"
        ).pack(side=tk.LEFT, padx=5)
    
    def setup_sun_moon_section(self):
        """Setup Section 2 & 3: Sun and Moon data display."""
        astro_frame = ttk.LabelFrame(
            self.scrollable_frame,
            text="Section 2 & 3: Sun and Moon Data",
            style="Section.TLabelframe"
        )
        astro_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)
        astro_frame.columnconfigure(1, weight=1)
        
        # Sun data section
        sun_frame = ttk.Frame(astro_frame)
        sun_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        self.setup_sun_data(sun_frame)
        
        # Moon data section
        moon_frame = ttk.Frame(astro_frame)
        moon_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        self.setup_moon_data(moon_frame)
    
    def setup_sun_data(self, parent):
        """Setup sun data display."""
        ttk.Label(parent, text="Sun Data", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=5)
        
        # Sun position labels
        self.sun_alt_label = ttk.Label(parent, text="Altitude: --°")
        self.sun_alt_label.grid(row=1, column=0, sticky=tk.W, padx=5)
        
        self.sun_az_label = ttk.Label(parent, text="Azimuth: --°")
        self.sun_az_label.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        self.sunset_label = ttk.Label(parent, text="Sunset: --:--")
        self.sunset_label.grid(row=2, column=0, sticky=tk.W, padx=5)
        
        self.sunrise_label = ttk.Label(parent, text="Sunrise: --:--")
        self.sunrise_label.grid(row=2, column=1, sticky=tk.W, padx=5)
        
        self.twilight_label = ttk.Label(parent, text="Nautical Twilight: --:--")
        self.twilight_label.grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=5)
    
    def setup_moon_data(self, parent):
        """Setup moon data display with phase graphic."""
        ttk.Label(parent, text="Moon Data", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=5)
        
        # Moon position labels
        self.moon_alt_label = ttk.Label(parent, text="Altitude: --°")
        self.moon_alt_label.grid(row=1, column=0, sticky=tk.W, padx=5)
        
        self.moon_az_label = ttk.Label(parent, text="Azimuth: --°")
        self.moon_az_label.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        self.moon_phase_label = ttk.Label(parent, text="Phase: --%")
        self.moon_phase_label.grid(row=2, column=0, sticky=tk.W, padx=5)
        
        self.moon_rise_label = ttk.Label(parent, text="Moonrise: --:--")
        self.moon_rise_label.grid(row=2, column=1, sticky=tk.W, padx=5)
        
        # Moon phase canvas for graphic display
        self.moon_canvas = tk.Canvas(parent, width=50, height=50, bg='black')
        self.moon_canvas.grid(row=3, column=0, columnspan=2, pady=5)
    
    def setup_filtering_section(self):
        """Setup Section 4: Filtering buttons."""
        filter_frame = ttk.LabelFrame(
            self.scrollable_frame,
            text="Section 4: Filtering Controls",
            style="Section.TLabelframe"
        )
        filter_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        # Create filter button groups
        self.setup_filter_buttons(filter_frame)
    
    def setup_filter_buttons(self, parent):
        """Setup comprehensive filtering button system."""
        # Declination limits (blue)
        dec_frame = ttk.Frame(parent)
        dec_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=2)
        
        ttk.Label(dec_frame, text="Declination Limits:").pack(side=tk.LEFT)
        
        self.min_dec_var = tk.StringVar(value="-30")
        ttk.Entry(dec_frame, textvariable=self.min_dec_var, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Label(dec_frame, text="to").pack(side=tk.LEFT, padx=2)
        self.max_dec_var = tk.StringVar(value="+90")
        ttk.Entry(dec_frame, textvariable=self.max_dec_var, width=8).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            dec_frame, text="Apply Dec Filter",
            command=self.apply_declination_filter,
            style="Filter.Dec.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        # Size limits (green)
        size_frame = ttk.Frame(parent)
        size_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=5, pady=2)
        
        ttk.Label(size_frame, text="Size Limits (arcmin):").pack(side=tk.LEFT)
        
        self.min_size_var = tk.StringVar(value="0")
        ttk.Entry(size_frame, textvariable=self.min_size_var, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Label(size_frame, text="to").pack(side=tk.LEFT, padx=2)
        self.max_size_var = tk.StringVar(value="999")
        ttk.Entry(size_frame, textvariable=self.max_size_var, width=8).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            size_frame, text="Apply Size Filter",
            command=self.apply_size_filter,
            style="Filter.Size.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        # Best targets (red)
        rating_frame = ttk.Frame(parent)
        rating_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=5, pady=2)
        
        ttk.Label(rating_frame, text="Best Targets:").pack(side=tk.LEFT)
        
        for rating, label in [(5, "Showcase (5)"), (4, "Excellent (4+)"), (3, "Good (3+)")]:
            ttk.Button(
                rating_frame, text=label,
                command=lambda r=rating: self.filter_by_rating(r),
                style="Filter.Rating.TButton"
            ).pack(side=tk.LEFT, padx=2)
        
        # Catalog filters (blue dropdown style)
        catalog_frame = ttk.Frame(parent)
        catalog_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), padx=5, pady=2)
        
        ttk.Label(catalog_frame, text="Catalogs:").pack(side=tk.LEFT)
        
        self.catalog_var = tk.StringVar()
        catalog_combo = ttk.Combobox(
            catalog_frame, textvariable=self.catalog_var,
            values=["All", "Messier", "NGC", "IC", "Caldwell", "Sharpless", "Barnard"],
            width=15, state="readonly"
        )
        catalog_combo.pack(side=tk.LEFT, padx=5)
        catalog_combo.bind('<<ComboboxSelected>>', self.on_catalog_filter_changed)
        
        # Object type filters (brown)
        type_frame = ttk.Frame(parent)
        type_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), padx=5, pady=2)
        
        ttk.Label(type_frame, text="Object Types:").pack(side=tk.LEFT)
        
        for obj_type in ["Galaxies", "Nebulae", "Clusters", "Planetary Nebulae"]:
            ttk.Button(
                type_frame, text=obj_type,
                command=lambda t=obj_type: self.filter_by_type(t),
                style="Filter.Type.TButton"
            ).pack(side=tk.LEFT, padx=2)
        
        # Clear filters (black)
        clear_frame = ttk.Frame(parent)
        clear_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Button(
            clear_frame, text="Clear All Filters",
            command=self.clear_filters,
            style="Filter.Clear.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            clear_frame, text="Reset to Defaults",
            command=self.reset_filters,
            style="Filter.Clear.TButton"
        ).pack(side=tk.LEFT, padx=5)
    
    def setup_object_data_section(self):
        """Setup Section 5: Object data with comprehensive column display."""
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
        
        # Filter buttons with different colors
        style.configure("Filter.Dec.TButton", foreground="blue")
        style.configure("Filter.Size.TButton", foreground="green") 
        style.configure("Filter.Rating.TButton", foreground="red")
        style.configure("Filter.Type.TButton", foreground="brown")
        style.configure("Filter.Clear.TButton", foreground="black", font=("Arial", 9, "bold"))
    
    # Event handlers and functionality methods
    def set_time_now(self):
        """Set time to current time."""
        self.current_time = datetime.now()
        self.update_time_controls()
        self.update_astronomical_data()
    
    def set_time_sunset(self):
        """Set time to sunset today."""
        # Calculate sunset time (simplified)
        sunset_time = self.astro_calc.calculate_sunset(
            self.observatory['latitude'], 
            self.observatory['longitude'],
            datetime.now().date()
        )
        self.current_time = sunset_time
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
    
    def on_location_changed(self, event=None):
        """Handle location parameter changes."""
        try:
            self.observatory['dst_active'] = self.dst_var.get()
            self.observatory['gmt_offset'] = float(self.gmt_offset_var.get())
            self.observatory['latitude'] = float(self.latitude_var.get())
            self.observatory['longitude'] = float(self.longitude_var.get())
            self.update_astronomical_data()
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
        # Update sun data
        sun_alt, sun_az = self.astro_calc.calculate_sun_position(
            self.current_time, self.observatory['latitude'], self.observatory['longitude']
        )
        
        self.sun_alt_label.config(text=f"Altitude: {sun_alt:.1f}°")
        self.sun_az_label.config(text=f"Azimuth: {sun_az:.1f}°")
        
        # Update moon data
        moon_alt, moon_az = self.astro_calc.calculate_moon_position(
            self.current_time, self.observatory['latitude'], self.observatory['longitude']
        )
        moon_phase = self.astro_calc.calculate_moon_phase(self.current_time)
        
        self.moon_alt_label.config(text=f"Altitude: {moon_alt:.1f}°")
        self.moon_az_label.config(text=f"Azimuth: {moon_az:.1f}°")
        self.moon_phase_label.config(text=f"Phase: {moon_phase:.0f}%")
        
        # Update moon phase graphic
        self.draw_moon_phase(moon_phase)
    
    def draw_moon_phase(self, phase_percent):
        """Draw moon phase graphic on canvas."""
        self.moon_canvas.delete("all")
        
        # Draw moon circle
        self.moon_canvas.create_oval(5, 5, 45, 45, fill="white", outline="gray")
        
        # Draw shadow for phase
        if phase_percent < 50:
            # Waxing - shadow on right
            shadow_width = int((50 - phase_percent) / 50 * 40)
            self.moon_canvas.create_arc(
                5, 5, 45, 45, start=270, extent=180,
                fill="black", outline="black"
            )
        else:
            # Waning - shadow on left  
            shadow_width = int((phase_percent - 50) / 50 * 40)
            self.moon_canvas.create_arc(
                5, 5, 45, 45, start=90, extent=180,
                fill="black", outline="black"
            )
    
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
            self.update_status(f"Filtered by declination: {min_dec}° to {max_dec}°")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid declination values")
    
    def apply_size_filter(self):
        """Apply size range filter."""
        try:
            min_size = float(self.min_size_var.get())
            max_size = float(self.max_size_var.get())
            if hasattr(self, 'target_selection_gui'):
                self.target_selection_gui.apply_size_filter(min_size, max_size)
            self.update_status(f"Filtered by size: {min_size}' to {max_size}'")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid size values")
    
    def filter_by_rating(self, min_rating):
        """Filter by minimum rating."""
        if hasattr(self, 'target_selection_gui'):
            self.target_selection_gui.apply_rating_filter(min_rating)
        self.update_status(f"Filtered by rating: {min_rating}+ stars")
    
    def on_catalog_filter_changed(self, event=None):
        """Handle catalog filter selection."""
        catalog = self.catalog_var.get()
        if hasattr(self, 'target_selection_gui'):
            self.target_selection_gui.apply_catalog_filter(catalog)
        self.update_status(f"Filtered by catalog: {catalog}")
    
    def filter_by_type(self, obj_type):
        """Filter by object type."""
        if hasattr(self, 'target_selection_gui'):
            self.target_selection_gui.apply_type_filter(obj_type)
        self.update_status(f"Filtered by type: {obj_type}")
    
    def clear_filters(self):
        """Clear all active filters."""
        if hasattr(self, 'target_selection_gui'):
            self.target_selection_gui.clear_all_filters()
        self.update_status("All filters cleared")
    
    def reset_filters(self):
        """Reset filters to default values."""
        self.min_dec_var.set("-30")
        self.max_dec_var.set("+90")
        self.min_size_var.set("0")
        self.max_size_var.set("999")
        self.catalog_var.set("")
        self.clear_filters()
        self.update_status("Filters reset to defaults")
    
    def update_status(self, message):
        """Update status message."""
        self.status_message.config(text=message)
        self.logger.info(f"Status: {message}")
    
    # Navigation methods (adapted from original)
    def check_database_and_navigate(self):
        """Check if database exists and navigate to appropriate screen."""
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
    
    def on_closing(self):
        """Handle application closing event."""
        self.logger.info("Enhanced application closing requested")
        
        result = messagebox.askyesno(
            "Exit NextAstroTarget",
            "Are you sure you want to exit NextAstroTarget?"
        )
        
        if result:
            self.logger.info("Enhanced application closing confirmed")
            self.root.quit()
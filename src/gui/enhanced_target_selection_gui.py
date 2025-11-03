"""
Enhanced Target Selection GUI for NextAstroTarget application.
Implements comprehensive spreadsheet-like interface per UserInterface.md specifications
with detailed object data columns, real-time calculations, and advanced filtering.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import pandas as pd
import logging
from typing import List, Dict, Any, Optional, Tuple
import threading
import warnings
import requests
from PIL import Image, ImageTk
from io import BytesIO

# Suppress pandas FutureWarnings for cleaner user experience
warnings.filterwarnings('ignore', category=FutureWarning, module='pandas')

from src.database.database_manager import DatabaseManager
from src.utils.astronomical_calculations import AstronomicalCalculator


class AstrobinTooltip:
    """Tooltip that displays Astrobin images when hovering over object names."""
    
    def __init__(self, widget):
        self.widget = widget
        self.tooltip_window = None
        self.current_object = None
        self.logger = logging.getLogger(__name__)
        self.image_cache = {}  # Cache loaded images
        
    def show_tooltip(self, event, object_data, object_name):
        """Show tooltip with Astrobin image and object information."""
        # Debug logging
        self.logger.info(f"AstrobinTooltip.show_tooltip called for {object_name}")
        
        # Avoid showing tooltip for the same object repeatedly
        if self.tooltip_window and self.current_object == object_name:
            return
            
        # Hide existing tooltip
        self.hide_tooltip()
        
        try:
            self.current_object = object_name
            
            # Create tooltip window
            self.tooltip_window = tk.Toplevel(self.widget)
            self.tooltip_window.wm_overrideredirect(True)
            self.tooltip_window.configure(bg='black', bd=2, relief='solid')
            
            # Position near cursor, but ensure it stays on screen
            x = event.x_root + 15
            y = event.y_root - 20
            
            # Get screen dimensions
            screen_width = self.tooltip_window.winfo_screenwidth()
            screen_height = self.tooltip_window.winfo_screenheight()
            
            # Adjust position if needed (account for larger tooltip)
            if x + 400 > screen_width:
                x = event.x_root - 400
            if y + 300 > screen_height:
                y = event.y_root - 300
                
            self.tooltip_window.geometry(f"+{x}+{y}")
            
            # Create main frame
            main_frame = tk.Frame(self.tooltip_window, bg='black', padx=5, pady=5)
            main_frame.pack()
            
            # Object name (header)
            name_label = tk.Label(
                main_frame,
                text=f"🌌 {object_name}",
                font=("Arial", 11, "bold"),
                bg="black",
                fg="white"
            )
            name_label.pack(anchor='w', pady=(0, 5))
            
            # Try to load and display Astrobin image
            astrobin_id = object_data.get('astrobin_id')
            self.logger.info(f"Astrobin ID for {object_name}: {astrobin_id}")
            image_loaded = False
            
            if astrobin_id and pd.notna(astrobin_id):
                try:
                    # Clean the ID
                    astrobin_id_clean = str(int(float(astrobin_id)))
                    self.logger.info(f"Attempting to load image for ID: {astrobin_id_clean}")
                    image_loaded = self._load_astrobin_image(main_frame, astrobin_id_clean, object_name)
                except (ValueError, TypeError):
                    self.logger.debug(f"Invalid Astrobin ID format: {astrobin_id}")
            else:
                self.logger.info(f"No valid Astrobin ID found for {object_name}")
            
            # If no image loaded, show object information
            if not image_loaded:
                self._show_object_info(main_frame, object_data, object_name)
                
        except Exception as e:
            self.logger.warning(f"Error showing Astrobin tooltip: {e}")
            
    def _load_astrobin_image(self, parent_frame, astrobin_id, object_name):
        """Try to load image from Astrobin."""
        self.logger.info(f"_load_astrobin_image called for ID {astrobin_id}")
        try:
            # Check cache first
            cache_key = f"astrobin_{astrobin_id}"
            if cache_key in self.image_cache:
                photo = self.image_cache[cache_key]
                if photo:
                    self.logger.info(f"Using cached image for ID {astrobin_id}")
                    image_label = tk.Label(parent_frame, image=photo, bg='black')
                    image_label.pack(pady=(0, 5))
                    return True
                else:
                    self.logger.info(f"Cached negative result for ID {astrobin_id}")
                    return False
            
            # Try to fetch image from Astrobin
            url = f"https://www.astrobin.com/{astrobin_id}/0/rawthumb/regular/"
            self.logger.info(f"Fetching image from: {url}")
            
            headers = {
                'User-Agent': 'NextAstroTarget/1.1.0 (Astronomy Application)',
                'Accept': 'image/*,*/*;q=0.8'
            }
            
            response = requests.get(url, headers=headers, timeout=5)
            self.logger.info(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                # Load and resize image
                img = Image.open(BytesIO(response.content))
                
                # Resize image to fit tooltip (max 300x250)
                img.thumbnail((300, 250), Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(img)
                
                # Cache the image
                self.image_cache[cache_key] = photo
                
                # Display image
                image_label = tk.Label(parent_frame, image=photo, bg='black')
                image_label.pack(pady=(0, 5))
                
                # Add credit label
                credit_label = tk.Label(
                    parent_frame,
                    text=f"📸 AstroBin ID: {astrobin_id}",
                    font=("Arial", 8),
                    bg="black",
                    fg="gray"
                )
                credit_label.pack(anchor='w')
                
                return True
            else:
                # Cache negative result to avoid repeated requests
                self.image_cache[cache_key] = None
                return False
                
        except Exception as e:
            self.logger.debug(f"Failed to load Astrobin image for ID {astrobin_id}: {e}")
            # Cache negative result
            self.image_cache[f"astrobin_{astrobin_id}"] = None
            return False
    
    def _show_object_info(self, parent_frame, object_data, object_name):
        """Show object information when no image is available."""
        # Create info frame with different background
        info_frame = tk.Frame(parent_frame, bg='navy', padx=8, pady=5)
        info_frame.pack(fill='x')
        
        # Object details
        details = []
        if object_data.get('object_type'):
            details.append(f"Type: {object_data['object_type']}")
        if object_data.get('constellation'):
            details.append(f"Constellation: {object_data['constellation']}")
        if object_data.get('magnitude'):
            details.append(f"Magnitude: {object_data['magnitude']}")
        if object_data.get('size_arcmin'):
            details.append(f"Size: {object_data['size_arcmin']}'")
        if object_data.get('rating'):
            stars = "⭐" * min(int(float(object_data['rating'])), 5)
            details.append(f"Rating: {stars}")
        
        # Display details
        for detail in details[:5]:
            detail_label = tk.Label(
                info_frame,
                text=detail,
                font=("Arial", 9),
                bg="navy",
                fg="white"
            )
            detail_label.pack(anchor='w')
        
        # Nick/Nickname if available
        if object_data.get('nick') and pd.notna(object_data['nick']):
            nick_label = tk.Label(
                info_frame,
                text=f"💫 \"{object_data['nick']}\"",
                font=("Arial", 9, "italic"),
                bg="navy",
                fg="cyan"
            )
            nick_label.pack(anchor='w', pady=(3, 0))
    
    def hide_tooltip(self, event=None):
        """Hide the tooltip."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
            self.current_object = None


class EnhancedTargetSelectionGUI:
    """Enhanced target selection interface with comprehensive object data display."""
    
    def __init__(self, parent_frame: ttk.Frame, db_manager: DatabaseManager, 
                 observatory: Dict[str, Any], current_time: datetime):
        self.parent_frame = parent_frame
        self.db_manager = db_manager
        self.observatory = observatory
        self.current_time = current_time
        self.logger = logging.getLogger(__name__)
        self.astro_calc = AstronomicalCalculator()
        
        # Data management
        self.all_objects = pd.DataFrame()
        self.filtered_objects = pd.DataFrame()
        self.active_filters = {}
        
        # GUI components
        self.main_frame = None
        self.tree = None
        self.scrollbar_v = None
        self.scrollbar_h = None
        self.tooltip = None
        self.tooltip_delay_timer = None
        
        # Search and filter components
        self.search_var = None
        self.search_entry = None
        self.astrobin_filter_var = None
        self.clear_search_btn = None
        self.astrobin_filter_check = None
        self.filter_status_label = None
        
        # Column definitions matching UserInterface.md Sections 5-10
        self.setup_column_definitions()
        
        # Status update callback
        self.update_status_callback = None
        
        # Initialize GUI
        self.setup_gui()
        self.load_objects()
    
    def set_status_callback(self, callback):
        """Set callback function for status updates."""
        self.update_status_callback = callback
    
    def setup_column_definitions(self):
        """Define columns based on available data from the Main table."""
        # Basic object information from available columns
        self.base_columns = [
            ('object_name', 'Object Name', 150),           # From first column
            ('object_type', 'Type', 80),                   # From Unnamed: 3
            ('subtype', 'Subtype', 80),                    # From Unnamed: 4
            ('classification', 'Class', 80),               # From Unnamed: 5
            ('size_arcmin', 'Size (\')', 80),              # From Unnamed: 6
            ('rating', 'Rating', 60),                      # From Unnamed: 9
            ('ra_degrees', 'RA (deg)', 100),               # From Unnamed: 12
            ('dec_degrees', 'Dec (deg)', 100),             # From Unnamed: 14
            ('constellation', 'Const', 80),                # From Unnamed: 15
            ('magnitude', 'Mag', 70),                      # From Unnamed: 19
            ('nick', 'Nick', 120),                         # From Unnamed: 16 (user nicknames)
            ('messier_designation', 'Messier', 70),        # From Unnamed: 37
            ('ngc_designation', 'NGC', 70),                # From Unnamed: 34
            ('ic_designation', 'IC', 70)                   # From Unnamed: 35
        ]
        
        # Calculated columns for real-time astronomy data
        self.calculated_columns = [
            ('alt_now', 'Alt Now', 70),
            ('alt_1hr', 'Alt +1h', 70),
            ('alt_2hr', 'Alt +2h', 70),
            ('alt_3hr', 'Alt +3h', 70),
            ('transit_time', 'Transit Time', 100),
            ('moon_separation', 'Moon Sep (°)', 90)
        ]
        
        # Combine all columns
        self.all_columns = self.base_columns + self.calculated_columns
    
    def setup_gui(self):
        """Setup the enhanced GUI with comprehensive data display."""
        self.main_frame = ttk.Frame(self.parent_frame)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create filtering controls (above the object list)
        self.create_filtering_controls()
        
        # Create treeview with all columns (below the controls)
        self.create_enhanced_treeview()
        
        # Create context menu
        self.create_context_menu()
        
        # Setup automatic updates
        self.start_update_timer()
    
    def create_filtering_controls(self):
        """Create filtering controls above the object list."""
        # Create main controls frame
        controls_frame = ttk.LabelFrame(self.main_frame, text="Search & Filtering Controls", padding=10)
        controls_frame.pack(fill='x', padx=5, pady=5)
        
        # First row: Search box and clear button
        search_row = ttk.Frame(controls_frame)
        search_row.pack(fill='x', pady=(0, 10))
        
        # Search label and entry
        ttk.Label(search_row, text="Search Objects:", font=('Arial', 10, 'bold')).pack(side='left', padx=(0, 10))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        self.search_entry = ttk.Entry(
            search_row,
            textvariable=self.search_var,
            width=30,
            font=('Arial', 10)
        )
        self.search_entry.pack(side='left', padx=(0, 10))
        
        # Add search help label
        help_label = ttk.Label(
            search_row,
            text="💡",
            font=('Arial', 12)
        )
        help_label.pack(side='left', padx=(0, 5))
        
        # Create tooltip for search help
        def show_search_help(event):
            help_text = """Smart Search Tips:
• Exact matches: "M31", "Orion Nebula"
• Partial matches: "neb" finds nebulae
• Abbreviations: "m" finds Messier objects
• Flexible: "m31" matches "M 031"
• Typo-friendly: "gal" finds galaxies"""
            
            # Simple tooltip
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.configure(bg='lightyellow', bd=1, relief='solid')
            
            x = event.x_root + 10
            y = event.y_root - 60
            tooltip.geometry(f"+{x}+{y}")
            
            tk.Label(
                tooltip,
                text=help_text,
                bg='lightyellow',
                font=('Arial', 9),
                justify='left',
                padx=8,
                pady=5
            ).pack()
            
            # Auto-hide after 4 seconds
            tooltip.after(4000, tooltip.destroy)
        
        help_label.bind('<Button-1>', show_search_help)
        
        # Clear search button
        self.clear_search_btn = ttk.Button(
            search_row,
            text="Clear Search",
            command=self.clear_search,
            width=12
        )
        self.clear_search_btn.pack(side='left', padx=(0, 20))
        
        # Astrobin filter checkbox
        self.astrobin_filter_var = tk.BooleanVar()
        self.astrobin_filter_check = ttk.Checkbutton(
            search_row,
            text="Show only objects with Astrobin images",
            variable=self.astrobin_filter_var,
            command=self.on_filter_change
        )
        self.astrobin_filter_check.pack(side='left', padx=(0, 20))
        
        # Status label
        self.filter_status_label = ttk.Label(
            search_row,
            text="All objects shown",
            font=('Arial', 9, 'italic'),
            foreground='gray'
        )
        self.filter_status_label.pack(side='right', padx=(10, 0))
        
        # Second row: Quick filter buttons
        buttons_row = ttk.Frame(controls_frame)
        buttons_row.pack(fill='x')
        
        ttk.Label(buttons_row, text="Quick Filters:", font=('Arial', 10, 'bold')).pack(side='left', padx=(0, 10))
        
        # Quick search buttons for common object types
        quick_searches = [
            ("Messier", "M "),
            ("NGC", "NGC"),
            ("IC", "IC"),
            ("Barnard", "Barnard"),
            ("Abell", "Abell")
        ]
        
        for label, search_term in quick_searches:
            btn = ttk.Button(
                buttons_row,
                text=label,
                command=lambda term=search_term: self.quick_search(term),
                width=10
            )
            btn.pack(side='left', padx=2)
        
        # Clear all button
        ttk.Button(
            buttons_row,
            text="Clear All Filters",
            command=self.clear_all_filters,
            width=15
        ).pack(side='right', padx=(20, 0))
    
    def create_enhanced_treeview(self):
        """Create comprehensive treeview with all specified columns."""
        # Create frame for treeview and scrollbars (below the filtering controls)
        tree_frame = ttk.Frame(self.main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        # Extract column identifiers and display names
        column_ids = [col[0] for col in self.all_columns]
        column_names = [col[1] for col in self.all_columns]
        column_widths = [col[2] for col in self.all_columns]
        
        # Create treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=column_ids,
            show='headings',
            height=20
        )
        
        # Configure columns with centered text alignment
        for i, (col_id, col_name, width) in enumerate(self.all_columns):
            self.tree.heading(col_id, text=col_name, 
                            command=lambda c=col_name: self.sort_by_column(c))
            self.tree.column(col_id, width=width, minwidth=50, anchor='center')
        
        # Create scrollbars
        self.scrollbar_v = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.scrollbar_h = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=self.scrollbar_v.set)
        self.tree.configure(xscrollcommand=self.scrollbar_h.set)
        
        # Pack components
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.scrollbar_v.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.scrollbar_h.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Configure grid weights
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Bind events
        self.tree.bind('<Double-1>', self.on_object_double_click)
        self.tree.bind('<Button-3>', self.show_context_menu)
        
        # Create Astrobin tooltip for object images
        self.tooltip = AstrobinTooltip(self.tree)
        self.tree.bind('<Motion>', self.on_tree_motion)
        self.tree.bind('<Leave>', self.on_tree_leave)
        
        # Status label
        self.status_label = ttk.Label(
            self.main_frame,
            text="Loading objects...",
            font=("Arial", 10)
        )
        self.status_label.pack(pady=5)
    
    def create_context_menu(self):
        """Create right-click context menu."""
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="View Details", command=self.view_object_details)
        self.context_menu.add_command(label="Add to Session", command=self.add_to_session)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Mark as Observed", command=self.mark_observed)
        self.context_menu.add_command(label="Edit Nick", command=self.edit_nick)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Export to CSV", command=self.export_selection)
        self.context_menu.add_command(label="Copy Coordinates", command=self.copy_coordinates)
    
    def load_objects(self):
        """Load all objects from database and calculate real-time data."""
        try:
            self.logger.info("Loading objects from database")
            
            # Load base object data from the Main table
            # Filter out header rows and invalid data
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
                  AND [Imm Deep Sky Compendium -  2023 - 4th Edition] != ''
                  AND [Imm Deep Sky Compendium -  2023 - 4th Edition] NOT LIKE '%Object%'
                  AND [Imm Deep Sky Compendium -  2023 - 4th Edition] NOT LIKE '%Link%'
                  AND [Imm Deep Sky Compendium -  2023 - 4th Edition] NOT LIKE '%Astrobin%'
                  AND [Unnamed: 12] NOT LIKE '%(Deg)%'
                  AND [Unnamed: 14] NOT LIKE '%(Deg)%'
                ORDER BY [Imm Deep Sky Compendium -  2023 - 4th Edition]
            """
            
            self.all_objects = pd.read_sql_query(query, self.db_manager.get_connection())
            
            # Add calculated columns
            self.calculate_real_time_data()
            
            # Apply filters and update display
            if hasattr(self, 'search_var') and self.search_var:
                self.apply_filters()
            else:
                # Fallback for initial load before search controls are created
                self.filtered_objects = self.all_objects.copy()
                self.update_display()
            
            self.logger.info(f"Loaded {len(self.all_objects)} objects")
            
        except Exception as e:
            self.logger.error(f"Error loading objects: {e}")
            messagebox.showerror("Error", f"Failed to load objects: {e}")
    
    def calculate_real_time_data(self):
        """Calculate real-time astronomical data for all objects."""
        if self.all_objects.empty:
            return
        
        try:
            self.logger.info("Calculating real-time astronomical data")
            
            # Initialize calculated columns with proper data types
            for col_id, _, _ in self.calculated_columns:
                if col_id not in self.all_objects.columns:
                    if col_id == 'transit_time':
                        self.all_objects[col_id] = pd.Series(['--:--'] * len(self.all_objects), dtype='object')
                    else:
                        self.all_objects[col_id] = pd.Series([0.0] * len(self.all_objects), dtype='float64')
            
            # Calculate data for each object
            for index, obj in self.all_objects.iterrows():
                try:
                    # Parse coordinates - use the degree columns from the database
                    ra_degrees = obj.get('ra_degrees', 0)
                    dec_degrees = obj.get('dec_degrees', 0)
                    
                    # Convert and validate coordinates
                    try:
                        ra_deg_float = float(ra_degrees) if ra_degrees and str(ra_degrees).strip() != '' else None
                        dec_deg_float = float(dec_degrees) if dec_degrees and str(dec_degrees).strip() != '' else None
                    except (ValueError, TypeError):
                        continue  # Skip objects with invalid coordinates
                    
                    if ra_deg_float is None or dec_deg_float is None:
                        continue
                    
                    # Convert RA degrees to hours
                    ra_hours = ra_deg_float / 15.0  # Convert degrees to hours
                    
                    # Calculate altitude for current time and next 3 hours
                    for i in range(4):
                        col_id = f'alt_{i}hr' if i > 0 else 'alt_now'
                        time_offset = timedelta(hours=i)
                        calc_time = self.current_time + time_offset
                        
                        altitude, _ = self.astro_calc.calculate_altitude_azimuth(
                            ra_hours, dec_deg_float, calc_time,
                            self.observatory['latitude'], self.observatory['longitude']
                        )
                        
                        self.all_objects.at[index, col_id] = round(altitude, 1)
                    
                    # Calculate transit time
                    transit_time = self.astro_calc.calculate_transit_time(
                        ra_hours, self.observatory['longitude'], self.current_time.date()
                    )
                    
                    # Safe string assignment to object dtype column
                    self.all_objects.at[index, 'transit_time'] = transit_time.strftime('%H:%M')
                    
                    # Calculate moon separation
                    moon_sep = self.astro_calc.calculate_moon_separation(
                        ra_hours, dec_deg_float, self.current_time
                    )
                    
                    self.all_objects.at[index, 'moon_separation'] = round(moon_sep, 1)
                    
                except Exception as obj_error:
                    self.logger.warning(f"Error calculating data for {obj.get('object_name', 'unknown')}: {obj_error}")
                    continue
            
            self.logger.info("Real-time calculations completed")
            
        except Exception as e:
            self.logger.error(f"Error in real-time calculations: {e}")
    
    def is_valid_coordinate(self, coord_value) -> bool:
        """Check if coordinate value is valid for calculations."""
        try:
            if pd.isna(coord_value):
                return False
            
            coord_float = float(coord_value)
            return coord_float != 0.0 and abs(coord_float) < 999.0
            
        except (ValueError, TypeError):
            return False
    
    # Search and Filter Methods
    def _apply_fuzzy_search(self, dataframe, search_term):
        """Apply fuzzy search with multiple matching strategies."""
        import re
        
        # Convert search term to lowercase for case-insensitive matching
        search_lower = search_term.lower()
        
        # Create different matching strategies
        matches = []
        
        # Strategy 1: Exact substring match (highest priority)
        exact_mask = (
            dataframe['object_name'].str.contains(search_term, case=False, na=False) |
            dataframe['object_type'].str.contains(search_term, case=False, na=False) |
            dataframe['constellation'].str.contains(search_term, case=False, na=False) |
            dataframe['messier_designation'].str.contains(search_term, case=False, na=False) |
            dataframe['ngc_designation'].str.contains(search_term, case=False, na=False) |
            dataframe['ic_designation'].str.contains(search_term, case=False, na=False) |
            dataframe['nick'].str.contains(search_term, case=False, na=False)
        )
        exact_matches = dataframe[exact_mask].copy()
        exact_matches['match_score'] = 100
        matches.append(exact_matches)
        
        # Strategy 2: Flexible catalog number matching (e.g., "m31" matches "M 031", "M31", "M 31")
        catalog_mask = pd.Series(False, index=dataframe.index)
        
        # Handle catalog patterns like M31, NGC123, IC456
        catalog_pattern = re.match(r'^([a-z]+)\s*(\d+)$', search_lower.strip())
        if catalog_pattern:
            prefix = catalog_pattern.group(1)
            number = catalog_pattern.group(2)
            
            # Create different number formats (with/without leading zeros, with/without spaces)
            number_int = int(number)  # Remove leading zeros
            number_padded = f"{number_int:03d}"  # Add leading zeros to make 3 digits
            
            # Create search patterns
            patterns = [
                f"{prefix}\\s*0*{number_int}\\b",      # M31, M 31, M031
                f"{prefix}\\s+0*{number_int}\\b",      # M 31 (with space)
                f"{prefix}\\s*{number_padded}\\b",     # M031
                f"{prefix}\\s+{number_padded}\\b"      # M 031 (with space)
            ]
            
            for pattern in patterns:
                catalog_mask |= (
                    dataframe['object_name'].str.contains(pattern, case=False, na=False, regex=True) |
                    dataframe['messier_designation'].str.contains(pattern, case=False, na=False, regex=True) |
                    dataframe['ngc_designation'].str.contains(pattern, case=False, na=False, regex=True) |
                    dataframe['ic_designation'].str.contains(pattern, case=False, na=False, regex=True)
                )
        else:
            # Fallback: Remove spaces and special characters for flexible matching
            clean_search = re.sub(r'[^\w]', '', search_lower)
            if len(clean_search) >= 2:
                def matches_cleaned(text):
                    if pd.isna(text):
                        return False
                    clean_text = re.sub(r'[^\w]', '', str(text).lower())
                    return clean_search in clean_text
                
                catalog_mask = (
                    dataframe['object_name'].apply(matches_cleaned) |
                    dataframe['messier_designation'].apply(matches_cleaned) |
                    dataframe['ngc_designation'].apply(matches_cleaned) |
                    dataframe['ic_designation'].apply(matches_cleaned)
                )
        
        # Exclude already found exact matches
        catalog_mask &= ~exact_mask
        if catalog_mask.any():
            catalog_matches = dataframe[catalog_mask].copy()
            catalog_matches['match_score'] = 80
            matches.append(catalog_matches)
        
        # Strategy 3: Partial word matching (e.g., "neb" matches "Nebula")
        if len(search_lower) >= 3:
            partial_words = search_lower.split()
            partial_mask = pd.Series(False, index=dataframe.index)
            
            for word in partial_words:
                if len(word) >= 3:
                    partial_mask |= (
                        dataframe['object_name'].str.contains(word, case=False, na=False) |
                        dataframe['object_type'].str.contains(word, case=False, na=False) |
                        dataframe['constellation'].str.contains(word, case=False, na=False)
                    )
            
            partial_mask &= ~exact_mask & ~(catalog_mask if catalog_mask.any() else False)
            partial_matches = dataframe[partial_mask].copy()
            partial_matches['match_score'] = 60
            matches.append(partial_matches)
        
        # Strategy 4: Number format matching (e.g., "31" matches "M031", "M 031", "NGC31")
        number_mask = pd.Series(False, index=dataframe.index)
        if re.match(r'^\d+$', search_term.strip()):
            number = search_term.strip()
            number_int = int(number)
            number_padded = f"{number_int:03d}"
            
            # Match various number formats in catalogs
            number_patterns = [
                f"\\b0*{number_int}\\b",     # Match the number with optional leading zeros
                f"\\b{number_padded}\\b",    # Match padded version
                f"\\s{number_int}\\b",       # Match after space
                f"\\s{number_padded}\\b"     # Match padded after space
            ]
            
            for pattern in number_patterns:
                number_mask |= (
                    dataframe['object_name'].str.contains(pattern, case=False, na=False, regex=True) |
                    dataframe['messier_designation'].str.contains(pattern, case=False, na=False, regex=True) |
                    dataframe['ngc_designation'].str.contains(pattern, case=False, na=False, regex=True) |
                    dataframe['ic_designation'].str.contains(pattern, case=False, na=False, regex=True)
                )
            
            # Exclude previous matches
            previous_masks_so_far = exact_mask
            if catalog_mask.any():
                previous_masks_so_far |= catalog_mask
            if 'partial_mask' in locals():
                previous_masks_so_far |= partial_mask
                
            number_mask &= ~previous_masks_so_far
            if number_mask.any():
                number_matches = dataframe[number_mask].copy()
                number_matches['match_score'] = 70
                matches.append(number_matches)
        
        # Strategy 5: Fuzzy matching for common typos and abbreviations
        fuzzy_patterns = {
            'messier': ['m', 'mes', 'mess'],
            'ngc': ['new general', 'general'],  
            'nebula': ['neb', 'nebu'],
            'galaxy': ['gal', 'gxy'],
            'cluster': ['cl', 'clus'],
            'planetary': ['plan', 'pn'],
            'andromeda': ['and', 'andro', 'm31'],
            'orion': ['ori'],
            'cygnus': ['cyg', 'swan'],
            'cassiopeia': ['cas', 'cass'],
            'veil': ['vel', 'ngc6960'],
            'rosette': ['rose', 'ngc2237'],
            'horsehead': ['horse', 'b33'],
            'eagle': ['eag', 'm16'],
            'ring': ['m57', 'lyra'],
            'crab': ['m1', 'taurus']
        }
        
        fuzzy_mask = pd.Series(False, index=dataframe.index)
        for full_word, abbreviations in fuzzy_patterns.items():
            if search_lower in abbreviations or any(abbr in search_lower for abbr in abbreviations):
                fuzzy_mask |= (
                    dataframe['object_name'].str.contains(full_word, case=False, na=False) |
                    dataframe['object_type'].str.contains(full_word, case=False, na=False) |
                    dataframe['constellation'].str.contains(full_word, case=False, na=False)
                )
            elif full_word in search_lower:
                for abbr in abbreviations:
                    fuzzy_mask |= (
                        dataframe['object_name'].str.contains(abbr, case=False, na=False) |
                        dataframe['messier_designation'].str.contains(abbr, case=False, na=False)
                    )
        
        # Exclude already found matches
        previous_masks = exact_mask
        if catalog_mask.any():
            previous_masks |= catalog_mask
        if 'partial_mask' in locals():
            previous_masks |= partial_mask
        if 'number_mask' in locals() and number_mask.any():
            previous_masks |= number_mask
        
        fuzzy_mask &= ~previous_masks
        if fuzzy_mask.any():
            fuzzy_matches = dataframe[fuzzy_mask].copy()
            fuzzy_matches['match_score'] = 40
            matches.append(fuzzy_matches)
        
        # Combine all matches and sort by score
        if matches:
            result = pd.concat(matches, ignore_index=True)
            result = result.sort_values(['match_score', 'object_name'], ascending=[False, True])
            result = result.drop('match_score', axis=1)
            return result
        else:
            # No matches found, return empty dataframe with same structure
            return dataframe.iloc[0:0].copy()
    
    def on_search_change(self, *args):
        """Handle search box changes."""
        self.apply_filters()
    
    def on_filter_change(self):
        """Handle filter checkbox changes."""
        self.apply_filters()
    
    def apply_filters(self):
        """Apply search and filter criteria to the object list."""
        try:
            # Start with all objects
            filtered = self.all_objects.copy()
            
            # Apply search filter with fuzzy matching
            search_term = self.search_var.get().strip()
            if search_term:
                filtered = self._apply_fuzzy_search(filtered, search_term)
            
            # Apply Astrobin filter
            if self.astrobin_filter_var.get():
                # Filter to show only objects with valid Astrobin IDs
                astrobin_mask = (
                    pd.notna(filtered['astrobin_id']) & 
                    (filtered['astrobin_id'] != '') &
                    (filtered['astrobin_id'] != 0)
                )
                filtered = filtered[astrobin_mask]
            
            self.filtered_objects = filtered
            self.update_display()
            
            # Update status
            total_count = len(self.all_objects)
            filtered_count = len(filtered)
            if search_term or self.astrobin_filter_var.get():
                status = f"Found {filtered_count} of {total_count} objects"
                if search_term:
                    if filtered_count > 0:
                        status += f" matching '{search_term}'"
                    else:
                        status = f"No matches found for '{search_term}'. Try partial words or abbreviations."
                if self.astrobin_filter_var.get():
                    status += " (with Astrobin images)"
            else:
                status = f"Showing all {total_count} objects"
            
            # Update status in the filter panel
            if hasattr(self, 'filter_status_label') and self.filter_status_label:
                self.filter_status_label.config(text=status)
            
            # Update main status if we have a status callback
            if hasattr(self, 'update_status_callback') and self.update_status_callback:
                self.update_status_callback(status)
            
        except Exception as e:
            self.logger.error(f"Error applying filters: {e}")
    
    def clear_search(self):
        """Clear the search box."""
        self.search_var.set("")
    
    def clear_all_filters(self):
        """Clear all search and filter settings."""
        self.search_var.set("")
        self.astrobin_filter_var.set(False)
        self.apply_filters()
    
    def quick_search(self, search_term):
        """Set search to a predefined term."""
        self.search_var.set(search_term)
    
    def update_display(self):
        """Update the treeview display with current filtered data."""
        try:
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Add filtered objects
            for index, obj in self.filtered_objects.iterrows():
                # Create values list in column order
                values = []
                for col_id, _, _ in self.all_columns:
                    value = obj.get(col_id, '')
                    
                    # Format special value types
                    if col_id == 'transit_time':
                        values.append(str(value) if pd.notna(value) else '--:--')
                    elif col_id.startswith('alt_') or col_id == 'moon_separation':
                        if pd.notna(value) and value != 0:
                            values.append(f"{float(value):.1f}°")
                        else:
                            values.append('--')
                    elif col_id in ['ra_degrees', 'dec_degrees']:
                        if pd.notna(value) and value != 0:
                            values.append(f"{float(value):.2f}")
                        else:
                            values.append('--')
                    elif col_id in ['size_arcmin']:
                        if pd.notna(value) and str(value).strip() != '':
                            values.append(str(value).strip())
                        else:
                            values.append('--')
                    else:
                        if pd.notna(value) and str(value).strip() != '':
                            values.append(str(value).strip())
                        else:
                            values.append('')
                
                # Insert into treeview
                self.tree.insert('', 'end', values=values)
            
            # Update status
            total_objects = len(self.all_objects)
            filtered_objects = len(self.filtered_objects)
            
            if filtered_objects == total_objects:
                status_text = f"Showing all {total_objects} objects"
            else:
                status_text = f"Showing {filtered_objects} of {total_objects} objects (filtered)"
            
            self.status_label.config(text=status_text)
            
        except Exception as e:
            self.logger.error(f"Error updating display: {e}")
    
    def start_update_timer(self):
        """Start timer for periodic real-time updates."""
        def update_worker():
            try:
                # Update every 5 minutes
                threading.Timer(300.0, update_worker).start()
                
                # Recalculate real-time data
                self.calculate_real_time_data()
                
                # Update display on main thread
                self.main_frame.after(0, self.update_display)
                
            except Exception as e:
                self.logger.error(f"Error in update worker: {e}")
        
        # Start the timer
        update_worker()
    
    # Filtering methods
    def apply_declination_filter(self, min_dec: float, max_dec: float):
        """Apply declination range filter."""
        try:
            self.active_filters['declination'] = (min_dec, max_dec)
            self.apply_all_filters()
        except Exception as e:
            self.logger.error(f"Error applying declination filter: {e}")
    
    def apply_size_filter(self, min_size: float, max_size: float):
        """Apply size range filter."""
        try:
            self.active_filters['size'] = (min_size, max_size)
            self.apply_all_filters()
        except Exception as e:
            self.logger.error(f"Error applying size filter: {e}")
    
    def apply_rating_filter(self, min_rating: int):
        """Apply minimum rating filter."""
        try:
            self.active_filters['rating'] = min_rating
            self.apply_all_filters()
        except Exception as e:
            self.logger.error(f"Error applying rating filter: {e}")
    
    def apply_catalog_filter(self, catalog: str):
        """Apply catalog filter."""
        try:
            if catalog and catalog != "All":
                self.active_filters['catalog'] = catalog.lower()
            elif 'catalog' in self.active_filters:
                del self.active_filters['catalog']
            
            self.apply_all_filters()
        except Exception as e:
            self.logger.error(f"Error applying catalog filter: {e}")
    
    def apply_type_filter(self, obj_type: str):
        """Apply object type filter."""
        try:
            self.active_filters['type'] = obj_type
            self.apply_all_filters()
        except Exception as e:
            self.logger.error(f"Error applying type filter: {e}")
    
    def apply_all_filters(self):
        """Apply all active filters to the data."""
        try:
            self.filtered_objects = self.all_objects.copy()
            
            # Apply each active filter
            for filter_name, filter_value in self.active_filters.items():
                if filter_name == 'declination':
                    min_dec, max_dec = filter_value
                    # Filter by declination degrees
                    self.filtered_objects = self.filtered_objects[
                        self.filtered_objects['dec_degrees'].apply(
                            lambda x: self.is_dec_in_range(x, min_dec, max_dec)
                        )
                    ]
                
                elif filter_name == 'size':
                    min_size, max_size = filter_value
                    self.filtered_objects = self.filtered_objects[
                        (pd.to_numeric(self.filtered_objects['size_arcmin'], errors='coerce').fillna(0) >= min_size) &
                        (pd.to_numeric(self.filtered_objects['size_arcmin'], errors='coerce').fillna(999) <= max_size)
                    ]
                
                elif filter_name == 'rating':
                    min_rating = filter_value
                    self.filtered_objects = self.filtered_objects[
                        pd.to_numeric(self.filtered_objects['rating'], errors='coerce').fillna(0) >= min_rating
                    ]
                
                elif filter_name == 'catalog':
                    catalog = filter_value
                    if catalog == 'messier':
                        self.filtered_objects = self.filtered_objects[
                            pd.notna(self.filtered_objects['messier_designation']) & 
                            (self.filtered_objects['messier_designation'] != '')
                        ]
                    elif catalog == 'ngc':
                        self.filtered_objects = self.filtered_objects[
                            pd.notna(self.filtered_objects['ngc_designation']) & 
                            (self.filtered_objects['ngc_designation'] != '')
                        ]
                    elif catalog == 'ic':
                        self.filtered_objects = self.filtered_objects[
                            pd.notna(self.filtered_objects['ic_designation']) & 
                            (self.filtered_objects['ic_designation'] != '')
                        ]
                
                elif filter_name == 'type':
                    obj_type = filter_value
                    
                    if obj_type == 'Galaxies':
                        self.filtered_objects = self.filtered_objects[
                            self.filtered_objects['object_type'] == 'Gal'
                        ]
                    elif obj_type == 'Nebulae':
                        # All nebulae except planetary nebulae
                        self.filtered_objects = self.filtered_objects[
                            (self.filtered_objects['object_type'].isin(['Neb', 'Neb '])) &
                            (~self.filtered_objects['subtype'].isin(['PN', 'PPN']))
                        ]
                    elif obj_type == 'Clusters':
                        self.filtered_objects = self.filtered_objects[
                            self.filtered_objects['object_type'] == 'Stars'
                        ]
                    elif obj_type == 'Planetary Nebulae':
                        # Planetary nebulae are nebulae with specific subtypes
                        self.filtered_objects = self.filtered_objects[
                            (self.filtered_objects['object_type'].isin(['Neb', 'Neb '])) &
                            (self.filtered_objects['subtype'].isin(['PN', 'PPN']))
                        ]
            
            # Update display
            self.update_display()
            
        except Exception as e:
            self.logger.error(f"Error applying filters: {e}")
    
    def is_dec_in_range(self, dec_value, min_dec: float, max_dec: float) -> bool:
        """Check if declination value is in the specified range."""
        try:
            if pd.isna(dec_value):
                return False
            dec_degrees = float(dec_value)
            return min_dec <= dec_degrees <= max_dec
        except (ValueError, TypeError):
            return False
    
    def clear_all_filters(self):
        """Clear all filters and show all objects."""
        try:
            self.active_filters.clear()
            self.filtered_objects = self.all_objects.copy()
            self.update_display()
        except Exception as e:
            self.logger.error(f"Error clearing filters: {e}")
    
    def sort_by_column(self, column_name: str):
        """Sort objects by specified column."""
        try:
            # Find column ID by display name
            col_id = None
            for c_id, c_name, _ in self.all_columns:
                if c_name == column_name:
                    col_id = c_id
                    break
            
            if col_id and col_id in self.filtered_objects.columns:
                # Sort by column (handle numeric vs string)
                if col_id in ['magnitude', 'size_max', 'alt_now', 'max_altitude', 'moon_separation']:
                    self.filtered_objects = self.filtered_objects.sort_values(
                        col_id, key=lambda x: pd.to_numeric(x, errors='coerce').fillna(999)
                    )
                else:
                    self.filtered_objects = self.filtered_objects.sort_values(col_id)
                
                self.update_display()
        
        except Exception as e:
            self.logger.error(f"Error sorting by column {column_name}: {e}")
    
    # Event handlers
    def on_object_double_click(self, event):
        """Handle double-click on object."""
        try:
            selection = self.tree.selection()
            if selection:
                item = self.tree.item(selection[0])
                object_name = item['values'][0]  # First column is object name
                self.view_object_details_by_name(object_name)
        except Exception as e:
            self.logger.error(f"Error handling double-click: {e}")
    
    def show_context_menu(self, event):
        """Show context menu on right-click."""
        try:
            item = self.tree.identify_row(event.y)
            if item:
                self.tree.selection_set(item)
                self.context_menu.post(event.x_root, event.y_root)
        except Exception as e:
            self.logger.error(f"Error showing context menu: {e}")
    
    def view_object_details(self):
        """View detailed information for selected object."""
        try:
            selection = self.tree.selection()
            if selection:
                item = self.tree.item(selection[0])
                object_name = item['values'][0]
                self.view_object_details_by_name(object_name)
        except Exception as e:
            self.logger.error(f"Error viewing object details: {e}")
    
    def view_object_details_by_name(self, object_name: str):
        """Show detailed popup for specific object."""
        try:
            # Find object data
            obj_data = self.filtered_objects[
                self.filtered_objects['object_name'] == object_name
            ]
            
            if obj_data.empty:
                messagebox.showwarning("Not Found", f"Object {object_name} not found")
                return
            
            obj = obj_data.iloc[0]
            
            # Create details window
            details_window = tk.Toplevel(self.main_frame)
            details_window.title(f"Object Details: {object_name}")
            details_window.geometry("600x500")
            
            # Create scrollable text widget
            text_frame = ttk.Frame(details_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            text_widget = tk.Text(text_frame, wrap=tk.WORD, width=70, height=30)
            scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            # Format object information
            details_text = f"Object: {obj.get('object_name', 'Unknown')}\n"
            details_text += f"Common Name: {obj.get('common_name', 'N/A')}\n"
            details_text += f"Type: {obj.get('object_type', 'N/A')}\n"
            details_text += f"Constellation: {obj.get('constellation', 'N/A')}\n\n"
            
            details_text += "Coordinates:\n"
            details_text += f"  RA (2000): {obj.get('ra_2000', 'N/A')}\n"
            details_text += f"  Dec (2000): {obj.get('dec_2000', 'N/A')}\n\n"
            
            details_text += "Physical Properties:\n"
            details_text += f"  Magnitude: {obj.get('magnitude', 'N/A')}\n"
            details_text += f"  Size: {obj.get('size_max', 'N/A')} x {obj.get('size_min', 'N/A')}\n"
            details_text += f"  Surface Brightness: {obj.get('surface_brightness', 'N/A')}\n\n"
            
            details_text += "Current Observing Conditions:\n"
            details_text += f"  Current Altitude: {obj.get('alt_now', 0):.1f}°\n"
            details_text += f"  Transit Time: {obj.get('transit_time', 'N/A')}\n"
            details_text += f"  Max Altitude: {obj.get('max_altitude', 0):.1f}°\n"
            details_text += f"  Moon Separation: {obj.get('moon_separation', 0):.1f}°\n\n"
            
            if obj.get('description'):
                details_text += f"Description:\n{obj.get('description', '')}\n\n"
            
            if obj.get('nick') and pd.notna(obj.get('nick')) and str(obj.get('nick')).strip():
                details_text += f"Nickname:\n\"{obj.get('nick', '')}\"\n\n"
            
            if obj.get('notes') and pd.notna(obj.get('notes')) and str(obj.get('notes')).strip():
                details_text += f"Notes:\n{obj.get('notes', '')}\n"
            
            text_widget.insert(tk.END, details_text)
            text_widget.config(state=tk.DISABLED)
            
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
        except Exception as e:
            self.logger.error(f"Error showing object details: {e}")
            messagebox.showerror("Error", f"Failed to show object details: {e}")
    
    def add_to_session(self):
        """Add selected object to observing session."""
        messagebox.showinfo("Feature Not Implemented", "Session management will be added in a future update.")
    
    def mark_observed(self):
        """Mark selected object as observed."""
        messagebox.showinfo("Feature Not Implemented", "Observation logging will be added in a future update.")
    
    def edit_nick(self):
        """Edit nickname for selected object."""
        messagebox.showinfo("Feature Not Implemented", "Nick editing will be added in a future update.")
    
    def export_selection(self):
        """Export selected objects to CSV."""
        messagebox.showinfo("Feature Not Implemented", "CSV export will be added in a future update.")
    
    def copy_coordinates(self):
        """Copy object coordinates to clipboard."""
        try:
            selection = self.tree.selection()
            if selection:
                item = self.tree.item(selection[0])
                values = item['values']
                
                # Find RA and Dec columns (columns 2 and 3)
                if len(values) >= 4:
                    ra = values[2]
                    dec = values[3]
                    coords = f"RA: {ra}, Dec: {dec}"
                    
                    # Copy to clipboard
                    self.main_frame.clipboard_clear()
                    self.main_frame.clipboard_append(coords)
                    
                    messagebox.showinfo("Copied", f"Coordinates copied to clipboard:\n{coords}")
        except Exception as e:
            self.logger.error(f"Error copying coordinates: {e}")
    
    def on_tree_motion(self, event):
        """Handle mouse motion over tree items."""
        try:
            # Cancel any pending tooltip timer
            if self.tooltip_delay_timer:
                self.main_frame.after_cancel(self.tooltip_delay_timer)
                self.tooltip_delay_timer = None
            
            # Identify item and column under cursor
            item_id = self.tree.identify('item', event.x, event.y)
            column = self.tree.identify('column', event.x, event.y)
            
            # Only show tooltip for Object Name column (first column, column '#1')
            if item_id and column == '#1':
                # Get object data
                item_data = self.tree.item(item_id)
                values = item_data['values']
                
                if values:
                    object_name = values[0]  # First column is object name
                    
                    # Find the object in our data to get Astrobin ID
                    obj_match = self.filtered_objects[
                        self.filtered_objects['object_name'] == object_name
                    ]
                    
                    if not obj_match.empty:
                        # Get object data for tooltip
                        object_data = obj_match.iloc[0].to_dict()
                        
                        # Debug logging
                        self.logger.debug(f"Hovering over {object_name}, Astrobin ID: {object_data.get('astrobin_id')}")
                        
                        # Schedule tooltip with delay to prevent flickering
                        self.tooltip_delay_timer = self.main_frame.after(
                            500,  # Increased delay for debugging
                            lambda odata=object_data, oname=object_name, ev=event: self.tooltip.show_tooltip(ev, odata, oname)
                        )
                    else:
                        # Object not found, hide tooltip
                        self.tooltip.hide_tooltip()
            else:
                # Not over Object Name column, hide tooltip
                self.tooltip.hide_tooltip()
                
        except Exception as e:
            self.logger.warning(f"Error in tree motion handler: {e}")
            # Hide tooltip on error to prevent stale tooltips
            self.tooltip.hide_tooltip()
    
    def on_tree_leave(self, event):
        """Handle mouse leaving the tree."""
        try:
            # Cancel any pending tooltip timer
            if self.tooltip_delay_timer:
                self.main_frame.after_cancel(self.tooltip_delay_timer)
                self.tooltip_delay_timer = None
                
            self.tooltip.hide_tooltip()
        except Exception as e:
            self.logger.warning(f"Error in tree leave handler: {e}")
    
    # Interface management methods
    def show(self):
        """Show this screen."""
        if self.main_frame:
            self.main_frame.pack(fill=tk.BOTH, expand=True)
    
    def hide(self):
        """Hide this screen."""
        if self.main_frame:
            self.main_frame.pack_forget()
    
    def destroy(self):
        """Destroy this screen."""
        if self.main_frame:
            self.main_frame.destroy()
            self.main_frame = None
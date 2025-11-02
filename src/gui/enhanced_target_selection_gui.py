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


class ObjectTooltip:
    """Tooltip that displays object information when hovering over object names."""
    
    def __init__(self, widget):
        self.widget = widget
        self.tooltip_window = None
        self.current_object = None  # Track current hover target
        
    def show_tooltip(self, event, object_data, object_name):
        """Show tooltip with object information."""
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
            self.tooltip_window.configure(bg='lightblue')
            
            # Position near cursor, but ensure it stays on screen
            x = event.x_root + 15
            y = event.y_root - 20
            
            # Get screen dimensions
            screen_width = self.tooltip_window.winfo_screenwidth()
            screen_height = self.tooltip_window.winfo_screenheight()
            
            # Adjust position if needed
            if x + 300 > screen_width:
                x = event.x_root - 300
            if y + 150 > screen_height:
                y = event.y_root - 150
                
            self.tooltip_window.geometry(f"+{x}+{y}")
            
            # Create info frame
            info_frame = tk.Frame(self.tooltip_window, bg='lightblue', padx=10, pady=8)
            info_frame.pack()
            
            # Object name (header)
            name_label = tk.Label(
                info_frame,
                text=f"🌌 {object_name}",
                font=("Arial", 11, "bold"),
                bg="lightblue",
                fg="darkblue"
            )
            name_label.pack(anchor='w')
            
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
            for detail in details[:5]:  # Limit to 5 lines
                detail_label = tk.Label(
                    info_frame,
                    text=detail,
                    font=("Arial", 9),
                    bg="lightblue",
                    fg="black"
                )
                detail_label.pack(anchor='w')
            
            # Nick/Nickname if available
            if object_data.get('nick') and pd.notna(object_data['nick']):
                nick_label = tk.Label(
                    info_frame,
                    text=f"💫 \"{object_data['nick']}\"",
                    font=("Arial", 9, "italic"),
                    bg="lightblue",
                    fg="purple"
                )
                nick_label.pack(anchor='w', pady=(3, 0))
            
        except Exception as e:
            logging.getLogger(__name__).warning(f"Error showing tooltip: {e}")
            
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
        
        # Column definitions matching UserInterface.md Sections 5-10
        self.setup_column_definitions()
        
        # Initialize GUI
        self.setup_gui()
        self.load_objects()
    
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
        
        # Create treeview with all columns
        self.create_enhanced_treeview()
        
        # Create context menu
        self.create_context_menu()
        
        # Setup automatic updates
        self.start_update_timer()
    
    def create_enhanced_treeview(self):
        """Create comprehensive treeview with all specified columns."""
        # Create frame for treeview and scrollbars
        tree_frame = ttk.Frame(self.main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
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
        
        # Configure columns
        for i, (col_id, col_name, width) in enumerate(self.all_columns):
            self.tree.heading(col_id, text=col_name, 
                            command=lambda c=col_name: self.sort_by_column(c))
            self.tree.column(col_id, width=width, minwidth=50)
        
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
        
        # Create tooltip for object information
        self.tooltip = ObjectTooltip(self.tree)
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
            
            # Apply default filters and update display
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
                    type_map = {
                        'Galaxies': ['Galaxy', 'Gx'],
                        'Nebulae': ['Neb', 'HII', 'Emission'],
                        'Clusters': ['Cluster', 'OC', 'GC'],
                        'Planetary Nebulae': ['PN', 'Planetary']
                    }
                    
                    if obj_type in type_map:
                        type_values = type_map[obj_type]
                        self.filtered_objects = self.filtered_objects[
                            self.filtered_objects['object_type'].isin(type_values)
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
            
            if obj.get('nick'):
                details_text += f"Nick:\n{obj.get('nick', '')}\n"
            
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
                        
                        # Schedule tooltip with delay to prevent flickering
                        self.tooltip_delay_timer = self.main_frame.after(
                            300,  # 300ms delay (reduced for better responsiveness)
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
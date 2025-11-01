"""
Target selection GUI for NextAstroTarget application.
Provides interface for searching and selecting astrophotography targets.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
import pandas as pd
from typing import Optional, List, Dict, Any

from src.database.database_manager import DatabaseManager
from src.gui.base_screen import BaseScreen


class TargetSelectionGUI(BaseScreen):
    """GUI for target selection and search."""
    
    def __init__(self, parent_frame: ttk.Frame, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.current_results = pd.DataFrame()
        self.selected_target = None
        
        super().__init__(parent_frame)
        self.load_initial_data()
    
    def setup_gui(self):
        """Set up the target selection GUI."""
        super().setup_gui()
        
        # Create notebook for different views
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        
        # Search tab
        self.search_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.search_frame, text="Search & Select")
        self.setup_search_tab()
        
        # Browse tab
        self.browse_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.browse_frame, text="Browse All")
        self.setup_browse_tab()
        
        # Info tab
        self.info_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.info_frame, text="Database Info")
        self.setup_info_tab()
    
    def setup_search_tab(self):
        """Set up the search and selection tab."""
        # Configure grid
        self.search_frame.columnconfigure(0, weight=1)
        self.search_frame.rowconfigure(1, weight=1)
        
        # Search controls frame
        search_controls = ttk.LabelFrame(self.search_frame, text="Search Filters")
        search_controls.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=20, pady=20)
        search_controls.columnconfigure(1, weight=1)
        search_controls.columnconfigure(3, weight=1)
        
        # Object name search
        ttk.Label(search_controls, text="Object Name:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(search_controls, textvariable=self.name_var, width=20)
        name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        # Object type search
        ttk.Label(search_controls, text="Type:").grid(row=0, column=2, sticky=tk.W, padx=(20, 5))
        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(search_controls, textvariable=self.type_var, width=15)
        self.type_combo.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=5)
        
        # Constellation search
        ttk.Label(search_controls, text="Constellation:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        self.constellation_var = tk.StringVar()
        self.constellation_combo = ttk.Combobox(search_controls, textvariable=self.constellation_var, width=20)
        self.constellation_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=(10, 0))
        
        # Magnitude range
        ttk.Label(search_controls, text="Max Magnitude:").grid(row=1, column=2, sticky=tk.W, padx=(20, 5), pady=(10, 0))
        self.magnitude_var = tk.StringVar()
        magnitude_entry = ttk.Entry(search_controls, textvariable=self.magnitude_var, width=10)
        magnitude_entry.grid(row=1, column=3, sticky=tk.W, padx=5, pady=(10, 0))
        
        # Search buttons
        button_frame = ttk.Frame(search_controls)
        button_frame.grid(row=2, column=0, columnspan=4, pady=(15, 5))
        
        search_button = ttk.Button(button_frame, text="Search", command=self.perform_search)
        search_button.grid(row=0, column=0, padx=(0, 10))
        
        clear_button = ttk.Button(button_frame, text="Clear", command=self.clear_search)
        clear_button.grid(row=0, column=1, padx=10)
        
        random_button = ttk.Button(button_frame, text="Random Target", command=self.get_random_target)
        random_button.grid(row=0, column=2, padx=10)
        
        # Results frame
        results_frame = ttk.LabelFrame(self.search_frame, text="Search Results")
        results_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=20, pady=10)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Results treeview
        columns = ('Name', 'Type', 'Constellation', 'RA', 'Dec', 'Magnitude')
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=15)
        
        # Configure column headings and widths
        column_widths = {'Name': 150, 'Type': 100, 'Constellation': 100, 'RA': 80, 'Dec': 80, 'Magnitude': 80}
        for col in columns:
            self.results_tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            self.results_tree.column(col, width=column_widths.get(col, 100), anchor='center')
        
        # Scrollbars for results
        v_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        h_scrollbar = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.results_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Bind double-click event
        self.results_tree.bind('<Double-1>', self.on_target_selected)
        
        # Target details frame
        details_frame = ttk.LabelFrame(self.search_frame, text="Target Details")
        details_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=10, pady=(5, 10))
        
        self.details_text = tk.Text(details_frame, height=6, wrap=tk.WORD, state='disabled')
        details_scroll = ttk.Scrollbar(details_frame, orient=tk.VERTICAL, command=self.details_text.yview)
        self.details_text.configure(yscrollcommand=details_scroll.set)
        
        self.details_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        details_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
    
    def setup_browse_tab(self):
        """Set up the browse all targets tab."""
        self.browse_frame.columnconfigure(0, weight=1)
        self.browse_frame.rowconfigure(0, weight=1)
        
        # Table selection
        table_frame = ttk.Frame(self.browse_frame)
        table_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=10, pady=10)
        
        ttk.Label(table_frame, text="Select Table:").grid(row=0, column=0, padx=(0, 10))
        
        self.table_var = tk.StringVar()
        self.table_combo = ttk.Combobox(table_frame, textvariable=self.table_var, width=30)
        self.table_combo.grid(row=0, column=1)
        self.table_combo.bind('<<ComboboxSelected>>', self.on_table_selected)
        
        # Browse results
        browse_results_frame = ttk.Frame(self.browse_frame)
        browse_results_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        browse_results_frame.columnconfigure(0, weight=1)
        browse_results_frame.rowconfigure(0, weight=1)
        
        # Browse treeview (will be created dynamically)
        self.browse_tree = None
    
    def setup_info_tab(self):
        """Set up the database information tab."""
        info_container = ttk.Frame(self.info_frame)
        info_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=20, pady=20)
        info_container.columnconfigure(0, weight=1)
        info_container.rowconfigure(1, weight=1)
        
        # Title
        ttk.Label(info_container, text="Database Information", 
                 font=("Arial", 12, "bold")).grid(row=0, column=0, pady=(0, 20))
        
        # Info text
        self.info_text = tk.Text(info_container, wrap=tk.WORD, state='disabled')
        info_scroll = ttk.Scrollbar(info_container, orient=tk.VERTICAL, command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=info_scroll.set)
        
        self.info_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        info_scroll.grid(row=1, column=1, sticky=(tk.N, tk.S))
    
    def load_initial_data(self):
        """Load initial data and populate dropdown options."""
        try:
            # Get table information
            self.table_info = self.db_manager.get_table_info()
            
            # Populate table dropdown
            if hasattr(self, 'table_combo'):
                self.table_combo['values'] = list(self.table_info.keys())
            
            # Load sample data to populate filter options
            self.load_filter_options()
            self.update_info_display()
            
        except Exception as e:
            self.logger.error(f"Error loading initial data: {e}")
            messagebox.showerror("Data Load Error", f"Error loading data: {e}")
    
    def load_filter_options(self):
        """Load options for search filters."""
        try:
            # Get the first available table for filter options
            tables = list(self.table_info.keys())
            if not tables:
                return
            
            # Try to find a main targets table
            main_table = None
            for table in tables:
                if any(keyword in table.lower() for keyword in ['target', 'object', 'deep', 'sky']):
                    main_table = table
                    break
            
            if not main_table:
                main_table = tables[0]
            
            # Load sample data
            query = f"SELECT * FROM {main_table} LIMIT 1000"
            sample_data = self.db_manager.execute_query(query)
            
            if sample_data.empty:
                return
            
            # Populate type options
            type_columns = [col for col in sample_data.columns if 'type' in col.lower()]
            if type_columns:
                types = sample_data[type_columns[0]].dropna().unique()
                self.type_combo['values'] = [''] + sorted(types)
            
            # Populate constellation options
            const_columns = [col for col in sample_data.columns if 'const' in col.lower()]
            if const_columns:
                constellations = sample_data[const_columns[0]].dropna().unique()
                self.constellation_combo['values'] = [''] + sorted(constellations)
            
        except Exception as e:
            self.logger.error(f"Error loading filter options: {e}")
    
    def perform_search(self):
        """Perform search based on current filter values."""
        try:
            # Build search query
            tables = list(self.table_info.keys())
            if not tables:
                messagebox.showwarning("No Data", "No tables found in database")
                return
            
            # Use first table for now (in a real app, you'd want better table selection)
            table = tables[0]
            
            conditions = []
            params = []
            
            # Name search
            if self.name_var.get().strip():
                # Search in multiple possible name columns
                name_conditions = []
                for col in ['name', 'object', 'designation']:
                    name_conditions.append(f"{col} LIKE ?")
                if name_conditions:
                    conditions.append(f"({' OR '.join(name_conditions)})")
                    params.extend([f"%{self.name_var.get().strip()}%"] * len(name_conditions))
            
            # Type filter
            if self.type_var.get().strip():
                type_columns = [col for col in self.get_table_columns(table) if 'type' in col.lower()]
                if type_columns:
                    conditions.append(f"{type_columns[0]} = ?")
                    params.append(self.type_var.get().strip())
            
            # Constellation filter
            if self.constellation_var.get().strip():
                const_columns = [col for col in self.get_table_columns(table) if 'const' in col.lower()]
                if const_columns:
                    conditions.append(f"{const_columns[0]} = ?")
                    params.append(self.constellation_var.get().strip())
            
            # Magnitude filter
            if self.magnitude_var.get().strip():
                try:
                    max_mag = float(self.magnitude_var.get().strip())
                    mag_columns = [col for col in self.get_table_columns(table) if 'mag' in col.lower()]
                    if mag_columns:
                        conditions.append(f"{mag_columns[0]} <= ?")
                        params.append(max_mag)
                except ValueError:
                    messagebox.showwarning("Invalid Input", "Magnitude must be a number")
                    return
            
            # Build final query
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            query = f"SELECT * FROM {table} WHERE {where_clause} LIMIT 1000"
            
            # Execute query
            self.current_results = self.db_manager.execute_query(query, tuple(params))
            self.display_search_results()
            
        except Exception as e:
            self.logger.error(f"Error performing search: {e}")
            messagebox.showerror("Search Error", f"Error performing search: {e}")
    
    def get_table_columns(self, table_name: str) -> List[str]:
        """Get column names for a table."""
        try:
            query = f"PRAGMA table_info({table_name})"
            result = self.db_manager.execute_query(query)
            return result['name'].tolist() if not result.empty else []
        except:
            return []
    
    def display_search_results(self):
        """Display search results in the treeview."""
        # Clear existing results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        if self.current_results.empty:
            messagebox.showinfo("No Results", "No targets found matching your search criteria")
            return
        
        # Map columns to display columns
        display_columns = ['Name', 'Type', 'Constellation', 'RA', 'Dec', 'Magnitude']
        result_columns = self.current_results.columns.tolist()
        
        # Try to map columns intelligently
        column_mapping = self.map_columns_to_display(result_columns, display_columns)
        
        # Insert results
        for idx, row in self.current_results.iterrows():
            values = []
            for display_col in display_columns:
                if display_col in column_mapping:
                    value = row.get(column_mapping[display_col], '')
                    values.append(str(value) if pd.notna(value) else '')
                else:
                    values.append('')
            
            self.results_tree.insert('', 'end', values=values)
        
        # Update status
        count = len(self.current_results)
        messagebox.showinfo("Search Complete", f"Found {count} target(s)")
    
    def map_columns_to_display(self, result_columns: List[str], display_columns: List[str]) -> Dict[str, str]:
        """Map result columns to display columns."""
        mapping = {}
        result_cols_lower = [col.lower() for col in result_columns]
        
        for display_col in display_columns:
            display_lower = display_col.lower()
            
            # Try exact match first
            if display_lower in result_cols_lower:
                mapping[display_col] = result_columns[result_cols_lower.index(display_lower)]
                continue
            
            # Try partial matches
            for i, col_lower in enumerate(result_cols_lower):
                if display_lower in col_lower or col_lower in display_lower:
                    mapping[display_col] = result_columns[i]
                    break
        
        return mapping
    
    def clear_search(self):
        """Clear all search filters."""
        self.name_var.set('')
        self.type_var.set('')
        self.constellation_var.set('')
        self.magnitude_var.set('')
        
        # Clear results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        self.current_results = pd.DataFrame()
    
    def get_random_target(self):
        """Get a random target from the database."""
        try:
            tables = list(self.table_info.keys())
            if not tables:
                messagebox.showwarning("No Data", "No tables found in database")
                return
            
            # Get random target from first table
            table = tables[0]
            query = f"SELECT * FROM {table} ORDER BY RANDOM() LIMIT 1"
            result = self.db_manager.execute_query(query)
            
            if not result.empty:
                self.current_results = result
                self.display_search_results()
                # Auto-select the target
                if self.results_tree.get_children():
                    self.results_tree.selection_set(self.results_tree.get_children()[0])
                    self.on_target_selected()
            
        except Exception as e:
            self.logger.error(f"Error getting random target: {e}")
            messagebox.showerror("Error", f"Error getting random target: {e}")
    
    def on_target_selected(self, event=None):
        """Handle target selection."""
        selection = self.results_tree.selection()
        if not selection:
            return
        
        # Get selected item index
        item = selection[0]
        item_index = self.results_tree.index(item)
        
        if item_index < len(self.current_results):
            self.selected_target = self.current_results.iloc[item_index]
            self.display_target_details()
    
    def display_target_details(self):
        """Display details of the selected target."""
        if self.selected_target is None:
            return
        
        # Format target details
        details = "Selected Target Details:\n\n"
        
        for column, value in self.selected_target.items():
            if pd.notna(value) and str(value).strip():
                details += f"{column}: {value}\n"
        
        # Update details text
        self.details_text.config(state='normal')
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(1.0, details)
        self.details_text.config(state='disabled')
    
    def sort_by_column(self, column: str):
        """Sort results by column."""
        # This is a simplified version - would need more sophisticated sorting
        messagebox.showinfo("Sort", f"Sorting by {column} (feature in development)")
    
    def on_table_selected(self, event=None):
        """Handle table selection in browse tab."""
        table_name = self.table_var.get()
        if not table_name:
            return
        
        try:
            # Load table data
            query = f"SELECT * FROM {table_name} LIMIT 500"  # Limit for performance
            data = self.db_manager.execute_query(query)
            
            if data.empty:
                messagebox.showinfo("No Data", f"No data found in table {table_name}")
                return
            
            # Create/update browse treeview
            self.create_browse_treeview(data)
            
        except Exception as e:
            self.logger.error(f"Error loading table {table_name}: {e}")
            messagebox.showerror("Error", f"Error loading table: {e}")
    
    def create_browse_treeview(self, data: pd.DataFrame):
        """Create treeview for browsing table data."""
        # Remove existing treeview
        if self.browse_tree:
            self.browse_tree.destroy()
        
        # Create new treeview
        browse_container = self.browse_frame.winfo_children()[1]  # Second frame
        
        columns = data.columns.tolist()[:10]  # Limit columns for display
        self.browse_tree = ttk.Treeview(browse_container, columns=columns, show='headings', height=20)
        
        # Configure columns
        for col in columns:
            self.browse_tree.heading(col, text=col)
            self.browse_tree.column(col, width=100)
        
        # Add scrollbars
        v_scroll = ttk.Scrollbar(browse_container, orient=tk.VERTICAL, command=self.browse_tree.yview)
        h_scroll = ttk.Scrollbar(browse_container, orient=tk.HORIZONTAL, command=self.browse_tree.xview)
        self.browse_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # Grid layout
        self.browse_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scroll.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Insert data
        for idx, row in data.iterrows():
            values = [str(row.get(col, '')) if pd.notna(row.get(col, '')) else '' for col in columns]
            self.browse_tree.insert('', 'end', values=values)
    
    def update_info_display(self):
        """Update the database information display."""
        info_text = "Database Information\n" + "="*50 + "\n\n"
        
        if not self.table_info:
            info_text += "No database information available.\n"
        else:
            total_records = sum(info['row_count'] for info in self.table_info.values())
            info_text += f"Total Tables: {len(self.table_info)}\n"
            info_text += f"Total Records: {total_records:,}\n\n"
            
            info_text += "Table Details:\n" + "-"*30 + "\n\n"
            
            for table_name, info in self.table_info.items():
                info_text += f"Table: {table_name}\n"
                info_text += f"  Records: {info['row_count']:,}\n"
                info_text += f"  Columns: {len(info['columns'])}\n"
                
                # Show first few columns
                col_names = [col['name'] for col in info['columns'][:5]]
                if len(info['columns']) > 5:
                    col_names.append(f"... and {len(info['columns']) - 5} more")
                info_text += f"  Fields: {', '.join(col_names)}\n\n"
        
        # Update info text widget
        self.info_text.config(state='normal')
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info_text)
        self.info_text.config(state='disabled')
    
    def show(self):
        """Show this screen and refresh data if needed."""
        super().show()
        
        # Refresh table info if it's empty (database might have been initialized)
        if not self.table_info:
            self.load_initial_data()
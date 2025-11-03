"""
Database initialization and management module for NextAstroTarget application.
Handles reading Excel data and creating/updating SQLite database.
"""

import sqlite3
import pandas as pd
import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import configparser


class DatabaseManager:
    """Manages database operations for the NextAstroTarget application."""
    
    def __init__(self, config_path: str = "config/config.ini"):
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        
        self.db_name = self.config.get('Database', 'db_name', fallback='astro_targets.db')
        self.excel_file = self.config.get('Database', 'excel_file', 
                                        fallback='Imm Deep Sky Compendium - 2023 - rev4g.xlsm')
        self.data_dir = self.config.get('Paths', 'data_dir', fallback='data')
        
        # Ensure data directory exists
        Path(self.data_dir).mkdir(exist_ok=True)
        
        self.db_path = os.path.join(self.data_dir, self.db_name)
        self.logger = logging.getLogger(__name__)
    
    def database_exists(self) -> bool:
        """Check if the database exists and has data."""
        if not os.path.exists(self.db_path):
            return False
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                return len(tables) > 0
        except Exception as e:
            self.logger.error(f"Error checking database existence: {e}")
            return False
    
    def initialize_database(self, progress_callback: Optional[callable] = None) -> bool:
        """
        Initialize the database by reading Excel file and creating tables.
        
        Args:
            progress_callback: Optional callback function for progress updates
            
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            if not os.path.exists(self.excel_file):
                self.logger.error(f"Excel file not found: {self.excel_file}")
                return False
            
            self.logger.info("Starting database initialization...")
            
            # Read Excel file
            if progress_callback:
                progress_callback("Reading Excel file...", 10)
            
            # Read all sheets from Excel file
            excel_data = pd.read_excel(self.excel_file, sheet_name=None, engine='openpyxl')
            
            if progress_callback:
                progress_callback("Creating database tables...", 30)
            
            # Create database connection
            with sqlite3.connect(self.db_path) as conn:
                # Create tables for each sheet
                total_sheets = len(excel_data)
                for i, (sheet_name, df) in enumerate(excel_data.items()):
                    try:
                        self.logger.info(f"Processing sheet '{sheet_name}' with {len(df)} rows and {len(df.columns)} columns")
                        
                        # Skip empty sheets
                        if df.empty:
                            self.logger.warning(f"Skipping empty sheet: {sheet_name}")
                            continue
                        
                        self._create_table_from_dataframe(conn, sheet_name, df)
                        
                        if progress_callback:
                            progress = 30 + int((i + 1) / total_sheets * 60)
                            progress_callback(f"Processing sheet: {sheet_name}", progress)
                    
                    except Exception as e:
                        self.logger.error(f"Error processing sheet '{sheet_name}': {e}")
                        # Continue with other sheets instead of failing completely
                        if progress_callback:
                            progress_callback(f"Error processing sheet {sheet_name}, continuing...", 
                                           30 + int((i + 1) / total_sheets * 60))
                
                # Create indexes for better performance
                if progress_callback:
                    progress_callback("Creating database indexes...", 90)
                
                self._create_indexes(conn)
                
                if progress_callback:
                    progress_callback("Database initialization completed!", 100)
            
            self.logger.info("Database initialization completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during database initialization: {e}")
            if progress_callback:
                progress_callback(f"Error: {str(e)}", 0)
            return False
    
    def _create_table_from_dataframe(self, conn: sqlite3.Connection, 
                                   table_name: str, df: pd.DataFrame):
        """Create a table from pandas DataFrame."""
        # Clean table name
        clean_table_name = self._clean_table_name(table_name)
        
        # Clean column names
        df = self._clean_dataframe_columns(df)
        
        # Drop table if exists
        conn.execute(f"DROP TABLE IF EXISTS {clean_table_name}")
        
        # Create table from DataFrame
        df.to_sql(clean_table_name, conn, index=False, if_exists='replace')
        
        self.logger.info(f"Created table '{clean_table_name}' with {len(df)} records")
    
    def _clean_table_name(self, name: str) -> str:
        """Clean table name to be SQLite compatible."""
        # Replace spaces and special characters with underscores
        cleaned = ''.join(c if c.isalnum() or c == '_' else '_' for c in name)
        # Ensure it starts with a letter or underscore
        if cleaned and not (cleaned[0].isalpha() or cleaned[0] == '_'):
            cleaned = 'table_' + cleaned
        return cleaned or 'unnamed_table'
    
    def _clean_dataframe_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean DataFrame column names to be SQLite compatible."""
        # Create a copy to avoid modifying original
        df = df.copy()
        
        # Clean column names
        new_columns = []
        for col in df.columns:
            # Convert to string and clean
            clean_col = str(col).strip()
            
            # Replace problematic characters with underscores
            clean_col = ''.join(c if c.isalnum() or c == '_' else '_' for c in clean_col)
            
            # Remove multiple consecutive underscores
            while '__' in clean_col:
                clean_col = clean_col.replace('__', '_')
            
            # Remove leading/trailing underscores
            clean_col = clean_col.strip('_')
            
            # Ensure it starts with a letter or underscore
            if clean_col and not (clean_col[0].isalpha() or clean_col[0] == '_'):
                clean_col = 'col_' + clean_col
            
            # Handle empty or invalid names
            if not clean_col or clean_col == '_':
                clean_col = f'column_{len(new_columns)}'
            
            # Handle duplicates
            original_clean = clean_col
            counter = 1
            while clean_col in new_columns:
                clean_col = f"{original_clean}_{counter}"
                counter += 1
            
            new_columns.append(clean_col)
        
        # Rename columns
        df.columns = new_columns
        
        # Remove completely empty rows
        df = df.dropna(how='all')
        
        # Fill NaN values with empty strings for text columns
        df = df.fillna('')
        
        return df
    
    def _create_indexes(self, conn: sqlite3.Connection):
        """Create indexes for better query performance."""
        try:
            # Get all table names
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            self.logger.info(f"Creating indexes for {len(tables)} tables")
            
            # Create common indexes (assuming common column names)
            common_columns = ['name', 'ra', 'dec', 'magnitude', 'type', 'constellation']
            
            for table in tables:
                try:
                    # Get column names for this table
                    cursor.execute(f"PRAGMA table_info([{table}])")
                    columns = [row[1].lower() for row in cursor.fetchall()]
                    
                    self.logger.debug(f"Table {table} has columns: {columns}")
                    
                    # Create indexes for common columns that exist
                    for col in common_columns:
                        # Check if column exists (case-insensitive)
                        matching_cols = [c for c in columns if col in c.lower() or c.lower() in col]
                        
                        for actual_col in matching_cols[:1]:  # Only create one index per pattern
                            try:
                                index_name = f"idx_{table}_{actual_col}".replace(' ', '_').replace('-', '_')
                                # Use brackets to handle special column names
                                conn.execute(f"CREATE INDEX IF NOT EXISTS [{index_name}] ON [{table}]([{actual_col}])")
                                self.logger.debug(f"Created index {index_name}")
                            except Exception as e:
                                self.logger.warning(f"Could not create index for {table}.{actual_col}: {e}")
                
                except Exception as e:
                    self.logger.warning(f"Error processing indexes for table {table}: {e}")
            
        except Exception as e:
            self.logger.warning(f"Error creating indexes: {e}")
    
    def get_table_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all tables in the database."""
        if not self.database_exists():
            return {}
        
        table_info = {}
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get all table names
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row[0] for row in cursor.fetchall()]
                
                for table in tables:
                    # Get row count
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    row_count = cursor.fetchone()[0]
                    
                    # Get column info
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = cursor.fetchall()
                    
                    table_info[table] = {
                        'row_count': row_count,
                        'columns': [{'name': col[1], 'type': col[2]} for col in columns]
                    }
            
        except Exception as e:
            self.logger.error(f"Error getting table info: {e}")
        
        return table_info
    
    def execute_query(self, query: str, params: tuple = ()) -> pd.DataFrame:
        """Execute a SQL query and return results as DataFrame."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                return pd.read_sql_query(query, conn, params=params)
        except Exception as e:
            self.logger.error(f"Error executing query: {e}")
            return pd.DataFrame()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        return sqlite3.connect(self.db_path)
    
    def create_settings_table(self) -> None:
        """Create settings table for persistent application settings."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS app_settings (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL
                    )
                """)
                conn.commit()
                self.logger.info("Settings table created successfully")
        except Exception as e:
            self.logger.error(f"Error creating settings table: {e}")
    
    def save_setting(self, key: str, value: str) -> bool:
        """
        Save a setting to the database.
        
        Args:
            key: Setting key
            value: Setting value (will be converted to string)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO app_settings (key, value)
                    VALUES (?, ?)
                """, (key, str(value)))
                conn.commit()
                return True
        except Exception as e:
            self.logger.error(f"Error saving setting {key}: {e}")
            return False
    
    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get a setting from the database.
        
        Args:
            key: Setting key
            default: Default value if setting not found
            
        Returns:
            Setting value or default
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM app_settings WHERE key = ?", (key,))
                result = cursor.fetchone()
                return result[0] if result else default
        except Exception as e:
            self.logger.error(f"Error getting setting {key}: {e}")
            return default
    
    def delete_setting(self, key: str) -> bool:
        """
        Delete a setting from the database.
        
        Args:
            key: Setting key
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM app_settings WHERE key = ?", (key,))
                conn.commit()
                return True
        except Exception as e:
            self.logger.error(f"Error deleting setting {key}: {e}")
            return False


if __name__ == "__main__":
    # Test the database manager
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from src.utils.logger import setup_logging
    
    setup_logging()
    
    db_manager = DatabaseManager()
    
    if db_manager.database_exists():
        print("Database exists")
        info = db_manager.get_table_info()
        for table, details in info.items():
            print(f"Table: {table}, Rows: {details['row_count']}")
    else:
        print("Database does not exist")
        print("Initializing database...")
        success = db_manager.initialize_database()
        print(f"Initialization {'successful' if success else 'failed'}")
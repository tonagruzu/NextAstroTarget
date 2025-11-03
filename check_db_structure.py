#!/usr/bin/env python3
"""Check database structure"""

import sqlite3
import os

db_path = os.path.join('data', 'astro_targets.db')
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print("Tables:", tables)
    
    if tables:
        # Get columns for first table
        table_name = tables[0]
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"Columns in {table_name}:", columns)
        
        # Get sample row
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
        sample = cursor.fetchone()
        print(f"Sample row:", sample)
    
    conn.close()
else:
    print("Database not found")
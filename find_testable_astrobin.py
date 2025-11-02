#!/usr/bin/env python3

from src.database.database_manager import DatabaseManager
import pandas as pd

def find_objects_with_testable_astrobin():
    """Find objects with Astrobin IDs that we can test."""
    
    db = DatabaseManager()
    if not db.database_exists():
        print("Database not found")
        return
        
    # Query to get objects with Astrobin IDs
    query = """
        SELECT 
            [Imm Deep Sky Compendium -  2023 - 4th Edition] as object_name,
            [Unnamed: 16] as nick,
            [Unnamed: 48] as astrobin_id
        FROM Main 
        WHERE [Imm Deep Sky Compendium -  2023 - 4th Edition] IS NOT NULL
          AND [Imm Deep Sky Compendium -  2023 - 4th Edition] != ''
          AND [Imm Deep Sky Compendium -  2023 - 4th Edition] NOT LIKE '%Object%'
          AND [Imm Deep Sky Compendium -  2023 - 4th Edition] NOT LIKE '%Link%'
          AND [Imm Deep Sky Compendium -  2023 - 4th Edition] NOT LIKE '%Astrobin%'
          AND [Unnamed: 48] IS NOT NULL
        LIMIT 20
    """
    
    df = pd.read_sql_query(query, db.get_connection())
    
    print("Objects with Astrobin IDs that you can test:")
    print("=" * 60)
    print(f"{'Object Name':<25} {'Nick':<20} {'Astrobin ID':<12}")
    print("-" * 60)
    
    valid_count = 0
    for _, row in df.iterrows():
        object_name = row['object_name']
        nick = row['nick'] if pd.notna(row['nick']) else "N/A"
        astrobin_id = row['astrobin_id']
        
        # Check if ID is numeric
        try:
            if pd.notna(astrobin_id):
                clean_id = str(int(float(astrobin_id)))
                print(f"{object_name:<25} {str(nick):<20} {clean_id:<12}")
                valid_count += 1
        except (ValueError, TypeError):
            print(f"{object_name:<25} {str(nick):<20} {str(astrobin_id):<12} (invalid)")
    
    print(f"\nFound {valid_count} objects with valid Astrobin IDs")
    print("\nTo test: Hover your mouse over these object names in the application")
    print("You should see Astrobin images appear as tooltips!")

if __name__ == "__main__":
    find_objects_with_testable_astrobin()
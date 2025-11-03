#!/usr/bin/env python3
"""
Debug coordinate data for DSS loading
"""

import sqlite3
import os

def debug_coordinates():
    """Check what coordinate data we have for the first few objects."""
    
    db_path = os.path.join('data', 'astro_targets.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get sample objects with their coordinate data
    cursor.execute("""
        SELECT 
            [Imm Deep Sky Compendium -  2023 - 4th Edition] as object_name,
            [Unnamed: 12] as ra_degrees,
            [Unnamed: 14] as dec_degrees,
            [Unnamed: 15] as constellation,
            [Unnamed: 48] as astrobin_id
        FROM Main 
        WHERE [Imm Deep Sky Compendium -  2023 - 4th Edition] LIKE 'Abell%'
        ORDER BY [Imm Deep Sky Compendium -  2023 - 4th Edition]
        LIMIT 10
    """)
    
    objects = cursor.fetchall()
    conn.close()
    
    print("🔍 Coordinate Data for First 10 Abell Objects:")
    print("-" * 80)
    
    for obj_name, ra_deg, dec_deg, constellation, astrobin_id in objects:
        print(f"Object: {obj_name}")
        print(f"  RA: {ra_deg} (type: {type(ra_deg)})")
        print(f"  Dec: {dec_deg} (type: {type(dec_deg)})")
        print(f"  Constellation: {constellation}")
        print(f"  Astrobin ID: {astrobin_id}")
        
        # Try to convert coordinates
        try:
            if ra_deg is not None and dec_deg is not None:
                ra_float = float(ra_deg)
                dec_float = float(dec_deg)
                print(f"  ✅ Valid coordinates: RA={ra_float:.3f}°, Dec={dec_float:.3f}°")
            else:
                print(f"  ❌ Missing coordinates")
        except (ValueError, TypeError) as e:
            print(f"  ❌ Invalid coordinates: {e}")
        
        print()

if __name__ == "__main__":
    debug_coordinates()

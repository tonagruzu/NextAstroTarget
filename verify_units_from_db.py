import sqlite3
import pandas as pd

conn = sqlite3.connect('data/astro_targets.db')

# Test a variety of object types
query = """
    SELECT 
        [Imm Deep Sky Compendium -  2023 - 4th Edition] as object_name,
        [Unnamed: 3] as object_type,
        [Unnamed: 7] as distance, 
        [Unnamed: 8] as diameter
    FROM Main 
    WHERE [Imm Deep Sky Compendium -  2023 - 4th Edition] IN (
        'M 001', 'M 031', 'M 042', 'M 051', 'M 081', 'M 082',
        'IC 1805', 'NGC 7635', 'NGC 7000', 'NGC 6960'
    )
    ORDER BY [Unnamed: 3], [Imm Deep Sky Compendium -  2023 - 4th Edition]
"""

df = pd.read_sql_query(query, conn)

def format_with_units(distance, diameter, obj_type):
    """Format distance and diameter with proper units"""
    is_galaxy = obj_type and str(obj_type).strip().lower() == 'gal'
    result = []
    
    distance_str = str(distance).strip().lower()
    if distance and distance_str and distance_str not in ['nan', 'none', '']:
        if distance_str == 'u':
            result.append("Distance: Unknown")
        else:
            try:
                dist_val = float(distance)
                if is_galaxy:
                    result.append(f"Distance: {dist_val:,.2f} Mly")
                else:
                    result.append(f"Distance: {dist_val:,.0f} ly")
            except (ValueError, TypeError):
                pass
    
    diameter_str = str(diameter).strip().lower()
    if diameter and diameter_str and diameter_str not in ['nan', 'none', '', 'u']:
        try:
            diam_val = float(diameter)
            if is_galaxy:
                result.append(f"Physical Size: {diam_val:,.1f} kly")
            else:
                result.append(f"Physical Size: {diam_val:,.1f} ly")
        except (ValueError, TypeError):
            pass
    
    return result

print("Database Objects with Proper Units:")
print("=" * 80)

for idx, row in df.iterrows():
    obj_type = row['object_type']
    is_gal = obj_type and str(obj_type).strip().lower() == 'gal'
    type_label = "GALAXY" if is_gal else "NEBULA"
    
    print(f"\n{row['object_name']} ({type_label})")
    formatted = format_with_units(row['distance'], row['diameter'], obj_type)
    for line in formatted:
        print(f"  {line}")

conn.close()

print("\n" + "=" * 80)
print("✓ Galaxies show distance in Mly and size in kly")
print("✓ Nebulae show distance in ly and size in ly")

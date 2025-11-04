import sqlite3
import pandas as pd

conn = sqlite3.connect('data/astro_targets.db')

# Test a few objects to see distance and diameter values
query = """
    SELECT 
        [Imm Deep Sky Compendium -  2023 - 4th Edition] as object_name,
        [Unnamed: 3] as object_type,
        [Unnamed: 7] as distance, 
        [Unnamed: 8] as diameter,
        [Quick Start Guide] as notes
    FROM Main 
    WHERE [Imm Deep Sky Compendium -  2023 - 4th Edition] IN (
        'M 001', 'M 031', 'M 042', 'M 051', 
        'IC 1805', 'NGC 7635', 
        'NGC 7000', 'NGC 281'
    )
    ORDER BY [Imm Deep Sky Compendium -  2023 - 4th Edition]
"""

df = pd.read_sql_query(query, conn)

print("Sample objects with Distance and Diameter:")
print("=" * 80)
for idx, row in df.iterrows():
    print(f"\nObject: {row['object_name']}")
    print(f"  Type: {row['object_type']}")
    print(f"  Distance: {row['distance']}")
    print(f"  Diameter: {row['diameter']}")
    if pd.notna(row['notes']) and str(row['notes']).strip():
        print(f"  Notes: {row['notes'][:60]}...")
    else:
        print(f"  Notes: (none)")

conn.close()

print("\n" + "=" * 80)
print("These values should now appear in the Object Card's Notes section!")

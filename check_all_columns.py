import pandas as pd
import sqlite3

# Check what we have in the database
conn = sqlite3.connect('data/astro_targets.db')
query = "SELECT * FROM Main WHERE [Imm Deep Sky Compendium -  2023 - 4th Edition] LIKE 'M%' LIMIT 1"
df = pd.read_sql_query(query, conn)

print("Available columns in database:")
for i, col in enumerate(df.columns):
    val = df.iloc[0, i]
    if pd.notna(val):
        print(f"{i:2d}: {col:50s} = {val}")

conn.close()

# Now check Excel to find Distance/Diameter
print("\n\nChecking Excel file structure:")
df_excel = pd.read_excel('Imm Deep Sky Compendium - 2023 - rev4g.xlsm', sheet_name='Main', header=None, skiprows=2, nrows=5)

# Look for columns that might be distance or diameter
for col_idx in range(len(df_excel.columns)):
    sample_values = []
    for row_idx in range(min(5, len(df_excel))):
        val = df_excel.iloc[row_idx, col_idx]
        if pd.notna(val):
            sample_values.append(str(val)[:50])
    if sample_values:
        # Check if values look like distance/diameter (numeric, reasonable range)
        print(f"\nColumn {col_idx}:")
        for val in sample_values[:3]:
            print(f"  {val}")

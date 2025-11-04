import sqlite3
import pandas as pd

conn = sqlite3.connect('data/astro_targets.db')
df = pd.read_sql_query("""
    SELECT 
        [Imm Deep Sky Compendium -  2023 - 4th Edition] as name, 
        [Unnamed: 7] as distance, 
        [Unnamed: 8] as diameter 
    FROM Main 
    WHERE [Imm Deep Sky Compendium -  2023 - 4th Edition] IN ('M 001', 'M 031', 'M 042', 'M 051')
""", conn)
print(df.to_string(index=False))
conn.close()

import sqlite3
import pandas as pd

conn = sqlite3.connect('data/astro_targets.db')
df = pd.read_sql_query('SELECT * FROM Main WHERE [Unnamed: 1] IS NOT NULL LIMIT 1', conn)

print("Column indices and values:")
for i, col in enumerate(df.columns):
    val = df.iloc[0, i]
    if pd.notna(val):
        print(f'{i}: {col} = {val}')

conn.close()

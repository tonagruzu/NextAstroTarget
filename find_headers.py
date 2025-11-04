import pandas as pd

# Read Excel file - first row might contain the actual header
df = pd.read_excel('Imm Deep Sky Compendium - 2023 - rev4g.xlsm', sheet_name='Main', header=None, nrows=3)

print('First 3 rows (to find headers):')
for i in range(len(df)):
    print(f'\nRow {i}:')
    for col_idx in range(min(60, len(df.columns))):
        val = df.iloc[i, col_idx]
        if pd.notna(val) and str(val).strip() and 'Unnamed' not in str(val):
            print(f'  Col {col_idx}: {val}')

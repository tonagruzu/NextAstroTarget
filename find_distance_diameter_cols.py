import pandas as pd

# Read Excel file headers
df = pd.read_excel('Imm Deep Sky Compendium - 2023 - rev4g.xlsm', sheet_name='Main', nrows=5)

print('Column headers:')
for i, col in enumerate(df.columns):
    print(f'{i}: {col}')

print('\n\nSample row (first object):')
df_sample = pd.read_excel('Imm Deep Sky Compendium - 2023 - rev4g.xlsm', sheet_name='Main', skiprows=2, nrows=1)
for i, col in enumerate(df_sample.columns):
    val = df_sample.iloc[0, i]
    if pd.notna(val) and str(val).strip():
        print(f'{i}: {col} = {val}')

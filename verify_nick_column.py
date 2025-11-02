#!/usr/bin/env python3

from src.database.database_manager import DatabaseManager
import pandas as pd

def main():
    db = DatabaseManager()
    if db.database_exists():
        # Look for objects with nicknames in column 16
        query = '''
            SELECT 
                [Imm Deep Sky Compendium -  2023 - 4th Edition] as object_name,
                [Unnamed: 16] as nick
            FROM Main 
            WHERE [Imm Deep Sky Compendium -  2023 - 4th Edition] IS NOT NULL
              AND [Imm Deep Sky Compendium -  2023 - 4th Edition] != ''
              AND [Imm Deep Sky Compendium -  2023 - 4th Edition] NOT LIKE '%Object%'
              AND [Imm Deep Sky Compendium -  2023 - 4th Edition] NOT LIKE '%Link%'
              AND [Imm Deep Sky Compendium -  2023 - 4th Edition] NOT LIKE '%Astrobin%'
              AND [Unnamed: 12] NOT LIKE '%(Deg)%'
              AND [Unnamed: 14] NOT LIKE '%(Deg)%'
              AND [Unnamed: 16] IS NOT NULL
              AND [Unnamed: 16] != ''
            LIMIT 30
        '''
        
        df = pd.read_sql_query(query, db.get_connection())
        print(f'Objects with nicknames ({len(df)} found):')
        print('=' * 60)
        
        for _, row in df.iterrows():
            print(f'{row["object_name"]}: {row["nick"]}')

if __name__ == "__main__":
    main()
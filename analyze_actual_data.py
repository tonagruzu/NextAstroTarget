#!/usr/bin/env python3

import pandas as pd
import os

def analyze_actual_data():
    """Analyze actual data to understand Astrobin structure."""
    
    excel_file = "Imm Deep Sky Compendium - 2023 - rev4g.xlsm"
    
    if not os.path.exists(excel_file):
        print(f"Excel file not found: {excel_file}")
        return
    
    try:
        # Read the Excel file  
        df = pd.read_excel(excel_file, sheet_name='Main', engine='openpyxl')
        
        print("Analyzing Actual Excel Data for Images:")
        print("=" * 80)
        
        # Look at rows that have actual object names (not header rows)
        actual_objects = []
        for i in range(len(df)):
            obj_name = df.iloc[i, 0]  # First column
            if pd.notna(obj_name) and isinstance(obj_name, str):
                # Skip header-like entries
                if not any(keyword in str(obj_name).lower() for keyword in 
                          ['object', 'link', 'astrobin', 'data', 'imm deep sky']):
                    actual_objects.append(i)
            if len(actual_objects) >= 50:  # Limit for analysis
                break
        
        print(f"Found {len(actual_objects)} actual object rows to analyze")
        
        # Check each object row
        objects_with_col48_data = []
        objects_with_url_parts = []
        
        for row_idx in actual_objects:
            row = df.iloc[row_idx]
            obj_name = row.iloc[0]
            
            # Check column 48 for numeric data
            col48 = row.iloc[48] if pd.notna(row.iloc[48]) else None
            if col48 is not None:
                try:
                    # Try to convert to a number
                    if isinstance(col48, (int, float)):
                        # Check if it's a reasonable Astrobin ID (whole number, reasonable range)
                        if isinstance(col48, float):
                            if col48 == int(col48):  # It's a whole number stored as float
                                col48 = int(col48)
                            else:
                                col48 = None  # Not a whole number, probably not an ID
                        
                        if isinstance(col48, int) and 1 <= col48 <= 9999999:
                            objects_with_col48_data.append((obj_name, col48))
                    elif isinstance(col48, str):
                        try:
                            num_val = int(float(col48))
                            if 1 <= num_val <= 9999999:
                                objects_with_col48_data.append((obj_name, num_val))
                        except:
                            pass
                except:
                    pass
            
            # Check for URL parts in columns 45-47
            col45 = row.iloc[45] if pd.notna(row.iloc[45]) else None
            col46 = row.iloc[46] if pd.notna(row.iloc[46]) else None
            col47 = row.iloc[47] if pd.notna(row.iloc[47]) else None
            
            if col45 or col46 or col47:
                objects_with_url_parts.append((obj_name, col45, col46, col47))
        
        print(f"\nObjects with potential Astrobin IDs in column 48: {len(objects_with_col48_data)}")
        print("Sample objects with Astrobin IDs:")
        for obj_name, astrobin_id in objects_with_col48_data[:10]:
            print(f"  {obj_name}: {astrobin_id}")
        
        print(f"\nObjects with URL parts in columns 45-47: {len(objects_with_url_parts)}")
        print("Sample objects with URL parts:")
        for obj_name, col45, col46, col47 in objects_with_url_parts[:10]:
            print(f"  {obj_name}:")
            if col45: print(f"    Col 45: {col45}")
            if col46: print(f"    Col 46: {col46}")  
            if col47: print(f"    Col 47: {col47}")
        
        # Now check our current database to see what we're actually loading
        print(f"\n" + "="*80)
        print("Checking what our current database contains:")
        
        from src.database.database_manager import DatabaseManager
        
        db = DatabaseManager()
        if db.database_exists():
            query = '''
                SELECT 
                    [Imm Deep Sky Compendium -  2023 - 4th Edition] as object_name,
                    [Unnamed: 48] as col48_raw,
                    [Unnamed: 45] as col45,
                    [Unnamed: 46] as col46,
                    [Unnamed: 47] as col47
                FROM Main 
                WHERE [Imm Deep Sky Compendium -  2023 - 4th Edition] IS NOT NULL
                  AND [Imm Deep Sky Compendium -  2023 - 4th Edition] != ''
                  AND [Imm Deep Sky Compendium -  2023 - 4th Edition] NOT LIKE '%Object%'
                LIMIT 20
            '''
            
            df_db = pd.read_sql_query(query, db.get_connection())
            
            print(f"Database query returned {len(df_db)} rows")
            print("\nSample database content:")
            
            for _, row in df_db.iterrows():
                obj_name = row['object_name']
                col48 = row['col48_raw']
                
                print(f"\n{obj_name}:")
                print(f"  Col 48 raw: {col48} (type: {type(col48)})")
                
                # Try to process as current code does
                if pd.notna(col48):
                    try:
                        astrobin_id_clean = str(int(float(col48)))
                        print(f"  Processed as: {astrobin_id_clean}")
                        
                        # Check if this is a reasonable Astrobin ID
                        if 1 <= int(astrobin_id_clean) <= 9999999:
                            print(f"  ✓ Valid Astrobin ID range")
                        else:
                            print(f"  ✗ Outside valid Astrobin ID range")
                    except:
                        print(f"  ✗ Cannot convert to Astrobin ID")
                else:
                    print(f"  ✗ No data in col 48")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_actual_data()
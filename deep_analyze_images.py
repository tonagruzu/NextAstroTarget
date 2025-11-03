#!/usr/bin/env python3

import pandas as pd
import os

def deep_analyze_image_structure():
    """Deep dive into the Excel structure to understand image URL construction."""
    
    excel_file = "Imm Deep Sky Compendium - 2023 - rev4g.xlsm"
    
    if not os.path.exists(excel_file):
        print(f"Excel file not found: {excel_file}")
        return
    
    try:
        # Read the Excel file
        df = pd.read_excel(excel_file, sheet_name='Main', engine='openpyxl')
        
        print("Deep Analysis of Image URL Structure:")
        print("=" * 80)
        
        # Focus on rows that have values in columns 45-48
        print("Analyzing rows with data in columns 45-48:")
        
        for i in range(min(20, len(df))):
            row = df.iloc[i]
            object_name = row.iloc[0]  # First column is object name
            
            # Check columns 45-48
            col45 = row.iloc[45] if pd.notna(row.iloc[45]) else None
            col46 = row.iloc[46] if pd.notna(row.iloc[46]) else None
            col47 = row.iloc[47] if pd.notna(row.iloc[47]) else None
            col48 = row.iloc[48] if pd.notna(row.iloc[48]) else None
            
            if any([col45, col46, col47, col48]):
                print(f"\nRow {i}: {object_name}")
                if col45: print(f"  Col 45: {col45}")
                if col46: print(f"  Col 46: {col46}")
                if col47: print(f"  Col 47: {col47}")
                if col48: print(f"  Col 48: {col48}")
                
                # Try to construct URL
                if col45 and col46 and isinstance(col45, str) and isinstance(col46, str):
                    if 'http' in col45:
                        constructed_url = f"{col45}{object_name.replace(' ', '+')}{col46}"
                        print(f"  Constructed URL: {constructed_url}")
        
        # Look for other patterns
        print(f"\n" + "="*80)
        print("Looking for alternative image URL patterns:")
        
        # Check if there are complete URLs in any single column
        for col_idx in range(len(df.columns)):
            col_data = df.iloc[:, col_idx]
            urls_found = 0
            astrobin_urls = 0
            
            for val in col_data:
                if pd.notna(val) and isinstance(val, str):
                    if 'astrobin.com' in val.lower():
                        astrobin_urls += 1
                        if astrobin_urls <= 3:
                            print(f"  Found Astrobin URL in column {col_idx}: {val}")
                    elif 'http' in val and len(val) > 20:
                        urls_found += 1
            
            if urls_found > 5 or astrobin_urls > 0:
                print(f"  Column {col_idx}: {urls_found} URLs, {astrobin_urls} Astrobin URLs")
        
        # Check if the image data is structured differently
        print(f"\n" + "="*80)
        print("Checking for embedded image data or alternative formats:")
        
        # Look at the pattern in column 47 and 48
        print("\nAnalyzing column 47 patterns (might be link type indicators):")
        col47_values = df.iloc[:, 47].dropna().value_counts()
        print(col47_values.head(10))
        
        print("\nAnalyzing column 48 data types:")
        col48_data = df.iloc[:, 48].dropna()
        
        # Separate numeric from text
        numeric_ids = []
        text_values = []
        
        for val in col48_data:
            try:
                numeric_val = float(val)
                if numeric_val == int(numeric_val):  # It's a whole number
                    numeric_ids.append(int(numeric_val))
                else:
                    numeric_ids.append(numeric_val)
            except:
                text_values.append(val)
        
        print(f"Numeric values in col 48: {len(numeric_ids)}")
        print(f"Text values in col 48: {len(text_values)}")
        print(f"Sample numeric IDs: {numeric_ids[:10] if numeric_ids else 'None'}")
        print(f"Sample text values: {text_values[:10] if text_values else 'None'}")
        
        # Check if numeric IDs are valid Astrobin IDs (typically 1-7 digits)
        valid_astrobin_ids = []
        for num_id in numeric_ids:
            if isinstance(num_id, int) and 1 <= num_id <= 9999999:  # Reasonable Astrobin ID range
                valid_astrobin_ids.append(num_id)
        
        print(f"Potentially valid Astrobin IDs: {len(valid_astrobin_ids)}")
        print(f"Sample valid IDs: {valid_astrobin_ids[:10] if valid_astrobin_ids else 'None'}")
        
        # Test a few URLs
        print(f"\n" + "="*80)
        print("Testing Astrobin URL patterns with sample IDs:")
        
        test_ids = valid_astrobin_ids[:5] if valid_astrobin_ids else [349, 1, 2]  # fallback test IDs
        
        for test_id in test_ids:
            print(f"\nTesting ID {test_id}:")
            
            # Different URL patterns to try
            urls_to_test = [
                f"https://www.astrobin.com/{test_id}/0/rawthumb/regular/",
                f"https://cdn.astrobin.com/thumbs/{test_id}_1824x0_q100_watermark.jpg",
                f"https://www.astrobin.com/{test_id}/thumb/",
                f"https://www.astrobin.com/{test_id}/rawthumb/gallery/",
            ]
            
            for url in urls_to_test:
                print(f"  {url}")
                
                # Note: We won't actually test these URLs in this analysis script
                # This is just to show what patterns we should try
        
    except Exception as e:
        print(f"Error reading Excel file: {e}")

if __name__ == "__main__":
    deep_analyze_image_structure()
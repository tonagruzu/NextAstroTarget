#!/usr/bin/env python3

import pandas as pd
import os

def analyze_astrobin_data():
    """Analyze the original Excel file to find all image-related data."""
    
    excel_file = "Imm Deep Sky Compendium - 2023 - rev4g.xlsm"
    
    if not os.path.exists(excel_file):
        print(f"Excel file not found: {excel_file}")
        return
    
    try:
        # Read the Excel file
        df = pd.read_excel(excel_file, sheet_name='Main', engine='openpyxl')
        
        print("Analyzing Excel file for Astrobin/Image data:")
        print("=" * 80)
        
        # Get column names
        print(f"\nTotal columns: {len(df.columns)}")
        
        # Look for columns that might contain image data
        image_related_columns = []
        for i, col in enumerate(df.columns):
            col_str = str(col).lower()
            if any(keyword in col_str for keyword in ['astro', 'bin', 'image', 'photo', 'link', 'url', 'http']):
                image_related_columns.append((i, col))
        
        print(f"\nColumns that might contain image data:")
        for i, col in image_related_columns:
            print(f"  Column {i}: {col}")
        
        # Check specific columns around Unnamed: 48 
        print(f"\nColumns around Unnamed: 48:")
        for i in range(45, 52):
            if i < len(df.columns):
                col_name = df.columns[i]
                print(f"  Column {i}: {col_name}")
                
                # Show sample non-empty values
                sample_values = []
                for val in df.iloc[:, i]:
                    if pd.notna(val) and str(val).strip() and str(val) not in ['nan', '']:
                        sample_values.append(str(val))
                        if len(sample_values) >= 3:
                            break
                            
                if sample_values:
                    print(f"    Sample values: {sample_values}")
                else:
                    print(f"    (Empty or all NaN)")
        
        # Look for HTTP/URL patterns in all columns
        print(f"\nSearching for HTTP/URL patterns in all columns:")
        url_columns = []
        
        for i, col in enumerate(df.columns):
            # Check for URLs in this column
            url_count = 0
            sample_urls = []
            
            for val in df.iloc[:, i]:
                if pd.notna(val) and 'http' in str(val).lower():
                    url_count += 1
                    if len(sample_urls) < 3:
                        sample_urls.append(str(val))
            
            if url_count > 0:
                url_columns.append((i, col, url_count, sample_urls))
        
        if url_columns:
            for i, col, count, samples in url_columns:
                print(f"  Column {i} ({col}): {count} URLs")
                for sample in samples:
                    print(f"    {sample[:100]}...")
        else:
            print("  No HTTP URLs found in any column")
        
        # Check for Astrobin-specific patterns
        print(f"\nSearching for Astrobin-specific patterns:")
        astrobin_columns = []
        
        for i, col in enumerate(df.columns):
            astrobin_count = 0
            sample_ids = []
            
            for val in df.iloc[:, i]:
                val_str = str(val).lower()
                if pd.notna(val) and ('astrobin' in val_str or 'astro-bin' in val_str):
                    astrobin_count += 1
                    if len(sample_ids) < 3:
                        sample_ids.append(str(val))
            
            if astrobin_count > 0:
                astrobin_columns.append((i, col, astrobin_count, sample_ids))
        
        if astrobin_columns:
            for i, col, count, samples in astrobin_columns:
                print(f"  Column {i} ({col}): {count} Astrobin references")
                for sample in samples:
                    print(f"    {sample}")
        else:
            print("  No explicit Astrobin references found")
        
        # Look for numeric IDs that might be Astrobin IDs
        print(f"\nChecking Unnamed: 48 (current Astrobin ID column):")
        col_48_index = None
        for i, col in enumerate(df.columns):
            if 'Unnamed: 48' in str(col):
                col_48_index = i
                break
        
        if col_48_index is not None:
            col_48_data = df.iloc[:, col_48_index]
            non_empty = col_48_data.dropna()
            print(f"  Total values: {len(col_48_data)}")
            print(f"  Non-empty values: {len(non_empty)}")
            
            if len(non_empty) > 0:
                print(f"  Sample values: {non_empty.head(10).tolist()}")
                
                # Check if these look like valid Astrobin IDs
                numeric_count = 0
                for val in non_empty:
                    try:
                        int(float(val))
                        numeric_count += 1
                    except:
                        pass
                
                print(f"  Numeric values: {numeric_count}")
        
        # Check adjacent columns for additional image data
        print(f"\nChecking adjacent columns for image data:")
        for offset in [-3, -2, -1, 1, 2, 3]:
            col_index = col_48_index + offset if col_48_index else 48 + offset
            if 0 <= col_index < len(df.columns):
                col_name = df.columns[col_index]
                col_data = df.iloc[:, col_index]
                non_empty = col_data.dropna()
                
                print(f"  Column {col_index} ({col_name}):")
                print(f"    Non-empty: {len(non_empty)}")
                if len(non_empty) > 0:
                    samples = non_empty.head(5).tolist()
                    print(f"    Samples: {samples}")
        
    except Exception as e:
        print(f"Error reading Excel file: {e}")

if __name__ == "__main__":
    analyze_astrobin_data()
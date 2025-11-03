#!/usr/bin/env python3

import pandas as pd
from src.database.database_manager import DatabaseManager

def check_alternative_image_sources():
    """Check for alternative image sources in the database."""
    
    print("🔍 Checking Alternative Image Sources")
    print("="*60)
    
    db = DatabaseManager()
    if not db.database_exists():
        print("Database not found")
        return
    
    # Get all objects and check what image-related data we have
    query = '''
        SELECT 
            [Imm Deep Sky Compendium -  2023 - 4th Edition] as object_name,
            [Unnamed: 45] as col45,
            [Unnamed: 46] as col46,
            [Unnamed: 47] as col47,
            [Unnamed: 48] as col48
        FROM Main 
        WHERE [Imm Deep Sky Compendium -  2023 - 4th Edition] IS NOT NULL
          AND [Imm Deep Sky Compendium -  2023 - 4th Edition] != ''
          AND [Imm Deep Sky Compendium -  2023 - 4th Edition] NOT LIKE '%Object%'
          AND [Imm Deep Sky Compendium -  2023 - 4th Edition] NOT LIKE '%Link%'
          AND [Imm Deep Sky Compendium -  2023 - 4th Edition] NOT LIKE '%Astrobin%'
    '''
    
    df = pd.read_sql_query(query, db.get_connection())
    
    print(f"📊 Analyzing {len(df)} objects for image data")
    
    # Count objects with data in each column
    col45_count = df['col45'].notna().sum()
    col46_count = df['col46'].notna().sum()  
    col47_count = df['col47'].notna().sum()
    col48_count = df['col48'].notna().sum()
    
    print(f"Objects with data:")
    print(f"  Column 45: {col45_count}")
    print(f"  Column 46: {col46_count}")
    print(f"  Column 47: {col47_count}")
    print(f"  Column 48: {col48_count}")
    
    # Check for valid Astrobin IDs in column 48
    valid_astrobin_ids = 0
    astrobin_samples = []
    
    for _, row in df.iterrows():
        col48 = row['col48']
        if pd.notna(col48):
            try:
                astrobin_id = int(float(col48))
                if 1 <= astrobin_id <= 9999999:
                    valid_astrobin_ids += 1
                    if len(astrobin_samples) < 10:
                        astrobin_samples.append((row['object_name'], astrobin_id))
            except:
                pass
    
    print(f"\n🎯 Valid Astrobin IDs found: {valid_astrobin_ids}")
    if astrobin_samples:
        print("Sample objects with Astrobin IDs:")
        for obj_name, astrobin_id in astrobin_samples:
            print(f"  {obj_name}: {astrobin_id}")
    
    # Check if we can use external image sources
    print(f"\n🌐 Alternative Image Source Strategy:")
    print("Since most objects don't have Astrobin IDs, we could:")
    print("1. Use a generic astronomy image search API")
    print("2. Use DSS (Digitized Sky Survey) images") 
    print("3. Use SIMBAD or other astronomical databases")
    print("4. Create placeholder images with object information")
    
    # Test external sources for a few objects
    sample_objects = df.head(5)
    
    print(f"\n🧪 Testing alternative sources for sample objects:")
    
    for _, row in sample_objects.iterrows():
        obj_name = row['object_name']
        print(f"\n{obj_name}:")
        
        # DSS URL (this actually works for most objects)
        dss_url = f"https://archive.stsci.edu/cgi-bin/dss_search?v=poss2ukstu_red&r={obj_name.replace(' ', '+')}&e=J2000&h=15.0&w=15.0&f=gif"
        print(f"  DSS: {dss_url}")
        
        # SIMBAD image (if available)
        simbad_url = f"http://simbad.u-strasbg.fr/simbad/sim-id?Ident={obj_name.replace(' ', '+')}"
        print(f"  SIMBAD: {simbad_url}")
        
        # Could also try:
        # - Aladin Sky Atlas: https://aladin.cds.unistra.fr/AladinLite/
        # - IPAC/NED: https://ned.ipac.caltech.edu/
        # - ESO/ESA Hubble images
    
    print(f"\n💡 Recommendation:")
    print("Implement a multi-source image fallback system:")
    print("1. First try Astrobin ID if available")
    print("2. Then try DSS (Digitized Sky Survey)")
    print("3. Then try SIMBAD")
    print("4. Finally show object info card as fallback")
    
    return valid_astrobin_ids, astrobin_samples

if __name__ == "__main__":
    check_alternative_image_sources()
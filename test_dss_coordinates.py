#!/usr/bin/env python3
"""
Test DSS image loading using actual coordinates from the database.
This should work much better than using object names.
"""

import sqlite3
import requests
from PIL import Image
from io import BytesIO
import os

def test_dss_with_coordinates():
    """Test DSS image retrieval using actual RA/Dec coordinates."""
    
    # Connect to database
    db_path = os.path.join('data', 'astro_targets.db')
    if not os.path.exists(db_path):
        print("❌ Database not found")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get sample objects with coordinates (using correct column names)
    cursor.execute("""
        SELECT 
            [Imm Deep Sky Compendium -  2023 - 4th Edition] as object_name,
            [Unnamed: 12] as ra_degrees,
            [Unnamed: 14] as dec_degrees,
            [Unnamed: 15] as constellation,
            [Unnamed: 3] as object_type,
            [Unnamed: 19] as magnitude
        FROM Main 
        WHERE [Unnamed: 12] IS NOT NULL AND [Unnamed: 14] IS NOT NULL 
        AND [Unnamed: 12] != '' AND [Unnamed: 14] != ''
        LIMIT 10
    """)
    
    objects = cursor.fetchall()
    conn.close()
    
    print(f"🔍 Testing DSS with {len(objects)} objects that have coordinates...")
    
    successful = 0
    for obj_name, ra_deg, dec_deg, constellation, obj_type, magnitude in objects:
        try:
            # RA and Dec should already be in degrees in this database
            ra_deg = float(ra_deg) if ra_deg else 0
            dec_deg = float(dec_deg) if dec_deg else 0
            
            print(f"\n📍 Testing: {obj_name} ({constellation}, {obj_type})")
            print(f"   Coordinates: RA={ra_deg:.3f}°, Dec={dec_deg:.3f}°")
            
            # DSS URL using coordinates
            # Using DSS2 Red survey with 15 arcmin field of view
            dss_url = f"https://archive.stsci.edu/cgi-bin/dss_search?v=poss2ukstu_red&r={ra_deg:.6f}&d={dec_deg:.6f}&e=J2000&h=15.0&w=15.0&f=gif&c=none&fov=NONE&v3="
            
            print(f"   DSS URL: {dss_url[:80]}...")
            
            # Request image
            headers = {
                'User-Agent': 'NextAstroTarget/1.1.0 (Astronomy Application)',
                'Accept': 'image/gif,image/*,*/*;q=0.8'
            }
            
            response = requests.get(dss_url, headers=headers, timeout=10)
            print(f"   Response: {response.status_code}, Content-Type: {response.headers.get('content-type', 'unknown')}")
            print(f"   Size: {len(response.content)} bytes")
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()
                if 'image' in content_type and len(response.content) > 1000:  # Reasonable size check
                    try:
                        # Try to open as image
                        img = Image.open(BytesIO(response.content))
                        print(f"   ✅ SUCCESS: Image {img.size[0]}x{img.size[1]} pixels")
                        successful += 1
                        
                        # Save sample image for verification
                        if successful == 1:
                            safe_name = obj_name.replace(' ', '_').replace('/', '_')
                            img.save(f"test_dss_{safe_name}.gif")
                            print(f"   💾 Saved sample: test_dss_{safe_name}.gif")
                            
                    except Exception as img_error:
                        print(f"   ❌ Image processing failed: {img_error}")
                else:
                    print(f"   ❌ Not a valid image (content-type: {content_type})")
            else:
                print(f"   ❌ HTTP error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n📊 Results: {successful}/{len(objects)} successful DSS retrievals")
    if successful > 0:
        print("✨ DSS coordinate-based approach looks promising!")
    else:
        print("⚠️  DSS coordinate approach needs refinement")

if __name__ == "__main__":
    test_dss_with_coordinates()
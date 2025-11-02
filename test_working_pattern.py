#!/usr/bin/env python3

import requests
from PIL import Image
from io import BytesIO
import logging

def test_working_astrobin_pattern():
    """Test the working Astrobin URL pattern we found."""
    
    # Test IDs that might have images
    test_ids = [349, 100, 200, 300, 400, 500, 1000, 2000, 5000]
    
    print("Testing working Astrobin pattern:")
    print("=" * 50)
    
    working_urls = []
    
    for astrobin_id in test_ids:
        url = f"https://www.astrobin.com/{astrobin_id}/0/rawthumb/regular/"
        print(f"\nTesting ID {astrobin_id}: {url}")
        
        try:
            headers = {
                'User-Agent': 'NextAstroTarget/1.1.0 (Astronomy Application)',
                'Accept': 'image/*,*/*;q=0.8'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    # Try to open as image
                    img = Image.open(BytesIO(response.content))
                    print(f"  ✓ Valid image: {img.size} pixels, {img.mode}")
                    working_urls.append((astrobin_id, url))
                except Exception as e:
                    print(f"  ✗ Not a valid image: {e}")
            else:
                print(f"  ✗ Failed to fetch")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print(f"\nWorking URLs found: {len(working_urls)}")
    for aid, url in working_urls:
        print(f"  ID {aid}: {url}")
    
    return working_urls

if __name__ == "__main__":
    test_working_astrobin_pattern()
#!/usr/bin/env python3

import requests
from PIL import Image
from io import BytesIO

def test_dss_images():
    """Test if DSS images work for common objects."""
    
    print("🧪 Testing DSS (Digitized Sky Survey) Image Loading")
    print("="*60)
    
    # Test with some well-known objects
    test_objects = [
        "M31",
        "M42", 
        "NGC 7000",
        "Abell 01",
        "Barnard 001"
    ]
    
    for obj_name in test_objects:
        print(f"\nTesting: {obj_name}")
        
        # DSS URL
        dss_url = f"https://archive.stsci.edu/cgi-bin/dss_search?v=poss2ukstu_red&r={obj_name.replace(' ', '+')}&e=J2000&h=15.0&w=15.0&f=gif"
        print(f"URL: {dss_url}")
        
        try:
            headers = {
                'User-Agent': 'NextAstroTarget/1.1.0 (Astronomy Application)',
                'Accept': 'image/*,*/*;q=0.8'
            }
            
            response = requests.get(dss_url, headers=headers, timeout=10)
            print(f"Status: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
            print(f"Content-Length: {len(response.content)} bytes")
            
            if response.status_code == 200 and len(response.content) > 1000:
                try:
                    # Try to open as image
                    img = Image.open(BytesIO(response.content))
                    print(f"✅ Image loaded successfully: {img.size} pixels, {img.mode}")
                except Exception as img_error:
                    print(f"❌ Failed to process image: {img_error}")
            else:
                print(f"❌ Failed to get valid image")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
    
    print(f"\n💡 DSS provides astronomical survey images for most objects")
    print(f"This should give us images for the majority of our 3000+ objects!")

if __name__ == "__main__":
    test_dss_images()
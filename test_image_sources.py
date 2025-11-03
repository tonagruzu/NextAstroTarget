"""
Test script to demonstrate SDSS vs DSS image quality.
"""

import requests
from PIL import Image
from io import BytesIO
import numpy as np

def test_sdss_vs_dss():
    """Compare SDSS and DSS for a well-known galaxy (M51 - Whirlpool Galaxy)."""
    
    # M51 coordinates
    ra = 202.4696  # 13h 29m 52.7s
    dec = 47.1952  # +47° 11' 43"
    
    print("Testing image sources for M51 (Whirlpool Galaxy)")
    print(f"Coordinates: RA={ra}°, Dec={dec}°\n")
    
    # Test SDSS
    print("1. Fetching SDSS image...")
    sdss_url = (
        f"http://skyserver.sdss.org/dr17/SkyServerWS/ImgCutout/getjpeg"
        f"?ra={ra:.6f}&dec={dec:.6f}&width=512&height=512&scale=0.4"
    )
    
    try:
        response = requests.get(sdss_url, timeout=10)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            img_gray = img.convert('L')
            avg_brightness = np.mean(np.array(img_gray))
            
            print(f"   ✓ SDSS: SUCCESS")
            print(f"   - Size: {img.size}")
            print(f"   - Format: {img.format} (Color JPEG)")
            print(f"   - Avg brightness: {avg_brightness:.1f}/255")
            print(f"   - Quality: High-quality color composite\n")
            
            # Save sample
            img.save("test_sdss_m51.jpg")
            print("   Saved as: test_sdss_m51.jpg\n")
    except Exception as e:
        print(f"   ✗ SDSS failed: {e}\n")
    
    # Test DSS
    print("2. Fetching DSS image (fallback)...")
    dss_url = (
        f"https://archive.stsci.edu/cgi-bin/dss_search"
        f"?v=poss2ukstu_red&r={ra:.6f}&d={dec:.6f}"
        f"&e=J2000&h=15.0&w=15.0&f=gif&c=none&fov=NONE&v3="
    )
    
    try:
        response = requests.get(dss_url, timeout=10)
        if response.status_code == 200 and len(response.content) > 10000:
            img = Image.open(BytesIO(response.content))
            
            print(f"   ✓ DSS: SUCCESS")
            print(f"   - Size: {img.size}")
            print(f"   - Format: {img.format} (Grayscale GIF)")
            print(f"   - Quality: Digitized photographic plates\n")
            
            # Save sample
            img.save("test_dss_m51.gif")
            print("   Saved as: test_dss_m51.gif\n")
    except Exception as e:
        print(f"   ✗ DSS failed: {e}\n")
    
    print("=" * 60)
    print("Summary:")
    print("  SDSS: Modern color CCD images, better for galaxies")
    print("  DSS:  Historical plates, good fallback, works everywhere")
    print("=" * 60)

if __name__ == "__main__":
    test_sdss_vs_dss()

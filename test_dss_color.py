"""
Test DSS color composite capability - demonstrates RGB image creation from multiple filters.
"""

import requests
from PIL import Image
from io import BytesIO
import numpy as np

def test_dss_color_composite():
    """Test DSS color composite for M51 (Whirlpool Galaxy)."""
    
    # M51 coordinates
    ra = 202.4696
    dec = 47.1952
    size = 15.0
    
    print("=" * 70)
    print("Testing DSS Color Composite (RGB from Red + Blue filters)")
    print("=" * 70)
    print(f"\nTarget: M51 Whirlpool Galaxy")
    print(f"Coordinates: RA={ra}°, Dec={dec}°\n")
    
    headers = {
        'User-Agent': 'NextAstroTarget/2.0.0',
        'Accept': 'image/gif,image/*'
    }
    
    # Fetch Red filter
    print("1. Fetching DSS Red filter (POSS2/UKSTU Red)...")
    red_url = (
        f"https://archive.stsci.edu/cgi-bin/dss_search"
        f"?v=poss2ukstu_red&r={ra:.6f}&d={dec:.6f}"
        f"&e=J2000&h={size}&w={size}&f=gif&c=none&fov=NONE&v3="
    )
    
    red_response = requests.get(red_url, headers=headers, timeout=10)
    if red_response.status_code == 200:
        red_img = Image.open(BytesIO(red_response.content)).convert('L')
        print(f"   ✓ Red channel: {red_img.size[0]}x{red_img.size[1]} pixels")
        red_img.save("test_dss_red.gif")
        print("   Saved: test_dss_red.gif\n")
    else:
        print("   ✗ Failed\n")
        return
    
    # Fetch Blue filter
    print("2. Fetching DSS Blue filter (POSS2/UKSTU Blue)...")
    blue_url = (
        f"https://archive.stsci.edu/cgi-bin/dss_search"
        f"?v=poss2ukstu_blue&r={ra:.6f}&d={dec:.6f}"
        f"&e=J2000&h={size}&w={size}&f=gif&c=none&fov=NONE&v3="
    )
    
    blue_response = requests.get(blue_url, headers=headers, timeout=10)
    if blue_response.status_code == 200:
        blue_img = Image.open(BytesIO(blue_response.content)).convert('L')
        print(f"   ✓ Blue channel: {blue_img.size[0]}x{blue_img.size[1]} pixels")
        blue_img.save("test_dss_blue.gif")
        print("   Saved: test_dss_blue.gif\n")
    else:
        print("   ✗ Failed\n")
        return
    
    # Create RGB composite
    print("3. Creating RGB color composite...")
    if red_img.size != blue_img.size:
        blue_img = blue_img.resize(red_img.size, Image.Resampling.LANCZOS)
    
    red_array = np.array(red_img)
    blue_array = np.array(blue_img)
    green_array = ((red_array.astype(np.float32) + blue_array.astype(np.float32)) / 2).astype(np.uint8)
    
    rgb_array = np.stack([red_array, green_array, blue_array], axis=2)
    color_img = Image.fromarray(rgb_array, mode='RGB')
    
    color_img.save("test_dss_color_composite.png")
    print(f"   ✓ RGB composite: {color_img.size[0]}x{color_img.size[1]} pixels")
    print("   Saved: test_dss_color_composite.png\n")
    
    print("=" * 70)
    print("Summary:")
    print("  • Red channel: DSS Red filter (deepest penetration)")
    print("  • Green channel: Average of Red + Blue (synthetic)")
    print("  • Blue channel: DSS Blue filter (shorter wavelengths)")
    print("\n  Result: Natural-looking color composite image!")
    print("=" * 70)

if __name__ == "__main__":
    test_dss_color_composite()

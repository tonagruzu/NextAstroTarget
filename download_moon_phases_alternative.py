#!/usr/bin/env python3
"""
Download moon phase images from alternative sources.
NASA SVS is not responding, so we'll try other reliable sources.
"""

import os
import requests
from pathlib import Path
from PIL import Image
import io

# Create cache directory
cache_dir = Path("data/moon_cache")
cache_dir.mkdir(parents=True, exist_ok=True)

print("Attempting to download moon phase images from alternative sources...")
print()

# Option 1: Try Wikipedia's moon phase images (from Wikimedia Commons)
# These are high-quality public domain images
wikimedia_base = "https://upload.wikimedia.org/wikipedia/commons/"

# Wikipedia has a nice set of moon phase images
# https://commons.wikimedia.org/wiki/File:Lunar_libration_with_phase_Oct_2007_450px.gif
# We can use individual frames from lunar phase series

# Option 2: Use Astronomy Picture of the Day archive or similar sources

# Option 3: Keep our generated images but improve them

print("Option 1: Testing Wikimedia Commons access...")
test_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Moon_Phase_Diagram.svg/800px-Moon_Phase_Diagram.svg.png"

try:
    response = requests.get(test_url, timeout=10)
    if response.status_code == 200:
        print(f"✓ Wikimedia Commons is accessible")
    else:
        print(f"✗ Wikimedia returned status {response.status_code}")
except Exception as e:
    print(f"✗ Wikimedia Commons error: {e}")

print()

# Option 4: Use a lunar phase API that provides images
print("Option 2: Testing farmsense.net moon phase API...")
try:
    # This API provides moon phase data and images
    test_url = "https://www.icalendar37.net/lunar/api/"
    response = requests.get(test_url, timeout=10)
    if response.status_code == 200:
        print(f"✓ Lunar API is accessible")
    else:
        print(f"✗ Lunar API returned status {response.status_code}")
except Exception as e:
    print(f"✗ Lunar API error: {e}")

print()

# Option 5: Use free astronomy resources
print("Option 3: Testing timeanddate.com moon phase images...")
try:
    # Timeanddate.com has moon phase visualizations
    test_url = "https://c.tadst.com/gfx/750x500/moon-phases.png"
    response = requests.get(test_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
    if response.status_code == 200:
        print(f"✓ timeanddate.com is accessible")
        img = Image.open(io.BytesIO(response.content))
        print(f"  Image size: {img.size}")
    else:
        print(f"✗ timeanddate.com returned status {response.status_code}")
except Exception as e:
    print(f"✗ timeanddate.com error: {e}")

print()

# Option 6: Astronomy.com or similar astronomy sites
print("Option 4: Testing astronomy image services...")

# List of potential moon phase image URLs from various sources
moon_image_sources = [
    # Wikimedia Commons - individual moon phases
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Waxing_gibbous_moon.jpg/400px-Waxing_gibbous_moon.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/7/71/Full_Moon_Luc_Viatour.jpg/400px-Full_Moon_Luc_Viatour.jpg",
    # NASA APOD mirror sites
    "https://apod.nasa.gov/apod/image/moon_phases.jpg",
]

for i, url in enumerate(moon_image_sources):
    print(f"Testing source {i+1}: {url[:50]}...")
    try:
        response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code == 200:
            print(f"  ✓ Accessible - {len(response.content)} bytes")
            img = Image.open(io.BytesIO(response.content))
            print(f"  Image: {img.size[0]}x{img.size[1]} {img.mode}")
        else:
            print(f"  ✗ Status {response.status_code}")
    except Exception as e:
        print(f"  ✗ Error: {type(e).__name__}")

print()
print("=" * 60)
print("RECOMMENDATION:")
print("=" * 60)
print()
print("Since NASA SVS is not responding, we have a few options:")
print()
print("1. Use Wikimedia Commons images (high quality, public domain)")
print("   - Download individual moon phase photos")
print("   - Process and standardize them")
print()
print("2. Keep our generated images but enhance them")
print("   - Add realistic lunar surface texture")
print("   - Improve the terminator rendering")
print("   - Add subtle shadowing")
print()
print("3. Use a combination approach")
print("   - Download one high-quality full moon image")
print("   - Apply phase masks to create all 29 phases")
print()
print("Which approach would you prefer?")

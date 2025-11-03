"""
Download all 30 moon phase images from NASA SVS for local backup.
This creates a complete local cache of moon phases so the app works offline.
"""

import requests
from pathlib import Path
import time

def download_moon_phases():
    """Download all 30 moon phase images."""
    
    # Create cache directory
    cache_dir = Path('data/moon_cache')
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    # NASA SVS moon phase images
    base_url = "https://svs.gsfc.nasa.gov/vis/a000000/a004900/a004955/frames/730x730_1x1_30p/"
    
    print("=" * 60)
    print("Downloading NASA Moon Phase Images")
    print("=" * 60)
    print(f"\nTarget directory: {cache_dir.absolute()}\n")
    
    success_count = 0
    for day in range(30):
        # NASA SVS has frames 1-29, no frame 0
        if day == 0:
            print(f"⊘ Day {day:2d}: Skipping (no frame 0 in NASA set)")
            continue
            
        image_url = f"{base_url}moon.{day:04d}.jpg"
        cache_file = cache_dir / f"moon_day_{day:02d}.jpg"
        
        # Skip if already exists
        if cache_file.exists():
            print(f"✓ Day {day:2d}: Already cached")
            success_count += 1
            continue
        
        try:
            print(f"⬇ Day {day:2d}: Downloading...", end=" ", flush=True)
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            
            # Save to disk
            with open(cache_file, 'wb') as f:
                f.write(response.content)
            
            file_size = len(response.content) / 1024  # KB
            print(f"✓ ({file_size:.1f} KB)")
            success_count += 1
            
            # Be nice to NASA's servers
            time.sleep(0.5)
            
        except Exception as e:
            print(f"✗ Error: {e}")
    
    print("\n" + "=" * 60)
    print(f"Download Complete: {success_count}/30 images")
    print("=" * 60)
    
    if success_count == 30:
        print("\n✓ All moon phase images cached successfully!")
        print("  The app will now work offline with real moon images.")
    else:
        print(f"\n⚠ {30 - success_count} images failed to download.")
        print("  The app will use fallback graphics for missing phases.")

if __name__ == "__main__":
    download_moon_phases()

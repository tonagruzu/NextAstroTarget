"""
Download high-quality moon phase images from NASA.
NASA Scientific Visualization Studio provides moon phases for 2024.
"""

import requests
import os
from pathlib import Path

def download_nasa_moon_phases():
    """
    Download NASA moon phase images.
    NASA SVS provides moon visualizations at:
    https://svs.gsfc.nasa.gov/5187
    
    We'll use the 2024 moon phase images which show accurate libration and phases.
    """
    
    cache_dir = Path('data/moon_cache')
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    print("Downloading NASA moon phase images...")
    print("Source: NASA Scientific Visualization Studio")
    print("https://svs.gsfc.nasa.gov/5187\n")
    
    # NASA provides moon phases for each day of 2024
    # We need to select 29 representative frames across the lunar cycle
    # The lunar cycle is approximately 29.5 days
    
    # Base URL for NASA 2024 moon phases (example - actual URL structure may vary)
    # These are 1920x1080 resolution images
    base_url = "https://svs.gsfc.nasa.gov/vis/a000000/a005100/a005187/frames/730x730_1x1_30p/moon.{:04d}.jpg"
    
    # Select frames that represent a complete lunar cycle
    # Frame 1 = Jan 1, 2024 (after New Moon on Dec 12, 2023)
    # We want to select evenly spaced frames across ~29 days
    
    # Calculate frame numbers for 29 phases (evenly distributed across lunar cycle)
    # Assuming frames represent daily progression
    frames_to_download = []
    for i in range(1, 30):  # 29 frames
        # Map frame 1-29 to actual NASA frame numbers
        # This distributes them across the lunar cycle
        nasa_frame = i * 12  # Approximate spacing
        frames_to_download.append((i, nasa_frame))
    
    success_count = 0
    failed_frames = []
    
    for local_frame, nasa_frame in frames_to_download:
        url = base_url.format(nasa_frame)
        output_file = cache_dir / f"moon_day_{local_frame:02d}.jpg"
        
        try:
            print(f"Frame {local_frame:02d}: Downloading from NASA frame {nasa_frame:04d}...", end=' ')
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                print("✓")
                success_count += 1
            else:
                print(f"✗ (HTTP {response.status_code})")
                failed_frames.append(local_frame)
                
        except requests.exceptions.RequestException as e:
            print(f"✗ (Error: {e})")
            failed_frames.append(local_frame)
    
    print(f"\n{'='*60}")
    print(f"Download complete:")
    print(f"  Success: {success_count}/29 frames")
    if failed_frames:
        print(f"  Failed: {failed_frames}")
        print(f"\nNote: If downloads failed, the URL structure may have changed.")
        print(f"Visit https://svs.gsfc.nasa.gov/5187 for the latest moon phase images.")
    else:
        print(f"  All frames downloaded successfully!")
    print(f"{'='*60}")


if __name__ == "__main__":
    download_nasa_moon_phases()

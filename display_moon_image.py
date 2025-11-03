"""Display a specific moon phase image to verify what it actually shows."""
import sys
from pathlib import Path
from PIL import Image

cache_dir = Path("data/moon_cache")

# Let's check what frames 14, 15, and a few others actually look like
frames_to_check = [1, 8, 14, 15, 16, 22, 29]

print("Checking moon phase images in cache:")
print()

for frame in frames_to_check:
    img_path = cache_dir / f"moon_day_{frame:02d}.jpg"
    if img_path.exists():
        print(f"Frame {frame:02d}: {img_path.name} - Opening...")
        img = Image.open(img_path)
        img.show()
        input(f"  Press Enter after viewing frame {frame} to continue...")
    else:
        print(f"Frame {frame:02d}: NOT FOUND")

print("\nDone checking images.")

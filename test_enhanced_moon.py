#!/usr/bin/env python3
"""
Test the enhanced moon phase images and verify correct frame selection.
"""

from datetime import datetime
from pathlib import Path
from PIL import Image
import sys

# Add src to path
sys.path.insert(0, 'src')

from utils.astronomical_calculations import AstronomicalCalculator

def calculate_moon_phase(dt):
    """Wrapper for calculate_moon_phase."""
    calc = AstronomicalCalculator()
    return calc.calculate_moon_phase(dt)

def test_moon_phase_display():
    """Test that the correct moon phase image is being selected."""
    
    print("=" * 70)
    print("MOON PHASE VERIFICATION TEST")
    print("=" * 70)
    print()
    
    # Get current moon phase data
    now = datetime.now()
    phase_data = calculate_moon_phase(now)
    
    print(f"Current date/time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print(f"Moon Phase: {phase_data['phase_name']}")
    print(f"Illumination: {phase_data['illumination']:.1f}%")
    print(f"Cycle Position: {phase_data['cycle_position']:.4f}")
    print()
    
    # Calculate which frame should be displayed
    cycle_pos = phase_data['cycle_position']
    frame_number = round(cycle_pos * 28) + 1
    
    print(f"Frame calculation:")
    print(f"  Cycle position: {cycle_pos:.4f}")
    print(f"  Formula: round({cycle_pos:.4f} * 28) + 1")
    print(f"  Selected frame: {frame_number}")
    print()
    
    # Check if the image exists
    cache_dir = Path("data/moon_cache")
    image_path = cache_dir / f"moon_day_{frame_number:02d}.jpg"
    
    if image_path.exists():
        print(f"✓ Image exists: {image_path}")
        
        # Load and check image
        img = Image.open(image_path)
        print(f"  Size: {img.size[0]}x{img.size[1]}")
        print(f"  Mode: {img.mode}")
        print(f"  Format: {img.format}")
    else:
        print(f"✗ Image NOT found: {image_path}")
    
    print()
    print("=" * 70)
    print("VERIFICATION")
    print("=" * 70)
    print()
    
    # Verify frame makes sense for the phase
    expected_frames = {
        "New Moon": [1, 29],
        "Waxing Crescent": [2, 3, 4, 5, 6, 7],
        "First Quarter": [8],
        "Waxing Gibbous": [9, 10, 11, 12, 13, 14],
        "Full Moon": [15],
        "Waning Gibbous": [16, 17, 18, 19, 20, 21],
        "Last Quarter": [22],
        "Waning Crescent": [23, 24, 25, 26, 27, 28],
    }
    
    phase_name = phase_data['phase_name']
    if phase_name in expected_frames:
        expected = expected_frames[phase_name]
        if frame_number in expected:
            print(f"✓ Frame {frame_number} is correct for {phase_name}")
        else:
            print(f"✗ Frame {frame_number} seems wrong for {phase_name}")
            print(f"  Expected one of: {expected}")
    
    print()
    
    # Show a few example dates and their frames
    print("Sample moon phases for different dates:")
    print()
    
    test_dates = [
        datetime(2025, 11, 1),   # New Moon period
        datetime(2025, 11, 8),   # First Quarter
        datetime(2025, 11, 15),  # Full Moon
        datetime(2025, 11, 23),  # Last Quarter
    ]
    
    for test_date in test_dates:
        data = calculate_moon_phase(test_date)
        frame = round(data['cycle_position'] * 28) + 1
        print(f"{test_date.strftime('%Y-%m-%d')}: {data['phase_name']:16} "
              f"({data['illumination']:5.1f}%) → Frame {frame:2}")
    
    print()
    print("=" * 70)
    
    # Display one of the images for visual verification
    print()
    print("Opening frame {frame_number} for visual verification...")
    try:
        img.show()
        print("Please verify the moon phase looks correct for the current date.")
    except:
        print("Could not open image viewer. Image is saved at:")
        print(f"  {image_path}")

if __name__ == "__main__":
    test_moon_phase_display()

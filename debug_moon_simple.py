"""Debug current moon phase calculation - simplified."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime
from src.utils.astronomical_calculations import AstronomicalCalculator

# Get current date
now = datetime.now()
print(f"Current date/time: {now}")
print()

# Get moon phase info
astro = AstronomicalCalculator()
phase_info = astro.calculate_moon_phase(now)

print("Moon Phase Information:")
print(f"  Phase name: {phase_info['phase_name']}")
print(f"  Cycle position: {phase_info['cycle_position']:.4f}")
print(f"  Illumination: {phase_info['illumination']:.1f}%")
print(f"  Days since new moon: {phase_info['days_since_new']:.1f}")
print()

# Calculate frame number using current formula
cycle_position = phase_info['cycle_position']

# Method currently in code
frame_num = round(cycle_position * 29) + 1
frame_num = max(1, min(29, frame_num))

print(f"Frame calculation:")
print(f"  cycle_position = {cycle_position:.4f}")
print(f"  cycle_position * 29 = {cycle_position * 29:.2f}")
print(f"  round(cycle_position * 29) = {round(cycle_position * 29)}")
print(f"  frame_num = {frame_num}")
print()

# Calculate what phase angle this frame represents
frame_cycle = (frame_num - 1) / 29.0
frame_angle = frame_cycle * 360
print(f"Frame {frame_num} represents:")
print(f"  Cycle position: {frame_cycle:.4f}")
print(f"  Angle: {frame_angle:.1f}°")

if frame_angle < 22.5 or frame_angle >= 337.5:
    expected_phase = "New Moon"
elif frame_angle < 67.5:
    expected_phase = "Waxing Crescent"
elif frame_angle < 112.5:
    expected_phase = "First Quarter"
elif frame_angle < 157.5:
    expected_phase = "Waxing Gibbous"
elif frame_angle < 202.5:
    expected_phase = "Full Moon"
elif frame_angle < 247.5:
    expected_phase = "Waning Gibbous"
elif frame_angle < 292.5:
    expected_phase = "Last Quarter"
else:
    expected_phase = "Waning Crescent"

print(f"  Expected phase for this frame: {expected_phase}")
print()

print(f"Actual moon phase today: {phase_info['phase_name']}")
print(f"Actual illumination: {phase_info['illumination']:.1f}%")
print()

# Check if they match
if expected_phase == phase_info['phase_name']:
    print("✓ Frame matches actual phase!")
else:
    print("⚠️ MISMATCH! Frame doesn't match actual phase!")
    print()
    print("PROBLEM: The generated images don't align with cycle positions!")
    print()
    print("The issue is in generate_moon_phases.py:")
    print(f"  It uses: phase_angle = (frame - 1) / 29.0 * 360")
    print(f"  Frame 1 = 0°, Frame 15 = 173.8°, Frame 29 = 347.6°")
    print()
    print("But the selection logic expects:")
    print(f"  Frame 1 at cycle 0.0 (new moon)")
    print(f"  Frame 15 at cycle 0.483 (almost full moon)")
    print()
    print("We need to regenerate images with corrected phase angles!")

"""Debug current moon phase calculation."""

from datetime import datetime
from src.astronomy.moon_phase import get_moon_phase

# Get current date
now = datetime.now()
print(f"Current date/time: {now}")
print()

# Get moon phase info
phase_info = get_moon_phase(now)

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
print(f"  cycle_position * 29 = {cycle_position * 29:.2f}")
print(f"  round(cycle_position * 29) = {round(cycle_position * 29)}")
print(f"  frame_num = {frame_num}")
print()

# Calculate what phase this frame should show
frame_angle = ((frame_num - 1) / 29.0) * 360
print(f"Frame {frame_num} should show:")
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

print(f"  Expected phase: {expected_phase}")
print()

# What it should be
print(f"Actual moon phase: {phase_info['phase_name']}")
print(f"Actual illumination: {phase_info['illumination']:.1f}%")
print()

# Check if they match
if expected_phase != phase_info['phase_name']:
    print("⚠️ MISMATCH! Frame doesn't match actual phase!")
    print()
    
    # Calculate correct frame for actual phase
    # We need to map cycle_position (0-1) to frame (1-29)
    # But cycle_position 0.0 = new moon, 0.5 = full moon
    
    # Try different mapping
    print("Alternative calculations:")
    
    # Method 1: Direct mapping
    alt1 = int(cycle_position * 29) + 1
    print(f"  int(cycle * 29) + 1 = {alt1}")
    
    # Method 2: Round
    alt2 = round(cycle_position * 29) + 1
    print(f"  round(cycle * 29) + 1 = {alt2}")
    
    # Method 3: Map to 0-28 range then add 1
    alt3 = int(cycle_position * 29 + 0.5)
    if alt3 == 0:
        alt3 = 1
    print(f"  int(cycle * 29 + 0.5) = {alt3}")
else:
    print("✓ Frame matches actual phase!")

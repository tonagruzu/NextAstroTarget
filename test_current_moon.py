"""Test current moon phase calculation and image selection."""

from datetime import datetime
from src.utils.astronomical_calculations import AstronomicalCalculator

# Calculate current moon phase
now = datetime.now()
calc = AstronomicalCalculator()
phase = calc.calculate_moon_phase(now)

print(f"\n=== Moon Phase for {now.strftime('%Y-%m-%d %H:%M:%S')} ===")
print(f"Cycle Position: {phase['cycle_position']:.4f}")
print(f"Illumination: {phase['illumination']:.1f}%")
print(f"Phase Name: {phase['phase_name']}")
print(f"Is Waxing: {phase['is_waxing']}")
print(f"Days since New Moon: {phase['days_since_new']:.2f}")

# Calculate frame number using same formula as MoonPhaseWidget
cycle_position = phase['cycle_position']
frame_num = round(cycle_position * 28) + 1
frame_num = max(1, min(29, frame_num))

print(f"\nSelected Frame: {frame_num}")
print(f"Frame File: moon_day_{frame_num:02d}.jpg")

# Show what frame should represent
frame_angle = (frame_num - 1) / 28.0 * 360
print(f"Frame Angle: {frame_angle:.1f}°")

# Show expected characteristics
if cycle_position < 0.01:
    expected = "New Moon (dark)"
elif 0.24 < cycle_position < 0.26:
    expected = "First Quarter (right half lit)"
elif 0.49 < cycle_position < 0.51:
    expected = "Full Moon (fully lit)"
elif 0.74 < cycle_position < 0.76:
    expected = "Last Quarter (left half lit)"
elif cycle_position < 0.5:
    expected = f"Waxing ({phase['illumination']:.0f}% lit, growing)"
else:
    expected = f"Waning ({phase['illumination']:.0f}% lit, shrinking)"

print(f"\nExpected appearance: {expected}")

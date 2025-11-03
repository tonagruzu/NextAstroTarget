from datetime import datetime
from src.utils.astronomical_calculations import AstronomicalCalculator

calc = AstronomicalCalculator()
phase = calc.calculate_moon_phase(datetime.now())

cycle_position = phase['cycle_position']
print(f"Current date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print(f"Cycle position: {cycle_position:.4f}")
print(f"Illumination: {phase['illumination']:.1f}%")
print(f"Phase name: {phase['phase_name']}")

# Old calculation (wrong)
lunar_day = int(cycle_position * 29.53)
print(f"\nOld method:")
print(f"  Lunar day: {lunar_day}")
print(f"  Expected image: moon.{max(1, lunar_day % 30):04d}.jpg")

# New calculation (correct)
frame_num = int(cycle_position * 29) + 1
frame_num = max(1, min(29, frame_num))
print(f"\nNew method:")
print(f"  Frame number: {frame_num}")
print(f"  Expected image: moon.{frame_num:04d}.jpg")
print(f"\nNote: Frame 1 = new moon, Frame 15 = full moon, Frame 29 = waning crescent")

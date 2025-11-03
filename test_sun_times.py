from datetime import datetime, timedelta
from src.utils.astronomical_calculations import AstronomicalCalculator

ac = AstronomicalCalculator()

print("Testing sun positions for Nov 3, 2025 at lat=54.38, lon=18.49")
print("UTC Time -> Sun Altitude")
print("-" * 40)

for h in range(12, 20):
    for m in [0, 30]:
        dt = datetime(2025, 11, 3, h, m)
        alt, az = ac.calculate_sun_position(dt, 54.38, 18.49)
        print(f"{h:02d}:{m:02d} UTC - Alt: {alt:6.2f}°")

print("\nTesting calculate_sun_times:")
sun_times = ac.calculate_sun_times(54.38, 18.49, datetime(2025, 11, 3).date())
gmt_offset = timedelta(hours=1)

print(f"Sunrise UTC: {sun_times['sunrise']}")
print(f"Sunset UTC: {sun_times['sunset']}")
print(f"Sunrise Local (GMT+1): {(sun_times['sunrise'] + gmt_offset).strftime('%H:%M')}")
print(f"Sunset Local (GMT+1): {(sun_times['sunset'] + gmt_offset).strftime('%H:%M')}")

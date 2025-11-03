from datetime import datetime, date, timedelta
from src.utils.astronomical_calculations import AstronomicalCalculator

calc = AstronomicalCalculator()

# Test for Gdansk location on November 3, 2025
lat = 54.38
lon = 18.49
test_date = date(2025, 11, 3)

print(f"Testing sun altitude progression for {lat}°N, {lon}°E on {test_date}")
print()

# Check altitudes around expected sunset time (15:07 UTC)
base_time = datetime.combine(test_date, datetime.min.time().replace(hour=15, minute=0))

print("Time (UTC)  | Altitude")
print("-" * 30)
for minutes in range(0, 15, 1):
    test_time = base_time + timedelta(minutes=minutes)
    altitude, azimuth = calc.calculate_sun_position(test_time, lat, lon)
    marker = " <-- CROSSING" if -0.9 < altitude < -0.7 else ""
    print(f"{test_time.strftime('%H:%M:%S')}  | {altitude:7.3f}°{marker}")

from datetime import datetime, date, timedelta
from src.utils.astronomical_calculations import AstronomicalCalculator

calc = AstronomicalCalculator()

# Test for current location from config
lat = 54.38
lon = 18.49
test_date = date.today()

print(f"Testing for location: {lat}°N, {lon}°E on {test_date}")
print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Calculate sun times
sun_times = calc.calculate_sun_times(lat, lon, test_date)

print("=== Calculated times (UTC) ===")
print(f"Sunrise: {sun_times['sunrise'].strftime('%H:%M:%S')}")
print(f"Sunset: {sun_times['sunset'].strftime('%H:%M:%S')}")
print(f"Nautical dawn: {sun_times['nautical_dawn'].strftime('%H:%M:%S')}")
print(f"Nautical dusk: {sun_times['nautical_dusk'].strftime('%H:%M:%S')}")
print()

# Apply GMT offset (Poland is GMT+1 in winter)
gmt_offset = timedelta(hours=1)
dst_active = False  # No DST in November

if dst_active:
    gmt_offset += timedelta(hours=1)

local_sunrise = sun_times['sunrise'] + gmt_offset
local_sunset = sun_times['sunset'] + gmt_offset
local_dawn = sun_times['nautical_dawn'] + gmt_offset
local_dusk = sun_times['nautical_dusk'] + gmt_offset

print("=== LOCAL times (CET = UTC+1) ===")
print(f"Sunrise: {local_sunrise.strftime('%H:%M:%S')} CET")
print(f"Sunset: {local_sunset.strftime('%H:%M:%S')} CET")
print(f"Nautical dawn: {local_dawn.strftime('%H:%M:%S')} CET")
print(f"Nautical dusk: {local_dusk.strftime('%H:%M:%S')} CET")
print()

# What app should display
print("=== APP SHOULD SHOW ===")
print(f"Sunrise: {local_sunrise.strftime('%H:%M')} | Sunset: {local_sunset.strftime('%H:%M')}")
print(f"Nautical: {local_dawn.strftime('%H:%M')} - {local_dusk.strftime('%H:%M')}")

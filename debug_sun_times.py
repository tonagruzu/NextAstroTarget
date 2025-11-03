from datetime import datetime, date
from src.utils.astronomical_calculations import AstronomicalCalculator

calc = AstronomicalCalculator()

# Test for Gdansk location on November 3, 2025
lat = 54.38
lon = 18.49
test_date = date(2025, 11, 3)

print(f"Testing for location: {lat}°N, {lon}°E on {test_date}")
print()

times = calc.calculate_sun_times(lat, lon, test_date)

print("=== Calculated times (UTC) ===")
print(f"Sunrise: {times['sunrise'].strftime('%H:%M:%S')}")
print(f"Sunset: {times['sunset'].strftime('%H:%M:%S')}")
print(f"Nautical dawn: {times['nautical_dawn'].strftime('%H:%M:%S')}")
print(f"Nautical dusk: {times['nautical_dusk'].strftime('%H:%M:%S')}")
print()

# Verify altitudes at calculated times
alt_sunrise, _ = calc.calculate_sun_position(times['sunrise'], lat, lon)
alt_sunset, _ = calc.calculate_sun_position(times['sunset'], lat, lon)
alt_dawn, _ = calc.calculate_sun_position(times['nautical_dawn'], lat, lon)
alt_dusk, _ = calc.calculate_sun_position(times['nautical_dusk'], lat, lon)

print("=== Altitude verification ===")
print(f"Altitude at sunrise: {alt_sunrise:.3f}° (expected: -0.833°)")
print(f"Altitude at sunset: {alt_sunset:.3f}° (expected: -0.833°)")
print(f"Altitude at nautical dawn: {alt_dawn:.3f}° (expected: -12.0°)")
print(f"Altitude at nautical dusk: {alt_dusk:.3f}° (expected: -12.0°)")
print()

# Compare with expected values for Gdansk on Nov 3, 2025
# From timeanddate.com: Sunrise ~06:52 CET (05:52 UTC), Sunset ~16:07 CET (15:07 UTC)
print("=== Expected values ===")
print("Sunrise: ~05:52 UTC (06:52 CET)")
print("Sunset: ~15:07 UTC (16:07 CET)")

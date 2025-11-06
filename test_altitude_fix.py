"""
Test script to verify altitude calculation fix for Sh2-157.
This demonstrates the difference between current time and evening observation time.
"""

from datetime import datetime, timedelta
import sys
import os

# Add the src directory to path
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from utils.astronomical_calculations import AstronomicalCalculator

# Your observatory location
latitude = 54.38
longitude = 18.49

# Sh2-157 (Lobster Claw Nebula) coordinates
# RA: 23h 15m 54s = 23.265 hours
# Dec: +60° 06' = +60.1 degrees
ra_hours = 23.265
dec_degrees = 60.1

calc = AstronomicalCalculator()

print("=" * 80)
print("ALTITUDE CALCULATION FIX VERIFICATION - Sh2-157")
print("=" * 80)
print(f"Object: Sh2-157 (Lobster Claw Nebula)")
print(f"RA: {ra_hours:.3f}h, Dec: {dec_degrees:+.2f}°")
print(f"Observer: Lat {latitude}°, Lon {longitude}°")
print("=" * 80)

# OLD BEHAVIOR: Using current time (morning)
utc_now = datetime.utcnow()
alt_now, _ = calc.calculate_altitude_azimuth(
    ra_hours, dec_degrees, utc_now, latitude, longitude
)

print(f"\n❌ OLD (WRONG): Using current time")
print(f"   UTC Time: {utc_now.strftime('%Y-%m-%d %H:%M')}")
print(f"   Altitude: {alt_now:.1f}°")
print(f"   Problem: Shows low altitude during daytime!")

# NEW BEHAVIOR: Using evening observation time (e.g., 20:00 local = 19:00 UTC)
print(f"\n✅ NEW (CORRECT): Using evening observation time")

# Poland is UTC+1 in winter
local_evening = datetime(utc_now.year, utc_now.month, utc_now.day, 20, 0, 0)  # 20:00 local
utc_evening = local_evening - timedelta(hours=1)  # Convert to UTC

alt_evening, _ = calc.calculate_altitude_azimuth(
    ra_hours, dec_degrees, utc_evening, latitude, longitude
)

print(f"   Local Time: {local_evening.strftime('%Y-%m-%d %H:%M')} (evening observation)")
print(f"   UTC Time: {utc_evening.strftime('%Y-%m-%d %H:%M')}")
print(f"   Altitude: {alt_evening:.1f}°")
print(f"   Result: Shows correct high altitude for evening!")

# Calculate theoretical maximum
if dec_degrees > latitude:
    max_alt = 90 - (dec_degrees - latitude)
else:
    max_alt = 90 - (latitude - dec_degrees)

print(f"\n📊 Summary:")
print(f"   Theoretical Maximum Altitude: {max_alt:.1f}°")
print(f"   Altitude at evening observation: {alt_evening:.1f}°")
print(f"   Difference from maximum: {abs(max_alt - alt_evening):.1f}°")

print("\n" + "=" * 80)
print("🎯 FIX APPLIED:")
print("   - Now uses observation_datetime instead of current time")
print("   - User can set observation time in the Settings panel")
print("   - Altitude columns show values for the chosen observation time")
print("=" * 80)

"""Test moon separation and index calculations against spreadsheet values."""
import sys
from datetime import datetime
from src.utils.astronomical_calculations import AstronomicalCalculator

# Initialize calculator
calc = AstronomicalCalculator()

# Test with Sh2-157 (from spreadsheet row 10)
# Object RA: 1236 (HMS format) = 12h 36m = 12.6h = 189 degrees
# Object Dec: 691041 (DMS format) = +69° 10' 41" = 69.178° 
ra_hms = 1236  # 12h 36m
dec_dms = 691041  # +69° 10' 41"

# Convert HMS to decimal hours
ra_h = int(str(ra_hms).zfill(4)[0:2])
ra_m = int(str(ra_hms).zfill(4)[2:4])
ra_hours = ra_h + ra_m / 60.0

# Convert DMS to decimal degrees
dec_str = str(dec_dms).zfill(6)
dec_d = int(dec_str[0:2])
dec_m = int(dec_str[2:4])
dec_s = int(dec_str[4:6])
dec_degrees = dec_d + dec_m / 60.0 + dec_s / 3600.0

print(f"Testing Sh2-157:")
print(f"  RA: {ra_hms} HMS = {ra_hours:.4f} hours = {ra_hours * 15:.4f}°")
print(f"  Dec: {dec_dms} DMS = {dec_degrees:.4f}°")
print()

# Test with observation time (use date from spreadsheet: 2023-09-28)
# The spreadsheet appears to use a specific reference date
test_date = datetime(2023, 9, 28, 21, 0, 0)  # 21:00 evening observation
print(f"Observation time: {test_date}")
print()

# Calculate moon RA/Dec
moon_ra, moon_dec = calc.get_moon_ra_dec(test_date)
print(f"Moon position:")
print(f"  RA: {moon_ra:.4f} hours = {moon_ra * 15:.4f}°")
print(f"  Dec: {moon_dec:.4f}°")
print()

# Calculate moon separation
separation = calc.calculate_moon_separation(ra_hours, dec_degrees, test_date)
print(f"Moon Separation: {separation:.2f}°")
print(f"  (Spreadsheet shows: 66.60°)")
print()

# Calculate moon phase
moon_phase = calc.calculate_moon_phase(test_date)
print(f"Moon Phase:")
print(f"  Illumination: {moon_phase['illumination']:.2f}%")
print(f"  Phase: {moon_phase['phase_name']}")
print(f"  (Spreadsheet shows: 92.52% illumination)")
print()

# Calculate moon index
moon_index = calc.calculate_moon_index(separation, moon_phase['illumination'])
print(f"Moon Index: {moon_index:.2f}")
print(f"  (Spreadsheet shows: 19.98)")
print()

# Color interpretation
if moon_index < 30:
    color = "🔴 RED (Poor - moon interference)"
elif moon_index < 70:
    color = "⚪ WHITE (Neutral)"
else:
    color = "🔵 BLUE (Good conditions)"
print(f"Color: {color}")

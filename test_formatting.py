"""Test the distance/diameter formatting logic"""

def format_distance_diameter(distance, diameter):
    """Test formatting function matching the UI code"""
    extended_notes = []
    
    # Add distance if available
    if distance and str(distance).strip() and str(distance).strip().lower() not in ['nan', 'none', '']:
        try:
            dist_val = float(distance)
            if dist_val >= 1000:
                # Use millions of light years for large distances
                extended_notes.append(f"🌌 Distance: {dist_val:,.0f} ly ({dist_val/1000:.1f} Mly)")
            elif dist_val >= 1:
                # Use millions of light years
                extended_notes.append(f"🌌 Distance: {dist_val:.2f} Mly ({dist_val*1000:.0f} kly)")
            else:
                # Small values in original units
                extended_notes.append(f"🌌 Distance: {dist_val} ly")
        except (ValueError, TypeError):
            pass
    
    # Add diameter if available
    if diameter and str(diameter).strip() and str(diameter).strip().lower() not in ['nan', 'none', '']:
        try:
            diam_val = float(diameter)
            extended_notes.append(f"📏 Apparent Size: {diam_val:.1f} arcmin")
        except (ValueError, TypeError):
            pass
    
    return extended_notes

# Test with sample objects
test_objects = [
    ('M 001', 6500, 13),
    ('M 031', 2.5, 150),
    ('M 042', 1600, 30),
    ('M 051', 25, 80),
    ('IC 1805', 7500, 190),
    ('NGC 7635', 7800, 35),
]

print("Distance and Diameter formatting test:")
print("=" * 80)
for name, distance, diameter in test_objects:
    print(f"\n{name}:")
    formatted = format_distance_diameter(distance, diameter)
    for line in formatted:
        print(f"  {line}")

print("\n" + "=" * 80)

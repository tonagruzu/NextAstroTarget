"""Test the updated distance/diameter formatting logic with proper units"""

def format_distance_diameter(distance, diameter, object_type):
    """Test formatting function matching the updated UI code"""
    extended_notes = []
    
    # Determine if object is a galaxy
    is_galaxy = object_type and str(object_type).strip().lower() == 'gal'
    
    # Add distance if available
    distance_str = str(distance).strip().lower()
    if distance and distance_str and distance_str not in ['nan', 'none', '']:
        # Check if distance is unknown (marked as 'u')
        if distance_str == 'u':
            extended_notes.append(f"🌌 Distance: Unknown")
        else:
            try:
                dist_val = float(distance)
                if is_galaxy:
                    # Galaxies: distance in Millions of Light Years (Mly)
                    extended_notes.append(f"🌌 Distance: {dist_val:,.2f} Mly")
                else:
                    # Other objects: distance in Light Years (ly)
                    extended_notes.append(f"🌌 Distance: {dist_val:,.0f} ly")
            except (ValueError, TypeError):
                pass
    
    # Add diameter if available
    diameter_str = str(diameter).strip().lower()
    if diameter and diameter_str and diameter_str not in ['nan', 'none', '', 'u']:
        try:
            diam_val = float(diameter)
            if is_galaxy:
                # Galaxies: diameter in thousands of light years (kly)
                extended_notes.append(f"📏 Physical Size: {diam_val:,.1f} kly")
            else:
                # Other objects: diameter in light years (ly)
                extended_notes.append(f"📏 Physical Size: {diam_val:,.1f} ly")
        except (ValueError, TypeError):
            pass
    
    return extended_notes

# Test with sample objects
test_objects = [
    ('M 001 (Crab Nebula)', 6500, 13, 'Neb'),
    ('M 031 (Andromeda)', 2.5, 150, 'Gal'),
    ('M 042 (Orion Nebula)', 1600, 30, 'Neb'),
    ('M 051 (Whirlpool)', 25, 80, 'Gal'),
    ('IC 1805 (Heart Nebula)', 7500, 190, 'Neb'),
    ('NGC 7635 (Bubble)', 7800, 35, 'Neb'),
    ('Test Unknown Distance', 'u', 50, 'Neb'),
]

print("Distance and Diameter formatting with proper units:")
print("=" * 80)
for name, distance, diameter, obj_type in test_objects:
    print(f"\n{name} (Type: {obj_type}):")
    formatted = format_distance_diameter(distance, diameter, obj_type)
    if formatted:
        for line in formatted:
            print(f"  {line}")
    else:
        print("  (no distance/diameter data)")

print("\n" + "=" * 80)
print("\nUnit Rules Applied:")
print("  • Galaxies: Distance in Mly, Physical Size in kly")
print("  • Other objects: Distance in ly, Physical Size in ly")
print("  • Unknown distance marked as 'u' displays as 'Unknown'")

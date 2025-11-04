"""
Distance and Diameter Display - Implementation Summary
======================================================

UNIT RULES IMPLEMENTED:

1. GALAXIES (object_type = 'Gal'):
   - Distance: Millions of Light Years (Mly)
   - Physical Size: Thousands of Light Years (kly)
   
   Example: M 031 (Andromeda Galaxy)
   - Distance: 2.50 Mly
   - Physical Size: 150.0 kly

2. OTHER OBJECTS (Nebulae, Clusters, etc.):
   - Distance: Light Years (ly)
   - Physical Size: Light Years (ly)
   
   Example: M 042 (Orion Nebula)
   - Distance: 1,600 ly
   - Physical Size: 30.0 ly

3. UNKNOWN DISTANCE (marked as 'u'):
   - Displays as "Distance: Unknown"

4. MISSING OR INVALID DATA:
   - Fields with NaN, None, empty, or 'u' (for diameter) are not displayed

DATABASE COLUMNS:
- [Unnamed: 7] = distance (raw numeric value or 'u')
- [Unnamed: 8] = diameter (raw numeric value or 'u')
- [Unnamed: 3] = object_type ('Gal', 'Neb', etc.)

DISPLAY LOCATION:
- Information appears in the "📝 Notes" section of the Object Card
- Displayed BEFORE the original notes text
- Each piece of information on a separate line

FORMAT EXAMPLES:
================

GALAXIES:
---------
M 031 (Andromeda Galaxy)
  🌌 Distance: 2.50 Mly
  📏 Physical Size: 150.0 kly
  [Original notes...]

M 051 (Whirlpool Galaxy)
  🌌 Distance: 25.00 Mly
  📏 Physical Size: 80.0 kly
  [Original notes...]

NEBULAE:
--------
M 001 (Crab Nebula)
  🌌 Distance: 6,500 ly
  📏 Physical Size: 13.0 ly
  [Original notes...]

IC 1805 (Heart Nebula)
  🌌 Distance: 7,500 ly
  📏 Physical Size: 190.0 ly
  [Original notes...]

UNKNOWN DISTANCE:
-----------------
Example Object
  🌌 Distance: Unknown
  📏 Physical Size: 50.0 ly
  [Original notes...]

CODE IMPLEMENTATION:
====================
File: src/gui/pyside6_target_selection.py
Function: show_object_detail_dialog()

Key logic:
1. Determine object type: is_galaxy = (object_type == 'Gal')
2. Format distance based on type and value ('u' = Unknown)
3. Format diameter based on type
4. Display in Notes section with emoji icons
"""

print(__doc__)

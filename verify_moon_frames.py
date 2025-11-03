"""Verify which NASA SVS frame corresponds to which moon phase."""

# NASA SVS frames 1-29 represent a full lunar cycle
# Frame 1 should be New Moon (0% illumination, cycle position 0.0)
# Frame 15 should be Full Moon (100% illumination, cycle position 0.5)
# Frame 29 should be back near New Moon (0% illumination, cycle position ~0.97)

# Current situation:
# Cycle position: 0.4730 (94.6% illumination) - almost full moon
# Current calculation: frame_num = int(0.4730 * 29) + 1 = int(13.717) + 1 = 14

# But frame 14 is close to new moon, not full moon!
# This means the frame sequence might be:
# - Starting from new moon at frame 1
# - But which direction? 

# Let's check: if frame 15 = full moon (cycle 0.5), then:
# Frame 1 = cycle 0.0 (new)
# Frame 15 = cycle 0.5 (full)
# Frame 29 = cycle 0.966 (waning crescent)

# So the formula should be: frame = cycle_position * 29 + 1
# But that gives us frame 14 for cycle 0.4730

# Wait - maybe the issue is that cycle_position 0.4730 should map closer to frame 15?
# Let's recalculate: 0.4730 * 29 = 13.717
# 0.5 * 29 = 14.5

print("Testing moon phase frame mapping:")
print()

cycle_position = 0.4730
print(f"Current cycle position: {cycle_position:.4f} (94.6% illumination)")
print(f"Expected: Almost full moon (just before full)")
print()

# Method 1: Current (wrong)
frame1 = int(cycle_position * 29) + 1
print(f"Method 1 - int(cycle * 29) + 1:")
print(f"  Frame: {frame1}")
print(f"  Problem: Frame 14 is too early in cycle")
print()

# Method 2: Round instead of int
frame2 = round(cycle_position * 29) + 1
print(f"Method 2 - round(cycle * 29) + 1:")
print(f"  Frame: {frame2}")
print()

# Method 3: Direct mapping with proper rounding
frame3 = int(cycle_position * 30) + 1
frame3 = max(1, min(29, frame3))
print(f"Method 3 - int(cycle * 30) + 1:")
print(f"  Frame: {frame3}")
print()

# Let's think about this differently
# Frame 1 = New Moon = cycle 0.0/29 = 0.0000
# Frame 15 = Full Moon = cycle 14/29 = 0.4828
# Frame 29 = Waning Crescent = cycle 28/29 = 0.9655

print("Expected frame numbers for key phases:")
print(f"  New Moon (cycle 0.00): Frame 1")
print(f"  First Quarter (cycle 0.25): Frame {int(0.25 * 29) + 1}")
print(f"  Full Moon (cycle 0.50): Frame {int(0.50 * 29) + 1}")
print(f"  Last Quarter (cycle 0.75): Frame {int(0.75 * 29) + 1}")
print()

print(f"For cycle 0.4730 (almost full moon):")
print(f"  Using int(): Frame {int(0.4730 * 29) + 1} = {int(0.4730 * 29) + 1}")
print(f"  Using round(): Frame {round(0.4730 * 29) + 1} = {round(0.4730 * 29) + 1}")
print()

# The issue: frame numbering starts at 1, not 0
# So: frame = round(cycle_position * 28) + 1 might work better?
frame4 = round(cycle_position * 28) + 1
print(f"Method 4 - round(cycle * 28) + 1:")
print(f"  Frame: {frame4}")

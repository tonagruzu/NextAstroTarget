"""Verify the actual moon phase images match their angles."""

# Frame 14 should be at (14-1)/28 * 360 = 13/28 * 360 = 167.1°
# At 167.1°, illumination = 167.1 / 180 = 0.928 = 92.8%
# This should be Waxing Gibbous (almost full)

# But you're seeing First Quarter (50% illumination, 90°)

# Frame 6 or 7:
# Frame 6: (6-1)/28 * 360 = 5/28 * 360 = 64.3° → illumination 35.7%
# Frame 7: (7-1)/28 * 360 = 6/28 * 360 = 77.1° → illumination 42.8%

# Today's actual: 170.5° → illumination 94.7%

print("Analysis of moon phase images:")
print()

for frame in [6, 7, 13, 14, 15]:
    angle = (frame - 1) / 28.0 * 360
    if angle <= 180:
        illumination = angle / 180.0 * 100
    else:
        illumination = (360 - angle) / 180.0 * 100
    
    if angle < 22.5:
        phase = "New Moon"
    elif angle < 67.5:
        phase = "Waxing Crescent"
    elif angle < 112.5:
        phase = "First Quarter"
    elif angle < 157.5:
        phase = "Waxing Gibbous"
    elif angle < 202.5:
        phase = "Full Moon"
    else:
        phase = "Other"
    
    print(f"Frame {frame:2d}: {angle:5.1f}° = {illumination:4.1f}% illumination = {phase}")

print()
print("Today's actual moon: 170.5° = 94.7% illumination = Waxing Gibbous")
print()
print("If frame 14 looks like First Quarter (50%), the images are REVERSED!")
print("The drawing function might be drawing the DARK side instead of the LIT side!")

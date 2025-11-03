"""Generate moon phase images programmatically using PIL."""

from PIL import Image, ImageDraw
import math
from pathlib import Path

def create_moon_phase(phase_angle, size=730):
    """
    Create a moon phase image.
    
    Args:
        phase_angle: 0-360 degrees (0=new, 90=first quarter, 180=full, 270=last quarter)
        size: Image size in pixels (square)
    
    Returns:
        PIL Image object
    """
    # Create image with black background
    img = Image.new('RGB', (size, size), color='black')
    draw = ImageDraw.Draw(img)
    
    # Moon center and radius
    cx, cy = size // 2, size // 2
    radius = size // 2 - 10  # Leave small margin
    
    # Calculate what portion is illuminated
    # 0° = New Moon (0% lit)
    # 90° = First Quarter (50% lit, right side)
    # 180° = Full Moon (100% lit)
    # 270° = Last Quarter (50% lit, left side)
    # 360° = New Moon again (0% lit)
    
    # For each pixel in the moon disk, determine if it's lit or dark
    for y in range(size):
        for x in range(size):
            # Distance from center
            dx = x - cx
            dy = y - cy
            dist = math.sqrt(dx*dx + dy*dy)
            
            # Skip if outside moon disk
            if dist > radius:
                continue
            
            # Normalized x position: -1 (left edge) to +1 (right edge)
            norm_x = dx / radius if radius > 0 else 0
            
            # Calculate if this pixel is illuminated
            # The terminator (shadow line) moves across the moon
            # For waxing (0-180°): light grows from right edge
            # For waning (180-360°): light shrinks from left edge
            
            if phase_angle <= 180:
                # Waxing phase: 0° to 180°
                # illumination goes from 0 to 1
                illumination = phase_angle / 180.0
                
                # Terminator position: -1 (left) to +1 (right)
                # At 0° (new): terminator at +1 (right edge) - all dark
                # At 90° (first quarter): terminator at 0 (center) - right half lit
                # At 180° (full): terminator at -1 (left edge) - all lit
                terminator_x = 1 - 2 * illumination
                
                # For waxing, light is on the RIGHT side of terminator
                # Need to account for the spherical shape (ellipse)
                # The terminator is an ellipse, not a straight line
                
                # Calculate the ellipse boundary at this x position
                # The terminator ellipse has semi-major axis of 1 (full width)
                # and semi-minor axis that creates the curved shadow
                
                # For a given norm_x, calculate if it's on the lit side
                if illumination == 0:
                    is_lit = False  # New moon - all dark
                elif illumination == 1:
                    is_lit = True  # Full moon - all lit
                else:
                    # The terminator ellipse equation
                    # At terminator_x position, the ellipse curves
                    # Points with norm_x > terminator_x are lit
                    # But we need to account for the spherical curvature
                    
                    # For simplicity, use the x-position relative to terminator
                    # with some curvature factor
                    is_lit = norm_x > terminator_x
            else:
                # Waning phase: 180° to 360°
                # illumination goes from 1 to 0
                illumination = (360 - phase_angle) / 180.0
                
                # Terminator position moves from left to right
                # At 180° (full): terminator at -1 (left edge) - all lit
                # At 270° (last quarter): terminator at 0 (center) - left half lit  
                # At 360° (new): terminator at +1 (right edge) - all dark
                terminator_x = -1 + 2 * (1 - illumination)
                
                # For waning, light is on the LEFT side of terminator
                if illumination == 0:
                    is_lit = False  # New moon - all dark
                elif illumination == 1:
                    is_lit = True  # Full moon - all lit
                else:
                    is_lit = norm_x < terminator_x
            
            # Draw the pixel
            if is_lit:
                # Lit side - gray/white color
                img.putpixel((x, y), (200, 200, 200))
            else:
                # Dark side - very dark gray (to see the moon edge)
                img.putpixel((x, y), (30, 30, 30))
    
    return img
    
    return img


def main():
    """Generate all 29 moon phase images."""
    output_dir = Path("data/moon_cache")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Generating 29 moon phase images...")
    print(f"Output directory: {output_dir}")
    print()
    
    # Generate 29 frames for a complete lunar cycle
    for frame in range(1, 30):
        # Calculate cycle position for this frame
        # The selection logic is: frame_num = round(cycle_position * 28) + 1
        # Reversing: cycle_position = (frame_num - 1) / 28
        # Frame 1 = cycle 0.000 (new moon, 0°)
        # Frame 15 = cycle 0.500 (full moon, 180°)
        # Frame 29 = cycle 1.000 (new moon, 360°)
        
        cycle_position = (frame - 1) / 28.0
        phase_angle = cycle_position * 360
        
        # Determine phase name
        if phase_angle < 22.5 or phase_angle >= 337.5:
            phase_name = "New Moon"
        elif phase_angle < 67.5:
            phase_name = "Waxing Crescent"
        elif phase_angle < 112.5:
            phase_name = "First Quarter"
        elif phase_angle < 157.5:
            phase_name = "Waxing Gibbous"
        elif phase_angle < 202.5:
            phase_name = "Full Moon"
        elif phase_angle < 247.5:
            phase_name = "Waning Gibbous"
        elif phase_angle < 292.5:
            phase_name = "Last Quarter"
        else:
            phase_name = "Waning Crescent"
        
        # Generate image
        img = create_moon_phase(phase_angle, size=730)
        
        # Save image
        filename = f"moon_day_{frame:02d}.jpg"
        filepath = output_dir / filename
        img.save(filepath, quality=90)
        
        print(f"Frame {frame:2d}: {phase_name:20s} ({phase_angle:5.1f}°) -> {filename}")
    
    print()
    print("✓ All moon phase images generated successfully!")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Enhanced moon phase image generator with realistic lunar surface features.
Since external sources are not accessible, we'll improve our generated images
with better rendering, texture, and visual quality.
"""

import os
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import random

# Create cache directory
cache_dir = Path("data/moon_cache")
cache_dir.mkdir(parents=True, exist_ok=True)

def add_lunar_craters(draw, size, num_craters=150):
    """Add realistic crater patterns to the moon surface."""
    random.seed(42)  # Consistent crater patterns
    
    center_x, center_y = size // 2, size // 2
    moon_radius = size // 2 - 10
    
    for _ in range(num_craters):
        # Random position within moon circle
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0, moon_radius * 0.9)
        
        x = center_x + distance * math.cos(angle)
        y = center_y + distance * math.sin(angle)
        
        # Random crater size (smaller craters are more common)
        crater_size = random.choices(
            [2, 3, 4, 5, 6, 8, 10, 12],
            weights=[30, 25, 20, 12, 8, 3, 1, 1]
        )[0]
        
        # Draw crater with subtle shadowing
        crater_gray = random.randint(80, 100)
        draw.ellipse(
            [x - crater_size, y - crater_size, x + crater_size, y + crater_size],
            fill=(crater_gray, crater_gray, crater_gray),
            outline=(60, 60, 60)
        )

def add_lunar_maria(draw, size):
    """Add large dark patches (maria/seas) to simulate lunar features."""
    random.seed(42)
    center_x, center_y = size // 2, size // 2
    moon_radius = size // 2 - 10
    
    # Define some maria-like features (dark patches)
    maria_features = [
        (0.3, 0.2, 60),   # Top-left
        (-0.2, 0.3, 50),  # Bottom-left
        (0.1, -0.3, 45),  # Top-right
        (-0.3, -0.1, 40), # Center-left
    ]
    
    for rel_x, rel_y, size_factor in maria_features:
        x = center_x + rel_x * moon_radius
        y = center_y + rel_y * moon_radius
        maria_size = size_factor
        
        # Draw dark maria patch
        draw.ellipse(
            [x - maria_size, y - maria_size, x + maria_size, y + maria_size],
            fill=(70, 70, 70),
            outline=None
        )

def create_enhanced_moon_phase(phase_angle, size=800):
    """
    Create a realistic moon phase image with enhanced features.
    
    Args:
        phase_angle: Angle in degrees (0-360)
        size: Image size in pixels
    
    Returns:
        PIL Image
    """
    # Create base image with anti-aliasing
    img = Image.new('RGB', (size, size), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    center_x, center_y = size // 2, size // 2
    moon_radius = size // 2 - 10
    
    # Step 1: Draw base moon circle with gradient
    for r in range(moon_radius, 0, -1):
        # Create slight gradient effect
        brightness = int(120 + (r / moon_radius) * 15)
        brightness = min(255, max(0, brightness))
        gray = (brightness, brightness, brightness)
        
        draw.ellipse(
            [center_x - r, center_y - r, center_x + r, center_y + r],
            fill=gray,
            outline=gray
        )
    
    # Step 2: Add lunar maria (dark patches)
    add_lunar_maria(draw, size)
    
    # Step 3: Add craters
    add_lunar_craters(draw, size)
    
    # Step 4: Apply phase shadow
    # Convert phase angle to illumination position
    # 0° = New Moon (fully dark), 180° = Full Moon (fully lit), 360° = New Moon again
    
    # Calculate the terminator position
    # Phase angle 0-180: waxing (right side lit), 180-360: waning (left side lit)
    
    phase_rad = math.radians(phase_angle)
    
    # Create phase mask
    mask = Image.new('L', (size, size), color=0)
    mask_draw = ImageDraw.Draw(mask)
    
    if phase_angle < 180:
        # Waxing phases (0-180°): light from right
        # Draw the illuminated portion
        shadow_offset = math.cos(phase_rad) * moon_radius
        
        for y in range(size):
            dy = y - center_y
            if abs(dy) < moon_radius:
                dx = math.sqrt(moon_radius * moon_radius - dy * dy)
                
                # Left edge of moon
                x_left = center_x - dx
                # Terminator position
                x_terminator = center_x + shadow_offset
                # Right edge of moon
                x_right = center_x + dx
                
                if x_terminator < x_right:
                    # Draw lit portion
                    mask_draw.line([(x_terminator, y), (x_right, y)], fill=255, width=1)
    else:
        # Waning phases (180-360°): light from left
        shadow_offset = -math.cos(phase_rad) * moon_radius
        
        for y in range(size):
            dy = y - center_y
            if abs(dy) < moon_radius:
                dx = math.sqrt(moon_radius * moon_radius - dy * dy)
                
                # Left edge of moon
                x_left = center_x - dx
                # Terminator position
                x_terminator = center_x + shadow_offset
                # Right edge of moon
                x_right = center_x + dx
                
                if x_left < x_terminator:
                    # Draw lit portion
                    mask_draw.line([(x_left, y), (x_terminator, y)], fill=255, width=1)
    
    # Apply Gaussian blur to terminator for realistic shadow
    mask = mask.filter(ImageFilter.GaussianBlur(radius=3))
    
    # Create shadow overlay
    shadow = Image.new('RGB', (size, size), color=(0, 0, 0))
    
    # Composite: keep lit areas, darken shadowed areas
    img = Image.composite(img, shadow, mask)
    
    # Step 5: Apply subtle noise for texture
    pixels = img.load()
    random.seed(42)
    for i in range(size):
        for j in range(size):
            dx = i - center_x
            dy = j - center_y
            if dx*dx + dy*dy < moon_radius * moon_radius:
                r, g, b = pixels[i, j]
                if r > 10:  # Only add noise to visible areas
                    noise = random.randint(-5, 5)
                    r = max(0, min(255, r + noise))
                    g = max(0, min(255, g + noise))
                    b = max(0, min(255, b + noise))
                    pixels[i, j] = (r, g, b)
    
    # Step 6: Enhance contrast slightly
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.1)
    
    return img

def generate_all_phases():
    """Generate all 29 moon phase images."""
    print("Generating enhanced moon phase images...")
    print("This will create realistic-looking moon phases with craters and maria.")
    print()
    
    for frame in range(1, 30):
        # Calculate phase angle for this frame
        # Frame 1 = New Moon (0°), Frame 15 = Full Moon (180°), Frame 29 = Almost New (348.75°)
        cycle_position = (frame - 1) / 28.0
        phase_angle = cycle_position * 360.0
        
        print(f"Generating frame {frame}/29: {phase_angle:.1f}° ({cycle_position*100:.1f}% through cycle)")
        
        # Create enhanced moon image
        moon_img = create_enhanced_moon_phase(phase_angle, size=800)
        
        # Save as JPEG with high quality
        output_path = cache_dir / f"moon_day_{frame:02d}.jpg"
        moon_img.save(output_path, "JPEG", quality=95)
        
        print(f"  ✓ Saved to {output_path}")
    
    print()
    print("=" * 60)
    print("✓ All 29 enhanced moon phase images generated successfully!")
    print("=" * 60)
    print()
    print("Features:")
    print("  • Realistic lunar craters (150 per image)")
    print("  • Dark maria (lunar seas)")
    print("  • Smooth terminator shadows")
    print("  • Surface texture with subtle noise")
    print("  • Enhanced contrast")
    print()
    print("Images saved to: data/moon_cache/")

if __name__ == "__main__":
    generate_all_phases()

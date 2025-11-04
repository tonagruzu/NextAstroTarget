#!/usr/bin/env python3
"""
Generate realistic moon phase images from the uploaded full moon photo.
Applies phase-accurate shadows with realistic terminator transitions.
"""

import os
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import numpy as np

# Paths
cache_dir = Path("data/moon_cache")
base_image_path = cache_dir / "full.png"

def create_phase_mask(size, phase_angle):
    """
    Create a phase mask for the moon with realistic spherical lighting.
    
    Args:
        size: Size of the mask (width, height)
        phase_angle: Angle in degrees (0-360)
            0° = New Moon (fully dark)
            90° = First Quarter (right half lit)
            180° = Full Moon (fully lit)
            270° = Last Quarter (left half lit)
            360° = New Moon again
    
    Returns:
        PIL Image in mode 'L' (grayscale mask)
    """
    width, height = size
    center_x, center_y = width / 2.0, height / 2.0
    moon_radius = min(width, height) / 2.0 - 2
    
    # Convert phase angle to radians
    phase_rad = math.radians(phase_angle)
    
    # Calculate the sun angle
    # For waxing (0-180°): sun moves from right to front
    # For waning (180-360°): sun moves from front to left
    sun_angle = phase_rad - math.pi / 2  # Offset so 0° is from the right
    
    # Sun direction vector
    sun_x = math.cos(sun_angle)
    sun_y = 0  # Sun is always in the equatorial plane for simplicity
    sun_z = math.sin(sun_angle)
    
    # Create mask using numpy for faster processing
    mask_array = np.zeros((height, width), dtype=np.float32)
    
    # For each pixel, calculate if it's on the lit side of the sphere
    for y in range(height):
        dy = y - center_y
        
        for x in range(width):
            dx = x - center_x
            
            # Distance from center
            dist_from_center = math.sqrt(dx * dx + dy * dy)
            
            # Check if pixel is within moon circle
            if dist_from_center <= moon_radius:
                # Calculate the 3D position on the sphere surface
                # Normalize to sphere coordinates (-1 to 1)
                norm_x = dx / moon_radius
                norm_y = dy / moon_radius
                
                # Calculate z coordinate (depth) on sphere
                # z^2 + x^2 + y^2 = 1
                z_squared = 1.0 - norm_x * norm_x - norm_y * norm_y
                
                if z_squared >= 0:
                    norm_z = math.sqrt(z_squared)
                    
                    # Surface normal at this point (pointing outward from sphere)
                    normal_x = norm_x
                    normal_y = norm_y
                    normal_z = norm_z
                    
                    # Calculate dot product between surface normal and sun direction
                    # This gives us the cosine of the angle between them
                    dot_product = normal_x * sun_x + normal_y * sun_y + normal_z * sun_z
                    
                    # Only lit if the surface faces the sun (dot product > 0)
                    if dot_product > 0:
                        # Apply Lambert's cosine law for diffuse reflection
                        # This creates the realistic gradual falloff
                        brightness = dot_product
                        
                        # Apply some gamma correction to make it look more realistic
                        # and increase contrast near the terminator
                        brightness = math.pow(brightness, 0.7)
                        
                        # Apply a smooth transition zone near the terminator
                        # This creates a more gradual darkening
                        if brightness < 0.3:
                            # Enhance the gradient in the dark zone
                            brightness = brightness * brightness / 0.3
                        
                        mask_array[y, x] = brightness * 255
                    else:
                        # Dark side - but add some subtle reflected light
                        # to prevent completely black shadows
                        mask_array[y, x] = max(0, dot_product * 20)
    
    # Convert numpy array back to PIL Image
    mask = Image.fromarray(mask_array.astype(np.uint8), mode='L')
    
    # Apply gentle blur to smooth out any remaining artifacts
    # and create more realistic limb darkening
    mask = mask.filter(ImageFilter.GaussianBlur(radius=3))
    
    return mask

def create_moon_phase_from_base(base_img, phase_angle):
    """
    Create a moon phase image by applying shadow to the base full moon image.
    
    Args:
        base_img: PIL Image of the full moon
        phase_angle: Phase angle in degrees (0-360)
    
    Returns:
        PIL Image of the moon at the specified phase
    """
    # Ensure base image is in RGB mode
    if base_img.mode != 'RGB':
        base_img = base_img.convert('RGB')
    
    size = base_img.size
    
    # Create the phase mask
    phase_mask = create_phase_mask(size, phase_angle)
    
    # Create a dark shadow layer
    shadow = Image.new('RGB', size, color=(0, 0, 0))
    
    # Composite: show base image where mask is bright, shadow where mask is dark
    result = Image.composite(base_img, shadow, phase_mask)
    
    # Optional: slightly enhance contrast for better visibility
    enhancer = ImageEnhance.Contrast(result)
    result = enhancer.enhance(1.05)
    
    return result

def generate_all_phases_from_base():
    """Generate all 29 moon phase images from the base full moon image."""
    
    print("=" * 70)
    print("GENERATING MOON PHASES FROM BASE IMAGE")
    print("=" * 70)
    print()
    
    # Check if base image exists
    if not base_image_path.exists():
        print(f"❌ ERROR: Base image not found at {base_image_path}")
        print("Please ensure 'full.png' exists in data/moon_cache/")
        return
    
    # Load the base full moon image
    print(f"Loading base image: {base_image_path}")
    base_img = Image.open(base_image_path)
    print(f"  Image size: {base_img.size[0]}x{base_img.size[1]}")
    print(f"  Image mode: {base_img.mode}")
    print()
    
    # Resize if necessary (we want consistent size, ideally 800x800 or similar)
    target_size = 800
    if base_img.size[0] != target_size or base_img.size[1] != target_size:
        print(f"Resizing image to {target_size}x{target_size}...")
        base_img = base_img.resize((target_size, target_size), Image.Resampling.LANCZOS)
        print("  ✓ Resized")
        print()
    
    print("Generating 29 moon phase images...")
    print()
    
    for frame in range(1, 30):
        # Calculate phase angle for this frame
        # Frame 1 = New Moon (0°), Frame 15 = Full Moon (180°), Frame 29 = Almost New (348.75°)
        cycle_position = (frame - 1) / 28.0
        phase_angle = cycle_position * 360.0
        
        # Calculate illumination percentage for display
        illumination = (1 - math.cos(math.radians(phase_angle))) / 2 * 100
        
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
        
        print(f"Frame {frame:2}/29: {phase_angle:6.2f}° | {illumination:5.1f}% | {phase_name:16}")
        
        # Create the moon phase image
        moon_phase = create_moon_phase_from_base(base_img, phase_angle)
        
        # Save as JPEG with high quality
        output_path = cache_dir / f"moon_day_{frame:02d}.jpg"
        moon_phase.save(output_path, "JPEG", quality=95)
        
        print(f"  ✓ Saved: {output_path.name}")
    
    print()
    print("=" * 70)
    print("✓ ALL MOON PHASES GENERATED SUCCESSFULLY!")
    print("=" * 70)
    print()
    print("Features:")
    print("  • Based on your uploaded full moon photo")
    print("  • Realistic phase-accurate shadows")
    print("  • Smooth terminator transitions with gradient")
    print("  • Proper waxing/waning direction")
    print("  • 29 frames covering the complete lunar cycle")
    print()
    print(f"Images saved to: {cache_dir}/")
    print()

if __name__ == "__main__":
    generate_all_phases_from_base()

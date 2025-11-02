#!/usr/bin/env python3
"""
NextAstroTarget Application Icon Creator
Creates a custom astronomical-themed icon for the application.

The icon features:
- Telescope/targeting crosshairs symbolizing precision target selection
- Stars representing deep sky objects
- Gradient background suggesting night sky
- Professional astronomical theme
"""

from PIL import Image, ImageDraw, ImageFont
import os
import math

def create_app_icon():
    """Create the NextAstroTarget application icon."""
    
    # Icon sizes for different contexts
    sizes = [16, 24, 32, 48, 64, 128, 256]
    
    # Create the largest version first (256x256)
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Color scheme - deep space theme
    bg_color = (20, 25, 40, 255)  # Dark blue-black
    primary_color = (100, 150, 255, 255)  # Light blue
    accent_color = (255, 220, 100, 255)  # Golden yellow
    crosshair_color = (200, 200, 200, 255)  # Light gray
    star_color = (255, 255, 255, 255)  # White
    
    # Draw background circle with gradient effect
    center = size // 2
    radius = center - 8
    
    # Create gradient background
    for i in range(radius):
        alpha = int(255 * (1 - i / radius))
        color = (20 + i//4, 25 + i//8, 40 + i//6, min(255, alpha + 100))
        draw.ellipse([center - radius + i, center - radius + i, 
                     center + radius - i, center + radius - i], fill=color)
    
    # Draw outer ring
    ring_width = 6
    draw.ellipse([center - radius, center - radius, 
                 center + radius, center + radius], 
                outline=primary_color, width=ring_width)
    
    # Draw targeting crosshairs
    crosshair_length = radius * 0.7
    crosshair_width = 4
    
    # Horizontal crosshair
    draw.rectangle([center - crosshair_length//2, center - crosshair_width//2,
                   center + crosshair_length//2, center + crosshair_width//2],
                  fill=crosshair_color)
    
    # Vertical crosshair
    draw.rectangle([center - crosshair_width//2, center - crosshair_length//2,
                   center + crosshair_width//2, center + crosshair_length//2],
                  fill=crosshair_color)
    
    # Draw central targeting circle
    target_radius = 20
    draw.ellipse([center - target_radius, center - target_radius,
                 center + target_radius, center + target_radius],
                outline=accent_color, width=3)
    
    # Draw inner target dot
    dot_radius = 6
    draw.ellipse([center - dot_radius, center - dot_radius,
                 center + dot_radius, center + dot_radius],
                fill=accent_color)
    
    # Add stars around the crosshairs
    star_positions = [
        (center - 60, center - 60), (center + 60, center - 60),
        (center - 60, center + 60), (center + 60, center + 60),
        (center - 80, center), (center + 80, center),
        (center, center - 80), (center, center + 80),
        (center - 45, center - 90), (center + 45, center + 90),
        (center - 90, center - 45), (center + 90, center + 45)
    ]
    
    for x, y in star_positions:
        if (x - center)**2 + (y - center)**2 < (radius - 20)**2:  # Only inside the circle
            draw_star(draw, x, y, 4, star_color)
    
    # Add small nebula-like effects
    nebula_positions = [
        (center - 40, center - 25, 8),
        (center + 35, center + 40, 6),
        (center - 25, center + 35, 5)
    ]
    
    for x, y, r in nebula_positions:
        # Create a soft glow effect
        for i in range(r, 0, -1):
            alpha = int(50 * i / r)
            glow_color = (*primary_color[:3], alpha)
            draw.ellipse([x - i, y - i, x + i, y + i], fill=glow_color)
    
    # Save the main icon
    base_icon = img.copy()
    
    # Create .ico file with multiple sizes
    icon_images = []
    for icon_size in sizes:
        if icon_size == 256:
            icon_images.append(base_icon)
        else:
            resized = base_icon.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
            icon_images.append(resized)
    
    # Ensure assets directory exists
    assets_dir = "assets"
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
    
    # Save as .ico file
    icon_images[0].save(
        os.path.join(assets_dir, "icon.ico"),
        format='ICO',
        sizes=[(s, s) for s in sizes]
    )
    
    # Save as PNG files for reference
    base_icon.save(os.path.join(assets_dir, "icon_256.png"))
    icon_images[4].save(os.path.join(assets_dir, "icon_64.png"))  # 64x64
    icon_images[3].save(os.path.join(assets_dir, "icon_48.png"))  # 48x48
    icon_images[2].save(os.path.join(assets_dir, "icon_32.png"))  # 32x32
    
    print("✅ Application icon created successfully!")
    print(f"   📁 Location: {os.path.abspath(os.path.join(assets_dir, 'icon.ico'))}")
    print(f"   📏 Sizes included: {sizes}")
    print(f"   🎨 Theme: Astronomical targeting crosshairs with stars")
    return True

def draw_star(draw, x, y, size, color):
    """Draw a star shape at the given position."""
    points = []
    for i in range(10):  # 5-pointed star = 10 points
        angle = i * math.pi / 5
        if i % 2 == 0:
            # Outer points
            px = x + size * math.cos(angle - math.pi / 2)
            py = y + size * math.sin(angle - math.pi / 2)
        else:
            # Inner points
            px = x + (size * 0.4) * math.cos(angle - math.pi / 2)
            py = y + (size * 0.4) * math.sin(angle - math.pi / 2)
        points.append((px, py))
    
    draw.polygon(points, fill=color)

if __name__ == "__main__":
    print("🎨 Creating NextAstroTarget Application Icon...")
    print("   Theme: Astronomical targeting with deep sky objects")
    
    try:
        create_app_icon()
        print("\n🌟 Icon creation complete!")
        print("   The icon represents precision astronomical target selection")
        print("   with crosshairs, stars, and a professional space theme.")
        
    except Exception as e:
        print(f"❌ Error creating icon: {e}")
        import traceback
        traceback.print_exc()
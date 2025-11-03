#!/usr/bin/env python3
"""
Test the enhanced DSS + Astrobin image loading directly
"""

import tkinter as tk
from tkinter import ttk
import sqlite3
import requests
from PIL import Image, ImageTk
from io import BytesIO
import os

class ImageTestWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("DSS + Astrobin Image Test")
        self.root.geometry("800x600")
        self.image_cache = {}
        
        # Create UI
        self.create_ui()
        self.load_test_objects()
        
    def create_ui(self):
        # Object selection
        self.objects_frame = ttk.Frame(self.root)
        self.objects_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(self.objects_frame, text="Select Object:").pack(side='left')
        self.object_var = tk.StringVar()
        self.object_combo = ttk.Combobox(self.objects_frame, textvariable=self.object_var, width=30)
        self.object_combo.pack(side='left', padx=5)
        self.object_combo.bind('<<ComboboxSelected>>', self.on_object_selected)
        
        # Load button
        self.load_button = ttk.Button(self.objects_frame, text="Load Image", command=self.load_image)
        self.load_button.pack(side='left', padx=5)
        
        # Image display area
        self.image_frame = tk.Frame(self.root, bg='black')
        self.image_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Status
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(self.root, textvariable=self.status_var)
        self.status_label.pack(fill='x', padx=10, pady=5)
        
    def load_test_objects(self):
        """Load objects from database."""
        try:
            db_path = os.path.join('data', 'astro_targets.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    [Imm Deep Sky Compendium -  2023 - 4th Edition] as object_name,
                    [Unnamed: 12] as ra_degrees,
                    [Unnamed: 14] as dec_degrees,
                    [Unnamed: 48] as astrobin_id
                FROM Main 
                WHERE [Imm Deep Sky Compendium -  2023 - 4th Edition] IS NOT NULL
                AND [Imm Deep Sky Compendium -  2023 - 4th Edition] != ''
                ORDER BY [Imm Deep Sky Compendium -  2023 - 4th Edition]
                LIMIT 50
            """)
            
            self.objects = cursor.fetchall()
            conn.close()
            
            # Populate combo box
            object_names = [obj[0] for obj in self.objects if obj[0]]
            self.object_combo['values'] = object_names
            if object_names:
                self.object_combo.set(object_names[0])
                
            self.status_var.set(f"Loaded {len(object_names)} objects")
            
        except Exception as e:
            self.status_var.set(f"Error loading objects: {e}")
            
    def on_object_selected(self, event=None):
        self.load_image()
        
    def load_image(self):
        """Load image for selected object."""
        # Clear previous image
        for widget in self.image_frame.winfo_children():
            widget.destroy()
            
        selected_name = self.object_var.get()
        if not selected_name:
            return
            
        # Find object data
        obj_data = None
        for obj in self.objects:
            if obj[0] == selected_name:
                obj_data = obj
                break
                
        if not obj_data:
            return
            
        object_name, ra_deg, dec_deg, astrobin_id = obj_data
        
        self.status_var.set(f"Loading image for {object_name}...")
        self.root.update()
        
        # Try DSS first if we have coordinates
        image_loaded = False
        if ra_deg and dec_deg:
            try:
                ra_float = float(ra_deg)
                dec_float = float(dec_deg)
                image_loaded = self.load_dss_image(ra_float, dec_float, object_name)
            except (ValueError, TypeError):
                pass
                
        # Try Astrobin as fallback
        if not image_loaded and astrobin_id:
            try:
                if astrobin_id != "0" and str(astrobin_id).isdigit() and int(float(astrobin_id)) > 0:
                    image_loaded = self.load_astrobin_image(str(int(float(astrobin_id))), object_name)
            except (ValueError, TypeError):
                pass
                
        if not image_loaded:
            # Show info instead
            info_label = tk.Label(
                self.image_frame, 
                text=f"No image available for {object_name}\\nRA: {ra_deg}°, Dec: {dec_deg}°\\nAstrobin ID: {astrobin_id}",
                bg='navy', 
                fg='white',
                font=('Arial', 12),
                justify='center'
            )
            info_label.pack(expand=True)
            self.status_var.set("No image sources available")
            
    def load_dss_image(self, ra_deg, dec_deg, object_name):
        """Load image from DSS."""
        try:
            cache_key = f"dss_{ra_deg:.3f}_{dec_deg:.3f}"
            
            if cache_key in self.image_cache:
                if self.image_cache[cache_key]:
                    self.display_image(self.image_cache[cache_key], "🔭 Digitized Sky Survey")
                    return True
                return False
                
            # DSS URL
            dss_url = f"https://archive.stsci.edu/cgi-bin/dss_search?v=poss2ukstu_red&r={ra_deg:.6f}&d={dec_deg:.6f}&e=J2000&h=12.0&w=12.0&f=gif&c=none&fov=NONE&v3="
            
            headers = {
                'User-Agent': 'NextAstroTarget/1.1.0 (Astronomy Application)',
                'Accept': 'image/gif,image/*,*/*;q=0.8'
            }
            
            response = requests.get(dss_url, headers=headers, timeout=10)
            
            if response.status_code == 200 and len(response.content) > 10000:
                content_type = response.headers.get('content-type', '').lower()
                if 'image' in content_type:
                    img = Image.open(BytesIO(response.content))
                    img.thumbnail((400, 350), Image.Resampling.LANCZOS)
                    
                    photo = ImageTk.PhotoImage(img)
                    self.image_cache[cache_key] = photo
                    
                    self.display_image(photo, "🔭 Digitized Sky Survey")
                    self.status_var.set(f"DSS image loaded: {img.size[0]}x{img.size[1]} pixels")
                    return True
                    
            self.image_cache[cache_key] = None
            return False
            
        except Exception as e:
            print(f"DSS error: {e}")
            return False
            
    def load_astrobin_image(self, astrobin_id, object_name):
        """Load image from Astrobin."""
        try:
            cache_key = f"astrobin_{astrobin_id}"
            
            if cache_key in self.image_cache:
                if self.image_cache[cache_key]:
                    self.display_image(self.image_cache[cache_key], f"📸 AstroBin ID: {astrobin_id}")
                    return True
                return False
                
            url = f"https://www.astrobin.com/{astrobin_id}/0/rawthumb/regular/"
            
            headers = {
                'User-Agent': 'NextAstroTarget/1.1.0 (Astronomy Application)',
                'Accept': 'image/*,*/*;q=0.8'
            }
            
            response = requests.get(url, headers=headers, timeout=8)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                if 'image' in content_type:
                    img = Image.open(BytesIO(response.content))
                    img.thumbnail((400, 350), Image.Resampling.LANCZOS)
                    
                    photo = ImageTk.PhotoImage(img)
                    self.image_cache[cache_key] = photo
                    
                    self.display_image(photo, f"📸 AstroBin ID: {astrobin_id}")
                    self.status_var.set(f"Astrobin image loaded: {img.size[0]}x{img.size[1]} pixels")
                    return True
                    
            self.image_cache[cache_key] = None
            return False
            
        except Exception as e:
            print(f"Astrobin error: {e}")
            return False
            
    def display_image(self, photo, credit_text):
        """Display image in the frame."""
        image_label = tk.Label(self.image_frame, image=photo, bg='black')
        image_label.pack(pady=10)
        
        credit_label = tk.Label(
            self.image_frame,
            text=credit_text,
            font=("Arial", 10),
            bg="black",
            fg="gray"
        )
        credit_label.pack()
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ImageTestWindow()
    app.run()
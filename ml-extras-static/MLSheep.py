#!/usr/bin/env python3
"""
MLFlame - Simple flame fractal generator
Just pretty math, no complexity
"""
import os
import tkinter as tk
import random
import math
from colorsys import hsv_to_rgb

class FlameGenerator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MLFlame")
        self.root.geometry("1280x720")
        self.root.configure(bg='black')
        
        # Canvas that resizes
        self.canvas = tk.Canvas(self.root, bg='black', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Get initial size
        self.root.update()
        self.width = self.canvas.winfo_width()
        self.height = self.canvas.winfo_height()
        
        # Transform functions (simplified)
        self.transforms = [
            self.linear,
            self.sinusoidal,
            self.spherical,
            self.swirl,
            self.horseshoe,
            self.polar,
            self.hyperbolic  # New transform
        ]
        
        # Pick 1-6 random transforms
        self.active_transforms = random.sample(self.transforms, random.randint(2, 6))
        
        # Julia effect variables
        self.julia_effect = False
        self.julia_c = (0, 0)
        
        # Color palette
        self.hue_shift = random.random()
        
        # Bind events
        self.canvas.bind('<Button-1>', lambda e: self.regenerate())
        self.root.bind('<space>', lambda e: self.regenerate())
        self.root.bind('<Escape>', lambda e: self.root.quit())
        self.root.bind('<Configure>', self.on_resize)
        
        # Initial generation
        self.generate()

    # Quick addition to MLFlame for image export
    def save_to_file(self, filename="flame_bg.png"):
        """Save fractal by regenerating directly to image"""
        from PIL import Image, ImageDraw
        
        # Create image
        img = Image.new('RGB', (self.width, self.height), 'black')
        draw = ImageDraw.Draw(img)
        
        # Same generation logic but draw to image
        scale = min(self.width, self.height) / 4
        cx = self.width / 2
        cy = self.height / 2
        
        x, y = random.uniform(-1, 1), random.uniform(-1, 1)
        
        for i in range(10000):
            transform = random.choice(self.active_transforms)
            x, y = transform(x, y)
            
            if self.julia_effect:
                x, y = x + self.julia_c[0], y + self.julia_c[1]
                
            x += random.uniform(-0.01, 0.01)
            y += random.uniform(-0.01, 0.01)
            
            if abs(x) > 10 or abs(y) > 10:
                x, y = random.uniform(-1, 1), random.uniform(-1, 1)
                continue
                
            if i > 20:
                sx = int(cx + x * scale)
                sy = int(cy + y * scale)
                
                if 0 <= sx < self.width and 0 <= sy < self.height:
                    hue = (self.hue_shift + i/10000) % 1.0
                    brightness = min(1.0, 0.2 + (i/10000)*0.8)
                    r, g, b = hsv_to_rgb(hue, 0.8, brightness)
                    color = (int(r*255), int(g*255), int(b*255))
                    draw.point((sx, sy), fill=color)
    
        img.save(filename)
        print(f"Saved to {filename}")
        
    def linear(self, x, y):
        """Identity transform"""
        return x, y
    
    def sinusoidal(self, x, y):
        """Sine waves"""
        return math.sin(x), math.sin(y)
    
    def spherical(self, x, y):
        """Bubble effect"""
        r2 = x*x + y*y + 0.0001
        return x/r2, y/r2
    
    def swirl(self, x, y):
        """Swirly"""
        r2 = x*x + y*y
        return x*math.sin(r2) - y*math.cos(r2), x*math.cos(r2) + y*math.sin(r2)
    
    def horseshoe(self, x, y):
        """Horseshoe bend"""
        r = math.sqrt(x*x + y*y) + 0.0001
        return (x-y)*(x+y)/r, 2*x*y/r
    
    def polar(self, x, y):
        """Polar coordinates"""
        theta = math.atan2(y, x)
        r = math.sqrt(x*x + y*y)
        return theta/math.pi, r - 1
    
    def hyperbolic(self, x, y):
        """Hyperbolic transform"""
        r = math.sqrt(x*x + y*y)
        theta = math.atan2(y, x)
        return math.sin(theta) / r, r * math.cos(theta)
    
    def on_resize(self, event):
        """Handle window resize"""
        if event.widget == self.root:
            # Get new size
            new_width = self.canvas.winfo_width()
            new_height = self.canvas.winfo_height()
            
            # Only regenerate if size actually changed significantly
            if abs(new_width - self.width) > 10 or abs(new_height - self.height) > 10:
                self.width = new_width
                self.height = new_height
                self.generate()
    
    def generate(self):
        """Generate the fractal"""
        # Clear canvas
        self.canvas.delete('all')
        
        # Adjust point count based on canvas size
        point_count = min(20000, int((self.width * self.height) / 40))
        
        # Calculate scale based on window size
        scale = min(self.width, self.height) / 4
        cx = self.width / 2
        cy = self.height / 2
        
        # Starting point
        x, y = random.uniform(-1, 1), random.uniform(-1, 1)
        
        # Iterate
        points = []
        for i in range(point_count):
            # Choose random transform
            transform = random.choice(self.active_transforms)
            x, y = transform(x, y)
            
            # Apply Julia effect if enabled
            if self.julia_effect:
                x, y = x + self.julia_c[0], y + self.julia_c[1]
            
            # Add variation
            x += random.uniform(-0.01, 0.01)
            y += random.uniform(-0.01, 0.01)
            
            # Keep bounded
            if abs(x) > 10 or abs(y) > 10:
                x, y = random.uniform(-1, 1), random.uniform(-1, 1)
                continue
            
            # Skip first iterations (chaos game warmup)
            if i > 20:
                # Map to screen
                sx = int(cx + x * scale)
                sy = int(cy + y * scale)
                
                if 0 <= sx < self.width and 0 <= sy < self.height:
                    points.append((sx, sy, i))
        
        # Draw points with color based on iteration
        for sx, sy, i in points:
            # Color based on iteration count
            hue = (self.hue_shift + i/point_count) % 1.0
            brightness = min(1.0, 0.2 + (i/point_count)*0.8)
            r, g, b = hsv_to_rgb(hue, 0.8, brightness)
            color = f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'
            
            # Draw point (small rectangle for visibility)
            self.canvas.create_rectangle(sx, sy, sx+1, sy+1, 
                                        fill=color, outline=color)
    
    def regenerate(self):
        """New fractal with new transforms and a chance for Julia effect"""
        self.active_transforms = random.sample(self.transforms, random.randint(2, 6))
        self.hue_shift = random.random()
        
        # 50% chance for Julia effect
        if random.random() > 0.5:
            self.julia_effect = True
            # Random complex constant
            self.julia_c = (random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5))
        else:
            self.julia_effect = False
            self.julia_c = (0, 0)
            
        self.generate()
    
    def run(self):
        """Start the app"""
        print("MLFlame - Click or press space for new fractal, Esc to quit")
        print(f"Using transforms: {[t.__name__ for t in self.active_transforms]}")
        if self.julia_effect:
            print(f"Julia effect active with C = {self.julia_c}")
        self.root.mainloop()

if __name__ == "__main__":
    app = FlameGenerator()
    # If --save argument is provided, save the current fractal
    if '--save' in os.sys.argv:
        app.save_to_file()
        print("Fractal saved to flame_bg.png")
    app.run()

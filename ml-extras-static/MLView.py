#!/usr/bin/env python3
"""
MLView - Simple image viewer
Because sometimes you need to see what's on that server
"""

import tkinter as tk
from PIL import Image, ImageTk, ImageFilter, ImageOps
import sys
from pathlib import Path

class MLView:
    def __init__(self, image_path):
        self.root = tk.Tk()
        self.root.title(f"MLView - {Path(image_path).name}")
        self.root.geometry("800x600")
        self.root.configure(bg='black')
        
        # Load image
        try:
            self.original = Image.open(image_path)
            self.image = self.original.copy()
        except Exception as e:
            print(f"Error loading image: {e}")
            sys.exit(1)
        
        # Display mode
        self.emboss_mode = False
        
        # Canvas
        self.canvas = tk.Canvas(self.root, bg='black', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bindings
        self.root.bind('<Configure>', self.on_resize)
        self.root.bind('<space>', self.toggle_emboss)
        self.root.bind('<Escape>', lambda e: self.root.quit())
        self.root.bind('<r>', self.reset_view)
        
        # Initial display
        self.update_display()
        
        print("MLView - Space for emboss mode, R to reset, Esc to quit")
    
    def calculate_fit(self, img_width, img_height, canvas_width, canvas_height):
        """Calculate size to fit image in canvas preserving aspect ratio"""
        # Calculate ratios
        width_ratio = canvas_width / img_width
        height_ratio = canvas_height / img_height
        
        # Use smaller ratio to ensure it fits
        ratio = min(width_ratio, height_ratio, 1.0)  # Don't upscale
        
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)
        
        return new_width, new_height
    
    def toggle_emboss(self, event=None):
        """Toggle emboss display mode"""
        self.emboss_mode = not self.emboss_mode
        self.update_display()
        
        mode = "EMBOSS" if self.emboss_mode else "NORMAL"
        print(f"Display mode: {mode}")
    
    def reset_view(self, event=None):
        """Reset to normal view"""
        self.emboss_mode = False
        self.update_display()
    
    def process_image(self):
        """Apply current display mode processing"""
        if self.emboss_mode:
            # Convert to grayscale
            img = self.image.convert('L')
            # Apply emboss filter
            img = img.filter(ImageFilter.EMBOSS)
            # Enhance contrast a bit
            img = ImageOps.autocontrast(img)
            return img
        else:
            return self.image
    
    def update_display(self):
        """Update the displayed image"""
        # Get canvas size
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            return
        
        # Calculate fit
        display_width, display_height = self.calculate_fit(
            self.original.width, self.original.height,
            canvas_width, canvas_height
        )
        
        # Resize image - simple, no fancy resampling
        self.image = self.original.resize((display_width, display_height))
        
        # Apply processing
        processed = self.process_image()
        
        # Convert to PhotoImage
        self.photo = ImageTk.PhotoImage(processed)
        
        # Clear canvas and display
        self.canvas.delete('all')
        x = (canvas_width - display_width) // 2
        y = (canvas_height - display_height) // 2
        self.canvas.create_image(x, y, anchor='nw', image=self.photo)
    
    def on_resize(self, event):
        """Handle window resize"""
        if event.widget == self.root:
            self.update_display()
    
    def run(self):
        """Start the viewer"""
        self.root.mainloop()

def main():
    """Entry point"""
    if len(sys.argv) < 2:
        print("MLView - Simple image viewer")
        print("Usage: mlview <image_file>")
        print("\nControls:")
        print("  Space - Toggle emboss mode")
        print("  R     - Reset to normal view")
        print("  Esc   - Quit")
        sys.exit(1)
    
    viewer = MLView(sys.argv[1])
    viewer.run()

if __name__ == "__main__":
    main()
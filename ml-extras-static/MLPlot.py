#!/usr/bin/env python3
"""
MLPlot - Minimal timeseries plotter
Part of ML-Extras
"""

import tkinter as tk
import csv
import sys
from pathlib import Path

# ML-style constants
COLORS = {
    'dark_gray': '#3C3C3C',
    'light_gray': '#C0C0C0',
    'green': '#00FF00',
    'white': '#FFFFFF',
    'black': '#000000',
    'blue': '#0000FF'
}

class MLPlot:
    def __init__(self, root, data, xlabel="X", ylabel="Y", title=""):
        self.root = root
        self.root.title(f"MLPlot - {title}" if title else "MLPlot")
        self.root.geometry("800x600")
        self.root.configure(bg=COLORS['dark_gray'])
        
        self.data = data
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.title = title
        
        self._create_ui()
        self._plot_data()
    
    def _create_ui(self):
        """Create the UI"""
        # Title bar
        title_frame = tk.Frame(self.root, bg=COLORS['light_gray'], 
                              height=40, relief='raised', bd=2)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)
        
        # Title label
        title_text = self.title if self.title else "Timeseries Plot"
        tk.Label(title_frame, text=title_text,
                bg=COLORS['green'], fg=COLORS['black'],
                font=('Courier', 14, 'bold')).pack(expand=True, fill='both', padx=2, pady=2)
        
        # Canvas for plot
        self.canvas = tk.Canvas(self.root, bg=COLORS['black'], 
                               highlightthickness=0)
        self.canvas.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Bind resize
        self.canvas.bind('<Configure>', lambda e: self._plot_data())
        
        # Status bar
        self.status = tk.Label(self.root, text=f"Points: {len(self.data)}",
                              bg=COLORS['light_gray'], fg=COLORS['black'],
                              anchor='w', padx=5)
        self.status.pack(fill='x')
        
        # Keyboard shortcuts
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        self.root.bind('<Escape>', lambda e: self.root.quit())
    
    def _plot_data(self):
        """Plot the data points"""
        self.canvas.delete('all')
        
        if not self.data or len(self.data) < 2:
            self.canvas.create_text(400, 300, text="No data to plot",
                                   fill=COLORS['green'], font=('Courier', 20))
            return
        
        # Get canvas dimensions
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width < 100 or height < 100:
            return  # Too small
        
        # Margins
        margin = 50
        plot_width = width - 2 * margin
        plot_height = height - 2 * margin
        
        # Find data ranges
        x_values = [point[0] for point in self.data]
        y_values = [point[1] for point in self.data]
        
        x_min, x_max = min(x_values), max(x_values)
        y_min, y_max = min(y_values), max(y_values)
        
        # Add padding to y range
        y_padding = (y_max - y_min) * 0.1 if y_max != y_min else 1
        y_min -= y_padding
        y_max += y_padding
        
        # Draw axes
        self.canvas.create_line(margin, height - margin, width - margin, height - margin,
                               fill=COLORS['white'], width=2)  # X axis
        self.canvas.create_line(margin, margin, margin, height - margin,
                               fill=COLORS['white'], width=2)  # Y axis
        
        # Draw labels
        self.canvas.create_text(width // 2, height - 10, text=self.xlabel,
                               fill=COLORS['white'], font=('Courier', 10))
        self.canvas.create_text(20, height // 2, text=self.ylabel, angle=90,
                               fill=COLORS['white'], font=('Courier', 10))
        
        # Draw grid lines and values
        for i in range(5):
            # Horizontal grid
            y = margin + i * plot_height / 4
            self.canvas.create_line(margin, y, width - margin, y,
                                   fill=COLORS['dark_gray'], dash=(2, 4))
            value = y_max - i * (y_max - y_min) / 4
            self.canvas.create_text(margin - 10, y, text=f"{value:.1f}",
                                   anchor='e', fill=COLORS['white'], font=('Courier', 8))
        
        # Scale data to canvas
        if x_max == x_min:
            x_scale = 0
        else:
            x_scale = plot_width / (x_max - x_min)
        
        if y_max == y_min:
            y_scale = 0
        else:
            y_scale = plot_height / (y_max - y_min)
        
        # Convert data to canvas coordinates
        points = []
        for x, y in self.data:
            px = margin + (x - x_min) * x_scale
            py = height - margin - (y - y_min) * y_scale
            points.extend([px, py])
        
        # Draw line
        if len(points) >= 4:
            self.canvas.create_line(points, fill=COLORS['green'], width=2)
        
        # Draw points
        for i in range(0, len(points), 2):
            x, y = points[i], points[i+1]
            self.canvas.create_oval(x-3, y-3, x+3, y+3,
                                   fill=COLORS['green'], outline=COLORS['white'])
        
        # Update status
        self.status.config(text=f"Points: {len(self.data)} | "
                               f"Range: [{x_min:.1f}, {x_max:.1f}] x [{y_min:.1f}, {y_max:.1f}]")

def load_csv(filename):
    """Load data from CSV file"""
    data = []
    try:
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            # Skip header if present
            first_row = next(reader, None)
            if first_row:
                # Check if header or data
                try:
                    float(first_row[0])
                    float(first_row[1])
                    data.append((float(first_row[0]), float(first_row[1])))
                except:
                    pass  # Was header, skip it
            
            # Read rest of data
            for row in reader:
                if len(row) >= 2:
                    try:
                        x = float(row[0])
                        y = float(row[1])
                        data.append((x, y))
                    except:
                        continue  # Skip bad rows
    except Exception as e:
        print(f"Error loading {filename}: {e}")
    
    return data

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("MLPlot - Minimal timeseries plotter")
        print("Usage: mlplot.py <csv_file> [xlabel] [ylabel] [title]")
        print("CSV format: x,y values (one per line)")
        sys.exit(1)
    
    # Parse arguments
    csv_file = sys.argv[1]
    xlabel = sys.argv[2] if len(sys.argv) > 2 else "X"
    ylabel = sys.argv[3] if len(sys.argv) > 3 else "Y"
    title = sys.argv[4] if len(sys.argv) > 4 else Path(csv_file).stem
    
    # Load data
    data = load_csv(csv_file)
    if not data:
        print(f"No valid data found in {csv_file}")
        sys.exit(1)
    
    # Create plot
    root = tk.Tk()
    plot = MLPlot(root, data, xlabel, ylabel, title)
    root.mainloop()

if __name__ == "__main__":
    main()
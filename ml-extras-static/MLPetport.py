#!/usr/bin/env python3
"""
MLPortrait - Generate deterministic ASCII portraits from seed data
Or digital horrors, depending on your perspective.
This breaks the rule - I'm not quite sure how it works or why parts of it don't work.
I'll give it an afternoon sometime.
Part of ML-Extras
"""

import sys
import json
import hashlib
import random
from pathlib import Path

class MLPortrait:
    def __init__(self, size=16):
        self.size = size
        self.chars = {
            'round': ['●', '○', '·', ' '],
            'block': ['█', '▓', '▒', '░', ' '],
            'ascii': ['#', '+', '-', '.', ' '],
            'cute': ['♥', '♦', '•', '·', ' '],
            'directional': ['▲', '▼', '◄', '►', ' ']
        }
        
    def generate(self, seed_data, style='block'):
        """Generate portrait from seed data"""
        # Create deterministic seed
        if isinstance(seed_data, dict):
            seed_str = json.dumps(seed_data, sort_keys=True)
        else:
            seed_str = str(seed_data)
            
        seed = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
        random.seed(seed)
        
        # Get character set
        charset = self.chars.get(style, self.chars['block'])
        
        # Generate grid with rules
        grid = []
        for y in range(self.size):
            row = []
            for x in range(self.size):
                # Apply rules based on position
                cell = self._apply_rules(x, y, seed)
                row.append(cell)
            grid.append(row)
            
        return grid, charset
    
    def _apply_rules(self, x, y, seed):
        """Cellular automaton-like rules for each cell"""
        # Create zones for creature-like appearance
        center_x = self.size // 2
        center_y = self.size // 2
        
        # Distance from center
        dist = abs(x - center_x) + abs(y - center_y)
        
        # Eye positions (symmetrical)
        if y == center_y - 2:
            if x == center_x - 2 or x == center_x + 2:
                return 2  # Special char for eyes
        
        # Body zone
        if dist < self.size * 0.6:
            # Use seed to determine density
            threshold = (seed % 100) / 100
            if random.random() > threshold * 0.3:
                return 1 if dist < self.size * 0.4 else random.choice([1, 0])
        
        # Outer area
        if dist > self.size * 0.5:
            return 0
            
        # Random fill based on seed
        return random.choice([0, 1, 1, 0])
    
    def render(self, grid, charset):
        """Render grid to ASCII string"""
        output = []
        for row in grid:
            line = ""
            for cell in row:
                if cell == 2:  # Special (eyes)
                    line += "◉ "
                else:
                    line += charset[min(cell, len(charset)-1)] + " "
            output.append(line.rstrip())
        return "\n".join(output)
    
    def to_json(self, grid):
        """Flatten grid for JSON storage"""
        return [cell for row in grid for cell in row]
    
    def from_json(self, flat):
        """Reconstruct grid from JSON"""
        grid = []
        for i in range(0, len(flat), self.size):
            grid.append(flat[i:i+self.size])
        return grid

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate ASCII portraits")
    parser.add_argument('seed', nargs='*', help='Seed words for portrait')
    parser.add_argument('-s', '--style', choices=['round', 'block', 'ascii', 'cute', 'directional'],
                       default='block', help='Character style')
    parser.add_argument('--size', type=int, default=16, help='Grid size (default: 16)')
    parser.add_argument('-j', '--json', action='store_true', help='Output as JSON array')
    parser.add_argument('-f', '--file', help='Read seed from JSON file')
    
    args = parser.parse_args()
    
    portrait = MLPortrait(args.size)
    
    # Determine seed
    if args.file:
        with open(args.file) as f:
            seed_data = json.load(f)
    elif args.seed:
        seed_data = ' '.join(args.seed)
    elif not sys.stdin.isatty():
        seed_data = sys.stdin.read().strip()
    else:
        # Interactive mode
        print("MLPortrait - ASCII Portrait Generator")
        print("Enter seed text (or JSON):")
        seed_data = input("> ").strip()
    
    # Generate portrait
    grid, charset = portrait.generate(seed_data, args.style)
    
    # Output
    if args.json:
        print(json.dumps(portrait.to_json(grid)))
    else:
        print(portrait.render(grid, charset))

if __name__ == "__main__":
    main()
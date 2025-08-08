#!/usr/bin/env python3
"""
MLBarchart - Visualize counts as terminal bar charts
Takes input as "label: count" or "label count" or JSON
Outputs fixed-width terminal bars
Part of ML-Extras

$ echo "CRM Containers: $(docker ps | grep crm | wc -l)
DB Containers: $(docker ps | grep mariadb | wc -l)
Disk Used: $(df / | awk 'NR==2 {print $5}' | sed 's/%//')
Memory Free GB: $(free -g | awk 'NR==2 {print $4}')" | mlbarchart

Label                          Count Bar
----------------------------------------------------------
Disk Used                         67 ██████████████████████████████████████████████████
CRM Containers                     3 ██
Memory Free GB                     2 █
DB Containers                      1 ▌
----------------------------------------------------------

echo "Comments: $(grep '#' MLComment.py | wc -l)
Functions: $(grep 'def ' MLComment.py | wc -l)
Classes: $(grep 'class ' MLComment.py | wc -l)" | python3 MLBarchart.py 
Label          Count Bar
--------------------------------------------------------------------------
Comments          38 ██████████████████████████████████████████████████
Functions         10 █████████████
Classes            2 ██
Total: 50

"""

import sys
import json
import re
from pathlib import Path

class MLBarchart:
    def __init__(self, width=50, height=20):
        self.width = width  # Bar width
        self.height = height  # Max rows to display
        self.data = []
        
    def parse_input(self, text):
        """Parse various input formats"""
        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Try JSON first
            try:
                data = json.loads(line)
                if isinstance(data, dict):
                    for k, v in data.items():
                        try:
                            self.data.append((str(k), float(v)))
                        except:
                            pass
                continue
            except:
                pass
            
            # Try "label: count" format
            if ':' in line:
                parts = line.split(':', 1)
                label = parts[0].strip()
                try:
                    count = float(parts[1].strip())
                    self.data.append((label, count))
                    continue
                except:
                    pass
            
            # Try "label count" format (tab or space separated)
            parts = line.split(None, 1)
            if len(parts) == 2:
                try:
                    # Try count first (like wc -l output)
                    count = float(parts[0])
                    label = parts[1]
                    self.data.append((label, count))
                except:
                    # Try label first
                    try:
                        label = parts[0]
                        count = float(parts[1])
                        self.data.append((label, count))
                    except:
                        pass
    
    def render(self, sort=True, char='█'):
        """Render as terminal bar chart"""
        if not self.data:
            return "No data to display"
        
        # Sort by value if requested
        if sort:
            self.data.sort(key=lambda x: x[1], reverse=True)
        
        # Limit to height
        display_data = self.data[:self.height]
        
        # Find max value for scaling
        max_val = max(d[1] for d in display_data) if display_data else 1
        
        # Find max label length for alignment
        max_label = max(len(d[0]) for d in display_data) if display_data else 10
        max_label = min(max_label, 30)  # Cap label length
        
        output = []
        
        # Header
        output.append(f"{'Label':<{max_label}} {'Count':>10} Bar")
        output.append("-" * (max_label + self.width + 15))
        
        # Bars
        for label, count in display_data:
            # Truncate long labels
            if len(label) > max_label:
                label = label[:max_label-2] + '..'
            
            # Calculate bar length
            bar_len = int((count / max_val) * self.width) if max_val > 0 else 0
            bar = char * bar_len
            
            # Format line
            output.append(f"{label:<{max_label}} {count:>10.0f} {bar}")
        
        # Footer with total
        if len(self.data) > self.height:
            output.append("-" * (max_label + self.width + 15))
            output.append(f"Showing top {self.height} of {len(self.data)} items")
        
        total = sum(d[1] for d in self.data)
        output.append(f"Total: {total:.0f}")
        
        return '\n'.join(output)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Terminal bar chart generator")
    parser.add_argument('-w', '--width', type=int, default=50,
                       help='Bar width (default: 50)')
    parser.add_argument('-n', '--height', type=int, default=20,
                       help='Max rows to display (default: 20)')
    parser.add_argument('-c', '--char', default='█',
                       help='Bar character (default: █)')
    parser.add_argument('--no-sort', action='store_true',
                       help='Don\'t sort by value')
    parser.add_argument('-o', '--output', help='Output to file')
    
    args = parser.parse_args()
    
    # Read input
    if not sys.stdin.isatty():
        input_text = sys.stdin.read()
    else:
        print("MLBarchart - Terminal bar charts")
        print("Enter data as 'label: count' or 'label count', blank line to end:")
        lines = []
        while True:
            try:
                line = input()
                if not line:
                    break
                lines.append(line)
            except (EOFError, KeyboardInterrupt):
                break
        input_text = '\n'.join(lines)
    
    # Process
    chart = MLBarchart(width=args.width, height=args.height)
    chart.parse_input(input_text)
    output = chart.render(sort=not args.no_sort, char=args.char)
    
    # Output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Chart saved to {args.output}")
    else:
        print(output)

if __name__ == "__main__":
    main()
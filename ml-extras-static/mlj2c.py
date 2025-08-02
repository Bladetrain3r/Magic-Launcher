#!/usr/bin/env python3
"""
MLJ2C - JSON to CSV converter
Part of ML-Extras
"""

import json
import sys
import csv
import io

def main():
    if len(sys.argv) != 4:
        print("MLJ2C - JSON to CSV converter")
        print("Usage: mlj2c.py <json_file> <key1> <key2>")
        print("Example: mlj2c.py stats.json timestamp time_seconds")
        print("\nOutputs CSV to stdout")
        sys.exit(1)
    
    filename, key1, key2 = sys.argv[1], sys.argv[2], sys.argv[3]
    
    try:
        # Handle stdin
        if filename == '-':
            data = json.load(sys.stdin)
        else:
            with open(filename, 'r') as f:
                data = json.load(f)
        
        # Force UTF-8 output on Windows
        if sys.platform == 'win32':
            import os
            if hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8')
        
        # Use StringIO buffer to ensure clean output
        output = io.StringIO()
        writer = csv.writer(output, lineterminator='\n')
        writer.writerow([key1, key2])
        
        # Extract and write data
        row_num = 0
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and key1 in item and key2 in item:
                    val1 = item[key1]
                    val2 = item[key2]
                    
                    # Convert values for plotting
                    # Booleans: True=1, False=0
                    if isinstance(val1, bool):
                        val1 = 1 if val1 else 0
                    if isinstance(val2, bool):
                        val2 = 1 if val2 else 0
                    
                    # Non-numeric values: use row number
                    try:
                        float(val1)
                    except (ValueError, TypeError):
                        val1 = row_num
                    
                    try:
                        float(val2)
                    except (ValueError, TypeError):
                        val2 = row_num
                    
                    writer.writerow([val1, val2])
                    row_num += 1
        elif isinstance(data, dict):
            # Handle single object
            if key1 in data and key2 in data:
                val1 = data[key1]
                val2 = data[key2]
                
                # Same conversions
                if isinstance(val1, bool):
                    val1 = 1 if val1 else 0
                if isinstance(val2, bool):
                    val2 = 1 if val2 else 0
                
                try:
                    float(val1)
                except (ValueError, TypeError):
                    val1 = 0
                
                try:
                    float(val2)
                except (ValueError, TypeError):
                    val2 = 0
                
                writer.writerow([val1, val2])
        
        # Write clean output
        sys.stdout.write(output.getvalue())
        
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: Invalid JSON", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
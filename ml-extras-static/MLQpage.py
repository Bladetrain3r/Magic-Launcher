#!/usr/bin/env python3
"""
MLQuickpage - Extract text sections by marker
Usage: mlquickpage <file> <section>

Markers can appear anywhere in a line, allowing them to be placed in comments:
  # mqp#section#     (Python)
  // mqp#section#    (C/JavaScript)  
  -- mqp#section#    (SQL)
  <!-- mqp#section# --> (HTML)
"""

import sys
import os
from pathlib import Path

# Force UTF-8 for pipes on Windows
if sys.platform == 'win32':
    import codecs
    # This forces UTF-8 even for redirected output
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def extract_section(content, section_name):
    """Extract a single section from content"""
    lines = content.split('\n')
    in_section = False
    result = []
    
    marker = f'mqp#{section_name}#'
    
    for line in lines:
        # Check if line contains our section marker
        if marker in line:
            in_section = True
            continue
        
        # Check if line contains any other mqp marker (signals new section)
        if in_section and 'mqp#' in line:
            # Check if it's actually a marker (has closing #)
            mqp_index = line.index('mqp#')
            remaining = line[mqp_index+4:]
            if '#' in remaining:
                # Hit another section marker, we're done
                break
        
        if in_section:
            result.append(line)
    
    return '\n'.join(result)

def list_sections(content):
    """List all sections found in content"""
    lines = content.split('\n')
    sections = []
    
    for line in lines:
        if 'mqp#' in line:
            # Try to extract section name
            mqp_index = line.index('mqp#')
            remaining = line[mqp_index+4:]
            if '#' in remaining:
                section_name = remaining[:remaining.index('#')]
                if section_name and section_name not in sections:
                    sections.append(section_name)
    
    return sections

def main():
    # Handle help request
    if len(sys.argv) == 2 and sys.argv[1] in ['-h', '--help']:
        print(__doc__)
        print("\nSpecial usage:")
        print("  mlquickpage <file> --list    List all sections in file")
        sys.exit(0)
    
    if len(sys.argv) != 3:
        script = Path(sys.argv[0]).name
        print(f"Usage: {script} <file> <section>")
        print(f"       {script} <file> --list")
        sys.exit(1)
    
    filepath = Path(sys.argv[1])
    section = sys.argv[2]
    
    if not filepath.exists():
        print(f"Error: File '{filepath}' not found!", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Handle --list option
    if section == '--list':
        sections = list_sections(content)
        if sections:
            print("Sections found:")
            for s in sections:
                print(f"  {s}")
        else:
            print("No sections found")
        sys.exit(0)
    
    # Extract the requested section
    result = extract_section(content, section)
    
    if result:
        print(result, end='')  # Don't add extra newline
    else:
        # Section not found, exit with error code (silent)
        sys.exit(1)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
MLHTMD - Convert between Markdown and HTML
Because sometimes you need docs in both formats
"""

import sys
import re
from pathlib import Path

class MLHTMD:
    def __init__(self):
        # Basic MD to HTML patterns
        self.md_patterns = [
            # Headers
            (r'^### (.*?)$', r'<h3>\1</h3>'),
            (r'^## (.*?)$', r'<h2>\1</h2>'),
            (r'^# (.*?)$', r'<h1>\1</h1>'),
            # Bold and italic
            (r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>'),
            (r'\*\*(.*?)\*\*', r'<strong>\1</strong>'),
            (r'\*(.*?)\*', r'<em>\1</em>'),
            # Code
            (r'`(.*?)`', r'<code>\1</code>'),
            # Links
            (r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>'),
            # Line breaks
            (r'  $', r'<br>'),
        ]
        
        # HTML to MD patterns (reverse)
        self.html_patterns = [
            # Headers
            (r'<h1>(.*?)</h1>', r'# \1'),
            (r'<h2>(.*?)</h2>', r'## \1'),
            (r'<h3>(.*?)</h3>', r'### \1'),
            # Bold and italic
            (r'<strong><em>(.*?)</em></strong>', r'***\1***'),
            (r'<strong>(.*?)</strong>', r'**\1**'),
            (r'<em>(.*?)</em>', r'*\1*'),
            (r'<b>(.*?)</b>', r'**\1**'),
            (r'<i>(.*?)</i>', r'*\1*'),
            # Code
            (r'<code>(.*?)</code>', r'`\1`'),
            # Links
            (r'<a href="([^"]+)">([^<]+)</a>', r'[\2](\1)'),
            # Breaks and paragraphs
            (r'<br\s*/?>', r'  \n'),
            (r'<p>(.*?)</p>', r'\1\n'),
            # Strip remaining tags
            (r'<[^>]+>', r''),
        ]
    
    def md_to_html(self, text):
        """Convert Markdown to HTML"""
        html_lines = []
        in_code_block = False
        in_list = False
        
        for line in text.split('\n'):
            # Code blocks
            if line.strip().startswith('```'):
                if in_code_block:
                    html_lines.append('</code></pre>')
                    in_code_block = False
                else:
                    html_lines.append('<pre><code>')
                    in_code_block = True
                continue
            
            if in_code_block:
                html_lines.append(line)
                continue
            
            # Lists
            if line.strip().startswith('- ') or line.strip().startswith('* '):
                if not in_list:
                    html_lines.append('<ul>')
                    in_list = True
                item = line.strip()[2:]
                html_lines.append(f'<li>{self._apply_inline_md(item)}</li>')
                continue
            elif in_list and line.strip() == '':
                html_lines.append('</ul>')
                in_list = False
            
            # Apply patterns
            processed = line
            for pattern, replacement in self.md_patterns:
                processed = re.sub(pattern, replacement, processed, flags=re.MULTILINE)
            
            # Paragraphs
            if processed.strip() and not processed.strip().startswith('<'):
                processed = f'<p>{processed}</p>'
            
            html_lines.append(processed)
        
        # Close any open lists
        if in_list:
            html_lines.append('</ul>')
        
        return '\n'.join(html_lines)
    
    def _apply_inline_md(self, text):
        """Apply inline markdown patterns"""
        for pattern, replacement in self.md_patterns[3:]:  # Skip headers
            text = re.sub(pattern, replacement, text)
        return text
    
    def html_to_md(self, text):
        """Convert HTML to Markdown"""
        # Pre-process
        text = text.replace('\r\n', '\n')
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Apply patterns
        for pattern, replacement in self.html_patterns:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE | re.DOTALL)
        
        # Clean up
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = text.strip()
        
        return text
    
    def convert_file(self, input_path, output_path=None, to_format=None):
        """Convert a file"""
        input_path = Path(input_path)
        
        # Auto-detect format
        if to_format is None:
            if input_path.suffix.lower() in ['.md', '.markdown']:
                to_format = 'html'
            else:
                to_format = 'md'
        
        # Read input
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            return False
        
        # Convert
        if to_format == 'html':
            output = self.md_to_html(content)
            default_ext = '.html'
        else:
            output = self.html_to_md(content)
            default_ext = '.md'
        
        # Output
        if output_path is None:
            output_path = input_path.with_suffix(default_ext)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Converted to: {output_path}")
            return True
        except Exception as e:
            print(f"Error writing file: {e}")
            return False

def main():
    """Entry point"""
    if len(sys.argv) < 2:
        print("MLHTMD - Markdown/HTML converter")
        print("Usage: mlhtmd <file> [--to-md|--to-html] [-o output]")
        print("\nExamples:")
        print("  mlhtmd README.md           # Creates README.html")
        print("  mlhtmd page.html --to-md   # Creates page.md")
        print("  mlhtmd doc.md -o web.html  # Specific output")
        sys.exit(1)
    
    # Parse args (simple)
    input_file = sys.argv[1]
    output_file = None
    to_format = None
    
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--to-md':
            to_format = 'md'
        elif sys.argv[i] == '--to-html':
            to_format = 'html'
        elif sys.argv[i] == '-o' and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
            i += 1
        i += 1
    
    # Convert
    converter = MLHTMD()
    converter.convert_file(input_file, output_file, to_format)

if __name__ == "__main__":
    main()
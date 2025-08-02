#!/usr/bin/env python3
"""
MLHTMD - Convert between Markdown and HTML
Now with Magic Launcher manifesto styling!
"""

import sys
import re
from pathlib import Path

class MLHTMD:
    def __init__(self, style='basic'):
        self.style = style  # 'basic', 'magic', or 'strip'
    
    def md_to_html(self, text, title="Document"):
        """Convert Markdown to HTML with chosen style"""
        if self.style == 'strip':
            # Just return the text content
            return self._strip_to_text(text)
        
        lines = []
        
        # HTML header
        lines.append('<!DOCTYPE html>')
        lines.append('<html lang="en">')
        lines.append('<head>')
        lines.append('    <meta charset="UTF-8">')
        lines.append('    <meta name="viewport" content="width=device-width, initial-scale=1.0">')
        lines.append(f'    <title>{title}</title>')
        
        if self.style == 'magic':
            # Full Magic Launcher manifesto style
            lines.extend(self._get_magic_style())
        else:
            # Basic terminal style
            lines.extend(self._get_basic_style())
        
        lines.append('</head>')
        lines.append('<body>')
        
        if self.style == 'magic':
            # Add Unitext-style header
            lines.append('    <div class="header">')
            lines.append(f'        <span class="header-title">UniText - {title}</span>')
            lines.append('        <div class="header-buttons">')
            lines.append('            <button class="header-button">_</button>')
            lines.append('            <button class="header-button">□</button>')
            lines.append('            <button class="header-button">X</button>')
            lines.append('        </div>')
            lines.append('    </div>')
            lines.append('    <div class="content">')
        
        # Process markdown content
        lines.extend(self._process_markdown(text))
        
        if self.style == 'magic':
            lines.append('    </div>')  # Close content div
        
        lines.append('</body>')
        lines.append('</html>')
        
        return '\n'.join(lines)
    
    def _get_basic_style(self):
        """Basic terminal style CSS"""
        return [
            '    <style>',
            '        body { background: #000; color: #0F0; font-family: monospace; line-height: 1.4; max-width: 80ch; margin: 0 auto; padding: 20px; }',
            '        h1, h2, h3 { color: #0FF; }',
            '        h2 { color: #FF0; }',
            '        pre { background: #111; border: 1px solid #0F0; padding: 10px; }',
            '        code { color: #0FF; }',
            '        a { color: #00F; }',
            '    </style>'
        ]
    
    def _get_magic_style(self):
        """Full Magic Launcher manifesto style"""
        return [
            '    <style>',
            '        body { margin: 0; padding: 0; background: #000; color: #0F0; font-family: "Courier New", monospace; font-size: 14px; line-height: 1.4; }',
            '        .header { background: #0F0; color: #000; padding: 2px 5px; display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #0F0; }',
            '        .header-title { font-weight: bold; }',
            '        .header-buttons { display: flex; gap: 10px; }',
            '        .header-button { background: #C0C0C0; color: #000; border: 2px outset #FFF; padding: 1px 6px; cursor: pointer; font-family: inherit; font-size: inherit; }',
            '        .content { padding: 10px; max-width: 80ch; margin: 0 auto; }',
            '        h1 { color: #0FF; text-align: center; border: 1px solid #0FF; padding: 10px; margin: 20px 0; }',
            '        h2 { color: #FF0; text-decoration: underline; }',
            '        h3 { color: #F0F; }',
            '        p { margin: 10px 0; text-align: justify; }',
            '        pre { background: #111; border: 1px solid #0F0; padding: 10px; overflow-x: auto; color: #FFF; }',
            '        code { color: #0FF; background: #111; padding: 2px 4px; }',
            '        ul, ol { margin: 10px 0; padding-left: 30px; }',
            '        li { margin: 5px 0; }',
            '        a { color: #00F; text-decoration: underline; }',
            '        a:hover { background: #00F; color: #FFF; }',
            '        .footer { text-align: center; color: #666; margin-top: 40px; padding: 20px; border-top: 1px solid #333; }',
            '    </style>'
        ]
    
    def _process_markdown(self, text):
        """Process markdown content"""
        lines = []
        in_code = False
        in_list = False
        
        for line in text.split('\n'):
            # Code blocks
            if line.strip().startswith('```'):
                if in_code:
                    lines.append('</pre>')
                    in_code = False
                else:
                    lines.append('<pre>')
                    in_code = True
                continue
            
            if in_code:
                lines.append(line)
                continue
            
            # Headers
            if line.startswith('### '):
                lines.append(f'<h3>{line[4:]}</h3>')
            elif line.startswith('## '):
                lines.append(f'<h2>{line[3:]}</h2>')
            elif line.startswith('# '):
                lines.append(f'<h1>{line[2:]}</h1>')
            # Lists
            elif line.strip().startswith(('- ', '* ')):
                if not in_list:
                    lines.append('<ul>')
                    in_list = True
                item = self._process_inline(line.strip()[2:])
                lines.append(f'    <li>{item}</li>')
            # Horizontal rule
            elif line.strip() == '---':
                lines.append('<hr>')
            # Regular text
            elif line.strip():
                if in_list:
                    lines.append('</ul>')
                    in_list = False
                processed = self._process_inline(line)
                lines.append(f'<p>{processed}</p>')
        
        # Close any open tags
        if in_list:
            lines.append('</ul>')
        if in_code:
            lines.append('</pre>')
        
        return lines
    
    def _process_inline(self, text):
        """Process inline markdown"""
        # Bold
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        # Italic  
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        # Code
        text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
        # Links
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
        return text
    
    def _strip_to_text(self, text):
        """Strip markdown to plain text (MLStrip functionality)"""
        # Remove code blocks
        text = re.sub(r'```[^`]*```', '', text, flags=re.DOTALL)
        # Remove headers
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        # Remove bold/italic
        text = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', text)
        # Remove links
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        # Remove code
        text = re.sub(r'`([^`]+)`', r'\1', text)
        # Clean up
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()
    
    def html_to_text(self, html):
        """Strip HTML to plain text"""
        # Remove script and style
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        # Convert breaks
        html = re.sub(r'<br\s*/?>', '\n', html, flags=re.IGNORECASE)
        html = re.sub(r'<p[^>]*>', '\n', html, flags=re.IGNORECASE)
        html = re.sub(r'</p>', '\n', html, flags=re.IGNORECASE)
        # Strip all tags
        html = re.sub(r'<[^>]+>', '', html)
        # Decode entities
        html = html.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        # Clean up whitespace
        html = re.sub(r'\n{3,}', '\n\n', html)
        return html.strip()

def main():
    """Entry point"""
    if len(sys.argv) < 2:
        print("MLHTMD - Markdown/HTML converter with Magic Launcher styling")
        print("Usage: mlhtmd <file> [--basic|--magic|--strip]")
        print("\nStyles:")
        print("  --basic  Simple terminal style (default)")
        print("  --magic  Full Magic Launcher manifesto style")  
        print("  --strip  Convert to plain text only")
        print("\nExamples:")
        print("  mlhtmd README.md           # Basic terminal HTML")
        print("  mlhtmd README.md --magic   # Magic Launcher style")
        print("  mlhtmd page.html --strip   # Strip to text (MLStrip mode)")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    style = 'basic'
    
    # Check for style flag
    if len(sys.argv) > 2:
        if sys.argv[2] == '--magic':
            style = 'magic'
        elif sys.argv[2] == '--strip':
            style = 'strip'
    
    if not input_file.exists():
        print(f"Error: {input_file} not found")
        sys.exit(1)
    
    # Read input
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Detect format and convert
    converter = MLHTMD(style)
    
    if input_file.suffix.lower() in ['.md', '.markdown']:
        # Markdown to HTML (or text)
        title = input_file.stem.replace('_', ' ').title()
        output = converter.md_to_html(content, title)
        output_ext = '.txt' if style == 'strip' else '.html'
    else:
        # HTML to text
        output = converter.html_to_text(content)
        output_ext = '.txt'
    
    # Write output
    output_file = input_file.with_suffix(output_ext)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output)
    
    print(f"Created: {output_file}")

if __name__ == "__main__":
    main()
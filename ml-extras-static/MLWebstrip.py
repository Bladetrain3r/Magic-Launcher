#!/usr/bin/env python3
"""
MLStrip - Strip HTML down to readable text
Because sometimes you just want the words
"""

import sys
import re
from urllib.request import urlopen
from html.parser import HTMLParser
from pathlib import Path

class MLStripper(HTMLParser):
    """HTML to clean text converter"""
    
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = []
        self.skip = False
        self.skip_tags = {'script', 'style', 'meta', 'link'}
        self.title = ""
        self.in_title = False
        
    def handle_starttag(self, tag, attrs):
        # Skip script and style content
        if tag in self.skip_tags:
            self.skip = True
        elif tag == 'title':
            self.in_title = True
        # Add newlines for block elements
        elif tag in ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'br']:
            self.text.append('\n')
        elif tag == 'hr':
            self.text.append('\n' + '─' * 40 + '\n')
            
    def handle_endtag(self, tag):
        if tag in self.skip_tags:
            self.skip = False
        elif tag == 'title':
            self.in_title = False
        # Extra newline after headings
        elif tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.text.append('\n')
            
    def handle_data(self, data):
        if not self.skip:
            text = data.strip()
            if text:
                if self.in_title:
                    self.title = text
                else:
                    self.text.append(text + ' ')
                    
    def get_text(self):
        """Get the cleaned text"""
        raw = ''.join(self.text)
        # Clean up excessive whitespace
        raw = re.sub(r'\n\s*\n', '\n\n', raw)
        raw = re.sub(r' +', ' ', raw)
        return raw.strip()

def strip_html(source):
    """Strip HTML from file or URL"""
    try:
        # Check if it's a file
        path = Path(source)
        if path.exists():
            print(f"Reading file: {source}")
            with open(path, 'r', encoding='utf-8') as f:
                html = f.read()
        else:
            # Try as URL
            url = source
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url
            print(f"Fetching: {url}")
            response = urlopen(url, timeout=10)
            html = response.read().decode('utf-8', errors='ignore')
            source = url  # Update for display
        
        # Strip it
        stripper = MLStripper()
        stripper.feed(html)
        
        # Format output
        output = []
        if stripper.title:
            output.append('=' * 60)
            output.append(f"TITLE: {stripper.title}")
            output.append(f"SOURCE: {source}")
            output.append('=' * 60)
            output.append("")
            
        output.append(stripper.get_text())
        
        return '\n'.join(output)
        
    except Exception as e:
        return f"Error processing {source}: {e}"

def main():
    """Entry point"""
    if len(sys.argv) < 2:
        print("MLStrip - Make HTML readable again")
        print("Usage: mlstrip <file.html or url>")
        print("\nExamples:")
        print("  mlstrip index.html")
        print("  mlstrip https://example.com")
        print("  mlstrip page.html | unitext")
        sys.exit(1)
        
    source = sys.argv[1]
    result = strip_html(source)
    print(result)

if __name__ == "__main__":
    main()
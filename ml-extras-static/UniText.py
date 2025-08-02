#!/usr/bin/env python3
"""
UniText - A minimal Unicode text viewer with embedded font support
Part of the ML-Extras collection
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox, font
import sys
import os
import tempfile
from pathlib import Path

# Try to import PIL for custom font support
try:
    from PIL import Image, ImageDraw, ImageFont, ImageTk
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    print("Note: Install Pillow for better font support (pip install Pillow)")

# Constants matching ML style
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
COLORS = {
    'dark_gray': '#3C3C3C',
    'light_gray': '#C0C0C0',
    'green': '#00FF00',
    'white': '#FFFFFF',
    'black': '#000000'
}

# Font fallback list for better Unicode support
FONT_FALLBACKS = [
    'DejaVu Sans Mono',
    'Noto Sans Mono',
    'Consolas',
    'Liberation Mono',
    'Courier New',
    'monospace'
]

class UniTextViewer:
    def __init__(self, root, filepath=None):
        self.root = root
        self.root.title("UniText Viewer")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.configure(bg=COLORS['dark_gray'])
        
        self.filepath = filepath
        self.content = ""
        self.font_size = 12
        
        # Search state
        self.search_pos = '1.0'
        self.search_term = ''
        
        # Find best available font
        self.font_family = self._find_best_font()
        
        self._create_ui()
        
        if filepath:
            self.load_file(filepath)
    
    def _find_best_font(self):
        """Find the best available font with Unicode support"""
        available_fonts = font.families()
        for f in FONT_FALLBACKS:
            if f in available_fonts:
                return f
        return 'TkFixedFont'  # Ultimate fallback
    
    def _create_ui(self):
        """Create the UI matching ML aesthetic"""
        # Title bar
        title_frame = tk.Frame(self.root, bg=COLORS['light_gray'], 
                              height=40, relief='raised', bd=2)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)
        
        # Title
        title_text = "UniText - Unicode Text Viewer"
        if self.filepath:
            title_text += f" - {os.path.basename(self.filepath)}"
        
        title = tk.Label(title_frame, text=title_text,
                        bg=COLORS['green'], fg=COLORS['black'],
                        font=('Courier', 14, 'bold'))
        title.pack(expand=True, fill='both', padx=2, pady=2)
        
        # Text display area with scrollbar
        text_frame = tk.Frame(self.root, bg=COLORS['dark_gray'])
        text_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # ScrolledText widget for Unicode content
        self.text_area = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            bg=COLORS['black'],
            fg=COLORS['white'],
            font=(self.font_family, self.font_size),
            insertbackground=COLORS['green'],
            selectbackground=COLORS['green'],
            selectforeground=COLORS['black']
        )
        self.text_area.pack(fill='both', expand=True)
        
        # Status bar with info button
        status_frame = tk.Frame(self.root, bg=COLORS['light_gray'])
        status_frame.pack(fill='x')
        
        self.status_bar = tk.Label(
            status_frame,
            text=f"Ready | Font: {self.font_family}",
            bg=COLORS['light_gray'],
            fg=COLORS['black'],
            anchor='w',
            padx=5
        )
        self.status_bar.pack(side='left', fill='x', expand=True)
        
        # Info button
        info_btn = tk.Button(
            status_frame,
            text="?",
            bg=COLORS['light_gray'],
            fg=COLORS['black'],
            font=('Courier', 10, 'bold'),
            bd=1,
            padx=10,
            command=self.show_help
        )
        info_btn.pack(side='right', padx=5)
        
        # Keyboard shortcuts
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-r>', lambda e: self.reload_file())
        self.root.bind('<Control-Alt-v>', lambda e: self.paste_from_clipboard())
        self.root.bind('<Control-plus>', lambda e: self.zoom_in())
        self.root.bind('<Control-minus>', lambda e: self.zoom_out())
        self.root.bind('<Control-0>', lambda e: self.reset_zoom())
        self.root.bind('<Control-s>', lambda e: self.save_current())
        self.root.bind('<Control-f>', lambda e: self.search_text())
        
        # Make text area read-only by default
        self.text_area.bind('<Key>', lambda e: 'break' if e.state == 0 else None)
    
    def paste_from_clipboard(self):
        """Paste clipboard content and display it"""
        try:
            # Get clipboard content
            clipboard_text = self.root.clipboard_get()
            
            # Create temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', 
                                           delete=False, encoding='utf-8') as tf:
                tf.write(clipboard_text)
                temp_path = tf.name
            
            # Load the temp file
            self.filepath = temp_path
            self.load_file(temp_path)
            
            # Update title to show it's from clipboard
            self.root.title("UniText - [Clipboard Content]")
            
        except tk.TclError:
            messagebox.showwarning("Clipboard Empty", 
                                 "No text found in clipboard")
        except Exception as e:
            messagebox.showerror("Error", 
                               f"Could not paste from clipboard:\n{str(e)}")
    
    def save_current(self):
        """Save current content to file"""
        if not self.content:
            messagebox.showinfo("Nothing to Save", "No content to save")
            return
            
        from tkinter import filedialog
        filepath = filedialog.asksaveasfilename(
            title="Save Unicode Text",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filepath:
            try:
                content = self.text_area.get('1.0', tk.END)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content.rstrip())
                self.status_bar.config(text=f"Saved: {os.path.basename(filepath)}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Could not save file:\n{str(e)}")
    
    def load_file(self, filepath):
        """Load and display a Unicode text file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.content = f.read()
            
            self.text_area.delete('1.0', tk.END)
            self.text_area.insert('1.0', self.content)
            
            # Update status
            lines = self.content.count('\n') + 1
            chars = len(self.content)
            self.status_bar.config(
                text=f"Loaded: {os.path.basename(filepath)} | "
                     f"{lines} lines | {chars} chars | Font: {self.font_family}"
            )
            
            # Update title
            if "[Clipboard Content]" not in self.root.title():
                self.root.title(f"UniText - {os.path.basename(filepath)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not load file:\n{str(e)}")
    
    def open_file(self):
        """Open file dialog"""
        from tkinter import filedialog
        filepath = filedialog.askopenfilename(
            title="Open Unicode Text File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filepath:
            self.filepath = filepath
            self.load_file(filepath)
    
    def reload_file(self):
        """Reload current file"""
        if self.filepath:
            self.load_file(self.filepath)
    
    def zoom_in(self):
        """Increase font size"""
        if self.font_size < 48:
            self.font_size += 2
            self.text_area.config(font=(self.font_family, self.font_size))
    
    def zoom_out(self):
        """Decrease font size"""
        if self.font_size > 8:
            self.font_size -= 2
            self.text_area.config(font=(self.font_family, self.font_size))
    
    def reset_zoom(self):
        """Reset to default font size"""
        self.font_size = 12
        self.text_area.config(font=(self.font_family, self.font_size))
    
    def search_text(self):
        """Simple text search"""
        # Create search dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Find")
        dialog.geometry("300x70")
        dialog.transient(self.root)
        
        # Search entry
        tk.Label(dialog, text="Find:").pack(side='left', padx=5)
        entry = tk.Entry(dialog, width=30)
        entry.pack(side='left', padx=5)
        entry.insert(0, self.search_term)
        entry.select_range(0, 'end')
        entry.focus()
        
        def do_search(event=None):
            term = entry.get()
            if not term:
                dialog.destroy()
                return
                
            self.search_term = term
            
            # Clear previous highlights
            self.text_area.tag_remove('search', '1.0', 'end')
            
            # Search from current position
            pos = self.text_area.search(term, self.search_pos, 'end')
            
            if not pos:
                # Wrap around to beginning
                pos = self.text_area.search(term, '1.0', 'end')
            
            if pos:
                # Highlight and scroll to match
                end_pos = f"{pos}+{len(term)}c"
                self.text_area.tag_add('search', pos, end_pos)
                self.text_area.tag_config('search', background='yellow', foreground='black')
                self.text_area.see(pos)
                self.search_pos = end_pos
            else:
                self.search_pos = '1.0'
            
            dialog.destroy()
        
        # Bind Enter to search
        entry.bind('<Return>', do_search)
        tk.Button(dialog, text="Find", command=do_search).pack(side='left')
    
    def show_help(self):
        """Show help dialog"""
        help_text = """UniText v1.0 - Unicode Text Viewer

Keyboard Shortcuts:
  Ctrl+O        Open file
  Ctrl+Alt+V    Paste from clipboard (new file)
  Ctrl+V        Regular Paste (if supported)
  Ctrl+S        Save current content
  Ctrl+R        Reload file
  Ctrl+F        Find text
  Ctrl+Q        Quit
  Ctrl++        Zoom in
  Ctrl+-        Zoom out
  Ctrl+0        Reset zoom

Tips:
• Best results with Noto fonts installed
• Some Unicode blocks may not display perfectly
• Use Ctrl+Alt+V to quickly view clipboard content
• Part of ML-Extras collection

🦊 zerofuchs.co.za"""
        
        messagebox.showinfo("UniText Help", help_text)

def download_noto_font():
    """Helper to download Noto font if needed"""
    print("""
To get the best Unicode support, install Noto fonts:

Ubuntu/Debian:
  sudo apt install fonts-noto-mono

Fedora:
  sudo dnf install google-noto-mono-fonts

Or download from:
  https://www.google.com/get/noto/
""")

def main():
    """Main entry point"""
    root = tk.Tk()
    
    # Get filepath from command line
    filepath = None
    if len(sys.argv) > 1:
        if sys.argv[1] == '--install-font':
            download_noto_font()
            sys.exit(0)
        
        filepath = sys.argv[1]
        if not os.path.exists(filepath):
            print(f"Error: File '{filepath}' not found")
            sys.exit(1)
    
    app = UniTextViewer(root, filepath)
    
    # Show usage if no file provided
    if not filepath:
        usage_text = """UniText - Unicode Text Viewer

Usage:
  python unitext.py [filename]
  python unitext.py --install-font

Keyboard Shortcuts:
  Ctrl+O        Open file
  Ctrl+Alt+V    Paste from clipboard (new file)
  Ctrl+V        Regular Paste (if supported)
  Ctrl+S        Save current content
  Ctrl+R        Reload file
  Ctrl+F        Find text
  Ctrl+Q        Quit
  Ctrl++        Zoom in
  Ctrl+-        Zoom out
  Ctrl+0        Reset zoom

Drop this in your Magic Launcher as a tool!
Perfect for viewing emoji notes, Unicode art,
or any text with special characters.

🔥 Part of ML-Extras 🔥
💀 Now with clipboard support! 💀
📝 Paste that Unicode art! 📝"""
        
        app.text_area.insert('1.0', usage_text)
        app.status_bar.config(text=f"No file loaded | Font: {app.font_family}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
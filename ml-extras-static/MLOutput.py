#!/usr/bin/env python3
"""
MLOutput - Terminal output viewer
Part of ML-Extras
"""

import tkinter as tk
from tkinter import scrolledtext
import subprocess
import threading
import sys
import re
import os
import shlex

# ML-style constants
COLORS = {
    'dark_gray': '#3C3C3C',
    'light_gray': '#C0C0C0',
    'green': '#00FF00',
    'red': '#FF0000',
    'yellow': '#FFFF00',
    'white': '#FFFFFF',
    'black': '#000000'
}

class MLOutput:
    def __init__(self, root, command):
        self.root = root
        self.root.title("MLOutput")
        self.root.geometry("800x600")
        self.root.configure(bg=COLORS['dark_gray'])
        
        self.command = command
        self.process = None
        self.paused = False
        self.buffer = []
        
        # Stream toggles
        self.show_stdout = tk.BooleanVar(value=True)
        self.show_stderr = tk.BooleanVar(value=True)
        self.filter_pattern = tk.StringVar()
        
        self._create_ui()
        self._start_process()
    
    def _create_ui(self):
        """Create the UI"""
        # Title bar
        title_frame = tk.Frame(self.root, bg=COLORS['light_gray'], 
                              height=40, relief='raised', bd=2)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)
        
        title = tk.Label(title_frame, text="MLOutput - Terminal Output Viewer",
                        bg=COLORS['green'], fg=COLORS['black'],
                        font=('Courier', 14, 'bold'))
        title.pack(expand=True, fill='both', padx=2, pady=2)
        
        # Control panel
        control_frame = tk.Frame(self.root, bg=COLORS['dark_gray'])
        control_frame.pack(fill='x', padx=10, pady=5)
        
        # Stream toggles
        tk.Checkbutton(control_frame, text="stdout", 
                      variable=self.show_stdout,
                      bg=COLORS['dark_gray'], fg=COLORS['white'],
                      selectcolor=COLORS['dark_gray'],
                      font=('Courier', 10)).pack(side='left', padx=5)
        
        tk.Checkbutton(control_frame, text="stderr",
                      variable=self.show_stderr,
                      bg=COLORS['dark_gray'], fg=COLORS['red'],
                      selectcolor=COLORS['dark_gray'],
                      font=('Courier', 10)).pack(side='left', padx=5)
        
        # Buttons
        self.pause_btn = tk.Button(control_frame, text="Pause",
                                  bg=COLORS['light_gray'], fg=COLORS['black'],
                                  font=('Courier', 10), width=8,
                                  command=self._toggle_pause)
        self.pause_btn.pack(side='left', padx=5)
        
        tk.Button(control_frame, text="Clear",
                 bg=COLORS['light_gray'], fg=COLORS['black'],
                 font=('Courier', 10), width=8,
                 command=self._clear).pack(side='left', padx=5)
        
        # Filter
        tk.Label(control_frame, text="Filter:",
                bg=COLORS['dark_gray'], fg=COLORS['white'],
                font=('Courier', 10)).pack(side='left', padx=5)
        
        filter_entry = tk.Entry(control_frame, textvariable=self.filter_pattern,
                               bg=COLORS['black'], fg=COLORS['green'],
                               font=('Courier', 10), width=20)
        filter_entry.pack(side='left', padx=5)
        
        # Output area
        self.output = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            bg=COLORS['black'],
            fg=COLORS['white'],
            font=('Courier', 10),
            insertbackground=COLORS['green']
        )
        self.output.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Tags for coloring
        self.output.tag_configure('stderr', foreground=COLORS['red'])
        self.output.tag_configure('filtered', background=COLORS['yellow'], 
                                 foreground=COLORS['black'])
        
        # Status bar
        self.status = tk.Label(self.root, text=f"Running: {' '.join(self.command)}",
                              bg=COLORS['light_gray'], fg=COLORS['black'],
                              anchor='w', padx=5)
        self.status.pack(fill='x')
        
        # Keyboard shortcuts
        self.root.bind('<Control-c>', lambda e: self._stop_process())
        self.root.bind('<space>', lambda e: self._toggle_pause())
        self.root.bind('<Escape>', lambda e: self.root.quit())
    
    def _start_process(self):
        """Start the subprocess"""
        try:
            # Set up environment for UTF-8
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            self.process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                # Use UTF-8 encoding explicitly
                encoding='utf-8',
                errors='replace',  # Replace undecodable chars with ?
                bufsize=1,
                universal_newlines=True,
                env=env
            )
            
            # Start reader threads
            threading.Thread(target=self._read_stdout, daemon=True).start()
            threading.Thread(target=self._read_stderr, daemon=True).start()
            
        except Exception as e:
            self.output.insert('end', f"Error starting process: {e}\n", 'stderr')
            self.status.config(text=f"Error: {e}")
    
    def _read_stdout(self):
        """Read stdout in background"""
        try:
            for line in self.process.stdout:
                if self.show_stdout.get():
                    self._add_line(line.rstrip(), 'stdout')
        except Exception as e:
            # Log any encoding errors
            self._add_line(f"Output error: {e}", 'stderr')
        finally:
            self.status.config(text="Process ended")
    
    def _read_stderr(self):
        """Read stderr in background"""
        try:
            for line in self.process.stderr:
                if self.show_stderr.get():
                    self._add_line(line.rstrip(), 'stderr')
        except Exception as e:
            # Log any encoding errors
            self._add_line(f"Error output error: {e}", 'stderr')
    
    def _add_line(self, line, stream):
        """Add line to output or buffer"""
        if self.paused:
            self.buffer.append((line, stream))
            return
        
        # Apply filter
        filter_text = self.filter_pattern.get()
        if filter_text:
            try:
                if not re.search(filter_text, line):
                    return
            except:
                pass  # Bad regex, ignore
        
        # Add to output
        self.root.after(0, self._append_output, line, stream, bool(filter_text))
    
    def _append_output(self, line, stream, is_filtered):
        """Append to output widget (must be called from main thread)"""
        try:
            self.output.insert('end', line + '\n', stream if not is_filtered else 'filtered')
            self.output.see('end')
        except tk.TclError as e:
            # Handle any Tkinter encoding issues
            # Replace problematic characters and try again
            safe_line = line.encode('ascii', errors='replace').decode('ascii')
            self.output.insert('end', safe_line + '\n', stream if not is_filtered else 'filtered')
            self.output.see('end')
    
    def _toggle_pause(self):
        """Toggle pause state"""
        self.paused = not self.paused
        self.pause_btn.config(text="Resume" if self.paused else "Pause")
        
        if not self.paused and self.buffer:
            # Flush buffer
            for line, stream in self.buffer:
                self._add_line(line, stream)
            self.buffer.clear()
    
    def _clear(self):
        """Clear output"""
        self.output.delete('1.0', 'end')
        self.buffer.clear()
    
    def _stop_process(self):
        """Stop the subprocess"""
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.status.config(text="Process terminated")

def main():
    # Force UTF-8 on Windows Python output
    if sys.platform == 'win32':
        import locale
        if sys.stdout.encoding != 'utf-8':
            sys.stdout.reconfigure(encoding='utf-8')
        if sys.stderr.encoding != 'utf-8':
            sys.stderr.reconfigure(encoding='utf-8')
    
    if len(sys.argv) < 2:
        print("MLOutput - Terminal output viewer")
        print("Usage: mloutput.py <command>")
        print("Examples:")
        print("  mloutput.py 'ping google.com'")
        print("  mloutput.py 'python script.py'")
        print("  mlquickpage file.txt section | mloutput.py -")
        print("\nKeyboard shortcuts:")
        print("  Space     - Pause/Resume")
        print("  Ctrl+C    - Stop process")
        print("  Escape    - Quit")
        sys.exit(1)
    
    # Handle piped input
    if sys.argv[1] == '-':
        # Read from stdin - ensure UTF-8
        command = [sys.executable, '-u', '-c', 
                  '''import sys
sys.stdout.reconfigure(encoding="utf-8")
for line in sys.stdin:
    print(line, end="")''']
    else:
        # Parse command
        command = shlex.split(' '.join(sys.argv[1:]))
    
    root = tk.Tk()
    app = MLOutput(root, command)
    
    try:
        root.mainloop()
    finally:
        if app.process:
            app.process.terminate()

if __name__ == "__main__":
    main()
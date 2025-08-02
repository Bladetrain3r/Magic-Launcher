#!/usr/bin/env python3
"""
MLTimer - Minimal countdown timer
Part of ML-Extras
"""

import tkinter as tk
import sys
import os

# ML-style constants
COLORS = {
    'dark_gray': '#3C3C3C',
    'light_gray': '#C0C0C0',
    'green': '#00FF00',
    'red': '#FF0000',
    'black': '#000000',
    'white': '#FFFFFF'
}

class MLTimer:
    def __init__(self, root, seconds, auto_exit=True):
        self.root = root
        self.root.title("MLTimer")
        self.root.geometry("300x150")
        self.root.configure(bg=COLORS['dark_gray'])
        self.root.resizable(False, False)
        
        self.total_seconds = seconds
        self.remaining = seconds
        self.running = True
        self.auto_exit = auto_exit
        
        self._create_ui()
        self._tick()
    
    def _create_ui(self):
        """Create the timer UI"""
        # Title bar
        title_frame = tk.Frame(self.root, bg=COLORS['light_gray'], 
                              height=30, relief='raised', bd=2)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)
        
        tk.Label(title_frame, text="MLTimer",
                bg=COLORS['green'], fg=COLORS['black'],
                font=('Courier', 12, 'bold')).pack(expand=True, fill='both')
        
        # Timer display
        self.timer_label = tk.Label(self.root, 
                                   text=self._format_time(self.remaining),
                                   bg=COLORS['black'], fg=COLORS['green'],
                                   font=('Courier', 48, 'bold'))
        self.timer_label.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Status bar
        self.status = tk.Label(self.root, text="Press ESC to cancel",
                              bg=COLORS['light_gray'], fg=COLORS['black'],
                              font=('Courier', 8))
        self.status.pack(fill='x')
        
        # Keyboard shortcuts
        self.root.bind('<Escape>', lambda e: self._cancel())
        self.root.bind('<space>', lambda e: self._pause_resume())
    
    def _format_time(self, seconds):
        """Format seconds as MM:SS"""
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02d}:{secs:02d}"
    
    def _tick(self):
        """Timer tick"""
        if not self.running:
            return
            
        if self.remaining > 0:
            self.timer_label.config(text=self._format_time(self.remaining))
            self.remaining -= 1
            self.root.after(1000, self._tick)
        else:
            self._finish()
    
    def _finish(self):
        """Timer finished"""
        self.timer_label.config(text="DONE!", fg=COLORS['red'])
        self.root.configure(bg=COLORS['red'])
        
        # System beep
        self.root.bell()
        
        if self.auto_exit:
            # Exit after 2 seconds
            self.root.after(2000, lambda: self.root.quit())
        else:
            # Stay open, update status
            self.status.config(text="Press ESC to close")
    
    def _cancel(self):
        """Cancel timer"""
        self.running = False
        sys.exit(1)  # Exit with error code
    
    def _pause_resume(self):
        """Toggle pause/resume"""
        self.running = not self.running
        if self.running:
            self.status.config(text="Press ESC to cancel")
            self._tick()
        else:
            self.status.config(text="PAUSED - Press SPACE to resume")

def parse_time(arg):
    """Parse time argument"""
    try:
        # Just minutes
        if arg.endswith('m'):
            return int(arg[:-1]) * 60
        # Just seconds  
        elif arg.endswith('s'):
            return int(arg[:-1])
        # MM:SS format
        elif ':' in arg:
            parts = arg.split(':')
            return int(parts[0]) * 60 + int(parts[1])
        # Default to seconds
        else:
            return int(arg)
    except:
        return None

def main():
    if len(sys.argv) < 2:
        print("MLTimer - Minimal countdown timer")
        print("Usage: mltimer.py <duration> [--no-exit]")
        print("Examples:")
        print("  mltimer.py 60          # 60 seconds")
        print("  mltimer.py 5m          # 5 minutes") 
        print("  mltimer.py 1:30        # 1 minute 30 seconds")
        print("  mltimer.py 10m --no-exit  # Stay open when done")
        print("\nReturns 0 on completion, 1 if cancelled")
        sys.exit(1)
    
    # Parse arguments
    auto_exit = '--no-exit' not in sys.argv
    duration_arg = sys.argv[1]
    
    seconds = parse_time(duration_arg)
    if not seconds or seconds <= 0:
        print("Invalid duration")
        sys.exit(1)
    
    root = tk.Tk()
    timer = MLTimer(root, seconds, auto_exit)
    
    try:
        root.mainloop()
        sys.exit(0)  # Success
    except:
        sys.exit(1)  # Cancelled/error

if __name__ == "__main__":
    main()
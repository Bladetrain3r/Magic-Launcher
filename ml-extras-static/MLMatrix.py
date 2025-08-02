#!/usr/bin/env python3
"""
MLMatrix - Matrix rain lock screen
Part of ML-Extras
"""

import tkinter as tk
import random
import hashlib
from pathlib import Path

# ML-style constants
CHARS = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ0123456789"
FONT_SIZE = 16
CHAR_WIDTH = 10

class MLMatrix:
    def __init__(self, root):
        self.root = root
        self.root.title("System Locked")
        self.root.configure(bg='black')
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        
        # Check for password file
        self.lock_file = Path.home() / '.config' / 'mlmatrix' / 'lock.txt'
        self.password_hash = None
        
        if self.lock_file.exists():
            with open(self.lock_file, 'r') as f:
                self.password_hash = f.read().strip()
        
        # Canvas for rain
        self.canvas = tk.Canvas(root, bg='black', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        
        # Get screen dimensions
        self.width = root.winfo_screenwidth()
        self.height = root.winfo_screenheight()
        
        # Calculate columns
        self.cols = self.width // CHAR_WIDTH
        self.drops = [random.randint(-20, 0) for _ in range(self.cols)]
        
        # Password buffer
        self.password_buffer = []
        
        # Bind keys
        root.bind('<Key>', self._check_password)
        root.bind('<Escape>', self._check_escape)
        
        # Start animation
        self._animate()
        
    def _animate(self):
        """Matrix rain animation"""
        self.canvas.delete('all')
        
        for i in range(self.cols):
            x = i * CHAR_WIDTH + 5
            y = self.drops[i] * FONT_SIZE
            
            # Draw newest character bright
            if 0 <= y <= self.height:
                char = random.choice(CHARS)
                self.canvas.create_text(x, y, text=char, fill='#00FF00',
                                      font=('Consolas', FONT_SIZE), anchor='w')
            
            # Draw fading trail
            for j in range(1, 64):
                trail_y = y - j * FONT_SIZE
                if trail_y > self.height:
                    break
                if trail_y >= 0:
                    trail_char = random.choice(CHARS)
                    fade = max(0, 255 - j * 17)
                    color = f'#{0:02x}{fade:02x}{0:02x}'
                    self.canvas.create_text(x, trail_y, text=trail_char,
                                          fill=color, font=('Consolas', FONT_SIZE), 
                                          anchor='w')
            
            # Move drop
            self.drops[i] += 1
            if self.drops[i] * FONT_SIZE > self.height + 300:
                self.drops[i] = random.randint(-20, -1)
        
        # Show hint if no password
        if not self.password_hash:
            self.canvas.create_text(self.width//2, self.height - 30,
                                  text="Press ESC to unlock", 
                                  fill='#00FF00', font=('Consolas', 12))
        
        # Continue animation
        self.root.after(1000, self._animate)
    
    def _check_password(self, event):
        """Check typed password"""
        if not self.password_hash or not event.char:
            return
            
        self.password_buffer.append(event.char)
        
        # Keep buffer reasonable size
        if len(self.password_buffer) > 50:
            self.password_buffer.pop(0)
        
        # Check all possible password lengths
        password_str = ''.join(self.password_buffer)
        for i in range(1, len(password_str) + 1):
            test = password_str[-i:]
            if hashlib.md5(test.encode()).hexdigest() == self.password_hash:
                self.root.quit()
                return
    
    def _check_escape(self, event):
        """ESC to exit if no password set"""
        if not self.password_hash:
            self.root.quit()

def main():
    """Run the lock screen"""
    root = tk.Tk()
    
    # Hide cursor
    root.config(cursor="none")
    
    lock = MLMatrix(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        root.destroy()

if __name__ == "__main__":
    main()
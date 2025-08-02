#!/usr/bin/env python3
"""
MLSweeper - Minesweeper following the Magic Launcher Paradigm
Part of ML-Extras
"""

import tkinter as tk
from tkinter import messagebox
import random
import time
import json
import os
from datetime import datetime
from pathlib import Path

# ML-style constants
COLORS = {
    'dark_gray': '#3C3C3C',
    'light_gray': '#C0C0C0', 
    'green': '#00FF00',
    'red': '#FF0000',
    'blue': '#0000FF',
    'white': '#FFFFFF',
    'black': '#000000',
    'yellow': '#FFFF00'
}

# Number colors (classic Minesweeper)
NUM_COLORS = {
    1: '#0000FF',
    2: '#008000',
    3: '#FF0000',
    4: '#000080',
    5: '#800000',
    6: '#008080',
    7: '#000000',
    8: '#808080'
}

class MLSweeper:
    def __init__(self, root, width=9, height=9, mines=10):
        self.root = root
        self.root.title("MLSweeper")
        self.root.configure(bg=COLORS['dark_gray'])
        
        self.width = width
        self.height = height
        self.mine_count = mines
        self.flags = set()
        self.revealed = set()
        self.mines = set()
        self.game_over = False
        self.start_time = None
        self.won = False
        
        # Stats file
        self.stats_file = Path.home() / '.config' / 'mlsweeper' / 'stats.json'
        self.stats_file.parent.mkdir(parents=True, exist_ok=True)
        
        self._create_ui()
        self._new_game()
        
    def _create_ui(self):
        """Create the game UI"""
        # Title bar
        title_frame = tk.Frame(self.root, bg=COLORS['light_gray'], 
                              height=40, relief='raised', bd=2)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)
        
        # New game button
        tk.Button(title_frame, text="NEW", bg=COLORS['green'], 
                 fg=COLORS['black'], font=('Courier', 10, 'bold'),
                 command=self._new_game).pack(side='left', padx=2)
        
        # Settings button
        tk.Button(title_frame, text="SIZE", bg=COLORS['light_gray'],
                 fg=COLORS['black'], font=('Courier', 10, 'bold'),
                 command=self._show_settings).pack(side='left', padx=2)
        
        # Timer and mine counter
        self.info_label = tk.Label(title_frame, text="Mines: 10 | Time: 0",
                                  bg=COLORS['light_gray'], fg=COLORS['black'],
                                  font=('Courier', 10))
        self.info_label.pack(side='left', expand=True)
        
        # Game grid frame
        self.grid_frame = tk.Frame(self.root, bg=COLORS['dark_gray'])
        self.grid_frame.pack(padx=10, pady=10)
        
        # Create grid of buttons
        self.buttons = {}
        for y in range(self.height):
            for x in range(self.width):
                btn = tk.Button(self.grid_frame, width=2, height=1,
                              font=('Courier', 12, 'bold'),
                              bg=COLORS['light_gray'], relief='raised')
                btn.grid(row=y, column=x, padx=1, pady=1)
                btn.bind('<Button-1>', lambda e, x=x, y=y: self._click(x, y))
                btn.bind('<Button-3>', lambda e, x=x, y=y: self._flag(x, y))
                self.buttons[(x, y)] = btn
        
        # Keyboard shortcuts
        self.root.bind('<F9>', lambda e: self._boss_key())
        
        # Timer update
        self._update_timer()
        
    def _new_game(self):
        """Start a new game"""
        self.flags.clear()
        self.revealed.clear()
        self.mines.clear()
        self.game_over = False
        self.won = False
        self.start_time = None
        
        # Place mines randomly
        positions = [(x, y) for x in range(self.width) for y in range(self.height)]
        self.mines = set(random.sample(positions, min(self.mine_count, len(positions))))
        
        # Reset all buttons
        for (x, y), btn in self.buttons.items():
            btn.config(text='', bg=COLORS['light_gray'], relief='raised',
                      state='normal')
        
        self._update_info()
        
    def _click(self, x, y):
        """Handle left click"""
        if self.game_over or (x, y) in self.revealed or (x, y) in self.flags:
            return
            
        if self.start_time is None:
            self.start_time = time.time()
        
        if (x, y) in self.mines:
            self._game_over(False)
        else:
            self._reveal(x, y)
            self._check_win()
    
    def _flag(self, x, y):
        """Handle right click (flag)"""
        if self.game_over or (x, y) in self.revealed:
            return
            
        if (x, y) in self.flags:
            self.flags.remove((x, y))
            self.buttons[(x, y)].config(text='', bg=COLORS['light_gray'])
        else:
            self.flags.add((x, y))
            self.buttons[(x, y)].config(text='🚩', bg=COLORS['yellow'])
        
        self._update_info()
    
    def _reveal(self, x, y):
        """Reveal a cell"""
        if (x, y) in self.revealed or not (0 <= x < self.width and 0 <= y < self.height):
            return
            
        self.revealed.add((x, y))
        count = self._count_adjacent_mines(x, y)
        
        btn = self.buttons[(x, y)]
        btn.config(relief='sunken', bg=COLORS['white'], state='disabled')
        
        if count > 0:
            btn.config(text=str(count), fg=NUM_COLORS.get(count, COLORS['black']))
        else:
            # Auto-reveal adjacent cells if no mines nearby
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    self._reveal(x + dx, y + dy)
    
    def _count_adjacent_mines(self, x, y):
        """Count mines in adjacent cells"""
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in self.mines:
                    count += 1
        return count
    
    def _check_win(self):
        """Check if player won"""
        unrevealed = set()
        for x in range(self.width):
            for y in range(self.height):
                if (x, y) not in self.revealed:
                    unrevealed.add((x, y))
        
        if unrevealed == self.mines:
            self._game_over(True)
    
    def _game_over(self, won):
        """End the game"""
        self.game_over = True
        self.won = won
        
        # Calculate time
        elapsed = int(time.time() - self.start_time) if self.start_time else 0
        
        # Reveal all mines
        for (x, y) in self.mines:
            if (x, y) not in self.flags:
                self.buttons[(x, y)].config(text='💣', bg=COLORS['red'])
        
        # Save stats
        self._save_stats(won, elapsed)
        
        # Show result
        if won:
            messagebox.showinfo("Victory!", f"You won in {elapsed} seconds!")
        else:
            messagebox.showinfo("Game Over", "Boom! Try again!")
    
    def _save_stats(self, won, time_seconds):
        """Save game stats to JSON"""
        stats = {
            'timestamp': datetime.now().isoformat(),
            'width': self.width,
            'height': self.height,
            'mines': self.mine_count,
            'won': won,
            'time_seconds': time_seconds
        }
        
        # Append to file
        try:
            if self.stats_file.exists():
                with open(self.stats_file, 'r') as f:
                    data = json.load(f)
            else:
                data = []
            
            data.append(stats)
            
            # Keep last 1000 games
            if len(data) > 1000:
                data = data[-1000:]
            
            with open(self.stats_file, 'w') as f:
                json.dump(data, f, indent=2)
        except:
            pass  # Fail silently
    
    def _update_info(self):
        """Update mine counter"""
        remaining = self.mine_count - len(self.flags)
        time_str = "0"
        if self.start_time and not self.game_over:
            time_str = str(int(time.time() - self.start_time))
        self.info_label.config(text=f"Mines: {remaining} | Time: {time_str}")
    
    def _update_timer(self):
        """Update timer display"""
        if not self.game_over:
            self._update_info()
        self.root.after(1000, self._update_timer)
    
    def _show_settings(self):
        """Show settings dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Game Settings")
        dialog.geometry("250x150")
        
        tk.Label(dialog, text="Width:").grid(row=0, column=0, padx=5, pady=5)
        width_var = tk.StringVar(value=str(self.width))
        tk.Entry(dialog, textvariable=width_var, width=10).grid(row=0, column=1)
        
        tk.Label(dialog, text="Height:").grid(row=1, column=0, padx=5, pady=5)
        height_var = tk.StringVar(value=str(self.height))
        tk.Entry(dialog, textvariable=height_var, width=10).grid(row=1, column=1)
        
        tk.Label(dialog, text="Mines:").grid(row=2, column=0, padx=5, pady=5)
        mines_var = tk.StringVar(value=str(self.mine_count))
        tk.Entry(dialog, textvariable=mines_var, width=10).grid(row=2, column=1)
        
        def apply_settings():
            try:
                w = int(width_var.get())
                h = int(height_var.get())
                m = int(mines_var.get())
                
                if 5 <= w <= 30 and 5 <= h <= 20 and 1 <= m < w * h:
                    self.width = w
                    self.height = h
                    self.mine_count = m
                    
                    # Rebuild grid
                    self.grid_frame.destroy()
                    self.grid_frame = tk.Frame(self.root, bg=COLORS['dark_gray'])
                    self.grid_frame.pack(padx=10, pady=10)
                    
                    self.buttons = {}
                    for y in range(self.height):
                        for x in range(self.width):
                            btn = tk.Button(self.grid_frame, width=2, height=1,
                                          font=('Courier', 12, 'bold'),
                                          bg=COLORS['light_gray'], relief='raised')
                            btn.grid(row=y, column=x, padx=1, pady=1)
                            btn.bind('<Button-1>', lambda e, x=x, y=y: self._click(x, y))
                            btn.bind('<Button-3>', lambda e, x=x, y=y: self._flag(x, y))
                            self.buttons[(x, y)] = btn
                    
                    self._new_game()
                    dialog.destroy()
                else:
                    messagebox.showerror("Invalid", "Invalid dimensions")
            except:
                messagebox.showerror("Error", "Invalid input")
        
        tk.Button(dialog, text="Apply", command=apply_settings).grid(row=3, column=0, columnspan=2, pady=10)
    
    def _boss_key(self):
        """Emergency work mode!"""
        # Hide the game
        self.root.withdraw()
        widthbase = 800
        heightbase = 600
        # Create fake terminal window
        boss = tk.Toplevel()
        boss.title("system-monitor.py")
        boss.geometry(f"{widthbase}x{heightbase}")
        boss.configure(bg='black')
        
        # Matrix-style text area
        text = tk.Text(boss, bg='black', fg="#008000", 
                      font=('Consolas', 10), wrap='none')
        text.pack(fill='both', expand=True)
        
        # Matrix rain content
        matrix_chars = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ0123456789"
        
        # Fill with convincing-looking system monitoring
        text.insert('1.0', """System Resource Monitor v2.1.3
=====================================
Loading kernel modules...
[OK] cpu_freq_scaling
[OK] memory_management  
[OK] disk_io_scheduler
[OK] network_stack_optimizer

Analyzing system performance metrics...
""")
        
        # Add some matrix rain
        def update_matrix():
            if not boss.winfo_exists():
                return
            # Add random matrix characters
            no_chars = random.randint(1, widthbase // 10)
            line = ''.join(random.choice(matrix_chars + '     ') for _ in range(no_chars))
            text.insert('end', line + '\n')
            text.see('end')
            # Keep last 40 lines
            if int(text.index('end-1c').split('.')[0]) > 40:
                text.delete('1.0', '2.0')
            boss.after(100, update_matrix)
        
        update_matrix()
        
        # Restore game on any key or close
        def restore(_=None):
            boss.destroy()
            self.root.deiconify()
            self.root.focus_force()

        boss.bind('<Escape>', restore)
        boss.bind('<Double-Button-1>', restore)
        boss.protocol("WM_DELETE_WINDOW", restore)
        
        # Focus the boss window
        boss.focus_force()

def main():
    root = tk.Tk()
    root.resizable(False, False)
    
    # Parse command line args
    import sys
    width = height = 9
    mines = 10
    
    if len(sys.argv) > 3:
        try:
            width = int(sys.argv[1])
            height = int(sys.argv[2]) 
            mines = int(sys.argv[3])
        except:
            print("Usage: mlsweeper.py [width] [height] [mines]")
            print("Default: mlsweeper.py 9 9 10")
    
    game = MLSweeper(root, width, height, mines)
    root.mainloop()

if __name__ == "__main__":
    main()
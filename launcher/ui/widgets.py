"""UI widgets for the launcher."""

import tkinter as tk
from typing import Callable, Optional, List
import os
from shutil import which

from constants import COLORS, ICON_SIZE
from models import BaseItem, Folder, Shortcut
from utils.icons import icon_manager
from utils.logger import logger


class IconWidget(tk.Frame):
    """Widget displaying a single launcher icon."""
    
    def __init__(self, parent, item: BaseItem, path: List[str] = None,
                 on_click: Callable = None, on_double_click: Callable = None,
                 on_right_click: Callable = None):
        super().__init__(parent, bg=COLORS['dark_gray'], width=120, height=140)
        self.pack_propagate(False)
        
        self.item = item
        self.path = path or []
        self.on_click = on_click
        self.on_double_click = on_double_click
        self.on_right_click = on_right_click
        
        self._create_widgets()
        self._bind_events()
    
    def _create_widgets(self):
        """Create the icon and label."""
        # Icon box
        icon_color = COLORS['yellow'] if isinstance(self.item, Folder) else COLORS['light_gray']
        self.icon_box = tk.Frame(self, bg=icon_color, width=ICON_SIZE, height=ICON_SIZE,
                                relief='raised', bd=3, highlightthickness=0)
        self.icon_box.pack(pady=(10, 5))
        self.icon_box.pack_propagate(False)
        
        # Try to load image icon
        icon_image = icon_manager.get_icon(self.item.icon)
        
        if icon_image:
            self.icon_label = tk.Label(self.icon_box, image=icon_image, 
                                      bg=icon_color, bd=0)
            self.icon_label.image = icon_image  # Keep reference
        else:
            # Text icon
            icon_text = self.item.icon[:2] if len(self.item.icon) <= 2 else self.item.name[0].upper()
            self.icon_label = tk.Label(self.icon_box, text=icon_text, bg=icon_color,
                                      font=('Courier', 36, 'bold'))
        
        self.icon_label.place(relx=0.5, rely=0.5, anchor='center')
        
        # Check if shortcut is broken and add red X overlay
        if isinstance(self.item, Shortcut) and self.item.path:
            if not self._is_valid_shortcut():
                self._add_broken_overlay()
        
        # Name label
        self.name_label = tk.Label(self, text=self.item.name, bg=COLORS['blue'], 
                                  fg=COLORS['white'], font=('Courier', 10), 
                                  width=12, anchor='center')
        self.name_label.pack()
    
    def _is_valid_shortcut(self) -> bool:
        """Check if a shortcut path is valid."""
        path = self.item.path
        
        # URLs are always considered valid (we can't check them quickly)
        if path.startswith(('http://', 'https://')):
            return True
        
        # Expand environment variables and user paths
        expanded = os.path.expanduser(os.path.expandvars(path))
        
        # Check if it's an absolute path that exists
        if os.path.isabs(expanded):
            return os.path.exists(expanded)
        
        # Check if it's a command in PATH
        from shutil import which
        # Extract just the command name (before any arguments)
        cmd = path.split()[0] if path else ""
        return which(cmd) is not None
    
    def _add_broken_overlay(self):
        """Add a red X overlay for broken shortcuts."""
        # Create red X using canvas
        self.overlay = tk.Canvas(self.icon_box, width=ICON_SIZE-6, height=ICON_SIZE-6,
                           bg=self.icon_box['bg'], highlightthickness=0)
        self.overlay.place(relx=0.5, rely=0.5, anchor='center')
        
        # Draw red X
        margin = 15
        # First diagonal
        self.overlay.create_line(margin, margin, 
                          ICON_SIZE-6-margin, ICON_SIZE-6-margin,
                          fill=COLORS['red'], width=4, capstyle='round')
        # Second diagonal
        self.overlay.create_line(ICON_SIZE-6-margin, margin,
                          margin, ICON_SIZE-6-margin,
                          fill=COLORS['red'], width=4, capstyle='round')
        
        # Make it semi-transparent to existing icon by using stipple
        self.overlay.tag_lower('all')  # Put behind text but in front of background
        
        # Bind events to overlay too
        self.overlay.bind('<ButtonPress-1>', self._on_press)
        self.overlay.bind('<ButtonRelease-1>', self._on_release)
        self.overlay.bind('<Double-Button-1>', self._on_double_click)
        self.overlay.bind('<Button-3>', self._on_right_click)
        self.overlay.bind('<Enter>', self._on_enter)
        self.overlay.bind('<Leave>', self._on_leave)
    
    def _bind_events(self):
        """Bind mouse events."""
        widgets = [self, self.icon_box, self.icon_label, self.name_label]
        
        # Also bind to overlay if it exists
        if hasattr(self, 'overlay'):
            widgets.append(self.overlay)
        
        for widget in widgets:
            widget.bind('<ButtonPress-1>', self._on_press)
            widget.bind('<ButtonRelease-1>', self._on_release)
            widget.bind('<Double-Button-1>', self._on_double_click)
            widget.bind('<Button-3>', self._on_right_click)
            widget.bind('<Enter>', self._on_enter)
            widget.bind('<Leave>', self._on_leave)
    
    def _on_press(self, event):
        self.icon_box.config(relief='sunken')
        if self.on_click:
            self.on_click(self.item, self.path)
    
    def _on_release(self, event):
        self.icon_box.config(relief='raised')
    
    def _on_double_click(self, event):
        if self.on_double_click:
            self.on_double_click(self.item, self.path)
    
    def _on_right_click(self, event):
        if self.on_right_click:
            self.on_right_click(event, self.item, self.path)
    
    def _on_enter(self, event):
        self.icon_box.config(relief='sunken')
    
    def _on_leave(self, event):
        self.icon_box.config(relief='raised')


class SearchBar(tk.Frame):
    """Search bar widget."""
    
    def __init__(self, parent, on_search: Callable = None):
        super().__init__(parent, bg=COLORS['black'], highlightthickness=2, 
                        highlightbackground=COLORS['white'])
        
        self.on_search = on_search
        self._create_widgets()
    
    def _create_widgets(self):
        """Create search entry."""
        self.entry = tk.Entry(self, bg=COLORS['black'], fg=COLORS['light_green'],
                             insertbackground=COLORS['light_green'],
                             font=('Courier', 10), bd=0)
        self.entry.pack(padx=5, pady=5)
        
        if self.on_search:
            self.entry.bind('<KeyRelease>', lambda e: self.on_search(self.get_query()))
    
    def get_query(self) -> str:
        """Get current search query."""
        return self.entry.get()
    
    def clear(self):
        """Clear search query."""
        self.entry.delete(0, 'end')
    
    def focus(self):
        """Focus the search entry."""
        self.entry.focus()
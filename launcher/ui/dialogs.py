"""Dialog windows for the launcher."""

import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Optional, Tuple
from pathlib import Path

from constants import COLORS, FILE_FILTERS, ICON_FILTERS, ICONS_DIR
from models import BaseItem, Shortcut, Folder
from utils.icons import icon_manager
from utils.logger import logger


class ItemDialog:
    """Dialog for creating/editing launcher items."""
    
    def __init__(self, parent, title: str = "Item", item: Optional[BaseItem] = None):
        self.result = None
        self.parent = parent
        self.item = item
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x350")
        self.dialog.resizable(False, False)
        self.dialog.configure(bg=COLORS['light_gray'])
        
        # Make modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._create_widgets()
        self._populate_fields()
        
        # Focus name entry
        self.name_entry.focus()
        
        # Center on parent
        self._center_on_parent()
    
    def _center_on_parent(self):
        """Center dialog on parent window."""
        self.dialog.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        """Create dialog widgets."""
        # Name
        tk.Label(self.dialog, text="Name:", bg=COLORS['light_gray']).grid(
            row=0, column=0, sticky='w', padx=10, pady=5)
        self.name_entry = tk.Entry(self.dialog, width=30)
        self.name_entry.grid(row=0, column=1, padx=10, pady=5, columnspan=2, sticky='ew')
        
        # Type
        tk.Label(self.dialog, text="Type:", bg=COLORS['light_gray']).grid(
            row=1, column=0, sticky='w', padx=10, pady=5)
        self.type_var = tk.StringVar(value='shortcut')
        type_menu = tk.OptionMenu(self.dialog, self.type_var, 'shortcut', 'folder')
        type_menu.grid(row=1, column=1, sticky='w', padx=10, pady=5)
        
        # Path with browse
        tk.Label(self.dialog, text="Path/URL:", bg=COLORS['light_gray']).grid(
            row=2, column=0, sticky='w', padx=10, pady=5)
        path_frame = tk.Frame(self.dialog, bg=COLORS['light_gray'])
        path_frame.grid(row=2, column=1, padx=10, pady=5, columnspan=2, sticky='ew')
        
        self.path_entry = tk.Entry(path_frame, width=25)
        self.path_entry.pack(side='left', fill='x', expand=True)
        
        self.browse_btn = tk.Button(path_frame, text="Browse...", 
                                   command=self._browse_file,
                                   bg=COLORS['light_gray'], fg=COLORS['black'],
                                   font=('Courier', 9), bd=2, relief='raised')
        self.browse_btn.pack(side='right', padx=(5, 0))
        
        # Arguments
        tk.Label(self.dialog, text="Arguments:", bg=COLORS['light_gray']).grid(
            row=3, column=0, sticky='w', padx=10, pady=5)
        self.args_entry = tk.Entry(self.dialog, width=30)
        self.args_entry.grid(row=3, column=1, padx=10, pady=5, columnspan=2, sticky='ew')
        
        # Icon with browse
        tk.Label(self.dialog, text="Icon:", bg=COLORS['light_gray']).grid(
            row=4, column=0, sticky='w', padx=10, pady=5)
        icon_frame = tk.Frame(self.dialog, bg=COLORS['light_gray'])
        icon_frame.grid(row=4, column=1, sticky='ew', padx=10, pady=5, columnspan=2)
        
        self.icon_entry = tk.Entry(icon_frame, width=15)
        self.icon_entry.pack(side='left')
        
        tk.Label(icon_frame, text="(1 char or .bmp)", bg=COLORS['light_gray'],
                font=('Courier', 8)).pack(side='left', padx=5)
        
        self.icon_browse_btn = tk.Button(icon_frame, text="Browse...",
                                        command=self._browse_icon,
                                        bg=COLORS['light_gray'], fg=COLORS['black'],
                                        font=('Courier', 9), bd=2, relief='raised')
        self.icon_browse_btn.pack(side='right')
        
        # Buttons
        button_frame = tk.Frame(self.dialog, bg=COLORS['light_gray'])
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        tk.Button(button_frame, text="Save", command=self._save,
                 bg=COLORS['light_gray'], fg=COLORS['black'],
                 font=('Courier', 10), bd=2, relief='raised').pack(side='left', padx=5)
        tk.Button(button_frame, text="Cancel", command=self._cancel,
                 bg=COLORS['light_gray'], fg=COLORS['black'],
                 font=('Courier', 10), bd=2, relief='raised').pack(side='left', padx=5)
        
        # Configure grid
        self.dialog.columnconfigure(1, weight=1)
        
        # Update fields based on type
        self.type_var.trace('w', self._on_type_change)
        self._on_type_change()
    
    def _populate_fields(self):
        """Populate fields if editing existing item."""
        if not self.item:
            return
        
        self.name_entry.insert(0, self.item.name)
        self.icon_entry.insert(0, self.item.icon)
        
        if isinstance(self.item, Shortcut):
            self.type_var.set('shortcut')
            self.path_entry.insert(0, self.item.path)
            self.args_entry.insert(0, self.item.args)
        else:
            self.type_var.set('folder')
    
    def _on_type_change(self, *args):
        """Handle type change."""
        is_folder = self.type_var.get() == 'folder'
        state = 'disabled' if is_folder else 'normal'
        
        self.path_entry.config(state=state)
        self.args_entry.config(state=state)
        self.browse_btn.config(state=state)
    
    def _browse_file(self):
        """Browse for executable file."""
        filename = filedialog.askopenfilename(
            parent=self.dialog,
            title="Select executable or script",
            filetypes=FILE_FILTERS
        )
        if filename:
            self.path_entry.delete(0, 'end')
            self.path_entry.insert(0, filename)
    
    def _browse_icon(self):
        """Browse for icon file."""
        filename = filedialog.askopenfilename(
            parent=self.dialog,
            title="Select BMP icon",
            initialdir=str(ICONS_DIR) if ICONS_DIR.exists() else None,
            filetypes=ICON_FILTERS
        )
        
        if filename:
            path = Path(filename)
            # If already in icons dir, just use filename
            if path.parent == ICONS_DIR:
                self.icon_entry.delete(0, 'end')
                self.icon_entry.insert(0, path.name)
            else:
                # Always copy to icons directory
                icon_name = icon_manager.copy_icon_to_storage(filename)
                if icon_name:
                    self.icon_entry.delete(0, 'end')
                    self.icon_entry.insert(0, icon_name)
                    logger.info(f"Imported icon: {filename} -> {icon_name}")
                else:
                    messagebox.showerror("Icon Error", 
                                       f"Could not import icon:\n{filename}",
                                       parent=self.dialog)
    
    def _save(self):
        """Save and close dialog."""
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Invalid Name", "Please enter a name",
                                 parent=self.dialog)
            return
        
        icon_value = self.icon_entry.get().strip()
        
        # If icon is a path to a file, copy it to icons directory
        if icon_value and (icon_value.endswith('.bmp') or '/' in icon_value or '\\' in icon_value):
            icon_path = Path(icon_value)
            if icon_path.is_absolute() and icon_path.exists():
                # Copy to icons directory
                new_icon = icon_manager.copy_icon_to_storage(str(icon_path))
                if new_icon:
                    icon_value = new_icon
                    logger.info(f"Auto-imported icon: {icon_path} -> {new_icon}")
                else:
                    logger.warning(f"Could not import icon: {icon_path}")
        
        self.result = (
            name,
            self.type_var.get(),
            self.path_entry.get().strip(),
            icon_value,
            self.args_entry.get().strip()
        )
        
        logger.info(f"Dialog saved: {name} ({self.type_var.get()})")
        self.dialog.destroy()
    
    def _cancel(self):
        """Cancel and close dialog."""
        self.dialog.destroy()
    
    def wait(self) -> Optional[Tuple[str, str, str, str, str]]:
        """Wait for dialog to close and return result."""
        self.dialog.wait_window()
        return self.result
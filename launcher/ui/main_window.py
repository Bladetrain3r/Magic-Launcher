"""Main window for the launcher."""

import tkinter as tk
from tkinter import messagebox
from typing import Dict, List, Tuple, Optional
import os
from shutil import which

from constants import *
from models import BaseItem, Folder, Shortcut, item_from_dict
from config import config_manager
from utils.launcher import Launcher
from utils.logger import logger
from ui.widgets import IconWidget, SearchBar
from ui.dialogs import ItemDialog


class MainWindow:
    """Main application window."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(f"{config_manager.get_app_name()} v{VERSION}")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(False, False)
        self.root.configure(bg=COLORS['dark_gray'])
        
        # State
        self.shortcuts: Dict[str, BaseItem] = {}
        self.current_path: List[str] = []
        self.search_active = False
        self.search_query = ""
        self.selected_item: Optional[Tuple[BaseItem, List[str]]] = None
        self.dialog_open = False
        
        # Load data
        self.load_shortcuts()
        
        # Create UI
        self._create_ui()
        self._bind_shortcuts()
        
        # Initial render
        self.render_items()
        
        logger.info(f"Main window initialized")
    
    def load_shortcuts(self):
        """Load shortcuts from config."""
        self.shortcuts = config_manager.load_shortcuts()
    
    def save_shortcuts(self):
        """Save shortcuts to config."""
        config_manager.save_shortcuts(self.shortcuts)

    def refresh_shortcuts(self):
        """Reload shortcuts from config."""
        self.load_shortcuts()
        self.render_items()
    
    def _create_ui(self):
        """Create the main UI."""
        # Title bar
        self._create_title_bar()
        
        # Info bar (breadcrumb and search)
        self._create_info_bar()
        
        # Main content area
        self._create_content_area()
    
    def _create_title_bar(self):
        """Create the title bar."""
        title_frame = tk.Frame(self.root, bg=COLORS['light_gray'], 
                              height=40, relief='raised', bd=2)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)
        
        # Buttons
        self._make_button(title_frame, "STOP", COLORS['red'], 
                         self.quit_app).pack(side='left', padx=2)
        self._make_button(title_frame, "i", COLORS['blue'], 
                         self.show_info).pack(side='left', padx=2)
        
        # Title
        title = tk.Label(title_frame, text=f"{config_manager.get_app_name()} v{VERSION}",
                        bg=COLORS['green'], fg=COLORS['white'],
                        font=('Courier', 16, 'bold'))
        title.pack(side='left', expand=True, fill='both', padx=2)

        self._make_button(title_frame, "S", COLORS['light_gray'],
                         self.substitute_paths_dialog).pack(side='right', padx=2)

        separator = tk.Frame(title_frame, width=2, bg=COLORS['dark_gray'], height=30)
        separator.pack(side='right', padx=5)
        
        # Right buttons
        self._make_button(title_frame, "FIND", COLORS['light_gray'],
                         self.toggle_search).pack(side='right', padx=2)
        self._make_button(title_frame, "+", COLORS['light_gray'],
                         self.add_item).pack(side='right', padx=2)
    
    def _create_info_bar(self):
        """Create the info bar with breadcrumb and search."""
        info_frame = tk.Frame(self.root, bg=COLORS['dark_gray'], height=30)
        info_frame.pack(fill='x')
        
        # Breadcrumb
        self.breadcrumb = tk.Label(info_frame, text="HOME",
                                  bg=COLORS['black'], fg=COLORS['light_cyan'],
                                  font=('Courier', 10), anchor='w', padx=5)
        self.breadcrumb.pack(side='left', padx=20, pady=5)
        
        # Search bar (hidden initially)
        self.search_bar = SearchBar(info_frame, on_search=self.on_search)
    
    def _create_content_area(self):
        """Create the scrollable content area."""
        # Canvas for scrolling
        self.canvas = tk.Canvas(self.root, bg=COLORS['dark_gray'], 
                               highlightthickness=0)
        self.canvas.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Scrollbar
        scrollbar = tk.Scrollbar(self.root, orient='vertical',
                                command=self.canvas.yview)
        scrollbar.pack(side='right', fill='y', padx=(0, 20))
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame for items
        self.item_frame = tk.Frame(self.canvas, bg=COLORS['dark_gray'])
        self.canvas_window = self.canvas.create_window((0, 0), 
                                                      window=self.item_frame,
                                                      anchor='nw')
        
        # Configure scrolling
        self.item_frame.bind('<Configure>', self._on_frame_configure)
        self.canvas.bind('<Configure>', self._on_canvas_configure)
    
    def _make_button(self, parent, text, bg, command):
        """Create a standard button."""
        return tk.Button(parent, text=text, bg=bg, fg=COLORS['white'],
                        font=('Courier', 10, 'bold'), bd=2, relief='raised',
                        activebackground=bg, command=command, cursor='hand2',
                        highlightthickness=0, padx=10)
    
    def _bind_shortcuts(self):
        """Bind keyboard shortcuts."""
        self.root.bind('<Control-q>', lambda e: self.quit_app())
        self.root.bind('<Control-i>', lambda e: self.show_info())
        self.root.bind('<Control-s>', lambda e: self.substitute_paths_dialog())
        self.root.bind('<Control-n>', lambda e: self.add_item())
        self.root.bind('<Control-h>', lambda e: self.go_home())
        self.root.bind('<Control-f>', lambda e: self.toggle_search())
        self.root.bind('<Control-d>', lambda e: self.duplicate_selected())
        self.root.bind('<Control-e>', lambda e: self.edit_item(self.selected_item[0]) if self.selected_item else None)
        self.root.bind('<Control-r>', lambda e: self.refresh_shortcuts())
        self.root.bind('<Control-p>', lambda e: self.show_properties(self.selected_item[0]) if self.selected_item else None)
        self.root.bind('<Escape>', self._handle_escape)
        self.root.bind('<Return>', self._handle_enter)
        self.root.bind('<BackSpace>', lambda e: self.go_up() if self.current_path else None)
        self.root.bind('<Left>', self.navigate_left)
        self.root.bind('<Right>', self.navigate_right)
    
    def render_items(self):
        """Render the current items."""
        # Clear existing
        for widget in self.item_frame.winfo_children():
            widget.destroy()
        
        items_to_show = self._get_items_to_show()
        
        # Create grid
        row, col = 0, 0
        for name, item, path in items_to_show:
            widget = IconWidget(self.item_frame, item, path,
                              on_click=self.on_item_click,
                              on_double_click=self.on_item_double_click,
                              on_right_click=self.on_item_right_click)
            widget.grid(row=row, column=col, padx=10, pady=10, sticky='n')
            
            col += 1
            if col >= ICON_GRID_COLUMNS:
                col = 0
                row += 1
        
        self._update_breadcrumb()
    
    def _get_items_to_show(self) -> List[Tuple[str, BaseItem, List[str]]]:
        """Get items to display based on current state."""
        items = []
        
        if self.search_active and self.search_query:
            # Recursive search
            items = self._search_recursive(self.shortcuts, self.search_query)
        else:
            # Current folder view
            folder = self._get_current_folder()
            
            # Add back button
            if self.current_path:
                back_item = Shortcut(name='..', icon='^', path='')
                back_item.type = 'up'
                items.append(('..', back_item, []))
            
            # Add folder items
            if isinstance(folder, dict):
                for name, item in folder.items():
                    items.append((name, item, self.current_path.copy()))
            elif isinstance(folder, Folder):
                for name, item in folder.items.items():
                    items.append((name, item, self.current_path.copy()))
        
        return items
    
    def _get_current_folder(self):
        """Get the current folder."""
        folder = self.shortcuts
        
        for name in self.current_path:
            if isinstance(folder, dict):
                item = folder.get(name)
            else:
                item = folder.items.get(name)
            
            if isinstance(item, Folder):
                folder = item.items
            else:
                break
        
        return folder
    
    def _search_recursive(self, items, query: str, path: List[str] = None) -> List[Tuple[str, BaseItem, List[str]]]:
        """Recursively search for items."""
        if path is None:
            path = []
        
        results = []
        query_lower = query.lower()
        
        # Handle dict or Folder
        if isinstance(items, dict):
            item_dict = items
        elif isinstance(items, Folder):
            item_dict = items.items
        else:
            return results
        
        for name, item in item_dict.items():
            # Check if name matches
            if query_lower in name.lower():
                display_name = name
                if path:
                    display_name = f"{name} ({' > '.join(path)})"
                results.append((display_name, item, path.copy()))
            
            # Search subfolders
            if isinstance(item, Folder):
                sub_results = self._search_recursive(item, query, path + [name])
                results.extend(sub_results)
        
        return results
    
    def _update_breadcrumb(self):
        """Update breadcrumb display."""
        if self.current_path:
            self.breadcrumb.config(text="HOME > " + " > ".join(self.current_path))
        else:
            self.breadcrumb.config(text="HOME")
    
    def on_item_click(self, item: BaseItem, path: List[str]):
        """Handle item click."""
        self.selected_item = (item, path)
        self._highlight_selected()
    
    def on_item_double_click(self, item: BaseItem, path: List[str]):
        """Handle item double-click."""
        if hasattr(item, 'type') and item.type == 'up':
            self.go_up()
        elif isinstance(item, Folder):
            # Navigate to folder
            if self.search_active:
                self.search_active = False
                self.search_bar.pack_forget()
                self.search_query = ""
                self.current_path = path + [item.name]
            else:
                self.current_path.append(item.name)
            self.render_items()
        elif isinstance(item, Shortcut):
            # Check if shortcut is valid before launching
            if self._is_valid_shortcut(item):
                if not Launcher.launch(item.path, item.args):
                    messagebox.showerror("Launch Error", 
                                       f"Could not launch {item.name}")
            else:
                messagebox.showerror("Broken Shortcut", 
                                   f"'{item.name}' points to a missing file or program:\n{item.path}\n\nRight-click to edit or delete.")
    
    def _is_valid_shortcut(self, shortcut: Shortcut) -> bool:
        """Check if a shortcut path is valid."""
        path = shortcut.path
        
        # Empty path is invalid
        if not path:
            return False
        
        # URLs are always considered valid
        if path.startswith(('http://', 'https://')):
            return True
        
        # Expand environment variables and user paths
        expanded = os.path.expanduser(os.path.expandvars(path))
        
        # Check if it's an absolute path that exists
        if os.path.isabs(expanded):
            return os.path.exists(expanded)
        
        # Check if it's a command in PATH
        from shutil import which
        cmd = path.split()[0] if path else ""
        return which(cmd) is not None
    
    def on_item_right_click(self, event, item: BaseItem, path: List[str]):
        """Handle right-click on item."""
        if hasattr(item, 'type') and item.type == 'up':
            return
        
        menu = tk.Menu(self.root, tearoff=0, bg=COLORS['light_gray'],
                      fg=COLORS['black'], activebackground=COLORS['blue'],
                      activeforeground=COLORS['white'])
        
        menu.add_command(label="Edit", 
                        command=lambda: self.edit_item(item))
        menu.add_command(label="Duplicate", 
                        command=lambda: self.duplicate_item(item))
        menu.add_command(label="Delete", 
                        command=lambda: self.delete_item(item))
        menu.add_separator()
        menu.add_command(label="Properties", 
                        command=lambda: self.show_properties(item))
        
        menu.post(event.x_root, event.y_root)
    
    def toggle_search(self):
        """Toggle search mode."""
        self.search_active = not self.search_active
        
        if self.search_active:
            self.search_bar.pack(side='right', padx=20, pady=5)
            self.search_bar.clear()
            self.search_bar.focus()
        else:
            self.search_bar.pack_forget()
            self.search_query = ""
            self.render_items()
    
    def on_search(self, query: str):
        """Handle search query change."""
        self.search_query = query
        self.render_items()

    def go_home(self):
        """Navigate to home directory."""
        self.current_path = []
        self.render_items()
    
    def go_up(self):
        """Navigate up one level."""
        if self.current_path:
            self.current_path.pop()
            self.render_items()

    def substitute_paths_dialog(self):
        """Open dialog for path substitution"""
        if self.dialog_open:
            return
            
        self.dialog_open = True
        
        # Create dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Substitute Values")
        dialog.geometry("400x150")

        # Block closing the dialog with the close button
        # Fix for bug in 0.3.2.1
        dialog.protocol("WM_DELETE_WINDOW", lambda: (dialog.destroy(), setattr(self, 'dialog_open', False)))
        
        # Create entries FIRST
        tk.Label(dialog, text="Old Value:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        old_entry = tk.Entry(dialog, width=40)
        old_entry.grid(row=0, column=1, columnspan=3, padx=5, pady=5, sticky='ew')
        
        tk.Label(dialog, text="New Value:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        new_entry = tk.Entry(dialog, width=40)
        new_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky='ew')
        
        # Now define the function that uses the entries
        def do_substitute(fieldtype="path"):
            old = old_entry.get()
            new = new_entry.get()
            if old and new:
                config_manager.substitute_field(old, new, fieldtype=fieldtype)
                self.load_shortcuts()
                self.render_items()
                messagebox.showinfo("Success", f"Replaced {fieldtype}: '{old}' → '{new}'")
                dialog.destroy()
                self.dialog_open = False
        
        # Use lambda to pass the fieldtype without calling the function
        tk.Button(dialog, text="Replace Paths", 
                  command=lambda: do_substitute(fieldtype="path")).grid(row=2, column=0, padx=5, pady=10)
        tk.Button(dialog, text="Replace Args", 
                  command=lambda: do_substitute(fieldtype="args")).grid(row=2, column=1, padx=5, pady=10)
        tk.Button(dialog, text="Replace Icons", 
                  command=lambda: do_substitute(fieldtype="icon")).grid(row=2, column=2, padx=5, pady=10)
        tk.Button(dialog, text="Cancel", 
                  command=lambda: (dialog.destroy(), setattr(self, 'dialog_open', False))).grid(row=2, column=3, padx=5, pady=10)
        
        # Configure grid weights for better layout
        dialog.columnconfigure(1, weight=1)
    
    def add_item(self):
        """Add a new item."""
        if self.dialog_open:
            return
            
        self.dialog_open = True
        dialog = ItemDialog(self.root, "New Item")
        result = dialog.wait()
        self.dialog_open = False
        
        if result:
            name, item_type, path, icon, args = result
            folder = self._get_current_folder()
            
            # Create new item
            if item_type == 'folder':
                new_item = Folder(name=name, icon=icon or name[0].upper())
            else:
                new_item = Shortcut(name=name, icon=icon or name[0].upper(),
                                   path=path, args=args)
            
            # Add to folder
            if isinstance(folder, dict):
                folder[name] = new_item
            else:
                folder.items[name] = new_item
            
            self.save_shortcuts()
            self.render_items()
    
    def edit_item(self, item: BaseItem):
        """Edit an item."""
        if self.dialog_open:
            return
            
        self.dialog_open = True
        dialog = ItemDialog(self.root, f"Edit {item.name}", item)
        result = dialog.wait()
        self.dialog_open = False
        
        if result:
            name, item_type, path, icon, args = result
            
            # Update item properties
            old_name = item.name
            item.name = name
            item.icon = icon or name[0].upper()
            
            if isinstance(item, Shortcut):
                item.path = path
                item.args = args
            
            # Update in parent if name changed
            if name != old_name:
                folder = self._get_current_folder()
                if isinstance(folder, dict):
                    del folder[old_name]
                    folder[name] = item
                else:
                    del folder.items[old_name]
                    folder.items[name] = item
            
            self.save_shortcuts()
            self.render_items()
    
    def duplicate_item(self, item: BaseItem):
        """Duplicate an item."""
        folder = self._get_current_folder()
        
        # Find unique name
        base_name = item.name
        new_name = f"{base_name} copy"
        counter = 2
        
        while True:
            if isinstance(folder, dict):
                if new_name not in folder:
                    break
            else:
                if new_name not in folder.items:
                    break
            new_name = f"{base_name} copy {counter}"
            counter += 1
        
        # Create duplicate
        if isinstance(item, Folder):
            new_item = Folder(name=new_name, icon=item.icon)
        else:
            new_item = Shortcut(name=new_name, icon=item.icon,
                               path=item.path, args=item.args)
        
        # Add to folder
        if isinstance(folder, dict):
            folder[new_name] = new_item
        else:
            folder.items[new_name] = new_item
        
        self.save_shortcuts()
        self.render_items()
        
        # Offer to edit
        if messagebox.askyesno("Edit Duplicate", 
                             f"Edit '{new_name}' now?"):
            self.edit_item(new_item)
    
    def duplicate_selected(self):
        """Duplicate the selected item."""
        if self.selected_item:
            item, path = self.selected_item
            self.duplicate_item(item)
    
    def delete_item(self, item: BaseItem):
        """Delete an item."""
        if messagebox.askyesno("Delete Item", 
                             f"Delete '{item.name}'?"):
            folder = self._get_current_folder()
            
            if isinstance(folder, dict):
                del folder[item.name]
            else:
                del folder.items[item.name]
            
            self.save_shortcuts()
            self.render_items()
    
    def show_properties(self, item: BaseItem):
        """Show item properties."""
        info = f"Name: {item.name}\n"
        info += f"Type: {item.__class__.__name__}\n"
        info += f"Icon: {item.icon}\n"
        
        if isinstance(item, Shortcut):
            info += f"Path: {item.path}\n"
            info += f"Args: {item.args}"
        else:
            info += f"Items: {len(item.items)}"
        
        messagebox.showinfo("Properties", info)
    
    def show_info(self):
        """Show about dialog."""
        info = f"""{config_manager.get_app_name()} v{VERSION}

A lightweight launcher for X11 systems
Designed for low-spec machines and SSH sessions

Shortcuts:
- Left/Right: Navigate items
- Ctrl+Q: Quit
- Ctrl+I: Show info
- Ctrl+S: Substitute paths
- Ctrl+N: Add new item
- Ctrl+H: Go home
- Ctrl+F: Search
- Ctrl+D: Duplicate selected
- Ctrl+E: Edit selected
- Ctrl+R: Refresh
- Ctrl+P: Show properties
- Enter: Launch selected
- Escape: Go up/close search
- Backspace: Go up one level

Right-click items for more options
Icons: Single char or .bmp in ~/.config/launcher/icons/
For more information visit: 
https://github.com/Bladetrain3r/Magic-Launcher"""
        
        messagebox.showinfo("About", info)
    
    def quit_app(self):
        """Quit the application."""
        if messagebox.askyesno("Exit", "Exit launcher?"):
            logger.info("Application shutting down")
            self.root.quit()
    
    def _handle_escape(self, event):
        """Handle escape key."""
        if self.search_active:
            self.toggle_search()
        elif self.current_path:
            self.go_up()
    
    def _handle_enter(self, event):
        """Handle enter key."""
        if self.selected_item:
            item, path = self.selected_item
            self.on_item_double_click(item, path)

    def navigate_left(self, event=None):
        """Move selection to previous item in current level"""
        self._navigate(-1)

    def navigate_right(self, event=None):
        """Move selection to next item in current level"""
        self._navigate(1)

    def _navigate(self, direction):
        """Navigate items by direction (-1 for left, 1 for right)"""
        items = self._get_items_to_show()
        if not items:
            return
        
        # If nothing selected, pick first or last based on direction
        if not self.selected_item:
            index = -1 if direction < 0 else 0
            name, item, path = items[index]
            self.selected_item = (item, path)
            self._highlight_selected()
            return
        
        # Find current index more efficiently
        current_item, _ = self.selected_item  # THIS LINE NEEDS TO BE INDENTED HERE
        try:
            current_index = next(i for i, (_, item, _) in enumerate(items) 
                               if item == current_item)
            # Move to next item with wraparound
            new_index = (current_index + direction) % len(items)
            name, item, path = items[new_index]
            self.selected_item = (item, path)
            self._highlight_selected()
        except StopIteration:
            # Current item not found, select first
            name, item, path = items[0]
            self.selected_item = (item, path)
            self._highlight_selected()

    def _highlight_selected(self):
        """Update visual highlight for selected item"""
        # Clear all highlights first
        for widget in self.item_frame.winfo_children():
            if isinstance(widget, IconWidget):
                widget.set_highlighted(False)
        
        # Highlight the selected one
        if self.selected_item:
            current_item, _ = self.selected_item
            for widget in self.item_frame.winfo_children():
                if isinstance(widget, IconWidget) and widget.item == current_item:
                    widget.set_highlighted(True)
                    break

    def _on_frame_configure(self, event):
        """Configure canvas scroll region."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _on_canvas_configure(self, event):
        """Configure canvas window width."""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)
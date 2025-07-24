#!/usr/bin/env python3
"""
Magic Desktop Clone v2.0 - A lightweight launcher for X11
New features: File browser, duplicate shortcuts
"""

import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import json
import os
import subprocess
import platform
from pathlib import Path
import shutil

# Try to import PIL for BMP support
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Note: Install Pillow for BMP icon support (pip install Pillow)")

# 16 color CGA/EGA palette
COLORS = {
    'black': '#000000',
    'blue': '#0000AA',
    'green': '#00AA00',
    'cyan': '#00AAAA',
    'red': '#AA0000',
    'magenta': '#AA00AA',
    'brown': '#AA5500',
    'light_gray': '#AAAAAA',
    'dark_gray': '#555555',
    'light_blue': '#5555FF',
    'light_green': '#55FF55',
    'light_cyan': '#55FFFF',
    'light_red': '#FF5555',
    'light_magenta': '#FF55FF',
    'yellow': '#FFFF55',
    'white': '#FFFFFF'
}

class LauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Magic Launcher v2.0")
        self.root.configure(bg=COLORS['dark_gray'])
        
        # Fixed 720p resolution
        self.root.geometry("1280x720")
        self.root.resizable(False, False)
        
        # State
        self.current_path = []
        self.search_active = False
        self.search_query = ""
        self.selected_item = None
        self.dialog_open = False  # Prevent multiple dialogs
        
        # Icon cache for BMPs
        self.icon_cache = {}
        
        # Load or create config
        self.config_path = Path.home() / '.config' / 'launcher' / 'shortcuts.json'
        self.icon_dir = Path.home() / '.config' / 'launcher' / 'icons'
        self.icon_dir.mkdir(parents=True, exist_ok=True)
        self.load_config()
        
        # Build UI
        self.setup_ui()
        self.render_items()
        
        # Keyboard bindings
        self.root.bind('<Control-f>', lambda e: self.toggle_search())
        self.root.bind('<Control-d>', lambda e: self.duplicate_selected())
        self.root.bind('<Escape>', self.handle_escape)
        self.root.bind('<Return>', self.handle_enter)
        self.root.bind('<BackSpace>', lambda e: self.go_up() if self.current_path else None)
        
    def setup_ui(self):
        # Title bar frame
        title_frame = tk.Frame(self.root, bg=COLORS['light_gray'], height=40, relief='raised', bd=2)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)
        
        # Title bar buttons
        self.make_button(title_frame, "STOP", COLORS['red'], self.quit_app).pack(side='left', padx=2)
        self.make_button(title_frame, "i", COLORS['blue'], self.show_info).pack(side='left', padx=2)
        
        # Title
        title_label = tk.Label(title_frame, text="LAUNCHER v2.0", 
                              bg=COLORS['green'], fg=COLORS['white'],
                              font=('Courier', 16, 'bold'))
        title_label.pack(side='left', expand=True, fill='both', padx=2)
        
        # Right side buttons
        self.make_button(title_frame, "FIND", COLORS['light_gray'], self.toggle_search).pack(side='right', padx=2)
        self.make_button(title_frame, "+", COLORS['light_gray'], self.add_item).pack(side='right', padx=2)
        
        # Path/search frame
        info_frame = tk.Frame(self.root, bg=COLORS['dark_gray'], height=30)
        info_frame.pack(fill='x')
        
        # Breadcrumb
        self.breadcrumb = tk.Label(info_frame, text="HOME", 
                                  bg=COLORS['black'], fg=COLORS['light_cyan'],
                                  font=('Courier', 10), anchor='w', padx=5)
        self.breadcrumb.pack(side='left', padx=20, pady=5)
        
        # Search box (hidden by default)
        self.search_frame = tk.Frame(info_frame, bg=COLORS['black'], 
                                    highlightthickness=2, highlightbackground=COLORS['white'])
        self.search_entry = tk.Entry(self.search_frame, bg=COLORS['black'], 
                                    fg=COLORS['light_green'], insertbackground=COLORS['light_green'],
                                    font=('Courier', 10), bd=0)
        self.search_entry.pack(padx=5, pady=5)
        self.search_entry.bind('<KeyRelease>', self.on_search_change)
        
        # Main area with canvas for scrolling
        self.canvas = tk.Canvas(self.root, bg=COLORS['dark_gray'], highlightthickness=0)
        self.canvas.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Scrollbar
        scrollbar = tk.Scrollbar(self.root, orient='vertical', command=self.canvas.yview)
        scrollbar.pack(side='right', fill='y', padx=(0, 20))
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame inside canvas for items
        self.item_frame = tk.Frame(self.canvas, bg=COLORS['dark_gray'])
        self.canvas_window = self.canvas.create_window((0, 0), window=self.item_frame, anchor='nw')
        
        # Configure canvas scrolling
        self.item_frame.bind('<Configure>', self.on_frame_configure)
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        
    def make_button(self, parent, text, bg, command):
        btn = tk.Button(parent, text=text, bg=bg, fg=COLORS['white'],
                       font=('Courier', 10, 'bold'), bd=2, relief='raised',
                       activebackground=bg, command=command, cursor='hand2',
                       highlightthickness=0, padx=10)
        return btn
        
    def load_config(self):
        default_config = {
            'Games': {
                'type': 'folder',
                'icon': 'G',
                'items': {
                    'Action': {
                        'type': 'folder',
                        'icon': 'A',
                        'items': {}
                    },
                    'Puzzle': {
                        'type': 'folder',
                        'icon': 'P',
                        'items': {}
                    }
                }
            },
            'Tools': {
                'type': 'folder',
                'icon': 'T',
                'items': {
                    'Terminal': {'type': 'shortcut', 'icon': '>', 'path': 'xterm'},
                    'Editor': {'type': 'shortcut', 'icon': 'E', 'path': 'nano'}
                }
            },
            'Scripts': {
                'type': 'folder',
                'icon': 'S',
                'items': {}
            }
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    self.items = json.load(f)
            except:
                self.items = default_config
        else:
            self.items = default_config
            self.save_config()
    
    def save_config(self):
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.items, f, indent=2)
    
    def get_current_folder(self):
        folder = self.items
        for name in self.current_path:
            folder = folder[name]['items']
        return folder
    
    def search_items_recursive(self, folder, query, path=[]):
        """Recursively search all folders for matching items"""
        results = []
        
        for name, item in folder.items():
            # Check if current item matches
            if query.lower() in name.lower():
                results.append((name, item, path.copy()))
            
            # If it's a folder, search inside it
            if item['type'] == 'folder' and 'items' in item:
                subfolder_results = self.search_items_recursive(
                    item['items'], query, path + [name]
                )
                results.extend(subfolder_results)
        
        return results
    
    def render_items(self):
        # Clear existing items
        for widget in self.item_frame.winfo_children():
            widget.destroy()
        
        items_to_show = []
        
        if self.search_active and self.search_query:
            # Recursive search from root
            search_results = self.search_items_recursive(self.items, self.search_query)
            for name, item, path in search_results:
                # Add path info to name for context
                display_name = name
                if path:
                    display_name = f"{name} ({' > '.join(path)})"
                items_to_show.append((display_name, item, path))
        else:
            # Normal folder view
            folder = self.get_current_folder()
            
            # Add back button if not at root
            if self.current_path:
                items_to_show.append(('..', {'type': 'up', 'icon': '^'}, []))
            
            # Add items in current folder
            for name, item in folder.items():
                items_to_show.append((name, item, self.current_path.copy()))
        
        # Create icon grid
        columns = 8  # Fixed columns for 1280px width
        row = 0
        col = 0
        
        for item_data in items_to_show:
            if len(item_data) == 3:
                name, item, path = item_data
                icon_frame = self.create_icon(self.item_frame, name, item, path)
            else:
                # Backwards compatibility
                name, item = item_data
                icon_frame = self.create_icon(self.item_frame, name, item, self.current_path)
                
            icon_frame.grid(row=row, column=col, padx=10, pady=10, sticky='n')
            
            col += 1
            if col >= columns:
                col = 0
                row += 1
        
        # Update breadcrumb
        if self.current_path:
            self.breadcrumb.config(text="HOME > " + " > ".join(self.current_path))
        else:
            self.breadcrumb.config(text="HOME")
    
    def load_icon(self, icon_spec):
        """Load icon - either character or BMP file"""
        if not icon_spec or not PIL_AVAILABLE:
            return None
            
        # Check if it's a BMP file reference
        if icon_spec.endswith('.bmp'):
            icon_path = self.icon_dir / icon_spec
            if icon_path.exists():
                # Check cache first
                if icon_spec in self.icon_cache:
                    return self.icon_cache[icon_spec]
                
                try:
                    # Load and scale BMP to 64x64 (leaving border space)
                    img = Image.open(icon_path)
                    img = img.resize((64, 64), Image.NEAREST)  # NEAREST for pixel art
                    photo = ImageTk.PhotoImage(img)
                    self.icon_cache[icon_spec] = photo
                    return photo
                except Exception as e:
                    print(f"Error loading icon {icon_spec}: {e}")
                    return None
        
        # Otherwise it's a character
        return None
    
    def create_icon(self, parent, name, item, path=None):
        frame = tk.Frame(parent, bg=COLORS['dark_gray'], width=120, height=140)
        frame.pack_propagate(False)
        
        # Store the path for this icon
        if path is None:
            path = self.current_path.copy()
        
        # Icon box
        icon_color = COLORS['yellow'] if item['type'] == 'folder' else COLORS['light_gray']
        icon_box = tk.Frame(frame, bg=icon_color, width=80, height=80, 
                           relief='raised', bd=3, highlightthickness=0)
        icon_box.pack(pady=(10, 5))
        icon_box.pack_propagate(False)
        
        # Try to load icon
        icon_spec = item.get('icon', name[0].upper())
        icon_image = self.load_icon(icon_spec)
        
        if icon_image:
            # Use image icon
            icon_label = tk.Label(icon_box, image=icon_image, bg=icon_color, bd=0)
            icon_label.image = icon_image  # Keep reference
        else:
            # Use text icon
            icon_text = icon_spec if len(icon_spec) <= 2 else name[0].upper()
            icon_label = tk.Label(icon_box, text=icon_text, bg=icon_color,
                                 font=('Courier', 36, 'bold'))
        
        icon_label.place(relx=0.5, rely=0.5, anchor='center')
        
        # Extract display name (remove path suffix for display)
        display_name = name.split(' (')[0] if ' (' in name else name
        
        # Name label
        name_bg = COLORS['blue']
        name_label = tk.Label(frame, text=display_name, bg=name_bg, fg=COLORS['white'],
                             font=('Courier', 10), width=12, anchor='center')
        name_label.pack()
        
        # Bindings - Fixed to prevent event conflicts
        def bind_all(widget, name, item, path):
            widget.bind('<ButtonPress-1>', lambda e: (self.on_click(name, item), icon_box.config(relief='sunken')))
            widget.bind('<ButtonRelease-1>', lambda e: icon_box.config(relief='raised'))
            widget.bind('<Double-Button-1>', lambda e: self.on_double_click(name, item, path))
            widget.bind('<Button-3>', lambda e: self.on_right_click(e, name, item))
            widget.bind('<Enter>', lambda e: icon_box.config(relief='sunken'))
            widget.bind('<Leave>', lambda e: icon_box.config(relief='raised'))
        
        for widget in [frame, icon_box, icon_label, name_label]:
            bind_all(widget, display_name, item, path)
        
        return frame
    
    def on_click(self, name, item):
        self.selected_item = (name, item)
    
    def on_double_click(self, name, item, path=None):
        if item.get('type') == 'folder':
            # If we're in search mode and clicking a folder, navigate to it
            if self.search_active and path is not None:
                self.search_active = False
                self.search_frame.pack_forget()
                self.search_query = ""
                self.current_path = path + [name]
            else:
                self.current_path.append(name)
            self.render_items()
        elif item.get('type') == 'up':
            self.go_up()
        elif item.get('type') == 'shortcut':
            self.launch_item(name, item)
    
    def on_right_click(self, event, name, item):
        if item.get('type') == 'up':
            return
            
        menu = tk.Menu(self.root, tearoff=0, bg=COLORS['light_gray'],
                      fg=COLORS['black'], activebackground=COLORS['blue'],
                      activeforeground=COLORS['white'])
        menu.add_command(label="Edit", command=lambda: self.edit_item(name, item))
        menu.add_command(label="Duplicate", command=lambda: self.duplicate_item(name, item))
        menu.add_command(label="Delete", command=lambda: self.delete_item(name))
        menu.add_separator()
        menu.add_command(label="Properties", command=lambda: self.show_properties(name, item))
        
        menu.post(event.x_root, event.y_root)
    
    def launch_item(self, name, item):
        path = item.get('path', '')
        args = item.get('args', '')
        
        if not path:
            messagebox.showwarning("No Path", f"No path defined for {name}")
            return
        
        try:
            # Build command
            if args:
                cmd = f"{path} {args}"
            else:
                cmd = path
            
            # Handle different path types
            if path.startswith('http://') or path.startswith('https://'):
                # Web URL
                if platform.system() == 'Darwin':
                    subprocess.Popen(['open', path])
                elif platform.system() == 'Windows':
                    subprocess.Popen(['start', path], shell=True)
                else:
                    subprocess.Popen(['xdg-open', path])
            elif path.endswith(('.txt', '.md', '.log', '.conf', '.cfg')):
                # Text files - use default editor
                if platform.system() == 'Windows':
                    subprocess.Popen(['notepad', path])
                else:
                    subprocess.Popen(['xdg-open', path])
            else:
                # Execute as command with args
                subprocess.Popen(cmd, shell=True)
        except Exception as e:
            messagebox.showerror("Launch Error", f"Could not launch {name}:\n{str(e)}")
    
    def go_up(self):
        if self.current_path:
            self.current_path.pop()
            self.render_items()
    
    def toggle_search(self):
        self.search_active = not self.search_active
        if self.search_active:
            self.search_frame.pack(side='right', padx=20, pady=5)
            self.search_entry.focus()
            self.search_entry.delete(0, 'end')
        else:
            self.search_frame.pack_forget()
            self.search_query = ""
            self.render_items()
    
    def on_search_change(self, event):
        self.search_query = self.search_entry.get()
        self.render_items()
    
    def handle_escape(self, event):
        if self.search_active:
            self.toggle_search()
        elif self.current_path:
            self.go_up()
    
    def handle_enter(self, event):
        if self.selected_item:
            name, item = self.selected_item
            self.on_double_click(name, item)
    
    def add_item(self):
        if self.dialog_open:
            return
        self.dialog_open = True
        
        dialog = ItemDialog(self.root, "New Item")
        self.root.wait_window(dialog.top)
        self.dialog_open = False
        
        if dialog.result:
            name, item_type, path, icon, args = dialog.result
            folder = self.get_current_folder()
            
            if item_type == 'folder':
                folder[name] = {
                    'type': 'folder',
                    'icon': icon or name[0].upper(),
                    'items': {}
                }
            else:
                folder[name] = {
                    'type': 'shortcut',
                    'icon': icon or name[0].upper(),
                    'path': path,
                    'args': args
                }
            
            self.save_config()
            self.render_items()
    
    def edit_item(self, name, item):
        if self.dialog_open:
            return
        self.dialog_open = True
        
        dialog = ItemDialog(self.root, "Edit Item", name, item)
        self.root.wait_window(dialog.top)
        self.dialog_open = False
        
        if dialog.result:
            new_name, item_type, path, icon, args = dialog.result
            folder = self.get_current_folder()
            
            # Remove old item if name changed
            if new_name != name:
                del folder[name]
            
            # Update item
            if item_type == 'folder':
                folder[new_name] = {
                    'type': 'folder',
                    'icon': icon or new_name[0].upper(),
                    'items': item.get('items', {})
                }
            else:
                folder[new_name] = {
                    'type': 'shortcut',
                    'icon': icon or new_name[0].upper(),
                    'path': path,
                    'args': args
                }
            
            self.save_config()
            self.render_items()
    
    def duplicate_item(self, name, item):
        # Find unique name
        folder = self.get_current_folder()
        new_name = name + " copy"
        counter = 2
        while new_name in folder:
            new_name = f"{name} copy {counter}"
            counter += 1
        
        # Deep copy the item
        if item['type'] == 'folder':
            folder[new_name] = {
                'type': 'folder',
                'icon': item.get('icon', ''),
                'items': {}  # Don't duplicate contents for folders
            }
        else:
            folder[new_name] = {
                'type': 'shortcut',
                'icon': item.get('icon', ''),
                'path': item.get('path', ''),
                'args': item.get('args', '')
            }
        
        self.save_config()
        self.render_items()
        
        # Optionally open edit dialog for the new item
        if messagebox.askyesno("Edit Duplicate", f"Edit '{new_name}' now?"):
            self.edit_item(new_name, folder[new_name])
    
    def duplicate_selected(self):
        if self.selected_item:
            name, item = self.selected_item
            self.duplicate_item(name, item)
    
    def delete_item(self, name):
        if messagebox.askyesno("Delete Item", f"Delete '{name}'?"):
            folder = self.get_current_folder()
            del folder[name]
            self.save_config()
            self.render_items()
    
    def show_properties(self, name, item):
        info = f"Name: {name}\n"
        info += f"Type: {item['type']}\n"
        info += f"Icon: {item.get('icon', 'default')}\n"
        if item['type'] == 'shortcut':
            info += f"Path: {item.get('path', 'none')}\n"
            info += f"Args: {item.get('args', 'none')}"
        else:
            info += f"Items: {len(item.get('items', {}))}"
        
        messagebox.showinfo("Properties", info)
    
    def show_info(self):
        info = """Magic Launcher v2.0
        
A lightweight launcher for X11 systems
Designed for low-spec machines and SSH sessions

Shortcuts:
- Ctrl+F: Search
- Ctrl+D: Duplicate selected
- Enter: Launch selected
- Escape: Go up/close search
- Backspace: Go up one level

Right-click items for more options
Icons: Single char or .bmp in ~/.config/launcher/icons/"""
        messagebox.showinfo("About", info)
    
    def quit_app(self):
        if messagebox.askyesno("Exit", "Exit launcher?"):
            self.root.quit()
    
    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_canvas_configure(self, event):
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)


class ItemDialog:
    def __init__(self, parent, title, name="", item=None):
        self.result = None
        
        self.top = tk.Toplevel(parent)
        self.top.title(title)
        self.top.geometry("500x350")
        self.top.resizable(False, False)
        self.top.configure(bg=COLORS['light_gray'])
        
        # Name
        tk.Label(self.top, text="Name:", bg=COLORS['light_gray']).grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.name_entry = tk.Entry(self.top, width=30)
        self.name_entry.grid(row=0, column=1, padx=10, pady=5, columnspan=2, sticky='ew')
        self.name_entry.insert(0, name)
        
        # Type
        tk.Label(self.top, text="Type:", bg=COLORS['light_gray']).grid(row=1, column=0, sticky='w', padx=10, pady=5)
        self.type_var = tk.StringVar(value=item['type'] if item else 'shortcut')
        type_menu = tk.OptionMenu(self.top, self.type_var, 'shortcut', 'folder')
        type_menu.grid(row=1, column=1, sticky='w', padx=10, pady=5)
        
        # Path with browse button
        tk.Label(self.top, text="Path/URL:", bg=COLORS['light_gray']).grid(row=2, column=0, sticky='w', padx=10, pady=5)
        path_frame = tk.Frame(self.top, bg=COLORS['light_gray'])
        path_frame.grid(row=2, column=1, padx=10, pady=5, columnspan=2, sticky='ew')
        
        self.path_entry = tk.Entry(path_frame, width=25)
        self.path_entry.pack(side='left', fill='x', expand=True)
        if item and item['type'] == 'shortcut':
            self.path_entry.insert(0, item.get('path', ''))
        
        self.browse_btn = tk.Button(path_frame, text="Browse...", command=self.browse_file,
                                   bg=COLORS['light_gray'], fg=COLORS['black'],
                                   font=('Courier', 9), bd=2, relief='raised')
        self.browse_btn.pack(side='right', padx=(5, 0))
        
        # Arguments (for shortcuts only)
        tk.Label(self.top, text="Arguments:", bg=COLORS['light_gray']).grid(row=3, column=0, sticky='w', padx=10, pady=5)
        self.args_entry = tk.Entry(self.top, width=30)
        self.args_entry.grid(row=3, column=1, padx=10, pady=5, columnspan=2, sticky='ew')
        if item and item['type'] == 'shortcut':
            self.args_entry.insert(0, item.get('args', ''))
        
        # Icon with browse button
        tk.Label(self.top, text="Icon:", bg=COLORS['light_gray']).grid(row=4, column=0, sticky='w', padx=10, pady=5)
        icon_frame = tk.Frame(self.top, bg=COLORS['light_gray'])
        icon_frame.grid(row=4, column=1, sticky='ew', padx=10, pady=5, columnspan=2)
        
        self.icon_entry = tk.Entry(icon_frame, width=15)
        self.icon_entry.pack(side='left')
        if item:
            self.icon_entry.insert(0, item.get('icon', ''))
        
        tk.Label(icon_frame, text="(1 char or .bmp)", bg=COLORS['light_gray'], 
                font=('Courier', 8)).pack(side='left', padx=5)
        
        self.icon_browse_btn = tk.Button(icon_frame, text="Browse...", command=self.browse_icon,
                                        bg=COLORS['light_gray'], fg=COLORS['black'],
                                        font=('Courier', 9), bd=2, relief='raised')
        self.icon_browse_btn.pack(side='right')
        
        # Buttons
        button_frame = tk.Frame(self.top, bg=COLORS['light_gray'])
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        tk.Button(button_frame, text="Save", command=self.save,
                 bg=COLORS['light_gray'], fg=COLORS['black'],
                 font=('Courier', 10), bd=2, relief='raised').pack(side='left', padx=5)
        tk.Button(button_frame, text="Cancel", command=self.cancel,
                 bg=COLORS['light_gray'], fg=COLORS['black'],
                 font=('Courier', 10), bd=2, relief='raised').pack(side='left', padx=5)
        
        # Update UI based on type
        self.type_var.trace('w', self.on_type_change)
        self.on_type_change()
        
        self.name_entry.focus()
        
        # Configure grid weights
        self.top.columnconfigure(1, weight=1)
    
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select executable or script",
            initialdir=os.path.expanduser("~"),
            filetypes=[
                ("All files", "*.*"),
                ("Executables", "*.exe *.sh *.py *.bat"),
                ("Scripts", "*.sh *.py *.pl *.rb"),
            ]
        )
        if filename:
            self.path_entry.delete(0, 'end')
            self.path_entry.insert(0, filename)
    
    def browse_icon(self):
        # Get the icon directory
        icon_dir = Path.home() / '.config' / 'launcher' / 'icons'
        
        filename = filedialog.askopenfilename(
            title="Select BMP icon",
            initialdir=str(icon_dir) if icon_dir.exists() else os.path.expanduser("~"),
            filetypes=[
                ("BMP files", "*.bmp"),
                ("All files", "*.*")
            ]
        )
        
        if filename:
            # If it's in the icon directory, just use the filename
            if Path(filename).parent == icon_dir:
                self.icon_entry.delete(0, 'end')
                self.icon_entry.insert(0, Path(filename).name)
            else:
                # Otherwise, copy it to the icon directory
                if messagebox.askyesno("Copy Icon", 
                                     f"Copy icon to launcher icons folder?\n\n{filename}"):
                    try:
                        dest = icon_dir / Path(filename).name
                        shutil.copy2(filename, dest)
                        self.icon_entry.delete(0, 'end')
                        self.icon_entry.insert(0, Path(filename).name)
                    except Exception as e:
                        messagebox.showerror("Error", f"Could not copy icon: {e}")
    
    def on_type_change(self, *args):
        if self.type_var.get() == 'folder':
            self.path_entry.config(state='disabled')
            self.args_entry.config(state='disabled')
            self.browse_btn.config(state='disabled')
        else:
            self.path_entry.config(state='normal')
            self.args_entry.config(state='normal')
            self.browse_btn.config(state='normal')
    
    def save(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Invalid Name", "Please enter a name")
            return
        
        self.result = (
            name,
            self.type_var.get(),
            self.path_entry.get().strip(),
            self.icon_entry.get().strip(),
            self.args_entry.get().strip() if self.type_var.get() == 'shortcut' else ''
        )
        self.top.destroy()
    
    def cancel(self):
        self.top.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = LauncherApp(root)
    root.mainloop()
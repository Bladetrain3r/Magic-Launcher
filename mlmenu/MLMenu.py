#!/usr/bin/env python3
"""
MLMENU - Magic Launcher for text terminals
When even Tkinter is too heavy
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# Cross-platform key input
try:
    import msvcrt  # Windows
    def get_key():
        return msvcrt.getch().decode('utf-8', errors='ignore').lower()
except ImportError:
    import termios, tty  # Unix/Linux
    def get_key():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            key = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return key.lower()

# Colors for terminals that support them
class Colors:
    # Use simple ANSI codes that work on most terminals
    BLUE = '\033[44m' if os.name != 'nt' else ''
    WHITE = '\033[97m' if os.name != 'nt' else ''
    YELLOW = '\033[93m' if os.name != 'nt' else ''
    RESET = '\033[0m' if os.name != 'nt' else ''
    
    @staticmethod
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')

class MLMenu:
    def __init__(self):
        self.config_file = Path.home() / '.config' / 'launcher' / 'shortcuts.json'
        self.shortcuts = {}
        self.current_path = []
        self.page = 0  # Current page
        self.load_shortcuts()
        
    def load_shortcuts(self):
        """Load shortcuts from Magic Launcher config"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Convert to expected format
                    self.shortcuts = self._convert_shortcuts(data)
            except Exception as e:
                print(f"Error loading config: {e}")
                self.shortcuts = self._get_demo_shortcuts()
        else:
            self.shortcuts = self._get_demo_shortcuts()
    
    def _convert_shortcuts(self, data):
        """Convert ML shortcuts to menu format"""
        result = {}
        for name, item in data.items():
            if item.get('type') == 'folder' and 'items' in item:
                result[name] = {
                    "type": "folder",
                    "items": self._convert_shortcuts(item['items'])
                }
            else:
                result[name] = item
        return result
    
    def _get_demo_shortcuts(self):
        """Demo shortcuts when no config available"""
        return {
            "System": {
                "type": "folder",
                "items": {
                    "Terminal": {
                        "type": "shortcut", 
                        "path": "cmd" if os.name == 'nt' else os.environ.get('SHELL', '/bin/bash')
                    },
                    "Directory": {"type": "shortcut", "path": "dir" if os.name == 'nt' else "ls"},
                    "Python": {"type": "shortcut", "path": "python", "args": "--version"}
                }
            },
            "Magic Launcher": {
                "type": "shortcut",
                "path": "python",
                "args": "~/.local/share/Magic-Launcher/launcher/app.py"
            },
            "Quit": {"type": "shortcut", "path": "exit"}
        }
    
    def get_current_items(self):
        """Get items in current folder"""
        current = self.shortcuts
        for folder in self.current_path:
            current = current[folder]["items"]
        return current
    
    def navigate_to(self, index):
        """Navigate to item by index (0-based)"""
        items = self.get_current_items()
        item_list = list(items.items())
        
        if 0 <= index < len(item_list):
            name, item = item_list[index]
            
            if item.get("type") == "folder":
                self.current_path.append(name)
                self.page = 0
                return True
            else:
                # Launch item (no interactive wait in command mode)
                return self.launch_item(item, wait=False)
        return False
    
    def draw_menu(self):
        """Draw the menu"""
        Colors.clear()
        
        # Header
        print(f"{Colors.BLUE}{Colors.WHITE}")
        print("╔══════════════════════════════════════╗")
        print("║          ML-MENU v1.0                ║")
        print("╠══════════════════════════════════════╣")
        
        # Current path
        if self.current_path:
            path_str = " > ".join(self.current_path)
            if len(path_str) > 36:
                path_str = "..." + path_str[-33:]
            print(f"║ {path_str:<36} ║")
            print("╠══════════════════════════════════════╣")
        
        # Menu items
        items = self.get_current_items()
        total_items = len(items)
        total_pages = (total_items + 8) // 9  # 9 items per page
        
        # Get current page items
        start_idx = self.page * 9
        end_idx = start_idx + 9
        item_list = list(items.items())[start_idx:end_idx]
        
        for i, (name, item) in enumerate(item_list):
            display_name = name[:30]  # Truncate long names
            if item.get("type") == "folder":
                display_name = f"[{display_name}]"
            print(f"║ {Colors.YELLOW}[{i+1}]{Colors.WHITE} {display_name:<32} ║")
        
        # Fill empty slots
        for i in range(len(item_list), 9):
            print(f"║ {' '*36} ║")
        
        # Footer with page info
        print("╠══════════════════════════════════════╣")
        if total_pages > 1:
            page_info = f"Page {self.page + 1}/{total_pages}"
            print(f"║ [Q]uit [B]ack [H]ome {page_info:>14}  ║")
            print("║ [<,>] Page  [R]efresh                ║")
        else:
            print("║ [Q]uit  [B]ack  [H]ome  [R]efresh    ║")
        print(f"╚══════════════════════════════════════╝{Colors.RESET}")
        print("\nSelect option: ", end='', flush=True)
    
    def launch_item(self, item, wait=True):
        """Launch a shortcut"""
        if wait:
            Colors.clear()
        
        print(f"Launching {item.get('path', 'unknown')}...")
        
        try:
            path = item.get('path', '')
            args = item.get('args', '')
            
            # Expand home directory
            path = os.path.expanduser(path)
            
            # Build command
            if args:
                if os.name == 'nt':
                    # Windows - use shell=True for simplicity
                    cmd = f'"{path}" {args}'
                    subprocess.run(cmd, shell=True)
                else:
                    # Unix - parse args properly
                    import shlex
                    cmd = [path] + shlex.split(args)
                    subprocess.run(cmd)
            else:
                subprocess.run([path])
            
            if wait:
                print("\nPress any key to continue...")
                get_key()
            
            return True
                
        except FileNotFoundError:
            print(f"Error: Command '{path}' not found")
            if wait:
                print("\nPress any key to continue...")
                get_key()
            return False
        except Exception as e:
            print(f"Error launching: {e}")
            if wait:
                print("\nPress any key to continue...")
                get_key()
            return False
    
    def run_commands(self, commands):
        """Run a sequence of commands"""
        for cmd in commands.split():
            if cmd.isdigit():
                idx = int(cmd) - 1  # Convert to 0-based
                print(f"Executing: {cmd}")
                if not self.navigate_to(idx):
                    print(f"Failed at command: {cmd}")
                    return False
            else:
                print(f"Skipping non-numeric: {cmd}")
        
        print("Command sequence complete")
        return True
    
    def run(self):
        """Main menu loop"""
        while True:
            self.draw_menu()
            key = get_key()
            
            if key == 'q':
                Colors.clear()
                print("Thanks for using ML-MENU!")
                break
            elif key == 'b' and self.current_path:
                self.current_path.pop()
                self.page = 0  # Reset to first page
            elif key == 'h':
                self.current_path = []
                self.page = 0  # Reset to first page
            elif key == 'r':
                self.load_shortcuts()
            elif key == '.' or key == '>':  # Next page
                items = self.get_current_items()
                total_pages = (len(items) + 8) // 9
                if self.page < total_pages - 1:
                    self.page += 1
            elif key == ',' or key == '<':  # Previous page
                if self.page > 0:
                    self.page -= 1
            elif key.isdigit() and '1' <= key <= '9':
                items = self.get_current_items()
                start_idx = self.page * 9
                item_list = list(items.items())[start_idx:start_idx + 9]
                index = int(key) - 1
                
                if index < len(item_list):
                    name, item = item_list[index]
                    
                    if item.get("type") == "folder":
                        self.current_path.append(name)
                        self.page = 0  # Reset page when entering folder
                    else:
                        self.launch_item(item)

def main():
    """Entry point"""
    # Parse args first
    if len(sys.argv) > 1:
        if sys.argv[1] == '-c' and len(sys.argv) > 2:
            menu = MLMenu()
            menu.run_commands(sys.argv[2])
            return
        elif sys.argv[1] in ['-h', '--help']:
            print("MLMenu - Terminal launcher")
            print("Usage: mlmenu [-c 'commands']")
            print("  -c '1 2 3'  Execute commands in sequence")
            print("  -h          Show this help")
            return
    
    # Normal interactive mode
    try:
        menu = MLMenu()
        menu.run()
    except KeyboardInterrupt:
        print("\n\nInterrupted!")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Reset terminal colors
        print(Colors.RESET)

if __name__ == "__main__":
    main()
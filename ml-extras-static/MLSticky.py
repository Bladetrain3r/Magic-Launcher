#!/usr/bin/env python3
"""
MLNote - Dead simple append-only notes for servers
Because sometimes you just need to write "don't delete this" somewhere
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import argparse
import re

# Platform-specific imports
try:
    import pwd
    HAS_PWD = True
except ImportError:
    HAS_PWD = False  # Windows doesn't have pwd

# Note locations
USER_NOTE = Path.home() / '.mlnotes' / 'user.txt'
SYSTEM_NOTE = Path('/var/log/mlnotes/system.txt')

def ensure_files():
    """Create note files if they don't exist"""
    # User notes - always available
    USER_NOTE.parent.mkdir(parents=True, exist_ok=True)
    if not USER_NOTE.exists():
        USER_NOTE.touch()
    
    # System notes - create if root (Unix) or just create on Windows
    if sys.platform != 'win32' and os.geteuid() == 0:  # Running as root on Unix
        SYSTEM_NOTE.parent.mkdir(parents=True, exist_ok=True)
        if not SYSTEM_NOTE.exists():
            SYSTEM_NOTE.touch()
            SYSTEM_NOTE.chmod(0o644)  # Everyone can read, only root can write
    elif sys.platform == 'win32':  # Windows doesn't have the same permission model
        SYSTEM_NOTE.parent.mkdir(parents=True, exist_ok=True)
        if not SYSTEM_NOTE.exists():
            SYSTEM_NOTE.touch()

def get_username():
    """Get actual username even when sudo"""
    try:
        # Try SUDO_USER first (preserves who ran sudo)
        sudo_user = os.environ.get('SUDO_USER')
        if sudo_user:
            return sudo_user
        # Try getting from pwd module (Unix)
        if HAS_PWD:
            return pwd.getpwuid(os.getuid()).pw_name
        # Fall back to environment variables (Windows)
        return os.environ.get('USERNAME', os.environ.get('USER', 'unknown'))
    except:
        return 'unknown'

def add_note(message, system=False):
    """Add a note with timestamp"""
    if system and sys.platform != 'win32' and os.geteuid() != 0:
        print("Error: System notes require root/admin privileges")
        print("Try: sudo mlnote -s 'your message'")
        return False
    
    note_file = SYSTEM_NOTE if system else USER_NOTE
    
    # Format: [2024-12-07 14:23:45] username: message
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    username = get_username()
    formatted = f"[{timestamp}] {username}: {message}\n"
    
    try:
        with open(note_file, 'a') as f:
            f.write(formatted)
        
        note_type = "System" if system else "User"
        print(f"{note_type} note added: {message}")
        return True
    except PermissionError:
        print(f"Error: Cannot write to {note_file}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def read_notes(lines=10, system=False, all_notes=False, grep=None):
    """Read recent notes"""
    if all_notes:
        files = []
        if USER_NOTE.exists():
            files.append(('User', USER_NOTE))
        if SYSTEM_NOTE.exists() and os.access(SYSTEM_NOTE, os.R_OK):
            files.append(('System', SYSTEM_NOTE))
    else:
        note_file = SYSTEM_NOTE if system else USER_NOTE
        if not note_file.exists():
            print(f"No {'system' if system else 'user'} notes yet")
            return
        files = [('', note_file)]
    
    for label, note_file in files:
        if not note_file.exists():
            continue
            
        try:
            with open(note_file, 'r') as f:
                all_lines = f.readlines()
            
            if grep:
                # Filter lines containing pattern (case insensitive)
                pattern = re.compile(grep, re.IGNORECASE)
                all_lines = [l for l in all_lines if pattern.search(l)]
                if not all_lines:
                    if label:
                        print(f"\n=== {label} Notes ===")
                    print(f"No notes matching '{grep}'")
                    continue
            
            # Get last N lines
            if lines > 0:
                display_lines = all_lines[-lines:]
            else:
                display_lines = all_lines
            
            if label:
                print(f"\n=== {label} Notes ===")
            
            for line in display_lines:
                print(line.rstrip())
                
        except PermissionError:
            print(f"Error: Cannot read {note_file}")
        except Exception as e:
            print(f"Error reading {note_file}: {e}")

def stats():
    """Show note statistics"""
    print("=== MLNote Statistics ===")
    
    for name, path in [("User", USER_NOTE), ("System", SYSTEM_NOTE)]:
        if path.exists() and os.access(path, os.R_OK):
            try:
                with open(path, 'r') as f:
                    lines = f.readlines()
                size = path.stat().st_size
                
                # Find date range
                if lines:
                    # Extract first and last timestamps
                    first_match = re.search(r'\[(\d{4}-\d{2}-\d{2})', lines[0])
                    last_match = re.search(r'\[(\d{4}-\d{2}-\d{2})', lines[-1])
                    
                    if first_match and last_match:
                        date_range = f"{first_match.group(1)} to {last_match.group(1)}"
                    else:
                        date_range = "unknown"
                else:
                    date_range = "empty"
                
                print(f"\n{name} Notes ({path}):")
                print(f"  Lines: {len(lines)}")
                print(f"  Size: {size:,} bytes")
                print(f"  Range: {date_range}")
            except:
                print(f"\n{name} Notes: Not accessible")
        else:
            print(f"\n{name} Notes: Not found")

def main():
    parser = argparse.ArgumentParser(
        description='MLNote - Append-only notes for servers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''Examples:
  mlnote "Fixed the thing"           # Add user note
  mlnote -s "Replaced disk"          # Add system note (needs sudo)
  mlnote -r                          # Read last 10 user notes
  mlnote -r 20 -s                    # Read last 20 system notes
  mlnote -a                          # Read all notes (user + system)
  mlnote -g "disk"                   # Grep all user notes for "disk"
  mlnote --stats                     # Show statistics
        ''')
    
    parser.add_argument('message', nargs='?', help='Note to add')
    parser.add_argument('-s', '--system', action='store_true',
                      help='Work with system notes (requires root to write)')
    parser.add_argument('-r', '--read', nargs='?', const=10, type=int, metavar='N',
                      help='Read last N notes (default: 10, 0 for all)')
    parser.add_argument('-a', '--all', action='store_true',
                      help='Read both user and system notes')
    parser.add_argument('-g', '--grep', metavar='PATTERN',
                      help='Filter notes by pattern')
    parser.add_argument('--stats', action='store_true',
                      help='Show note statistics')
    
    args = parser.parse_args()
    
    # Ensure note files exist
    ensure_files()
    
    # Handle operations
    if args.stats:
        stats()
    elif args.read is not None or args.grep or args.all:
        # Reading mode
        lines = args.read if args.read is not None else (0 if args.grep else 10)
        read_notes(lines=lines, system=args.system, all_notes=args.all, grep=args.grep)
    elif args.message:
        # Writing mode
        add_note(args.message, system=args.system)
    else:
        # No arguments - show recent user notes
        read_notes(lines=10, system=False)

if __name__ == '__main__':
    main()
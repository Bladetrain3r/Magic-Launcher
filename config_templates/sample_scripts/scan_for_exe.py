#!/usr/bin/env python3
# scan_for_exes.py
import json
import sys
from pathlib import Path

def scan_folder_for_exes(folder_path, config_path=None):
    """Scan folder for .exe files and create shortcuts config."""
    folder = Path(folder_path)
    if not folder.exists():
        print(f"Error: {folder} does not exist")
        return False
    
    # Default config path
    if not config_path:
        config_path = Path.home() / '.config/launcher/shortcuts.json'
    
    # Load existing config
    try:
        with open(config_path) as f:
            config = json.load(f)
    except:
        config = {}
    
    # Create folder name from path
    folder_name = f"{folder.name} Apps"
    
    # Create new folder entry
    new_folder = {
        "type": "folder",
        "icon": folder.name[0].upper(),
        "items": {}
    }
    
    # Scan for executables
    exe_count = 0
    for exe in folder.rglob('*.exe'):
        # Skip common junk
        if any(skip in exe.name.lower() for skip in ['uninstall', 'update', 'crash']):
            continue
            
        # Create clean name
        name = exe.stem.replace('_', ' ').replace('-', ' ').title()
        
        # Add shortcut
        new_folder["items"][name] = {
            "type": "shortcut",
            "icon": name[0].upper(),
            "path": str(exe),
            "args": ""
        }
        exe_count += 1
    
    if exe_count == 0:
        print("No executables found!")
        return False
    
    # Add to config
    config[folder_name] = new_folder
    
    # Save
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Added {exe_count} shortcuts to '{folder_name}'")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: scan_for_exes.py <folder_path> [config_path]")
        sys.exit(1)
    
    folder = sys.argv[1]
    config = sys.argv[2] if len(sys.argv) > 2 else None
    
    scan_folder_for_exes(folder, config)
#!/usr/bin/env python3
"""
scan_for_doom.py - Scans folders for Doom executables and creates shortcuts config.
"""
import json
import sys
from pathlib import Path
from argparse import ArgumentParser

def parse_args():
    """Parse command line arguments."""
    parser = ArgumentParser(description="Scan folder for Doom executables and create shortcuts config.")
    parser.add_argument("folder", help="Path to the folder to scan")
    parser.add_argument("--config", default=None, help="Path to the shortcuts config file (default: ~/.config/launcher/shortcuts.json)")
    parser.add_argument("--allow-duplicates", action='store_true', help="Allow duplicate entries in the config")
    return parser.parse_args()

def scan_folder_for_exes(folder_path, config_path=None, allow_duplicates=False):
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
        with open(config_path, encoding='utf-8') as f:
            config_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        config_data = {}
    
    # Create folder name from path
    folder_name = f"{folder.name} Doom"
    
    # Create new folder entry
    new_folder = {
        "type": "folder",
        "icon": "D",
        "items": {}
    }
    
    # Scan for executables
    found_count = 0
    duplicate_num = 1

    for exe in folder.rglob('*.exe'):
        if not exe.is_file():
            continue
            
        # Check for doom-related names
        doom_related = ['doom', 'boom', 'heretic', 'hexen', 'strife']
        if not any(term in exe.name.lower() for term in doom_related):
            continue
        
        # Skip common junk
        if any(skip in exe.name.lower() for skip in ['uninstall', 'update', 'crash']):
            continue
        
        found_count += 1  # INCREMENT HERE!
        
        # Create clean name
        name = exe.stem.replace('_', ' ').replace('-', ' ').title()
        
        # Create safe key for the shortcut
        safe_key = ''.join(c if c.isalnum() or c in ' _-' else '' for c in name)
        if not safe_key.strip():
            safe_key = f"Doom_Game_{found_count}"
        
        # Handle duplicates if enabled
        if allow_duplicates and safe_key in new_folder["items"]:
            original_key = safe_key
            while safe_key in new_folder["items"]:
                safe_key = f"{original_key}_{duplicate_num}"
                duplicate_num += 1
        
        # Add shortcut
        new_folder["items"][safe_key] = {
            "type": "shortcut",
            "icon": name[0].upper() if name else "D",
            "path": str(exe),
            "args": ""
        }
    
    if found_count == 0:
        print("No Doom executables found!")
        return False
    
    # Special character handling in folder name
    safe_folder_name = ''.join(c if c.isalnum() or c in ' _-' else '_' for c in folder_name)
    safe_folder_name = safe_folder_name.replace(' ', '_').replace('__', '_').strip('_')
    
    # Add to config
    config_data[safe_folder_name] = new_folder
    
    # Save
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=2)
    
    # Count what was actually added
    actually_added = len(new_folder["items"])
    
    print(f"✓ Found {found_count} Doom executables")
    if actually_added < found_count:
        print(f"✓ Added {actually_added} unique shortcuts to '{safe_folder_name}' (skipped {found_count - actually_added} duplicates)")
    else:
        print(f"✓ Added all {actually_added} shortcuts to '{safe_folder_name}'")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: scan_for_doom.py <folder_path> [config_path]")
        sys.exit(1)

    args = parse_args()
    folder = args.folder
    config = args.config
    allow_duplicates = args.allow_duplicates

    scan_folder_for_exes(folder, config, allow_duplicates)
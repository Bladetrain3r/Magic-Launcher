# validate_shortcuts.py
import json
from pathlib import Path
from models import item_from_dict, Shortcut, Folder, BaseItem
from argparse import ArgumentParser

def validate_config(path=None):
    if path:
        config_file = Path(path)
    else:
        config_file = Path.home() / '.config/launcher/shortcuts.json'
    
    try:
        data = json.loads(config_file.read_text())
    except json.JSONDecodeError as e:
        print(f"X Invalid JSON: {e}")
        return False
    
    if not config_file.exists():
        print(f"X Config file does not exist: {config_file}")
        exit(1)
    
    errors = []
    
    def check_items(items_dict, path=""):
        for name, item_data in items_dict.items():
            current_path = f"{path}/{name}" if path else name
            try:
                # Check if it's already an object or still a dict
                if isinstance(item_data, BaseItem):
                    # Already instantiated, skip
                    errors.append(f"Already instantiated at {current_path}")
                    continue
                    
                # Should be a dict
                if not isinstance(item_data, dict):
                    errors.append(f"Expected dict at {current_path}, got {type(item_data)}")
                    continue
                
                # Try to instantiate
                item = item_from_dict(name, item_data)
                
                # Additional checks
                if isinstance(item, Shortcut) and not item.path:
                    errors.append(f"Empty path: {current_path}")

                # If shortcut has args, check it's a string
                if isinstance(item, Shortcut) and 'args' in item_data:
                    if not isinstance(item_data['args'], str):
                        errors.append(f"Args should be a string at {current_path}")
                
                # Check shortcut isn't blank
                if isinstance(item, Shortcut) and not item.name:
                    errors.append(f"Shortcut name is blank at {current_path}")

                # Check keys are present in raw dict. Type is always required to have a value. Everything else can be empty as long as the key exists for consistency.
                required_keys = ['type']

                may_be_blank_keys = ['icon']
                if isinstance(item, Folder):
                    # if it's empty, must be a dict
                    may_be_blank_keys.append('items')
                
                if isinstance(item, Shortcut):
                    required_keys.append('path')

                for key in required_keys:
                    if key not in item_data or not item_data[key]:
                        errors.append(f"Missing required key '{key}' at {current_path}")

                for key in may_be_blank_keys:
                    if key not in item_data:
                        errors.append(f"Missing optional key '{key}' at {current_path}")

                # Check each field for required properties
                if not item.name:
                    errors.append(f"Missing name at {current_path}")
                if not item.icon:
                    errors.append(f"Missing icon at {current_path}")
                if not item.type or item.type not in ['shortcut', 'folder']:
                    errors.append(f"Missing type at {current_path}")
                if isinstance(item, Shortcut) and not item.path and not item.type == 'folder':
                    errors.append(f"Empty path or missing path key for shortcut at {current_path}")

                # For folders, recurse with the raw dict items
                if isinstance(item, Folder) and 'items' in item_data:
                    check_items(item_data['items'], current_path)
                    
            except Exception as e:
                errors.append(f"Invalid item at {current_path}: {e}")
    
    check_items(data)
    
    if errors:
        print("X Validation errors:")
        for error in errors:
            print(f"  - {error}")

    if len(errors) == 0:
        print("All shortcuts are valid.")
        exit(0)
    else:
        print("Some shortcuts are invalid. Please fix the errors above.")
        exit(1)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--path", help="Path to shortcuts.json")
    args = parser.parse_args()
    validate_config(args.path)
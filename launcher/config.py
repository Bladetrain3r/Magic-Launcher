"""Configuration management for launcher."""

import json
from typing import Dict, Any
from pathlib import Path

from constants import CONFIG_FILE, CONFIG_DIR, DEFAULT_SHORTCUTS, SETTINGS_FILE
from models import item_from_dict, BaseItem, Folder
from utils.logger import logger


class ConfigManager:
    """Manages loading and saving configuration."""
    
    def __init__(self):
        self.shortcuts = {}
        self.settings = {}
        self.ensure_directories()
    
    def ensure_directories(self):
        """Create necessary directories."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        (CONFIG_DIR / 'icons').mkdir(exist_ok=True)
        logger.info(f"Config directory: {CONFIG_DIR}")
    
    def load_shortcuts(self) -> Dict[str, BaseItem]:
        """Load shortcuts from config file."""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                
                # Convert to model objects
                shortcuts = {}
                for name, item_data in data.items():
                    shortcuts[name] = item_from_dict(name, item_data)
                
                logger.info(f"Loaded {len(shortcuts)} top-level items")
                self.shortcuts = shortcuts
                return shortcuts
                
            except Exception as e:
                logger.error(f"Error loading config: {e}")
                return self._get_default_shortcuts()
        else:
            logger.info("No config file found, using defaults")
            return self._get_default_shortcuts()
    
    def save_shortcuts(self, shortcuts: Dict[str, BaseItem]):
        """Save shortcuts to config file."""
        try:
            # Convert models to dict
            data = {
                name: item.to_dict() 
                for name, item in shortcuts.items()
            }
            
            with open(CONFIG_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved {len(shortcuts)} items to config")
            return True
            
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            return False
    
    def load_settings(self) -> Dict[str, Any]:
        """Load user settings."""
        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    settings = json.load(f)
                logger.info("Loaded user settings")
                self.settings = settings
                return settings
            except Exception as e:
                logger.error(f"Error loading settings: {e}")
                return {}
        return {}
    
    def save_settings(self, settings: Dict[str, Any]):
        """Save user settings."""
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(settings, f, indent=2)
            logger.info("Saved user settings")
            self.settings = settings
            return True
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            return False
    
    def _get_default_shortcuts(self) -> Dict[str, BaseItem]:
        """Get default shortcuts as model objects."""
        shortcuts = {}
        for name, data in DEFAULT_SHORTCUTS.items():
            shortcuts[name] = item_from_dict(name, data)
        
        # Save defaults
        self.save_shortcuts(shortcuts)
        return shortcuts

    def substitute_paths(self, old_path, new_path):
        """Replace exact path strings across all shortcuts"""
        shortcuts = self.load_shortcuts()
        if not shortcuts:
            logger.warning("No shortcuts loaded, cannot substitute paths")
            return {}
        
        # Helper function for recursion
        def _substitute_in_items(items):
            for name, item in items.items():
                # Check if it's a Shortcut with matching path
                if hasattr(item, 'path') and item.path == old_path:
                    item.path = new_path
                # If it's a Folder, recurse into its items
                elif isinstance(item, Folder) and hasattr(item, 'items'):
                    _substitute_in_items(item.items)
        
        _substitute_in_items(shortcuts)
        self.save_shortcuts(shortcuts)
        return shortcuts

# Global config instance
config_manager = ConfigManager()
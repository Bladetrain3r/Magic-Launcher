from pathlib import Path

# Version
VERSION = "0.3.1"
APP_NAME = "Magic Launcher"

# Paths
CONFIG_DIR = Path.home() / '.config' / 'launcher'
CONFIG_FILE = CONFIG_DIR / 'shortcuts.json'
ICONS_DIR = CONFIG_DIR / 'icons'
LOG_FILE = CONFIG_DIR / 'launcher.log'
SETTINGS_FILE = CONFIG_DIR / 'settings.json'

# UI Constants
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
ICON_SIZE = 80
ICON_GRID_COLUMNS = 8

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

# Default shortcuts structure
DEFAULT_SHORTCUTS = {
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
        }
    },
    'Scripts': {
        'type': 'folder',
        'icon': 'S',
        'items': {}
    }
}

# File dialog filters
FILE_FILTERS = [
    ("All files", "*.*"),
    ("Executables", "*.exe *.sh *.py *.bat"),
    ("Scripts", "*.sh *.py *.pl *.rb"),
]

ICON_FILTERS = [
    ("BMP files", "*.bmp"),
    ("All files", "*.*")
]
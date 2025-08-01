from pathlib import Path

# Version
VERSION = "1.0.0"

APP_NAME = "Shouldn't see this, use ConfigManager.get_app_name() instead"

# Paths
CONFIG_DIR = Path.home() / '.config' / 'launcher'
CONFIG_FILE = CONFIG_DIR / 'shortcuts.json'
ICONS_DIR = CONFIG_DIR / 'icons'
LOG_FILE = CONFIG_DIR / 'launcher.log'
SETTINGS_FILE = CONFIG_DIR / 'settings.json'
APP_NAME_PATH = CONFIG_DIR / 'title.txt'

# UI Constants
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
ICON_SIZE = 80
ICON_GRID_COLUMNS = 9
LABEL_BASE_WIDTH = 10  # Base width for labels, can be adjusted based on name length

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
DEFAULT_SHORTCUTS_PATH = Path(__file__).parent / 'config' / 'default.json'

# File dialog filters
FILE_FILTERS = [
    ("All files", "*.*"),
    ("Executables", "*.exe *.sh *.py *.bat *.ps1"),
    ("Scripts", "*.sh *.py *.pl *.rb"),
]

ICON_FILTERS = [
    ("BMP files", "*.bmp"),
    ("All files", "*.*")
]
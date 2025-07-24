"""Icon loading and caching utilities."""

from pathlib import Path
from typing import Optional, Dict
import shutil

from constants import ICONS_DIR
from utils.logger import logger

# Try to import PIL
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger.warning("PIL not available - BMP icons disabled")


class IconManager:
    """Manages icon loading and caching."""
    
    def __init__(self):
        self.cache: Dict[str, 'ImageTk.PhotoImage'] = {}
        self.icon_size = (64, 64)  # Default icon size
    
    def get_icon(self, icon_spec: str) -> Optional['ImageTk.PhotoImage']:
        """
        Load an icon from specification.
        
        Returns PhotoImage for BMP files, None for text icons.
        """
        if not icon_spec or not PIL_AVAILABLE:
            return None
        
        # Only handle BMP files
        if not icon_spec.endswith('.bmp'):
            return None
        
        # Check cache first
        if icon_spec in self.cache:
            return self.cache[icon_spec]
        
        # Try to load from icons directory
        icon_path = ICONS_DIR / icon_spec
        if icon_path.exists():
            try:
                img = Image.open(icon_path)
                img = img.resize(self.icon_size, Image.NEAREST)
                photo = ImageTk.PhotoImage(img)
                self.cache[icon_spec] = photo
                logger.debug(f"Loaded icon: {icon_spec}")
                return photo
            except Exception as e:
                logger.error(f"Error loading icon {icon_spec}: {e}")
        
        return None
    
    def copy_icon_to_storage(self, source_path: str) -> Optional[str]:
        """
        Copy an icon file to the icons directory.
        
        Returns the filename if successful, None otherwise.
        """
        source = Path(source_path)
        if not source.exists():
            return None
        
        try:
            dest = ICONS_DIR / source.name
            shutil.copy2(source, dest)
            logger.info(f"Copied icon to {dest}")
            return source.name
        except Exception as e:
            logger.error(f"Error copying icon: {e}")
            return None
    
    def clear_cache(self):
        """Clear the icon cache."""
        self.cache.clear()
        logger.debug("Cleared icon cache")


# Global icon manager instance
icon_manager = IconManager()
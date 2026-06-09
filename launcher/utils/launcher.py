"""Utilities for launching applications and shortcuts."""

import subprocess
import platform
import os
from pathlib import Path
from shutil import which
from typing import Optional
from utils.logger import logger

# Cache of path -> validity so re-renders (especially search-as-you-type)
# don't hit the filesystem or PATH lookup for every icon, every keystroke.
_validity_cache = {}


def is_valid_target(path: str) -> bool:
    """Check if a shortcut target points at something launchable."""
    if not path:
        return False

    if path in _validity_cache:
        return _validity_cache[path]

    # URLs are always considered valid (we can't check them quickly)
    if path.startswith(('http://', 'https://')):
        valid = True
    else:
        expanded = os.path.expanduser(os.path.expandvars(path))
        if os.path.isabs(expanded):
            valid = os.path.exists(expanded)
        else:
            # Might be a command in PATH
            cmd = path.split()[0]
            valid = which(cmd) is not None

    _validity_cache[path] = valid
    return valid


def clear_validity_cache():
    """Forget cached path checks (e.g. on config refresh)."""
    _validity_cache.clear()


class Launcher:
    """Handles launching shortcuts and applications."""
    
    @staticmethod
    def launch(path: str, args: str = "") -> bool:
        """
        Launch a program, URL, or file.
        
        Returns True if successful, False otherwise.
        """
        if not path:
            logger.warning("Attempted to launch empty path")
            return False
        
        try:
            # Build full command
            if args:
                cmd = f"{path} {args}"
            else:
                cmd = path
            
            logger.info(f"Launching: {cmd}")
            
            # Handle URLs
            if path.startswith(('http://', 'https://')):
                return Launcher._open_url(path)
            
            # Handle text files
            if Path(path).suffix in ['.txt', '.md', '.log', '.conf', '.cfg']:
                return Launcher._open_text_file(path)
            
            # PDF treated as a browser link for compatibility
            if Path(path).suffix == '.pdf':
                return Launcher._open_url(path)
            
            # Determine working directory
            cwd = None
            expanded_path = os.path.expanduser(os.path.expandvars(path))
            
            if os.path.isabs(expanded_path) and os.path.exists(expanded_path):
                # If it's an absolute path to a file, use its directory as cwd
                cwd = str(Path(expanded_path).parent)
                logger.info(f"Setting working directory to: {cwd}")
            
            # Execute as command
            subprocess.Popen(cmd, shell=True, cwd=cwd)
            return True
            
        except Exception as e:
            logger.error(f"Launch error for '{path}': {e}")
            return False
    
    @staticmethod
    def _open_url(url: str) -> bool:
        """Open a URL in the default browser."""
        try:
            if platform.system() == 'Darwin':
                subprocess.Popen(['open', url])
            elif platform.system() == 'Windows':
                subprocess.Popen(['start', url], shell=True)
            else:
                subprocess.Popen(['xdg-open', url])
            return True
        except Exception as e:
            logger.error(f"Error opening URL '{url}': {e}")
            return False
    
    @staticmethod
    def _open_text_file(path: str) -> bool:
        """Open a text file in the default editor."""
        try:
            if platform.system() == 'Windows':
                subprocess.Popen(['notepad', path])
            else:
                subprocess.Popen(['xdg-open', path])
            return True
        except Exception as e:
            logger.error(f"Error opening text file '{path}': {e}")
            return False
    
    @staticmethod
    def validate_path(path: str) -> Optional[str]:
        """
        Validate and expand a path.
        
        Returns expanded path or None if invalid.
        """
        if not path:
            return None
        
        # Don't validate URLs
        if path.startswith(('http://', 'https://')):
            return path
        
        # Expand path
        expanded = os.path.expanduser(os.path.expandvars(path))
        
        # Check if it's a command in PATH
        if os.path.isabs(expanded):
            if os.path.exists(expanded):
                return expanded
        else:
            # It might be a command in PATH
            return path
        
        return None
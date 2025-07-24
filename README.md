# Magic Launcher

A lightweight, retro-styled application launcher designed for low-spec systems. Inspired by DOS-era menu systems, it provides a simple, keyboard-friendly interface for organizing and launching applications, scripts, and URLs.

## Features

- **Lightweight**: Runs smoothly on systems with as little as 256MB RAM
- **SSH/X11 Friendly**: 720p resolution, minimal graphics
- **Retro Aesthetic**: 16-color CGA/EGA palette, DOS-style UI
- **Nested Folders**: Organize shortcuts in hierarchical folders
- **Search**: Recursive search across all folders (Ctrl+F)
- **BMP Icons**: Support for bitmap icons or text characters
- **No Dependencies**: Uses only Python standard library (Tkinter)
- **Portable**: All config stored in `~/.config/launcher/`

## Installation

1. Clone or download the repository
2. Ensure Python 3.6+ is installed
3. (Optional) Install Pillow for BMP icon support: `pip install Pillow`

## Usage

```bash
cd launcher
python app.py
```

### Keyboard Shortcuts

- **Ctrl+F**: Toggle search mode
- **Ctrl+D**: Duplicate selected item  
- **Enter**: Launch selected item
- **Escape**: Go up one level / Exit search
- **Backspace**: Go up one level
- **Double-click**: Launch item or open folder

### Mouse Actions

- **Right-click**: Context menu (Edit, Duplicate, Delete, Properties)
- **Hover**: Visual feedback on icons

## Configuration

All configuration is stored in `~/.config/launcher/`:

- `shortcuts.json`: Your shortcuts and folders
- `icons/`: BMP icon files
- `launcher.log`: Application logs

### Adding Shortcuts

1. Click the **+** button or right-click and select "New"
2. Choose type (Shortcut or Folder)
3. For shortcuts:
   - **Name**: Display name
   - **Path**: Executable path, URL, or command
   - **Arguments**: Command-line arguments
   - **Icon**: Single character or .bmp filename

### Icon System

- **Text Icons**: Any 1-2 character string (e.g., "G" for Games)
- **BMP Icons**: Bitmap files in `~/.config/launcher/icons/`
- Icons are automatically imported when browsing
- Recommended size: 64x64 pixels (will be scaled if needed)

## Examples

### Game Launcher
```json
{
  "name": "DOOM",
  "type": "shortcut",
  "icon": "doom.bmp",
  "path": "/usr/games/doom",
  "args": "-fullscreen"
}
```

### Script with Arguments
```json
{
  "name": "Backup Home",
  "type": "shortcut", 
  "icon": "B",
  "path": "/home/user/scripts/backup.sh",
  "args": "--incremental /home/user"
}
```

### Web Link
```json
{
  "name": "GitHub",
  "type": "shortcut",
  "icon": "G",
  "path": "https://github.com"
}
```

## Design Philosophy

Magic Launcher follows the Unix philosophy: do one thing and do it well. It's not a desktop environment or file manager - it's purely a shortcut organizer and launcher. This focused approach means:

- Tiny codebase (~2000 lines)
- Minimal dependencies
- Fast startup
- Low memory usage
- SSH-friendly

## System Requirements

- Python 3.6 or higher
- Tkinter (usually included with Python)
- ~10MB disk space
- ~20MB RAM
- X11 (on Linux/Unix)

## Optional Dependencies

- **Pillow**: For BMP icon support (`pip install Pillow`)

## Troubleshooting

### Icons not showing
- Install Pillow: `pip install Pillow`
- Ensure icons are in `~/.config/launcher/icons/`
- Use 16-color BMP format

### Application won't launch
- Check the path in shortcut properties
- Look at `~/.config/launcher/launcher.log` for errors
- Ensure the executable has proper permissions

### SSH/X11 Issues
- Ensure X11 forwarding is enabled: `ssh -X user@host`
- The fixed 720p resolution should work on most displays

## License

This project is released into the public domain. See LICENSE file for details.

## Contributing

Contributions are welcome! The codebase is modular and well-documented. Key areas for contribution:

- Import/export functionality  
- Platform-specific improvements
- Documentation and examples
- Useful extensions to the core emphasising immediate utility

## Acknowledgments

Inspired by classic DOS menu systems and the need for a lightweight launcher that works well on low-spec hardware.
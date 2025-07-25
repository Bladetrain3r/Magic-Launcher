# Magic Launcher - Your Shortcut Palette

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
4. (Optional) Install xdg-utils and/or x11-apps to get GUI passthrough

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

### Shortcuts.json

- This is the source of truth for all shortcut data
- Icons are loaded in the order they are retrieved from the shortcuts file
- Reordering of shortcuts is best done via editing
- Needs better validation

### Icon System

- **Text Icons**: Any 1-2 character string (e.g., "G" for Games)
- **BMP Icons**: Bitmap files in `~/.config/launcher/icons/`
- Icons are automatically imported when browsing
- Recommended size: 64x64 pixels (will be scaled if needed)

#### Unicode Icons
Yes, specials work too!
```
Games & Entertainment

🎮 🎯 🎲 🎰 🎪 🎨 🎭 🎬 🎵 🎸 🎹 🎺 🎪 ♠ ♣ ♥ ♦ ♟ ♜ ⚀ ⚁ ⚂ ⚃ ⚄ ⚅

Tools & System

⚙ 🔧 🔨 ⚒ 🛠 🔩 ⚡ 💾 💿 📀 🖥 💻 ⌨ 🖱 🖨 📱 ☎ 📞 🔌 🔋 🔒 🔓 🔐 🔑 🗝

Files & Folders

📁 📂 📄 📃 📋 📌 📎 📏 📐 ✂ 📝 ✏ ✒ 🖊 🖋 📜 📊 📈 📉 🗂 🗃 🗄

Navigation & Actions

▶ ◀ ▲ ▼ ⏵ ⏴ ⏶ ⏷ ⏯ ⏸ ⏹ ⏺ ⏭ ⏮ ⏩ ⏪ ↩ ↪ ⤴ ⤵ ⬆ ⬇ ⬅ ➡ ↗ ↘ ↙ ↖ ↕ ↔ 🔃 🔄

Internet & Communication

🌐 🌍 🌎 🌏 📧 📨 📩 ✉ 📮 📪 📫 📬 📭 💬 💭 🗨 🗯 📢 📣 📡 📶 📳 📴

Math & Symbols

➕ ➖ ✖ ➗ ± × ÷ = ≈ ≠ < > ≤ ≥ ∞ ∑ √ ∛ ∜ π Σ Ω ∆ ∇ ∫ ∂

Status & Indicators

✓ ✔ ✗ ✘ ⚠ ⚡ ⛔ 🚫 ❌ ⭕ ❗ ❓ ❕ ❔ 💡 🔍 🔎 👁 🎯 📍 🏁 🏴 🏳 🚩

Misc Useful

⭐ ★ ☆ ❤ ♥ 👍 👎 👌 ✋ ✊ 🏠 🏢 🏭 🏗 🚀 ✈ 🚁 ⚓ 🎪 🎨 🍕 ☕ 🍺

Box Drawing (DOS-style)

═ ║ ╔ ╗ ╚ ╝ ╠ ╣ ╦ ╩ ╬ ▀ ▄ █ ▌ ▐ ░ ▒ ▓

Most of these should display fine in the launcher. Some tips:

Test the character first - font support varies
Emojis work but may look different across systems
Box drawing characters give that authentic DOS feel
Arrows are great for navigation/back buttons

Copy and paste right into the icon field!
```

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

### Plaintext File (Log, Config)
- These will launch in the default editor for their filetype
```json
{
  "name": "Shortcut Config",
  "type": "shortcut",
  "icon": "⚙",
  "path": "C:\Users\Jimmy\.config\launcher\launcher.log"
}
```

### Directories with your local file explorer
- Handles quoted args too
```json
{
  "name": "My Documents",
  "type": "shortcut",
  "icon": "📁",
  "path": "explorer",
  "args": "\"C:\Users\Jimmy\Documents\""
}
```

### Run SSH commands or remotely view logs if running in Linux
```json
  "Dev DB SysLogs": {
    "type": "shortcut",
    "icon": "D",
    "path": "/mnt/c/Users/Jimmy/getlogs.sh",
    "args": ""
  },
  "Dev DB Top": {
    "type": "shortcut",
    "icon": "T",
    "path": "ssh",
    "args": "utu@111.211.121.212 -t \"top\""
  }
```

### X11 Remote Forwarding
You can run Magic Launcher on a remote server using X forwarding.
Best on a LAN but it will function over WAN too.
```bash
ssh -X -t user@server "python3 /~/Magic-Launcher/launcher/app.py"
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

### Known Issues
- Launching multiple terminal apps at once is permitted and will cause a mess in your TTY
- Unicode doesn't work via WSL
- Right-click dialogue starts popping up every time you mouse over certain coordinates, sometimes. Right click event not handling properly?
- Occasionally multiple right click dialogues start appearing for bo reason

## License

This project is released into the public domain. See LICENSE file for details.

## Contributing

Contributions are welcome! The codebase is modular and well-documented. Key areas for contribution:

- Import/export functionality  
- Platform-specific improvements
- Documentation and examples
- Security issues
- Bugs
- Useful extensions to the core emphasising immediate utility
- The goal remains to keep bloat relatively minimal and focus on task high.

## Acknowledgments

Inspired by classic DOS menu systems and the need for a lightweight launcher that works well on low-spec hardware.
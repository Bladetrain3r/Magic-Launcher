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

## Host Setup

- To run it reliably on a machine, the following steps and prerequisites will be needed.

1. Clone or download the repository
2. Ensure Python 3 is installed. I recommend 3.10 or above but 3.6+ should work.
3. Confirm tkinter is installed (standard, sometimes)
4. Install x11-apps to get display passthrough on Linux
5. (Optional) On Windows, install an X server to avoid WSL passthrough for Docker containers.
6. (Optional) Install Pillow for BMP icon support: `pip install Pillow`
7. (Optional) Install xdg-utils

## Usage
### Linux:
```
python3 path_to/Magic-Launcher/launcher/app.py
```

### X11 Forwarding
You can run Magic Launcher on a remote host if it's running an X server.
Best on a LAN but it will function over WAN too.
```bash
ssh -XC -t user@server "python3 path_to/Magic-Launcher/launcher/app.py"
```

#### Setting up for easy launch
Paste to set up with git:
```bash
git clone https://github.com/Bladetrain3r/Magic-Launcher.git ~/.local/share/Magic-Launcher
echo 'alias magiclauncher="python3 ~/.local/share/Magic-Launcher/launcher/app.py"' >> ~/.bashrc
# To launch on login
echo 'if [ -n "$DISPLAY" ]; then magiclauncher & fi' >> ~/.bashrc
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

### Substituting Paths
This is a function intended for mass migration of shortcuts when a frequently used application is moved or you port a config between environments.
Exact string matches only.

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



## Design Philosophy

Magic Launcher follows the Unix philosophy: do one thing and do it well. It's not a desktop environment or file manager - it's purely a shortcut organizer and launcher. This focused approach means:

- Tiny codebase (~2000 lines)
- Minimal dependencies
- Fast startup
- Low memory usage
- SSH-friendly

### Design Guideposts

- Any feature needing more than a hundred or two lines of code is probably too complicated for a single feature
- Bloat is the speed killer, bloat is the technical debt that leads to stagnation.
- Any feature which violates these two principles *will* be dropped.

## System Requirements

- Python 3.6 or higher
- Tkinter (usually included with Python)
- ~10MB disk space
- ~20MB RAM
- X11 (on Linux/Unix)

### Tested In
- A Powershell environment on multiple Windows devices
- WSL/Ubuntu through BASH
- A Raspberry Pi B running Debian Buster (works on ARM7)
- Alpine inside Docker (Problems)
- Ubuntu inside a container (less problems)
- Running remotely on a Debian VM over WAN (Cloud Desktop)
- On an old laptop running Pop!OS
- My gran's PC

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

### Spaces and special characters can cause problems in Windows
- Workaround: Use powershell to launch with Start-Process e.g.
```
"path": powershell
"args": -Noninteractive Start-Process 'C:\Program Files (x86)\VideoLAN\VLC\vlc.exe'
```

### Known Issues
- Launching multiple terminal apps at once is permitted and will cause a mess in your TTY
- Unicode font support may be limited on other OS'
- Right-click dialogue starts popping up every time you mouse over certain coordinates, sometimes. Right click event not handling properly?
- Delayed response over a network and multiple inputs can make things weird.
- String handling needs... work.
- When run on Linux the resizing is enabled (future feature, current bug)
- Changing a an empty shortcut to a folder still results in a missing shortcut error. Delete seems to work.

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
- Dialogue state handling for substitution may cause new dialogues to stop appearing. Restart the app to work around.

## Acknowledgments

Inspired by classic DOS menu systems and the need for a lightweight launcher that works well on low-spec hardware.
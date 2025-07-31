# Features
Through simplicity and composability, Magic Launcher has demonstrated exceptionally flexible abilities:

## Cross-Environment Isolation

Separate configs per environment (Windows/WSL/Remote)
Each environment's ~/.config/launcher/ is independent
Run different launcher instances with completely different shortcuts
Share code, not configurations

## Terminal Integration

Launched from terminal = terminal apps output to that terminal
GUI apps detach properly while terminal apps stay connected
Works with interactive terminal programs (vim, htop, ssh)
No need for terminal window management

## Remote Execution

SSH shortcuts work seamlessly: ssh -t server htop
Chain commands: ssh server 'cd /logs && tail -f app.log'
Remote interactive sessions just work
Minimal special handling needed

## Docker Compose Database and a Frontend

Spin up a container with MariaDB and a container with Dbeaver
Preconfigure shortcuts to connect with Dbeaver to Mariadb
Connect within the container network or outside
Optional bind mounts can ensure persistence of queries

## Working Directory Intelligence

Executables launch from their directory
Games/apps find their data files correctly
Scripts run in proper context
Automatic cwd detection from executable path

## URL Handling

Windows: Opens in default Windows browser
WSL with X11: Opens in Linux browser through X forwarding
No environment detection needed
Same (web) shortcut works everywhere

## File/Folder Opening

Documents open in default editors
Folders open in native file explorer
Works cross-platform without modification
Supports quoted paths with spaces

## Visual Feedback

Broken shortcuts show red X overlay
Still editable/deletable when broken
Immediate visual indication of problems
No functionality blocked

## Script Chaining

Wrapper scripts can perform complex operations
Download → Edit → Cleanup workflows
Returns when complete

## Emergency Reordering

Duplicate + Delete = Move to end
Manual JSON editing for precise control
Scriptable via JSON manipulation
No complex drag-drop needed

## Easy Automation
Easy to modify config files make automation easy, and maintenance scripts can be run from within the launcher.

```
scripts/maintenance/
├── validate_shortcuts.py      # Check for broken paths, missing icons
├── backup_config.py          # Timestamped backups
├── migrate_config.py         # Handle version upgrades
├── clean_unused_icons.py     # Remove orphaned BMPs
└── generate_stats.py         # "You have 47 shortcuts across 12 folders"
```

## Icon Flexibility

Unicode/emoji characters work as icons
BMP images auto-import to central storage
Mix text and image icons freely
Icons portable with config

## Natural Organization

Folders for categories
Search supersedes manual organization
Recursive search finds items anywhere

## Configuration as Interface

JSON files editable as "settings panel"
Launcher shortcuts to config folder
Version control friendly
Easy backup/sharing

## Mass Path Migration

Universal path substitution across all shortcuts
Migrate between systems with one operation
Port configs from /usr/local to /opt instantly
No regex or patterns - just exact string replacement

## Portable Deployment

Single JSON config file
No database or complex state
Export/import is just file copy
Docker-friendly minimal footprint

## Keyboard Power Users

Ctrl+D duplicate without mouse
Search with instant results
Navigate folders with keyboard
Launch by pressing Enter

# Ephemeral Tools & Self-Destructing Services Ideas

## Core Concept
Using Magic Launcher to spin up temporary, containerized services that vanish without a trace. Perfect for demonstrating the "OS-free desktop" philosophy - no permanent installations, no system contamination.

## 1. Self-Contained Secure Document Vault (Primary Demo)

### Overview
A Docker container that includes:
- Encrypted document archive
- Embedded Magic Launcher instance
- Decrypt operations as launcher shortcuts
- Auto-destructs when closed

### Implementation Concept
```bash
# Container structure
/vault/
├── magic-launcher/
│   ├── app.py
│   └── shortcuts.json  # Contains decrypt shortcuts
├── encrypted/
│   ├── report.pdf.gpg
│   ├── contracts.tar.gpg.gz
│   └── sensitive-data.zip.gpg
├── keys/
│   └── vault.key  # Generated at runtime, never persisted
└── start.sh  # Launches VNC + Magic Launcher
```

### Magic Launcher Shortcuts Inside Container
- "Decrypt Financial Report" → `gpg -d /vault/encrypted/report.pdf.gpg > /tmp/report.pdf && xdg-open /tmp/report.pdf`
- "Extract Contracts" → `gpg -d /vault/encrypted/contracts.tar.gpg.gz | tar -xz -C /tmp/`
- "Shred All Decrypted" → `shred -vfz /tmp/*`
- "Self Destruct" → `killall Xvnc` (triggers container exit)

### Access Method
- VNC/Xming into container for Windows: `docker run -p 5901:5901 vault-image`
- Or X11 forwarding for Linux hosts
- Magic Launcher provides the UI for all decrypt operations
- Keys exist only in container memory

### Security Features
- Password prompt before showing decrypt shortcuts
- Optional timeout auto-destruct
- No keys on host system
- Entire environment vanishes on exit

## 2. Temporary SMB/Samba Share

Quick script to share files temporarily:
```bash
#!/bin/bash
docker run -d --name temp-share \
  -p 445:445 \
  -v /tmp/share:/share \
  dperson/samba \
  -s "docs;/share;yes;no;no;all"
  
echo "Share available at \\\\$(hostname -I | cut -d' ' -f1)\\docs"
echo "Press enter to destroy..."
read
docker rm -f temp-share && rm -rf /tmp/share
```

## 3. Disposable Web Server

One-click Python HTTP server in a container:
```bash
docker run -d --name temp-web \
  -p 8080:8000 \
  -v /tmp/serve:/usr/share/nginx/html \
  python:alpine \
  python -m http.server 8000
```

## 4. Burn-After-Reading Note System

Serves a file once, then self-destructs:
```bash
# Simple version using netcat
echo "SECRET MESSAGE" | docker run -i --rm -p 8888:8888 alpine \
  sh -c 'nc -l -p 8888 -q 0 < /dev/stdin'
```

## 5. Ephemeral VPN Endpoint

Temporary WireGuard/OpenVPN container that generates configs on the fly and vanishes after use.

## 6. One-Time Pastebin

Container that:
- Accepts text input
- Generates unique URL
- Serves content once
- Self-destructs after serving

## Demo Video Concepts

### "5 Self-Destructing Services in 5 Minutes"
Show rapid-fire creation and destruction of temporary services, all launched from Magic Launcher.

### "The Paranoid Pack"
Bundle these as pre-configured Magic Launcher shortcuts with icons:
- 🔒 Secure Vault
- 📁 Temp Share  
- 🌐 Quick Server
- 💣 Burn Note
- 🛡️ Ghost VPN

### Key Selling Points
- No permanent installation required
- No cleanup needed
- Perfect for sensitive operations
- Demonstrates launcher flexibility
- Shows "OS-free" philosophy in action

## Implementation Notes
- Keep containers minimal (Alpine base)
- Use environment variables for configuration
- Pre-build images for instant startup
- Include timeout options for auto-cleanup
- Consider RAM-only operation for extra paranoia


### These features emerged naturally from:

Not capturing subprocess output
Using standard config locations
Keeping shortcuts as simple JSON
Launching via basic subprocess calls
Not trying to be clever about environment detection
Treating configs as data, not code
Simple exact-match operations over complex patterns
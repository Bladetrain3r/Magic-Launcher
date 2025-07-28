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

### These features emerged naturally from:

Not capturing subprocess output
Using standard config locations
Keeping shortcuts as simple JSON
Launching via basic subprocess calls
Not trying to be clever about environment detection
Treating configs as data, not code
Simple exact-match operations over complex patterns
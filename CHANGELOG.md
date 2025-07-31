# Changelog

All notable changes to Magic Launcher will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.3.5] (OnDev)
### Quality of Life
- Subtly extend shortcut label for those long shortcut names
- Semi-hidden feature: Set MLHQ environment variable to scale the window and grid by two. 

### Bugfix
- Icon_label_place set to fixed so that the box borders remain consistently sized when selecting an icon.

## [0.3.4.2] - 2025-07-31

### Tagline
- Have decided my cheeky but not entirely untrue tagline will be: "An OS-free Desktop!"

### UI Alteration
- Allowed vertical resizing of window in Windows. Tiles excellently.

### Documentation
- General improvements and expansions on setup guidance.

### Examples
- Additional sample scripts and a functional docker compose template for sidecar loading

## [0.3.4.1] - 2025-07-29

### UI Alteration
- The power of a 9th column compels you!
- Increased default column count.

### Technical
- Enforce UTF-8 US locale in terminal or revert to local default only if unavailable

## [0.3.4] - 2025-07-29
### Added
- Title bar can now be customised by creating ~/.config/launcher/app_name.txt and populating it with a string
- Validation script (validate_shortcuts.py) for checking config integrity
- Bulk scanning script (\config_templates\sample_scripts\scan_for_exe.py) for importing executables from folders
- Config reload and redraw (refresh_config()) bound to Ctrl+R
- Debug log level added via MLENV environment variable.
- Tkinter check on startup for less cryptic import headaches.

### Documentation
- Updated FAQ with explicit dogfooding mention and use case expansions
- Added "Traps that will not be fallen into" section to roadmap

## [0.3.3] - 2025-07-28
### Added
- Shortcut keys of numerous types to make it fully keyboard usable. Easy to add, but important.

### Technical
- Migrated default config to a json file and implemented handling as part of porting not-actually-constants out of the constants file.

## [0.3.2.2] - 2025-07-28
### Added

- Left and Right arrow keys now allow you to navigate within a folder.
- Selected shortcuts now highlight properly.
- About menu updated with nav keys and Github link

Additional core hotkeys to be added later.

## [0.3.2.1] - 2025-07-27
### Added

- Path substitution now also applies to args and icons fields.

### Bugfix
- Ensured dialogue state set properly to false on closing substitute window.

### Bugs
- Discovered brackets* in Windows path names are problematic
- Workaround: Use powershell to launch with Start-Process e.g.
```
"path": powershell
"args": -Noninteractive Start-Process 'C:\Program Files (x86)\VideoLAN\VLC\vlc.exe'
```

## [0.3.2] - 2025-07-26
### Added

- Universal path substitute function. Useful for changing all your GZDoom shortcuts to a new version or when migrating configuration to a new environment.

### Known Bugs

- Improperly closing or switching focus from the substitution dialogue may cause the dialogue open status to get stuck in false and prevent new dialogues opening

### Documentation

- Updated roadmap, readme, FAQ

### Docker
- More Docker Shenanigans

### Config
- Added default URL pointing to a video that will never let you down.

## [0.3.1] - 2025-07-24
### Added

- Red X overlay for broken shortcuts
- Automatic validation of shortcut paths
- Visual feedback for missing executables

### Technical

- Path validation checks both absolute paths and PATH commands
- URLs are always considered valid (not checked)
- Overlay uses Canvas for clean rendering

## [0.3.0] - 2025-07-24

### Added
- Complete modular rewrite for production use
- Proper logging with rotation (utils/logger.py)
- Structured data models (models.py) 
- Centralized configuration management (config.py)
- Error handling throughout the application
- Automatic working directory setting for launched applications
- Icon auto-import functionality (copies to icons folder on selection)

### Changed
- Restructured into proper Python package with modules
- Simplified imports - single entry point via app.py
- Icons now always copy to central storage on import
- Better separation of UI and business logic

### Fixed
- Working directory issue for launched applications
- Dialog focus problems when browsing files
- Dataclass field ordering issues
- Import path complexity

## [0.2.0] - 2025-07-24

### Added
- File browser for selecting executables when creating shortcuts
- Duplicate function (right-click → Duplicate or Ctrl+D)
- Recursive search across all folders
- Search results show path context
- Dialog to prevent multiple edit windows
- Icon browse button with auto-copy functionality

### Changed
- Improved dialog layout with browse buttons
- Search now searches all folders, not just current
- Better keyboard navigation

### Fixed
- Single-click error on icons
- Search mode navigation

## [0.1.0] - 2025-07-24

### Initial Release
- Basic launcher functionality
- Nested folder support
- 16-color CGA/EGA palette
- Fixed 720p resolution for low-spec systems
- Keyboard shortcuts (Ctrl+F search, navigation)
- Right-click context menus
- JSON configuration storage
- BMP icon support (requires Pillow)
- Text character icons
- Launch support for:
  - Local executables
  - Shell commands  
  - URLs
  - Scripts with arguments
- Persistent configuration in ~/.config/launcher/
- Basic search within current folder

## Roadmap / Future Ideas

### DONE
- Universal path substitute - replace exact path strings across all shortcuts. And args/icons too. (DONE - 0.3.2)
- Arrow key navigation (DONE - 0.3.2.2)
- Move away from default shortcuts in constants, port into config (DONE - 0.3.3)
- Keyboard shortcuts for all major functions (DONE - 0.3.3)
- Edit Title Bar (DONE - 0.3.4)
- --reload parameter for instant config refresh without restart (DONE - Bound to Ctrl+R instead - 0.3.4)
- Config Validator and import/export util (Validator/Import scripts instead, keep it out of the app. Export is a shortcut to the local copy command.) (DONE - 0.3.4)
- Extend text bar for long shortcut names (PENDING RELEASE - 0.3.5)

### Short Term (Quick Implement)
- Only render unique shortcuts in search - if [name/target file/args] match only the first result is shown.
   - This way people can have copies of shortcuts in different folders if there is overlap, e.g. "Favorites" might share multiple shortcuts or you might have a game listed under "GOG" and "Action" folders.
- SIMPLE auto reorder of the current level only (load the level in as a dict, order it by type first, then alphabetical, the re-insert in it's former spot?). Bind to Ctrl+Alt+S.
- Secure String shortcut type (maybe - keepass or a simple script can handle secret retrieval)
- Add scid (shortcut id) to BaseItem in models.py
- Using scid as test, add function to check shortcuts for compulsory fields and assign a default/generated value - migrate old configs in code without bespoke logic.
- Hidden flag for shortcuts. Prevents showing up in search. Similar to SCID.
- Folder level indicator on search results (small roman numeral on top left corner of the shortcut). Mitigate confusion from similarly named results.
- Auto-open folders in the local file explorer (should be a trivial check of the object type in path)

### Medium Term
- Maintenance Menu via F11
- Point to shortcuts file (--profile I guess)
- Add startup check to confirm it's running from ~/.local/share/Magic-Launcher/
  - If not, migrate install to ~/.local/share/Magic-Launcher/ and use a symbolic or junction link to make it visible in the user's target folder.
- Break keyboard shortcut handling out of main_window.py into it's own ui module
- Portable mode putting .config in the working directory. (Check for empty file "portable", enable by creating the file)
- Full screen (simple output scaling)
- Import .lnk, .desktop and .shortcut files from system
- Custom color schemes
- Better handling of streaming output like tail -f
- "Duplicate to..." function to copy shortcuts to other folders
- Figure out how to move interface construction out of main_window so it can focus on the rendering
- Setup scripts for Linux and Windows not relying on Git clone except maybe the first time.
- Neaten up dependencies and imports for proper packaging.

### Long Term
- Standardised deployment package (zip) + Python setup script (install tkinter and Launcher with Python, which is hopefully already installed)
- Nail Down New User Experience and Default Shortcuts
- Fix Unicode support on Linux workspaces. If the terminal can display it the icon should work.
- Two modes: Admin/Unlocked and Locked/User.
- Password protected shortcuts/folders - can't launch or open without inputting a password.
- Dialogue to assign shortcuts to keys 1-9 (this is why shortcut IDs)
- Default app association customisation by file extension
- Arrangement Editor
- Gamepad/controller support
- Touch screen support (virtual keyboard mostly, mouse actions covered as long as it's multitouch)
- Grid size scaling
- Neaten up widgets
- Create and include default maintenance and some fun stat scripts to set up as shortcuts.

### Super Maybe
- Recent items tracking
- Icon and font scaling
- Select a field for find
- Alternative icon formats (ICO, PNG, JPG) (Unofficially supported already)
- Background Image Loading (Got Pillow already but strictly a nice to have later)

### 1.0 and Beyond
I intend to keep the application focused but continue adding features IF they contribute meaningfully to solving the core problem.

#### The Magic Launcher Paradigm
The Magic Launcher paradigm is one which emphasises stripping a project down to the core problem it solves.
First solve that, then consider the impact on it's ability to solve that when making changes.
This sounds obvious but anyone who has worked on enterprise scale software stacks understands that, when filtered through multiple teams and motivations, the core problem becomes murky.
Magic Launcher, being the name behind my paradigm, shall aim to set a strong example of what minimalism and focus can do for software ease of use and capability.

### Traps that will not be fallen into
- Cloud Integration
- Dependency Bloat
- Additional application integration. THE LAUNCHER STANDS ALONE.
- Extensions, plugins. The whole point is visual macros just run a script.
- Shiny Syndrome. Never mind that I like blocky EGA aesthetics, every customisation comes with cost.
- Universal glyph support for every combination of display manager, font, and text encoding under the sun. Unicode icons are best effort depending on your terminal and display window manager.
- Built in tools for SSH sync, cloud upload, or profile migration between hosts. That can ALL be done with a simple shell script with a shortcut, and has a high bloatage risk.

### Priority Reminder
- Any feature needing more than a hundred or two lines of code is probably too complicated for a single feature
- Bloat is the speed killer, bloat is the technical debt that leads to stagnation.
- Speed is life. Creep is death. 
- Any feature which violates these two principles *will* be dropped.
- Also: Anything which might produce an unexpectedly slow response time is not part of the code

## Particular Feature Notes

#### Secure String
```
Path field: Non-sensitive context (username, service name, etc.) - visible
Args field: The actual secret - hidden/obscured
Visual Indicators: Unicode lock icon, but maybe just a pair of bars to start to ensure it displays. Blue for secure.
Visual Indicators: Maybe a special blue border when selected too, trivial to add a type check and coloured borders are a flexible visual aid.
UI: Obscure inputs and don't show the value in properties.
Implementation: A new type of shortcut. Only Args field is active.
Hashing: SHA256, even a Pi can do it.
Salt: Randomly generate a secure salt with a (bounded) random length using a base64 string generator.
Use: Double click attempts to copy to the clipboard. Right click and edit to update.
Duplication seems pointless but "duplicate to" once implemented may be useful, so we won't prevent it.
```

### Maintenance Menu
For managing shortcuts.json
```
Bind to F11 by default
Next to the Info button keeps the UI clean.
|[STOP] [i] [⚙]           Magic Launcher v0.3.4|
Settings menu could include:

Backup Config → Save shortcuts.json with timestamp
Restore Config → Load from backup
Export Config → Save to custom location
Import Config → Load from file (auto-validates)
Open Config Folder → Quick access to ~/.config/launcher/

Example Structure:
~/.config/launcher/
├── shortcuts.json
├── backups/
│   ├── shortcuts_20250728_143022.json
│   └── shortcuts_20250727_091510.json
└── icons/
```

#### Admin Mode
```
Visual indicators:

Red padlock icon in title bar when locked
Disabled + and edit buttons
Right-click menu only shows "Properties" (if that)
Maybe different title bar color

The key check could be:

Hash the key file contents
Compare to stored hash in ./config/launcher/key
If match, enable edit mode

e.g. python app.py --unlock ~/.ssh/admin_key
```

#### Hidden flag for shortcuts
```
Easy enough to add - a single optional field in the BaseItem properties.
If field is present and/or True, don't render in search results.
Consider performance impact, but should be trivial next to search itself.
Visual indicator for flagged icons (different icon background?)
```

#### Password Protected Folders
```
Similar to the Hidden flag, easy optional field, backwards compatible by default as absence means False/blank.
An extra field in shortcut properties.
Treat similarly to secure strings, store as salted hash in the shortcut properties, and obfuscate in the UI.
Not really secure (they can add a shortcut to edit shortcuts.json and get all the hashes) but combined with lock mode or a read-only environment, good for an extra hindrance.
```

#### Profiles
```
Just --profile pointing to a path instead of the default shortcuts.json
Maybe 6 lines, few complications.
```

### 1-9 Shortcut Keys
```
Requires Shortcut IDs (scid) to be implemented.
Purely keyboard driven.
Ctrl+1 - Ctrl+9 assigns selected shortcut by ID
To launch, F1-F9 keys
To delete, Ctrl + Alt + Number
Shortcut gets a special green font, or green border if it has an image icon.
F10 filters for only the assigned shortcuts, escape to return to previous screen or Ctrl+H to go home.
```

## What is 1.0?
When three criteria are met:
- Stable, low bugs, passes a code review without too many raised problems.
- No features or design changes left that aren't explicitly post-1.0 (bit flexible but roadmap as of 0.3 is the core planned featureset)
- Packages available on Pypi, apt/snap, yum, apk and chocolatey
- Public Docker image available

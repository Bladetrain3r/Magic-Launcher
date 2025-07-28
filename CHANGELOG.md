# Changelog

All notable changes to Magic Launcher will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.3.4] - PENDING
- Title bar can now be customised by creating ~/.config/launcher/app_name.txt and populating it with a string. 

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
- Move away from constants, port into config (DONE - 0.3.3)
- Ctrl + N for new shortcut (DONE - 0.3.3)
- Ctrl + H to return to Home (DONE - 0.3.3)
- Other Shortcuts Too (DONE - 0.3.3)
- Edit Title Bar (PENDING RELEASE - 0.3.3.1)

### Short Term (Quick Implement)
- Secure String shortcut type
- Add scid (shortcut id) to BaseItem in models.py
- Using scid as test, add function to check shortcuts for compulsory fields and assign a default/generated value - migrate old configs in code without bespoke logic.
- Hidden flag for shortcuts. Prevents showing up in search. Similar to SCID.
- Folder level indicator on search results (small roman numeral on top left corner of the shortcut). Mitigate confusion from similarly named results.

### Medium Term
- Add startup check to confirm it's running from ~/.local/share/Magic-Launcher/
  - If not, migrate install to ~/.local/share/Magic-Launcher/ and use a symbolic or junction link to make it visible in the user's target folder.
- Break shortcut handling out of main_window.py into it's own ui module
- Portable mode putting .config in the working directory. (Check for empty file "portable", enable by creating the file)
- Full screen (simple output scaling)
- Import .lnk, .desktop and .shortcut files from system
- Config Validator and import/export util
- Multiple launcher profiles (subfolders in .config?)
- Custom color schemes
- Better handling of streaming output like tail -f
- "Duplicate to..." function to copy shortcuts to other folders
- Figure out how to move interface construction out of main_window so it can focus on the rendering
- Setup scripts for Linux and Windows not relying on Git clone.
- Same for the update scripts. Or at least don't assume.

### Long Term
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

### Super Maybe
- Recent items tracking
- Icon and font scaling
- Select a field for find
- Alternative icon formats (ICO, PNG, JPG) (Unofficially supported already)

### Traps that will not be fallen into
- Cloud Integration
- Dependency Bloat
- Additional application integration. THE LAUNCHER STANDS ALONE.
- Extensions, plugins. The whole point is visual macros just run a script.
- Shiny Syndrome. Never mind that I like blocky EGA aesthetics, every customisation comes with cost.

### Priority Reminder
- Any feature needing more than a hundred or two lines of code is probably too complicated for a single feature
- Bloat is the speed killer, bloat is the technical debt that leads to stagnation.
- Any feature which violates these two principles *will* be dropped.

## Particular Feature Notes

#### Secure String
```
Visual Indicators: Unicode lock icon, but maybe just a pair of bars to start to ensure it displays. Blue for secure.
UI: Obscure inputs and don't show the value in properties.
Implementation: A new type of shortcut. Only Args field is active.
Hashing: SHA256, even a Pi can do it.
Salt: Randomly generate a secure salt with a (bounded) random length using a base64 string generator.
Use: Double click attempts to copy to the clipboard. Right click and edit to update.
Duplication seems pointless but "duplicate to" once implemented may be useful, so we won't prevent it.
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

## What is 1.0?
When three criteria are met:
- Stable, low bugs, passes a code review without too many raised problems.
- No features or design changes left that aren't explicitly post-1.0 (bit flexible but roadmap as of 0.3 is the core planned featureset)
- Packages available on Pypi, apt/snap, yum, apk and chocolatey
- Public Docker image available

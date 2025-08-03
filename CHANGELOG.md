# Changelog

All notable changes to Magic Launcher will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.2] - Obscurity not Security - PLANNING

### Save Our Strings
- Obscured string type added
- Uses initial implementation of path prefix system - prepend path with mlh. to hash it and store said hash as the path
- Paths appended with .mlh will automatically be unhashed and copied to clipboard
- This is just a quick way to store useful strings and commands, not a password manager.

### Diet README
- Put README through an intense cardio session to lose a lot of weight
- INTRO doc created to cover the bare basics

## [1.1] - The conf.d Apprach - PENDING
### My Top Ten: (PENDING)
- Ctrl+1 to Ctrl+0 now bind the selected shortcut to a doubletap of that number 
- These hotkey-bound shortcuts are stored as individual files named 1.json, 2.json, etc., containing the full shortcut definition.

### Hide My Shame (PENDING)
- Ctrl + L now "locks" the screen
- Reloads screen with blank JSON - no shortcuts to load, nothing to see.
- Ctrl + U to unlock.
- If password.txt exists in ~/.config/launcher/ it will pop up a password dialogue on unlock. 
- (Remove once confirmed) Check if empty passwords.txt will allow a blank password to be input.
- Won't even bother hashing it this is just a quick speedbump for casual compromisers

### Not a Couples Game:
Password field in shortcuts.json: Mess with top level hierarchy, it should be all shortcuts and folders.
SCID field. Reason for Rejection: The new hotkey file system makes this field unnecessary, as the filename itself serves as the identifier.
IsFavorite/Hotkey field. Reason for Rejection: This is an additional label to the shortcut, not essential to it's function.

### MOTD
- Shallow Duplication is a better solution than Deep Coupling

## [1.0] - 2025-08-03
### Extras Integration
- MLMenu is now a core Magic Launcher util and will be maintained and updated within the same repo
- MLRun (experimental) similarly so, which is a tool to autolaunch in sequence/parallel from shortcuts.json
- Both applications directly serve gaps in Magic Launcher's core functionality - a terminal menu for MLMenu, a pipeline executor for MLRun.

### Addendums
- ADDENDUMS_B.md added covering:
- The compositing pipelines enabled by simple command to json mapping
- An exploration of how metadata becomes a cancer on your application

## [1.0] - 2025-08-02

### Beyond Update
- Not actually but despite some significant work, no feature changes or bug fixes.

### Code Zen Found
- After far too much thought on the topic, came to the conclusion that Magic Launcher:
a) Solves the problem it set out to do, better than day 1 but still since day 1
b) Mostly has bugs relating to terminal collision which are trivial to work around

- Magic Launcher is therefore promoted to 1.0 as it is ready to solve problems and be composed into toolchains as-is. 
- Roadmap remains unaltered and will continue to be worked on, this is just... an admission that, if the goal was to launch things, it has been achieved.
- It's danger has never been *hidden* weaknesses. And why should a launcher be responsible for system security? So that is not a factor for 1.0

#### Leave Well Enough Alone
- Resisted urge to add another addendum covering why obsession with unexploitable code misses the point that it's the environment that is vulnerable.
- Also resisted adding 69 other features that seemed like good ideas at 3am

#### Hey Kid, Want Some Apps?
- ml-extras-static is not a part of Magic Launcher and never will be. External apps are a black box to it by design.
- But they're pretty nifty. Maybe I'm biased.
- Current count: 15 tools that each do ONE thing with maybe, a token shiny gubbin. Except MLSweeper which really couldn't resist a boss screen. So unhealthy.

#### Either Enlightenment or Intoxication

- Accidentally wrote 11,000 words explaining why simplicity matters
- Created RUP methodology (Repeat Until Predictable) while getting rather WET (Write Everything Twice)
- Proved desktop tools are better microservices than microservices
- Discovered AI prefers numbered menus
- Made ASCII art cool again (was it ever not?)

## 1.0 Contemplations

### What Works Since Day 1
```
Click button → thing launches ✓
No accounts needed ✓
No internet required ✓
No updates forced ✓
No analytics collected ✓
No fucks given about what you launch ✓
```

### What Changed Since Day 1
```
Window can now scale (but doesn't have to)
Better keyboard navigation
Search that actually helps
Documentation that explains why this all matters
A suite of tools proving the philosophy works
The rage of 1000 DevOps engineers channeled into productivity
```
### Known Issues That Won't Be Fixed
```
Still launches rm -rf / if you tell it to
Still doesn't judge your choices
Still refuses to be smart
Still just fucking works
Insistently persistent modals on a "bad" right click
```

### The Stats

Core launcher: ~2000 lines (sorry, not 200)
Average ML tool: 150-400 lines
Total manifesto: ~11,000 words (10,771 as per Focus Writer)
Methodologies created: 1 (RUP)
Paradigm shifts: Several
Subprocess.run() calls: ALL OF THEM

### Special Thanks

To Terraform for showing us how not to do it
To microservices for being distributed monoliths
To modern gaming for forgetting what tools are
To subprocess.run() for never letting us down
And yes, to Anthropic for their *service* which is good enough as a *tool* to *solve problems* - the important parts.

### The Promise, Kept
Magic Launcher 1.0 does what it said on the tin:

Starts instantly ✓
Works everywhere ✓
Never surprises you ✓
Respects your time ✓
Respects your hardware ✓
Just. Fucking. Works. ✓

Magic Launcher 1.0: Because sometimes, done is better than perfect.

## [0.3.5] - 2025-07-31
### Quality of Life
- Set horizontal resolution on launch by creating ~/.config/launcher/mlwidth.txt with the horizontal resolution you want.
- Dynamic window resizing now supported, please hit Ctrl+R to recalculate the grid arrangement

### Bugfix
- Icon_label_place set to fixed so that the box borders remain consistently sized when selecting an icon.

### Tagline
- Have decided my cheeky but not entirely untrue tagline will be: "An OS-free Desktop!"

### UI Alteration
- Allowed vertical resizing of window in Windows. Tiles excellently.
- Subtly extend shortcut label for those long shortcut names

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
- Extend text bar for long shortcut names (DONE - 0.3.5)
- Window and Grid size scaling (DONE - 0.3.5)

### Short Term (Quick Implement)
- Fig Leaf Mode (load blank shortcuts file, basic unencrypted password.txt)
  - Blocks all input to prevent circumvention by hotkey. 
  - Auto lock on password.txt presence, if you want that off delete the file.
  - Add default shortcut to edit password.txt with Unitext
- Only render unique shortcuts in search - if [name/target file/args] match only the first result is shown.
   - This way people can have copies of shortcuts in different folders if there is overlap, e.g. "Favorites" might share multiple shortcuts or you might have a game listed under "GOG" and "Action" folders.
- SIMPLE auto reorder of the current level only (load the level in as a dict, order it by type first, then alphabetical, the re-insert in it's former spot?). Bind to Ctrl+Alt+S.
- Folder level indicator on search results (small roman numeral on top left corner of the shortcut). Mitigate confusion from similarly named results.
    - Should need no metadata, the launcher just needs to quantify how nested the JSON object is
- Auto-open folders in the local file explorer (should be a trivial check of the object type in path, e.g. [[ -f "path" ]] in BASH terms )
- Obscure String shortcut type (creates a hashed copy of the string and sets THAT as the path after user clicks OK)

### Medium Term
- Maintenance Menu via F11
- Point to shortcuts file (--profile I guess)
- Add startup check to confirm it's running from ~/.local/share/Magic-Launcher/
  - If not, migrate install to ~/.local/share/Magic-Launcher/ and use a symbolic or junction link to make it visible in the user's target folder.
- Break keyboard shortcut handling out of main_window.py into it's own ui module
- Portable mode putting .config in the working directory. (Check for empty file "portable", enable by creating the file)
- Custom color schemes
- Better handling of streaming output like tail -f
- "Duplicate to..." function to copy shortcuts to other folders
- Figure out how to move interface construction out of main_window so it can focus on the rendering
- Setup scripts for Linux and Windows not relying on Git clone except maybe the first time.
- Neaten up dependencies and imports for proper packaging.

### Long Term
- Nail Down New User Experience and Default Shortcuts
- Fix Unicode support on Linux workspaces. If the terminal can display it the icon should work.
- Two modes: Admin/Unlocked and Locked/User.
- Password protected shortcuts/folders - can't launch or open without inputting a password.
- Dialogue to assign shortcuts to keys 1-9 (this is why shortcut IDs)
- Default app association customisation by file extension
- Arrangement Editor
- Gamepad/controller support
- Touch screen support (virtual keyboard mostly, mouse actions covered as long as it's multitouch)
- Neaten up widgets
- Create and include default maintenance and some fun stat scripts to set up as shortcuts.
- Standardised deployment package (zip) + Python setup script (install tkinter and Launcher with Python, which is hopefully already installed)
    - I may glob the app into one file as a single script package so it can be deployed via a simple curl piped into python. Closest we want to a package.
    - If it's coded right, it'll still be a megabyte or two at most, and will force better organisational patterns for classes and functions to maintain coherence.

### Super Maybe
- Hidden flag for shortcuts. Prevents showing up in search. Similar to SCID. (Can be done indirectly with hotkeys as they don't use shortcuts.json)
- Import .lnk, .desktop and .shortcut files from system (Shiny, requires per platform logic)
- Full screen (simple output scaling). You can already maximize it and fullscreen focus is frankly, a fucky affair.
- Recent items tracking
- Icon and font scaling
- Select a field for find
- Alternative icon formats (ICO, PNG, JPG) (Unofficially supported already)
- Background Image Loading (Got Pillow already but strictly a nice to have later)
- Super safe mode/ML-Lite. Pure text with lowest denominator font support.
 
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
Once hotkeys are implemented you will have up to 10 "secret" shortcuts.
Search will not check those files and so, deleting it from shortcuts.json makes it effectively hidden.

#### Password Protected Folders
```
Passwords flag might be unwise
```

#### Profiles
```
Just --profile pointing to a path instead of the default shortcuts.json
Maybe 6 lines, few complications.
```

### 1-9 Shortcut Keys
```
Refers to 1.json to 0.json in .config/launcher/hotkeys folder
Each is a direct copy of a shortcut, no weird linking - one to one better than one to many for our purposes
Ctrl+Numkey to assign, doubletap Numkey to run
Keep it Simple, Keep it Safe.
```

### Obscured Strings
```
- A new faux file extension called .mlh (Magic Launcher Hash) will be added to existing extension checks
- If a shortcut path ends in .mlh, it is treated as a string to be de-hashed
- STARTING a path with mlh. hashes the proceeding string, removes the mlh., and adds .mlh to the path
    - Initial thought, subject to examination for complications first, but a basic pre-path check seems a useful way to add flags without building new GUI elements.
```

## What is 1.0?
When several criteria are met:
- Stable, low bugs, passes a code review without too many raised problems.
- No features or design changes left that aren't explicitly post-1.0 (bit flexible but roadmap as of 0.3 is the core planned featureset)
- Packages available on Pypi, apt/snap, yum, apk and chocolatey
- Public Docker image available

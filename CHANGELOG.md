# Changelog

All notable changes to Magic Launcher will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

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

### Short Term
- Drag and drop to reorder shortcuts
- "Duplicate to..." function to copy shortcuts to other folders
- Custom arrangement with reset to auto-arrange option
- Import .desktop files from system
- Export/import shortcut collections

### Medium Term  
- Function key hotkeys (F1-F10)
- Recent items tracking
- Multiple launcher profiles
- Grid size preferences
- Custom color schemes

### Long Term
- Plugin system for extended functionality
- Network launcher (shared shortcuts)
- Gamepad/controller support
- Touch screen support
- Alternative icon formats (ICO, PNG)
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Mixed-System Collections**: Support for `SystemName:GameName` syntax in `.sub` files. This allows a single collection to display and launch games from multiple different systems/emulators while preserving the specified list order.
- **Advanced Sort & Metadata Filtering**:
    - New `nextSort` control to cycle through sorting methods: Title, Year, Players, Manufacturer, Genre, Rating, and Score.
    - New `filterPlayers` control to toggle between All, 1-Player, 2-Player, and 4-Player games.
- **Developer Tools**:
    - `DevTools.bat`: A central menu for developer operations.
    - `build_and_store.ps1`: Automated build script with branch selection, environment validation (GStreamer/CMake), and timestamped build storage.
    - `branch_manager.ps1`: Integrated branch switching and creation tool with automatic work-stashing.

### Changed
- Updated `CMakeLists.txt` to require CMake 3.5+, improving compatibility with modern build environments.

### Fixed
- Fixed division-by-zero guards in various easing functions (`Tween.cpp`).
- Corrected typo in quintic easing function name.

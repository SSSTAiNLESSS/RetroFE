# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RetroFE is a cross-platform frontend for MAME cabinets and game centers. Written in C++ with SDL2 for graphics and libVLC for video playback, it provides an arcade game management and launching system with sophisticated XML-based UI layouts, animations, and metadata management.

**Key Technologies:**
- C++11/14 with CMake build system
- SDL2 (graphics, input, windowing)
- libVLC 3.x (video playback)
- SQLite3 (metadata storage)
- RapidXML (layout parsing)

## Build Commands

### Windows (Visual Studio)

**Prerequisites:**
- Visual Studio 2019 or newer
- CMake
- Python 2.7
- libVLC Development SDK (MSVC **x86 32-bit**)

**libVLC Setup:**

RetroFE now uses libVLC instead of GStreamer for video playback. Download and setup:

1. Download VLC for Windows (32-bit) - **ZIP version**:
   - Direct link: https://mirror.aarnet.edu.au/pub/videolan/vlc/3.0.21/win32/vlc-3.0.21-win32.zip
   - Alternative: https://get.videolan.org/vlc/3.0.21/win32/vlc-3.0.21-win32.zip

2. Extract to `C:\libvlc\`:
   - Download to `C:\libvlc\vlc-3.0.21-win32.zip`
   - Extract to get `C:\libvlc\vlc-3.0.21\`
   - After extraction, you should have:
     - `C:\libvlc\vlc-3.0.21\sdk\include\vlc\vlc.h`
     - `C:\libvlc\vlc-3.0.21\sdk\lib\libvlc.lib`
     - `C:\libvlc\vlc-3.0.21\sdk\lib\libvlccore.lib`
     - `C:\libvlc\vlc-3.0.21\libvlc.dll`
     - `C:\libvlc\vlc-3.0.21\libvlccore.dll`
     - `C:\libvlc\vlc-3.0.21\plugins\` (directory)

**Generate Visual Studio solution:**

```powershell
cmake -A Win32 -B .\RetroFE\Build -D LIBVLC_ROOT=C:\libvlc\vlc-3.0.21 -S .\RetroFE\Source
```

**If extracted to different location:**
```powershell
cmake -A Win32 -B .\RetroFE\Build -D LIBVLC_ROOT=<your_path> -S .\RetroFE\Source
```

**Build in Release mode:**
```powershell
cmake --build RetroFE/Build --config Release --clean-first
```

**Package full environment:**
```powershell
python Scripts\Package.py --os=windows --build=full
```

Output will be in `Artifacts\windows\RetroFE`

**Runtime DLLs:**

Copy these DLLs from `libvlc\` to your RetroFE executable directory:
- `libvlc.dll`
- `libvlccore.dll`
- The `plugins\` directory (entire folder)

### Linux (Ubuntu/Debian)

**Install dependencies:**
```bash
sudo apt-get install git g++ cmake dos2unix zlib1g-dev libsdl2-2.0 libsdl2-mixer-2.0 libsdl2-image-2.0 libsdl2-ttf-2.0 \
  libsdl2-dev libsdl2-mixer-dev libsdl2-image-dev libsdl2-ttf-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev \
  libgstreamer-plugins-good1.0-dev gstreamer1.0-libav zlib1g-dev libglib2.0-0 libglib2.0-dev sqlite3
```

**Generate makefiles:**
```bash
cmake RetroFE/Source -BRetroFE/Build -DVERSION_MAJOR=0 -DVERSION_MINOR=0 -DVERSION_BUILD=0
```

**Build:**
```bash
cmake --build RetroFE/Build
```

**Package:**
```bash
python Scripts/Package.py --os=linux --build=full
```

Output will be in `Artifacts/linux/RetroFE`

### macOS

**Generate makefiles:**
```bash
cmake RetroFE/Source -BRetroFE/Build -DVERSION_MAJOR=0 -DVERSION_MINOR=0 -DVERSION_BUILD=0
```

**Build:**
```bash
cmake --build RetroFE/Build
```

**Package:**
```bash
python Scripts/Package.py --os=mac --build=full
```

Output will be in `Artifacts/mac/RetroFE`

## High-Level Architecture

### Main Application Flow (RetroFE.cpp)

RetroFE operates as a **state machine** with 45+ states handling UI transitions, collection navigation, game launching, and attract mode. The main loop runs at 60+ FPS, processing input events, updating animations, and rendering to potentially multiple displays (arcade cabinet support).

**Lifecycle:**
```
Main.cpp
  → Configuration::initialize() (load all .conf files)
  → RetroFE constructor (create state machine)
  → RetroFE.run()
    → SDL::initialize() (multi-display setup)
    → Load splash page
    → Main loop:
      - Process SDL events
      - Update state machine
      - Page.update(deltaTime) - update animations/components
      - Page.draw() - render to all displays
```

**Key States:**
- `RETROFE_IDLE` - Waiting for user input
- `RETROFE_HIGHLIGHT_MENU_*` - Animating menu transitions
- `RETROFE_LAUNCH_*` - Game launching sequence
- `RETROFE_ATTRACT_*` - Automated demo mode

### Graphics System (Graphics/)

**Component Hierarchy:** All visual elements inherit from `Component` base class:
- `Image` / `ImageBuilder` - Static images
- `Text` - Static text
- `ReloadableText` / `ReloadableScrollingText` - Dynamic text that updates with item selection
- `ScrollingList` - Animated menu lists
- `Video` / `VideoComponent` - GStreamer-based video playback
- `Container` - Groups other components

**Page & Layout System:**
- `PageBuilder` parses `layouts/<layoutName>/layout.xml`
- Constructs tree of Components with positioning (ViewInfo)
- Supports multiple `ScrollingList` menus in hierarchical structure
- Each Page has animation events (onEnter, onExit, onHighlight*, etc.)

**Animation Engine:**
- `Animation` contains sequences of `TweenSet` objects
- Each `TweenSet` has parallel `Tween` objects
- Tweens animate properties: alpha, x, y, width, height, rotation, etc.
- Easing functions: linear, quadratic, cubic, sine, exponential, circular (all with in/out/inOut variants)
- Event-triggered animations: onEnter, onExit, onMenuEnter, onMenuExit, onHighlightEnter, onHighlightExit, onGameEnter, onGameExit, onPlaylistEnter, onPlaylistExit, onAttractEnter, onAttract, onAttractExit

### Collection Management (Collection/)

**CollectionInfo** represents a game category (e.g., "MAME", "Sega Genesis"):
- Contains list of `Item` objects (games or sub-collections)
- Has playlists: "all", "favorites", custom playlists from .pls files
- Links to launcher configuration
- Can have nested subcollections

**Item** represents individual game/menu entry:
- Metadata: name, title, year, manufacturer, developer, genre, rating
- File path to ROM or executable
- `leaf` flag: true=game, false=collection
- Can be marked as favorite

**CollectionInfoBuilder** loads collections by:
1. Reading `collections.conf` for collection definitions
2. Scanning ROM directories or reading list files
3. Loading metadata from MetadataDatabase (SQLite)
4. Parsing menu structure from `menu.txt` files
5. Creating subcollections from `.sub` files

### Input System (Control/)

**UserInput** manages all input devices:
- Keyboards (KeyboardHandler)
- Joystick buttons (JoyButtonHandler)
- Joystick analog sticks (JoyAxisHandler)
- D-pads/hat switches (JoyHatHandler)
- Mouse buttons (MouseButtonHandler)

Maps physical input to 45 logical KeyCodes:
- Navigation: Up, Down, Left, Right, PageUp, PageDown
- Collections: CollectionUp/Down/Left/Right
- Playlists: NextPlaylist, PrevPlaylist, FavPlaylist
- Actions: Select, Back, Quit, Random, Menu
- Jukebox: SkipForward, SkipBackward, Pause, Restart

All handlers read from `controls.conf`.

### Game Launching (Execute/)

**Launcher:**
- Reads launcher configuration from `launchers/<emulator>.conf`
- Performs variable substitution:
  - `%ITEM_NAME%` - Game identifier
  - `%ITEM_FILEPATH%` - Full path to ROM
  - `%COLLECTION_NAME%` - Collection name
  - `%ITEM_DIRECTORY%` - Directory containing ROM
- Launches emulator with appropriate arguments
- Supports LEDBlinky integration for cabinet control

**AttractMode:**
- Automatic demo mode with configurable timeouts
- Cycles through items/playlists/collections
- Triggers attract-specific animations

### Video Playback (Video/)

**IVideo interface** with VLCVideo implementation:
- Background video playback without blocking UI using libVLC
- Converts video frames to SDL_Texture for rendering via lockCallback/unlockCallback
- Volume control, playback state management
- Configurable loop count (0 = infinite)
- Supports seeking: skipForward/skipBackward (10s), skipForwardp/skipBackwardp (5%)
- Pause/restart controls

**VideoComponent** wrapper:
- Manages video lifecycle
- Switches videos based on item selection
- Handles animation events (onEnter/onExit)

### Database & Configuration (Database/)

**Configuration:**
- Hierarchical property tree loaded from `.conf` files
- Global: `settings.conf`
- Per-launcher: `launchers/<name>.conf`
- Per-collection: `collections/<name>/settings.conf`
- Format: `key = value` or `section.subsection.key = value`
- Type support: string, int, bool
- Path resolution: relative paths converted to absolute

**MetadataDatabase:**
- SQLite3 backend in `meta.db`
- Caches game metadata: titles, descriptions, year, ratings, player count
- Can integrate with MAME XML and external APIs

**DB:**
- SQLite3 wrapper for database operations
- Used for settings persistence and favorites tracking

## Critical Implementation Details

### libVLC Requirements

**CRITICAL for Windows:** RetroFE requires **32-bit (x86)** libVLC SDK. The build system looks for libVLC at `C:\libvlc` by default (configurable via `LIBVLC_ROOT` cmake variable). Do not use 64-bit libVLC.

**Video Format Support:** libVLC supports virtually all video formats (mp4, avi, mkv, wmv, flv, etc.) without additional codec installation. The VLCVideo implementation uses RGBA32 format for SDL texture conversion.

### Multi-Display Support

RetroFE supports arcade cabinets with multiple monitors:
- Each display has independent SDL_Window and SDL_Renderer
- Layouts specify per-monitor dimensions
- All screens render synchronously with mutex locking
- Configured in `settings.conf`

### Portability Constraints

**Never use absolute paths** in core engine code:
- All paths must be relative to executable location
- Configurable via `$RETROFE_PATH` environment variable
- Alternative: `.retrofe` flat file in user HOME directory
- Search order: ENV variable → flat file → executable location

### XML Safety

When modifying XML files (layouts or metadata):
- Escape special characters: `&` → `&amp;`, `<` → `&lt;`, `>` → `&gt;`
- **NEVER modify `name` attribute** in `meta/hyperlist/*.xml` - entire infrastructure relies on exact string matches
- Only edit metadata tags: `<story>`, `<description>`, `<year>`, etc.

### Configuration File Structure

RetroFE runtime directory layout:
```
RetroFE/
├── settings.conf (global config)
├── controls.conf (input mappings)
├── launchers/ (per-emulator configs)
│   └── <emulator>.conf
├── collections/ (game data)
│   └── <collection>/
│       ├── roms/ (ROM files)
│       ├── medium_artwork/ (images/videos)
│       │   ├── screenshot/
│       │   ├── logo/
│       │   ├── video/
│       │   └── story/ (per-game text)
│       ├── info.conf (collection metadata)
│       └── settings.conf (collection-specific)
├── layouts/ (UI themes)
│   └── <layoutName>/
│       ├── layout.xml
│       └── splash.xml
├── menu/ (special menu mode)
└── log.txt (runtime log - check for GStreamer errors)
```

## Development Patterns

### Builder Pattern
- `PageBuilder` constructs Page from XML
- `CollectionInfoBuilder` builds collections from filesystem/config
- `ImageBuilder`, `VideoBuilder` create components

### Factory Pattern
- `VideoFactory` creates IVideo implementations
- `SDL` static factory for renderer/window management

### Component Pattern
- All visual elements derive from Component base class
- Containers hold any Component subtype
- Reusable throughout layout hierarchy

### State Machine
- RetroFE main class implements complex state transitions
- AttractMode timer-based state machine
- Component animation state tracking

## Testing & Debugging

**Check log.txt for runtime errors**, especially:
- libVLC initialization failures
- Missing configuration files
- Metadata loading issues
- SDL initialization problems

**Common Issues:**
- libpng warnings about sRGB profile: Use `pngcrush` to fix artwork
- libVLC errors: Verify libVLC DLLs are in executable directory
  - Required: `libvlc.dll`, `libvlccore.dll`, `plugins/` directory
  - Check log for: `[ERROR] [Video] Failed to initialize libVLC`
- Video playback failure: Ensure video files are in correct format and path
- Missing ROMs: Check collection `roms/` directory and list files
- Input not working: Verify `controls.conf` mappings

## Branch Development Workflow

This project uses an atomic branch workflow for feature development:

1. **Branch Creation:** Create new branch from `master` with descriptive name:
   - `feature/<name>` for new features
   - `fix/<name>` for bug fixes

2. **Implementation:** Apply changes within branch

3. **Documentation:**
   - Update `submissions/pull_requests.md` with branch details
   - Update `CHANGELOG.md` with format: `# Changelog: <Branch Name>`
   - Include Added/Changed/Fixed items specific to that branch

4. **Context:** Always confirm which branch you're working on before changes

## Special Project Context

This repository is being used for an automated YouTube content pipeline that leverages RetroFE as a real-time video compositor. The workflow involves:
- Creating curated game collections with metadata
- Using RetroFE to display artwork and gameplay clips
- Managing metadata via Hyperlist XML files
- Generating story text files for narration

When working on content pipeline features, be aware of the `collection_videos/` workflow and the importance of maintaining XML integrity in `meta/hyperlist/` files.

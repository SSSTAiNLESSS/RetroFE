# Submission Guide: RetroFE Pull Requests

This document contains the information needed to submit the Pull Requests for your changes.

## 1. Feature: Reverse Launcher Mapping
**Branch:** `feature/reverse-launcher-mapping`

### How to Submit
1. Push changes:
   ```powershell
   git checkout feature/reverse-launcher-mapping
   git push origin-fork feature/reverse-launcher-mapping
   ```
2. Open PR: [https://github.com/SSSTAiNLESSS/RetroFE/pull/new/feature/reverse-launcher-mapping](https://github.com/SSSTAiNLESSS/RetroFE/pull/new/feature/reverse-launcher-mapping)

### PR Description
**Title:** `Feat: Add reverse launcher mapping via <Launcher>.conf lookup`
**Body:**
```markdown
## Feature: Reverse Launcher Mapping

This PR adds support for defining launcher overrides by listing games inside a `<Launcher>.conf` file within a collection's launcher directory, rather than requiring individual `<Game>.conf` files for every game.

### Changes
- Added `resolveLauncherName` to the `Launcher` class to handle priority-based lookup.
- The logic now follows this priority:
  1. Specific Override: `collections/<Col>/launchers/<Game>.conf`
  2. Reverse Mapping: Scans `collections/<Col>/launchers/*.conf` for the game name (one per line).
  3. Default: Uses the collection's default launcher.
```

---

## 2. Fix: Tween Easing Bugs
**Branch:** `fix/tween-easing-bugs`

### How to Submit
1. Push changes:
   ```powershell
   git checkout fix/tween-easing-bugs
   git push origin-fork fix/tween-easing-bugs
   ```
2. Open PR: [https://github.com/SSSTAiNLESSS/RetroFE/pull/new/fix/tween-easing-bugs](https://github.com/SSSTAiNLESSS/RetroFE/pull/new/fix/tween-easing-bugs)

### PR Description
**Title:** `Fix: Correct typo in quintic easing and add div-by-zero guards`
**Body:**
```markdown
## Fix: Tween Easing Bugs

This PR fixes a typo in the easing function map and adds safety guards for division by zero in easing calculations.

### Changes
- **Typo Fix:** Corrected `easeonoutquintic` to `easeinoutquintic` in `Tween.cpp`. Added an alias for the typo to maintain backward compatibility.
- **Safety Guards:** Added `if (d == 0) return b;` checks to Sine, Exponential, and Circular easing functions to prevent division by zero when duration is 0.
```

---

## 3. Feature: Playlist Menu Wheel
**Branch:** `feature/playlist-menu-wheel`

### How to Submit
1. Push changes:
   ```powershell
   git checkout feature/playlist-menu-wheel
   git push origin-fork feature/playlist-menu-wheel
   ```
2. Open PR: [https://github.com/SSSTAiNLESSS/RetroFE/pull/new/feature/playlist-menu-wheel](https://github.com/SSSTAiNLESSS/RetroFE/pull/new/feature/playlist-menu-wheel)

### PR Description
**Title:** `Feat: Add playlist menu wheel support`
**Body:**
```markdown
## Feature: Playlist Menu Wheel

This PR introduces a new menu mode that allows users to navigate playlists via a dedicated menu wheel (e.g., logos or text) on the same page as the game list.

### Changes
- Added `mode="playlist"` support to the `<menu>` tag in `layout.xml`.
- Implemented real-time synchronization between the playlist menu and the game menu.
- Added input routing to allow simultaneous control of both wheels.
```

---

## 4. Feature: Advanced Sort and Metadata Filtering
**Branch:** `feature/sort-and-filter`

### How to Submit
1. Push changes:
   ```powershell
   git checkout feature/sort-and-filter
   git push origin-fork feature/sort-and-filter
   ```
2. Open PR: [https://github.com/SSSTAiNLESSS/RetroFE/pull/new/feature/sort-and-filter](https://github.com/SSSTAiNLESSS/RetroFE/pull/new/feature/sort-and-filter)

### PR Description
**Title:** `Feat: Add dynamic sorting (Year, Genre, etc.) and Player filtering`
**Body:**
```markdown
## Feature: Advanced Sort and Metadata Filtering

This PR enables users to utilize XML metadata for dynamic sorting and filtering of game collections directly within the frontend.

### Changes
- **Dynamic Sorting:** Implemented `cycleSort()` to switch between Title, Year, Players, Manufacturer, Genre, Rating, and Score.
- **Player Filtering:** Added `togglePlayerFilter()` to cycle through All, 1P, 2P, and 4P games.
- **Input Mapping:** Added `nextSort` and `filterPlayers` keys to `controls.conf` and `UserInput` mapping.
- **State Management:** Added state transitions in the core engine to refresh the UI smoothly when sorting or filtering changes.
```

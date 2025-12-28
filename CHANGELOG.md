# Changelog: Feature/Playlist-Menu-Wheel

This branch implements a new visual mode for navigating playlists directly on the game selection screen.

## [feature/playlist-menu-wheel]

### Added
- **Playlist Menu Mode**: Added support for `mode="playlist"` in `layout.xml` `<menu>` tags. This allows skinners to create a dedicated wheel or list for playlists (e.g., Favorites, Last Played, All Games) that sits alongside the game wheel.
- **Synchronized Navigation**: Implemented logic to ensure the playlist wheel updates in real-time as the user switches playlists.
- **Input Routing**: Added new input controls to allow navigating the playlist wheel independently or simultaneously with the game wheel.

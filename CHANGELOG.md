# Changelog: Feature/Sort-And-Filter

This branch adds advanced, on-the-fly sorting and filtering capabilities to RetroFE, allowing users to organize and view their game lists based on rich metadata from their HyperList XML files.

## [feature/sort-and-filter]

### Added
- **Dynamic List Sorting**: Implemented a `nextSort` control that cycles the current game list's sort order through the following metadata fields:
  - Title (Default)
  - Year
  - Number of Players
  - Manufacturer
  - Genre
  - Rating
  - Score
- **Player Count Filtering**: Implemented a `filterPlayers` control that cycles through filters to show games for:
  - All Players (Default)
  - 1 Player
  - 2 Players
  - 4 Players
- **New Input Mappings**: Added `nextSort` and `filterPlayers` to `controls.conf` to be mapped to keyboard or joystick inputs.
- **UI State Transitions**: The frontend now uses a smooth exit/enter animation when the list is sorted or filtered to provide clear visual feedback.
- **Filter State Management**: The filter logic correctly backs up and restores the full game list, ensuring no items are permanently lost from view when a filter is cleared.

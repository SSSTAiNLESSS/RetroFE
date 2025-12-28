# Changelog: Feature/Reverse-Launcher-Mapping

This branch introduces a more flexible way to assign launchers to games, reducing the need for individual configuration files for every single game.

## [feature/reverse-launcher-mapping]

### Added
- **Reverse Launcher Mapping**: The launcher resolution logic has been enhanced. Instead of only checking for a `<GameName>.conf` file, RetroFE now performs a "reverse lookup".
- **New Lookup Priority**:
  1.  **Game-Specific Override**: `collections/<Collection>/launchers/<GameName>.conf` (Highest priority, as before).
  2.  **Reverse Mapping (New)**: If the above is not found, RetroFE will now scan all `.conf` files inside `collections/<Collection>/launchers/` (e.g., `MAME_Games.conf`, `Special_Launch.conf`). If it finds a line inside one of these files that exactly matches the game's name, it will use the launcher defined in that file.
  3.  **Collection Default**: If neither of the above is found, it falls back to the default launcher specified in the collection's `settings.conf`.

### Use Case
This allows users to group multiple games that share a specific launcher configuration into a single `.conf` file, dramatically simplifying management for large collections with multiple emulators or launch options. For example, `MAME_CHD_Games.conf` could list all CHD-based games that require a special MAME configuration.

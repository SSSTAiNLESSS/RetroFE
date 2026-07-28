# Changelog: Feature/Settings-Reboot-Restore

This branch makes on-screen settings menus usable in sequence. Launchers can carry an
undocumented `reboot = yes` property that restarts RetroFE so a settings change takes effect;
until now that restart also dropped the user back at the first collection, so changing several
settings in a row meant navigating back into the menu each time. RetroFE now records the route
taken, walks it back on the next start, and skips the intro while doing so.

## [feature/settings-reboot-restore]

### Added
- **`restoreStateOnReboot` setting** (`settings.conf`, default `no`): after a launcher with
  `reboot = yes` restarts RetroFE, return to the menu the user was in rather than the first
  collection. Shipped builds are unaffected until the key is added.
- **Navigation route tracking**: new `collectionPath_` records the ordered list of collections
  from the root down to the current position. Pushed in `RETROFE_NEXT_PAGE_MENU_EXIT` and
  `RETROFE_MENUMODE_START_REQUEST`, popped in `RETROFE_BACK_MENU_EXIT` and both
  `RETROFE_COLLECTION_*_EXIT` states, so pushes and pops stay balanced across every navigation
  path.
- **Route persistence**: `saveRestoreState()` writes `restorePath`, `restoreOffsets` and
  `restorePlaylists` into `settings_saved.conf`, pipe-separated and index-aligned. Called only
  from the reboot branch of `RETROFE_LAUNCH_REQUEST`, so an ordinary game launch leaves no route
  behind.
- **Route replay**: `loadRestoreState()` parses and consumes the keys at `RETROFE_NEW`, seeding
  the existing `lastMenuOffsets_` / `lastMenuPlaylists_` maps so `rememberMenu` restores the
  position within each tier. `restoreNextTier()` then drains one tier per `RETROFE_IDLE`.
- **Intro skip on restore**: a queued route sets `exitSplashMode` at startup — the same flag
  pressing select during the splash sets — dropping the minimum show time and the wait for the
  intro video. Measured on the test rig: **13 s to under 2 s**. Initialization itself still has
  to complete.
- **Documentation**: `docs/RetroFE/Settings-Menu-Reboot-Restore.md`, which is also the first
  written record of `reboot = yes` itself — that property has existed for years and is
  undocumented upstream. `restoreStateOnReboot` added to the shipped `settings.conf` template and
  `reboot` referenced in the `launchers/Main.conf` template.

### Design notes
- **The route is replayed through the real navigation states, never jumped to.** A component only
  changes state when an event fires *and* it has a matching animation block at its current
  `menuIndex`, so a page's appearance is the accumulated result of the whole descent rather than
  a function of its final depth. Jumping to the target depth would leave everything made visible
  at a shallower tier at its authored alpha — the same black-screen failure that ended the
  page-rebuild approach in the layout hot-reload work.
- **The saved root is ignored.** Startup always uses whatever `firstCollection` currently says, so
  editing that setting can never strand the user somewhere unexpected.
- **The keys are consumed on load**, making the restore strictly one-shot; an ordinary start never
  teleports the user into a settings menu.

### Failure behaviour
- A missing tier — a settings script renamed or removed a collection since the route was saved —
  stops the restore at the last tier that resolved and logs the reason. Landing one tier short is
  recoverable; a crash or blank screen is not.
- Collection and playlist names containing `|` or `#` are refused with a logged reason. `|`
  separates the fields and `#` opens a comment in the config parser.
- Warns when `restoreStateOnReboot` is set but `rememberMenu` is not, since the item-level
  position depends on it. Silent degradation there would read as a bug rather than a setting.

### Tooling added on this branch
Not part of the feature, but carried here and inherited by the CORE baseline:
- **`feature-done` skill** (`.claude/skills/feature-done/`) and
  **`Scripts/check_branch_ready.ps1`**: mechanical definition-of-done checks — per-branch
  `CHANGELOG.md`, shipped `settings.conf` template, `docs/` tracking registration, `HANDOVER.md`,
  push state, and whether the git procedure doc on the baseline is current. Added after a
  convention was missed on this branch and had to be caught by STAiNLESS.
- **`.gitignore` narrowed** from `.claude/` to `.claude/*` + `!.claude/skills/`, so skills are
  committed and survive a fresh clone while `settings.local.json` and caches stay out. This also
  surfaced `layout-lint` and `layout-new`, two RetroFE skills that existed only on disk and were
  never tracked.

### Notes for future work
- **Config files must not carry a UTF-8 BOM.** A BOM binds to the first key name, so `restorePath`
  parses as `﻿restorePath` and never matches. This applies to every RetroFE config file via
  `Configuration::parseLine` — unlike `.sub` file parsing, which strips BOMs explicitly.
- **`settings_saved.conf` is imported before `settings.conf`** and `Configuration` uses
  `map::insert`, which does not overwrite. Anything left in that file outranks the user's
  `settings.conf` permanently, which is why the writer preserves every line it does not own.

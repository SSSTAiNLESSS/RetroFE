# Settings menus: `reboot` and `restoreStateOnReboot`

How an on-screen settings menu applies a change and puts you back where you were.

Covers two launcher/settings properties:

| Property | Where | Status |
|---|---|---|
| `reboot = yes` | a launcher `.conf` | Pre-existing, and **undocumented upstream** until this file |
| `restoreStateOnReboot = yes` | `settings.conf` | Added 2026-07-28 on `feature/settings-reboot-restore` |

---

## 1. The problem

A settings menu in RetroFE is an ordinary collection whose "games" are scripts. Selecting
one runs the script through a launcher. The scripts typically rewrite `layout.xml` — commenting
whole component blocks in or out, or swapping an art `type` such as `bezel_night` → `bezel_day` —
and rename artwork files.

RetroFE reads all of that **at startup**, so the change does not show until it restarts. That is
what `reboot = yes` is for.

The cost is that a restart drops you back at the first collection. Changing five settings meant
navigating back into the settings menu five times.

## 2. `reboot = yes` — the existing mechanism

Put it in a launcher `.conf` alongside `executable` and `arguments`:

```conf
executable = settings\BEZELS\cmd.exe
arguments  = /C "%ITEM_FILEPATH%"
reboot     = yes
```

`Launcher::run()` returns this flag, `RetroFE::run()` returns it to `main()`, and `Main.cpp`
loops: `config.clearProperties()`, re-import every config file, construct a fresh `RetroFE`. It
is a genuine full restart — every `.conf`, every collection and every layout is re-read.

**It is per launcher, not per item.** A settings collection whose entries need different
behaviour should use the per-item launcher override: a file at
`collections/<COLLECTION>/launchers/<ITEM NAME>.conf` containing just a launcher name redirects
that one item (`Launcher.cpp:48-57`). Use it to stop items that change nothing inside RetroFE —
an emulator shader toggle, for instance — from rebooting at all.

## 3. `restoreStateOnReboot = yes` — returning to your place

In `settings.conf`:

```conf
restoreStateOnReboot = yes
```

Default is **no**, so existing installs are unaffected until it is added.

On a `reboot = yes` launch, RetroFE records the route you took — the ordered list of collections
from the root down to where you were standing — plus each tier's scroll position and playlist,
into `settings_saved.conf`. On the next start it walks that route back.

It also **skips the intro video wait**. A queued route means you are waiting to get back to a
menu, so the splash is dismissed as soon as initialization finishes rather than playing out.
Measured on the test rig: **13 s → under 2 s**. Initialization itself still has to complete; only
the waiting is skipped.

### Companion setting

`rememberMenu = yes` is required to restore the **selected item** within each collection.
Without it the route is still replayed but you land on the collection's default entry. RetroFE
logs a warning if `restoreStateOnReboot` is on and `rememberMenu` is off, rather than degrading
silently.

### What it writes

```conf
restorePath      = Main|SETTINGS TITAN
restoreOffsets   = 12|4
restorePlaylists = all|all
```

Pipe-separated and index-aligned. The keys are **consumed on load** — stripped from the file — so
the restore is strictly one-shot and an ordinary start never teleports you.

`settings_saved.conf` is imported *before* `settings.conf`, and `Configuration` uses
`map::insert`, which does not overwrite. Anything left in that file therefore outranks
`settings.conf` permanently, which is why the writer preserves every line it does not own rather
than rewriting the file wholesale.

## 4. Why the route is replayed rather than jumped to

This is the load-bearing design decision.

`Component::update()` only changes a component's state when an event fires **and** that component
has a matching animation block at its current `menuIndex`; otherwise the request is silently
dropped and the component keeps its existing state. A page's appearance is therefore the
*accumulated* result of the whole navigation, not a function of its final depth.

Jumping straight to the target depth leaves everything that was made visible at a shallower tier
sitting at its authored alpha — black for most themes — and it gets worse the deeper you go. That
is the exact failure that killed the page-rebuild approach during the layout hot-reload work
(`Layout-Hot-Reload-Blueprint.md`, and `HANDOVER.md` §1).

Replaying the real navigation states makes the restored page correct by construction, because it
genuinely is the same journey.

## 5. Limits and failure behaviour

- **A missing tier stops the restore.** If a settings script renamed or removed a collection since
  the route was saved, RetroFE stops at the last tier that resolved and logs
  `Restore stopped: "<name>" not found in <collection>`. Landing one tier short is recoverable; a
  crash or blank screen is not.
- **The saved root is ignored.** The run always starts at whatever `firstCollection` currently
  says, so editing that setting can never strand you somewhere unexpected.
- **Collection and playlist names containing `|` or `#` are refused**, with a logged reason. `|`
  separates the fields and `#` opens a comment in the config parser (`Utils::filterComments`), so
  either would read back as a different route.
- **Config files must not carry a UTF-8 BOM.** A BOM binds to the first key name, so
  `restorePath` parses as `﻿restorePath` and is never matched. This applies to every RetroFE
  config file, not just this one — it is a property of `Configuration::parseLine`. Save as UTF-8
  without BOM, or plain ASCII.

## 6. Implementation map

All in `RetroFE/Source/RetroFE.cpp` / `.h`:

| Piece | Role |
|---|---|
| `collectionPath_` | Ordered route from root to current position. Pushed in `RETROFE_NEXT_PAGE_MENU_EXIT` and `RETROFE_MENUMODE_START_REQUEST`, popped in `RETROFE_BACK_MENU_EXIT` and both `RETROFE_COLLECTION_*_EXIT` states. |
| `saveRestoreState()` | Serialises the route. Called only from the reboot branch of `RETROFE_LAUNCH_REQUEST`, so ordinary game launches leave no route behind. |
| `loadRestoreState()` | Parses and consumes the keys at `RETROFE_NEW`; seeds `lastMenuOffsets_` / `lastMenuPlaylists_`; queues `pendingRestore_`. |
| `restoreNextTier()` | Drains one tier per `RETROFE_IDLE`. Every tier passes through idle, so one hook covers the whole descent. |
| `hasPendingRestore()` | Non-consuming check, used to skip the splash wait. |
| `writeSavedSettings()` | Shared rewrite helper preserving unowned lines. |

# Blueprint — Slice 1: `layout.xml` Hot-Reload

**Branch:** `feature/layout-hot-reload` (off `feature/data-modernization` @ `ecea8ab`)
**Date:** 2026-07-23
**Status:** blueprint — no code written, awaiting go

Foundation for a visual theme editor. Every fact below was measured against the repo
and against 228 real theme `layout.xml` files, not assumed.

---

## 1. What the survey of real themes established

228 `layout.xml` files across the 10 reference themes (Theta, Refried, ReCORE,
Ergo Proxy, 1MiLLiON, Banner, Back2Basics, Theme_Pack ×7, Aeon Nox).
Sizes run **13 KB – 91 KB** — ordinary files, not the 676 KB TITAN outlier.

### 1.1 ⚠️ Real themes are not well-formed XML — and the engine does not care

**141 of 228 files (62%) are rejected by a strict XML parser.** They are not corrupt;
they work fine in RetroFE. The reason is exact and verifiable:

`PageBuilder.cpp:137` calls `doc.parse<0>(...)`. Flag `0` means
`rapidxml::parse_validate_closing_tags` (`0x200`) is **not** set. At
`rapidxml.hpp:2193` the parser therefore takes the `else` branch and **skips the
closing-tag name without comparing it**.

So this — real, from `Theta/collections/2 SONY/layout/layout.xml:88..99` — is
accepted by RetroFE and parsed as a `text` node:

```xml
<text value="|" x="960" ...>
  ...
</reloadableText>
```

**1558 mismatched closing tags across 80 files.** This is the single most important
constraint on the whole project, and it is *not* a TITAN quirk — it is engine-wide.

**Consequence: any theme editor must parse with RetroFE's own rapidxml `parse<0>`
semantics.** An editor built on a strict XML library would refuse to open 62% of
existing themes, and a parse-and-serialize round-trip would silently rewrite the
document's structure. This is the same conclusion the TITAN analysis reached, arrived
at independently — it strongly reinforces *make RetroFE itself the editing surface*.

### 1.2 Silently-dead configuration is widespread

`first_attribute()` defaults to `case_sensitive = true` (`rapidxml.hpp:1025`), so
mis-cased **attribute names** are read as absent and silently ignored:

| Dead in the wild | Occurrences | Correct form |
|---|---|---|
| `MenuIndex` | 36 | `menuIndex` |
| `Height` / `Width` | 173 | `height` / `width` |
| `maxheight` | 29 | `maxHeight` |

Mis-typed **element names** are ignored too: `Reloadableimage` (21),
`onMenutEnter`/`onMenutExit` (24), `onJumpExit` (27).

Attribute **values** behave differently: `Tween::getTweenType` lowercases the input
and falls back to `linear` for anything unrecognised (`Tween.cpp:77-115`), so
`easeInquadratic` (198 uses) works — but a typo'd algorithm silently becomes linear.

**This is a feature opportunity, not just trivia.** A theme editor that surfaces
"this attribute is being ignored" would fix bugs that have shipped in public themes
for years. It is the clearest early win over hand-editing XML.

### 1.3 The schema the editor must round-trip

35 distinct element names, of which 31 are real (4 are typos). Structure:

```
layout
├── image | video | text | container            (static components)
├── reloadableImage | reloadableVideo
│   | reloadableText | reloadableScrollingText  (data-bound components)
├── menu › itemDefaults, item                   (the scrolling list)
├── sound
└── <any component> › on<Event> › set › animate (animation tree)
```

**Events observed** (17): `onEnter`, `onExit`, `onIdle`, `onMenuEnter`, `onMenuExit`,
`onMenuIdle`, `onMenuScroll`, `onMenuJumpEnter`, `onMenuJumpExit`, `onHighlightEnter`,
`onHighlightExit`, `onPlaylistEnter`, `onPlaylistExit`, `onGameEnter`, `onGameExit`,
`onAttractExit`, (+`onJumpExit` — typo, dead).

**Animation is the bulk of a theme by volume:** 43 891 `animate` nodes vs 2133 `image`
nodes. `animate` carries only `type`/`to`/`from`/`algorithm`; `set` carries `duration`.
79 distinct tween `type` values, top being `alpha` (26 619), `xOffset` (5787), `y` (3358),
`nop` (2206). Only 7 distinct `algorithm` values are used in practice, dominated by
`easeinquadratic` (15 978) and `linear` (2322).

**Design implication:** a property inspector alone is near-useless here — the thing
authors actually spend their time on is the animation tree. Slice 2's editor should
prioritise event/tween editing, not X/Y nudging.

### 1.4 One page is built from many files

`PageBuilder::buildPage()` loops over monitors (`PageBuilder.cpp:100-130`) and for each
tries an aspect-specific name first, then a plain one:

```
<layoutPath>/<page> <W>x<H> - <N>.xml   →  preferred
<layoutPath>/<page> - <N>.xml           →  fallback
```

So the watcher must track a **set** of candidate paths per page, not one file — and
must also watch paths that *don't exist yet*, since creating `layout 16x9.xml` changes
which file wins.

---

## 2. Slice 1 design

### 2.1 Scope

Watch the resolved layout file set → on change, rebuild the page → swap it in →
restore where the user was. Gated off by default. **No editor UI in this slice.**

### 2.2 Decisions and reasons

| Decision | Reason |
|---|---|
| **Poll mtime + size, 250 ms**, not a native file-watcher API | Minimization ladder: zero new dependencies, identical on Win/Linux/Mac. `ReadDirectoryChangesW`/`inotify` would need two implementations and buy nothing at this scale (≤ a few dozen paths). |
| **Debounce: require the stat to be stable across 2 consecutive polls** | Editors write partial files. Rebuilding mid-save is the #1 source of spurious failures. Costs 250 ms of latency; worth it. |
| **Build the new page fully, and only swap if it succeeds** | Malformed XML must never take the process down or blank the screen. On failure: log, keep the current page, keep watching. This is the safety property that makes hot-reload usable at all. |
| **Gate behind `layoutHotReload` in `settings.conf`, default `false`** | Shipped CORE builds are bit-identical in behaviour. Read via the existing `config_.getProperty(key, bool&)` overload (`Configuration.h:36`) — no new config machinery. |
| **Capture/restore selection state around the swap** | Losing your place on every keystroke-save makes the feature worthless in practice. |

### 2.3 State to preserve across a swap

Captured before teardown, reapplied after the new page starts:

- current collection name
- selected item index within the active menu
- menu stack depth / active menu index
- current playlist

If the new layout can't honour a value (e.g. menu is shorter), clamp rather than fail.

### 2.4 The risk that needs proving first

**Teardown safety.** `buildPage()` allocates SDL textures, font-cache entries, and
libVLC video handles. Destroying a live `Page` while a video is decoding is the most
likely crash in this design, and it is *not* something the existing code has ever had
to do — pages are currently only destroyed at state transitions the state machine
controls.

**Therefore step 1 is a spike, not the feature:** force a page rebuild on a keypress
and confirm clean teardown with video playing. If that is not clean, the whole slice
changes shape and it is better to know on day one.

### 2.5 Implementation order

1. **Spike** — manual rebuild on a hotkey; prove teardown is clean with video running.
2. `LayoutWatcher` — small class: resolve candidate paths, poll, debounce, report change.
3. Wire into the main loop behind `layoutHotReload`.
4. Build-then-swap with state capture/restore.
5. Failure path — malformed XML keeps the last good page; verify by saving a broken file.

Each step ends with something demonstrable. Steps 1 and 5 are the ones that actually
prove the design.

### 2.6 What is explicitly NOT in this slice

Editor overlay, bounding boxes, drag/resize, property HUD, any XML *writing*, the
lint/dead-attribute warnings from §1.2. Those are slices 2+. Writing XML is the point
at which §1.1 becomes dangerous, and nothing in slice 1 writes anything.

---

## 3. How to test slice 1 when it lands

1. Build; set `layoutHotReload=true` in `settings.conf`.
2. Launch RetroFE on a theme with video (Theta or Ergo Proxy).
3. Scroll a few items in, so selection state is non-default.
4. Edit the theme's `layout.xml` — change an `alpha` or an `x` — and save.

**Success:** the change appears within ~0.5 s, the same item is still selected, video
still plays, no flicker, no crash.

**Then break it deliberately:** save a file with an unclosed `<image`. Success is that
RetroFE logs the error and *keeps running on the last good layout*.

Finally set `layoutHotReload=false` and confirm behaviour is identical to a build
without the feature.

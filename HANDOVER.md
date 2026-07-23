# HANDOVER

Session checkpoint for a fresh context window. Read this first, then `CLAUDE.md`.

**Last updated:** 2026-07-23
**Branch at handover:** `feature/layout-hot-reload` (cut this session from
`feature/data-modernization` @ `ecea8ab`)

---

## 1. Where things stand

### Just completed this session

Cut **`feature/layout-hot-reload`** off `feature/data-modernization` (`ecea8ab`) and
produced the blueprint for slice 1. **No engine code written yet** — by design.

Surveyed all **228 `layout.xml` files** across the ten reference themes (Theta, Refried,
ReCORE, Ergo Proxy, 1MiLLiON, Banner, Back2Basics, Theme_Pack ×7, Aeon Nox). Findings are
written up in **`docs/RetroFE/Layout-Hot-Reload-Blueprint.md`** — read that before resuming;
the headlines are in §4 below.

TITAN is **out of scope** for the theme-editor work (user's call this session). It turned
out not to matter: the constraint TITAN was thought to impose is present in ordinary
community themes anyway, and much more strongly (§4).

### Previously (prior session) — VLC fixes, still current

Ported the two VLC fixes from `feature/data-modernization` back onto the VLC branch and
pushed them. `feature/vlc-replacement` went `2e1ddb4` → `06de5ed`, local and origin in sync:

| Commit | What |
|---|---|
| `31bbc65` | Fix CMake to find VLC SDK in `lib/msvc` (cherry-pick of `2acf7b6`) |
| `641daf7` | Fix VLC videos not looping — play once then freeze (cherry-pick of `76e344d`) |
| `06de5ed` | Bump `cmake_minimum_required` 2.8 → 3.5 |

Both cherry-picks applied without conflict. Verified before pushing: full clean Release
build succeeded, and CMake resolved libVLC from the `lib/msvc` path the first commit adds.

Deliberately **not** carried across: the unrelated mixed-collections work sitting between
those commits on `data-modernization` (`1d4dc9f`, `7866e0e`, `4279a70`, `a81beb4`, `d6d7bdd`,
merge `c4cf1b2`) and the roadmap/gitignore commits (`92baa40`, `2a90884`).

### Next single action

**Run the teardown spike.** Add a temporary hotkey that forces a page rebuild
(`RetroFE::loadPage()` → swap `currentPage_`) and confirm teardown is clean **with a video
playing**. Nothing else. This is step 1 of §2.5 in the blueprint.

Why this and not the watcher: `buildPage()` allocates SDL textures, font-cache entries and
libVLC handles, and destroying a live `Page` mid-decode is something the engine has never had
to do — pages are currently only torn down at state transitions the state machine controls.
If teardown isn't clean the whole slice changes shape, so this is the cheapest way to find out.

Blueprint is written and awaiting an explicit go; the user had not yet said go at handoff.

---

## 2. Open items to deal with early

1. ~~**The GitHub repo was renamed and `origin` is stale.**~~ **Done 2026-07-23.** `origin`
   re-pointed to `RetroFE-CORE`, and `upstream` added. See §7 for the full remote topology
   and the blocking finding it uncovered.

2. ~~**Untracked files on `feature/data-modernization`**~~ **Mostly resolved 2026-07-23.**
   `RustCore/` + both metadata headers are now committed (`ecea8ab`); `RustCore/target/`
   is gitignored (`cb9616f`); `=2.31.0` and `nul` deleted — both were shell-redirect debris,
   **not** a build number. Detail in §8.

   **Partially resolved 2026-07-23 (this session).** A shape was chosen and applied:
   *engine design docs are tracked; reference material and agent tooling are not.* So
   `docs/RetroFE/Layout-Hot-Reload-Blueprint.md` is committed while the rest of `docs/`
   is not. `docs/` is therefore **partially tracked** — deliberate, not an oversight.

   Still untracked, still undecided: the remaining **`docs/`** (1.7 MB, incl. two PDFs, a
   226 KB HTML and a 72 KB PNG), **`.mcp.json`**, **`Scripts/mcp-servers/`** (45 KB).
   `.gitignore` already excludes `.claude/` and `CLAUDE.md`, so convention says agent tooling
   stays out. Given the repo is already ~1.2 GB from committed binaries (§7), **do not
   `git add -A` here** — it sweeps all of it in. Stage selectively.

3. **`CLAUDE.md` is stale on video backend.** It lists "Replace VLC with **libmpv**" under
   the modernization mission, but GStreamer → **libVLC** already shipped and is what CORE
   runs today. `CHANGELOG_MODERNIZATION.md` correctly files libmpv as Phase 4 (future).
   Reword the mission bullet so it stops reading as pending work.

---

## 3. Build — verified working commands

Toolchain actually present: **CMake 4.3.2**, **Visual Studio 18 2026**, **MSVC 19.50**,
target **Win32 (32-bit)**. VLC SDK vendored at `tools/vlc-sdk` (gitignored, `lib/msvc` layout).

```powershell
# from repo root
cd RetroFE\Build
cmake -A Win32 -D LIBVLC_ROOT="J:\Documents\github\RetroFE\tools\vlc-sdk" -S ..\Source
cmake --build . --config Release --clean-first
# -> RetroFE\Build\Release\retrofe.exe
```

**Gotcha:** `Scripts\build_and_store.ps1` uses `Read-Host` for branch selection, so it
**cannot be run from an agent shell** (stdin is the null device). Use the raw cmake commands
above, or run the script yourself in a real terminal. The script also passes
`-DCMAKE_POLICY_VERSION_MINIMUM=3.5`; after commit `06de5ed` that flag is no longer needed
on the VLC branch (configure was tested without it).

### How this repo reaches the CORE Type R build

Confirmed by hash, not assumed:

```
M:\CORE - TYPE R\core\retrofe.exe
  SHA256 51DF46285DC24C0B39CEADB46530F39CB697DE0474ADF6B612FFF0B46A8A2E21
  == Builds\2026-07-22_08-33-30_feature-data-modernization\retrofe.exe
```

So the live CORE Type R arcade build is already running this fork's binary, built from
`feature/data-modernization`. Pipeline is: build here → copy `retrofe.exe` into `core\`.
Any engine change ships to CORE the moment that copy happens — and must then be registered
for the next free release via the `update-package` skill in the CORE repo.

The `M:\CORE - TYPE R` git repo is scoped to `.claude` tooling only, **not** the build
itself. Engine code belongs here; only the built exe (plus any new `settings.conf` key)
crosses over.

---

## 4. Layout hot-reload → visual theme editor

> **Full blueprint: `docs/RetroFE/Layout-Hot-Reload-Blueprint.md`** (written 2026-07-23,
> tracked in git). This section is the summary; that file is the detail and the test plan.

### Why

Prompted by LaunchBox's *COMMUNITY Theme Creator* — a WPF app that visually edits BigBox
themes. It's tractable for them because BigBox themes **are** WPF/XAML and the editor **is**
a WPF app, so its canvas is literally the renderer BigBox uses. WYSIWYG comes nearly free.

RetroFE has no such luxury: `layout.xml` is a bespoke schema rendered by RetroFE's own
C++/SDL2 renderer. An external WYSIWYG editor would have to **reimplement that renderer**,
and every divergence becomes a lie on screen. **Do not take that path.**

### Chosen direction

Make RetroFE itself the editing surface, in three slices:

1. **Hot-reload `layout.xml`** ← start here, highest value per unit of work
2. **`--edit` overlay** — bounding boxes, component ids/layers, click-select, drag/resize,
   nudge, property HUD. Pixel-perfect by construction because it *is* the renderer.
3. *(optional)* External panel app for ergonomics (property inspector, asset browser, undo,
   tween timeline) that writes `layout.xml` while RetroFE hot-reloads as ground truth.
   Dual-screen setup already makes this natural. The panel must never pretend to render.

### Slice 1 scope

Watch `layout.xml` → on change call `PageBuilder::buildPage()` → swap `currentPage_` →
restore current collection and selected index so you don't lose your place.
Gate behind a `settings.conf` key, default off, so shipped CORE builds are untouched.

### ⚠️ The decisive finding — measured 2026-07-23, do not re-derive

**141 of 228 real theme `layout.xml` files (62%) are rejected by a strict XML parser, and
RetroFE does not care.** Mechanism verified in source, not inferred:
`PageBuilder.cpp:137` calls `doc.parse<0>()`, so `parse_validate_closing_tags` (`0x200`) is
unset and `rapidxml.hpp:2193` **skips closing-tag names without comparing them**. Hence
`<text ...>` closed by `</reloadableText>` parses fine as a `text` node —
**1558 such mismatches across 80 files**, e.g. `Theta/collections/2 SONY/layout/layout.xml:88`.

**Consequence:** a theme editor must parse using RetroFE's own rapidxml `parse<0>` semantics.
A strict XML library would refuse 62% of existing themes, and a parse-and-serialize round-trip
would silently rewrite documents. This independently reproduces the TITAN conclusion from
ordinary community themes, so it is an **engine-wide** property — the strongest argument for
*make RetroFE itself the editing surface*.

**Related, and an early feature win:** attribute *names* are case-sensitive
(`rapidxml.hpp:1025`, `case_sensitive = true`), so mis-cased ones are silently dead —
`MenuIndex` ×36, `Height`/`Width` ×173, `maxheight` ×29, plus typo'd elements
`Reloadableimage` ×21, `onMenutEnter`/`onMenutExit` ×24. Attribute *values* differ:
`Tween::getTweenType` lowercases and falls back to `linear` for anything unknown
(`Tween.cpp:77-115`), so `easeInquadratic` ×198 works but a typo'd algorithm silently
becomes linear. An editor that surfaces "this is being ignored" fixes bugs shipping in
public themes today.

**Themes are mostly animation, not layout:** 43 891 `animate` nodes vs 2133 `image` nodes.
A property inspector for nudging X/Y misses what authors actually do — the slice-2 editor
should lead with event/tween editing. 17 real event names; 31 real elements (+4 typos);
only 7 distinct `algorithm` values in practice.

**One page is built from many files:** `PageBuilder.cpp:100-130` loops monitors and prefers
an aspect-specific name (`<page> <W>x<H> - <N>.xml`) over the plain one. The watcher must
track a *set* of candidate paths, including ones that don't exist yet.

### Other findings already established — do not re-derive

- **No file watcher or reload path exists today.** `PageBuilder::buildPage()` is called from
  `RetroFE.cpp` at lines **668, 1260, 1809, 1827** only — re-confirmed 2026-07-23. Current
  feedback loop is *edit → reboot RetroFE → navigate back to the screen*.
- **Reference themes** live under `J:\Documents\games\FRONTENDS\CORE\Themes\` (plus
  `Aeon Nox` under `...\FRONTENDS\RetroFE\RetroFE\layouts\`). Real files are **13–91 KB** —
  ordinary, nothing like the 676 KB TITAN outlier. Wiki reference:
  `docs/RetroFE_Wiki/RetroFE_Documentation.md`.
- **`Graphics/PageBuilder.cpp`** (58 KB) is the sole `layout.xml` parser — **44 attributes**.
  Component element names seen in the parser include `reloadableImage`, `reloadableVideo`,
  `reloadableText`, `reloadableScrollingText`, `reloadableAudio`, alongside classes for
  `Image`, `Text`, `Container`, `ScrollingList`, `Video`.
- **`Graphics/ViewInfo.h`** holds the live visual state, ~35 properties: X/Y, XOrigin/YOrigin,
  XOffset/YOffset, Width/Height + Min/Max, ImageWidth/Height, FontSize, Angle, Alpha, Layer,
  Background RGBA, Reflection (+distance/scale/alpha), Container X/Y/W/H, Monitor, Volume.
- **`Graphics/Animate/TweenTypes.h`** — 22 easing algorithms × 21 tweenable properties
  (+ `TWEEN_PROPERTY_NOP`), driven by `onGameEnter`/`onMenuEnter`-style events.

### Design questions — now answered in the blueprint (§2.2)

Resolved 2026-07-23: **poll mtime+size at 250 ms** (no new dependency, one implementation
across platforms); **debounce by requiring the stat stable across 2 polls** (editors write
partial files); **build the new page fully and swap only on success** (malformed XML must
never blank the screen or kill the process); **gate on `layoutHotReload`, default false**,
read via the existing `config_.getProperty(key, bool&)` overload (`Configuration.h:36`);
**capture/restore collection + selected index + menu depth + playlist**, clamping rather
than failing.

Still genuinely open: **teardown safety** on page swap (in-flight libVLC handles, font cache,
SDL textures) — which is exactly why the next action is a spike, not the watcher. Keep the
design loosely coupled to the video backend, since libmpv is Phase 4.

### TITAN — descoped 2026-07-23

Explicitly **out of scope** for the theme editor (user's call). It no longer drives the design:
the comment-marker fragility it was thought to impose uniquely is a *weaker* version of the
engine-wide parser finding above, which applies to every theme regardless. The conclusion
("surgical, comment-preserving text edits; never parse-and-serialize") survives on its own
merits and is now justified by ordinary community themes.

Two stale facts corrected while checking: the file is at
`M:\CORE - TYPE R\layouts\TITAN\layout.xml` (**not** `core\layouts\`), and it is **676 KB**,
not 563 KB. Mechanics, if ever needed again: `M:\CORE - TYPE R\.claude\KNOWLEDGE.md` §2–§3.

---

## 5. Branch map

| Branch | Tip | State |
|---|---|---|
| `feature/layout-hot-reload` | see §1 | **current branch**; theme-editor work; docs only so far; **not pushed** |
| `feature/data-modernization` | `ecea8ab` | parent of the above; source of the live CORE exe; **not pushed** |
| `feature/vlc-replacement` | `06de5ed` | in sync with origin ✅ |
| `feature/mixed-collections` | `2acf7b6` | in sync with origin |
| `master` | `75bdeea` | **not** a clean upstream mirror — `upstream/master` + 3 local commits. See §7 |

Others: `feature/playlist-menu-wheel`, `feature/reverse-launcher-mapping`,
`feature/sort-and-filter`, `fix/tween-easing-bugs` — all local ahead of origin.

~~Suggested next branch~~ **Done 2026-07-23:** `feature/layout-hot-reload` was cut from
`feature/data-modernization` (not `master`) — otherwise the editor build loses the libVLC work
and can't be tested against the real CORE build.

---

## 6. Working agreement reminders

- `CLAUDE.md` here mandates delegating bulk file reading to the LM Studio local LLM. Follow
  it; if LM Studio isn't running, say so plainly rather than silently burning API tokens.
  **Note (2026-07-23):** the `mcp__lm-studio-worker` tools were **not** loaded this session.
  Ollama is installed and has 5 models (Qwen3.6-35B-A3B ×2, Ornith-1.0-35B, gemma-4-31B,
  oba-roblox). `J:\Documents\Models\Qwen3.6-40B-Deck-Opus-NEO-CODE-*.gguf` (24 GB) is the
  code-tuned one and is **not** imported into Ollama yet — it fits the 32 GB RTX 5090 with
  headroom; worth importing for C++ generation.
- **Delegation judgement call, applied this session:** the layout survey was done with a
  deterministic Python script, not an LLM. Extracting which elements/attributes themes use is
  parsing, not reasoning — a script gives an exact, checkable answer where a model could
  hallucinate schema. Delegate fuzzy work; script the countable work. Scripts used:
  `layout_inventory.py` / `rapid_inventory.py` (scratchpad, not kept — trivial to rewrite from
  the blueprint).
- One small verified slice at a time. Blueprint → explicit go → build → prove it → stop.
- Verify facts against live files. Everything stated in this document was checked against the
  repo on 2026-07-23; re-confirm anything load-bearing before relying on it.

---

## 7. Fork topology & the PR-blocking commit

Established 2026-07-23. All figures measured, not assumed.

### Remotes — now configured

```
origin    https://github.com/SSSTAiNLESSS/RetroFE-CORE.git   (fetch + push)
upstream  https://github.com/phulshof/RetroFE.git            (fetch only)
```

`upstream`'s **push URL is deliberately set to `DISABLED`** so a stray `git push upstream`
fails loudly instead of attempting to write to someone else's repo. Undo with
`git remote set-url --push upstream https://github.com/phulshof/RetroFE.git` if ever needed.

Upstream identity confirmed from `README.md:55`, not guessed. `upstream/master` is at
`9f9230d` and has **not moved since the fork** — upstream also carries `Release-0.10.30`
and `Release-0.10.31` branches.

### Divergence

```
master  vs  upstream/master:   0 behind,  3 ahead
merge-base == 9f9230d == upstream/master tip
```

Zero behind is the good case: no upstream changes to absorb, no rebase pressure, and
`master` is a strict superset of upstream.

### ⚠️ The blocking finding

The 3 commits sitting between `upstream/master` and `master`:

| Commit | Contents | Verdict |
|---|---|---|
| `d11032c` | "added 1.4 core files" — **279 files**, binary `.dll`/`.exe`, incl. a literal `retrofe - Copy.exe` | **junk — must not reach a PR** |
| `a7fb3da` | Revert `playbin3`→`playbin` for GStreamer 1.4 compat, 1 line in `GStreamerVideo.cpp` | genuine fix, **PR-worthy** |
| `75bdeea` | `.gitignore`: adds `tools/` | trivial, harmless |

**Every feature branch descends from `75bdeea`, so every one of them contains `d11032c`.**
Verified by `git merge-base --is-ancestor` against all four small branches. A PR opened from
any of them today would show its own 2–3 commits *plus 279 committed binaries*. That alone
would get a PR closed on sight.

Repo is currently **~1.2 GB** of git objects on disk, largely from this.

### The fix, when PRs are actually wanted

Do **not** rewrite history on branches already pushed to `origin`. Instead cut clean PR
branches straight off `upstream/master` and cherry-pick:

```bash
git fetch upstream
git switch -c pr/tween-easing-bugs upstream/master
git cherry-pick <the 2 real commits from fix/tween-easing-bugs>
git push -u origin pr/tween-easing-bugs
```

PR base `phulshof/RetroFE:master` ← compare `SSSTAiNLESSS/RetroFE-CORE:pr/tween-easing-bugs`.
The binary blob never enters the picture. `a7fb3da` deserves its own PR by the same route —
note it's a **GStreamer** fix and upstream still runs GStreamer, so it remains relevant to
them even though CORE has moved to libVLC.

### Branch shape — already correct

No restructuring needed. Every branch forks cleanly off `75bdeea`:

| Branch | Commits ahead of base | PR-shaped? |
|---|---|---|
| `fix/tween-easing-bugs` | 2 | yes |
| `feature/playlist-menu-wheel` | 2 | yes |
| `feature/reverse-launcher-mapping` | 2 | yes |
| `feature/sort-and-filter` | 3 | yes |
| `feature/mixed-collections` | 17 | large |
| `feature/data-modernization` | 20 | large; **descends from `mixed-collections`** |

That last relationship is verified: `mixed-collections` is a direct ancestor of
`data-modernization`, so it would have to land upstream first, or a PR carries both.

### Still missing: an integration branch

Nothing currently combines tween fixes + playlist wheel + launcher mapping + sort/filter into
one shippable build. `feature/data-modernization` is the biggest branch but does **not**
contain the other four. If CORE is to ship as one binary with all of them, an integration
branch (`core-personal` or similar) is the gap to fill — and it's where conflicts between
`sort-and-filter` and `data-modernization` will surface, since both touch collection/metadata
code. Not attempted yet; no merge has been trialled.

### Licensing note for distribution

RetroFE is **GPLv3**. Submitting PRs is entirely voluntary. Distributing modified *binaries*
does require offering corresponding source — tag each released build
(`git tag -a core-v1.0`) so the public source matches the shipped exe exactly. Third-party
assets bundled with CORE (themes, artwork, fonts, DLLs) carry their own licences and are
**not** covered by RetroFE's GPL.

---

## 8. RustCore — what it actually is

Settled 2026-07-23, after it was briefly misremembered as part of the VLC fix. **It is not.**
The VLC work is separate and already shipped (§1, commits `31bbc65` / `641daf7` on
`feature/vlc-replacement`). `RustCore/` is **Phase 1/3 modernization** — Arrow, Parquet,
DuckDB, cxx. No video code in it.

```toml
name = "retrofe-core"          crate-type = ["staticlib"]
arrow = "53.3"   parquet = "53.3"   duckdb = "1.1.3" (bundled)
quick-xml = "0.36"   cxx = "1.0"    tokio (optional, Phase 3)
```

### Now committed — `ecea8ab` on `feature/data-modernization`

| File | Lines |
|---|---|
| `RustCore/src/bridge.rs` | 34 |
| `RustCore/src/lib.rs` | 18 |
| `RustCore/build.rs` | 12 |
| `RustCore/Cargo.toml` | 39 |
| `RustCore/Cargo.lock` | 2347 |
| `Database/IMetadataBackend.h` | 112 |
| `Database/SQLiteMetadataBackend.h` | 64 |

Verified never committed on any branch before this (`git log --all -- '*RustCore*'` was
empty), so nothing was duplicated.

**It is an early scaffold, not working code.** `CMakeLists.txt` contains no reference to
`RustCore`, `retrofe-core`, or `cargo` — the crate does not participate in the C++ build and
changes no runtime behaviour. Wiring it into CMake is unstarted work.

### The 2.2 GB trap — closed

`RustCore/target/` reaches **2.2 GB** (DuckDB builds from source under the `bundled` feature)
and was untracked *but not gitignored*. One `git add -A` would have put it in history
permanently, on top of the 279 binaries `d11032c` already added (§7). Now ignored via
`cb9616f`. **Do not remove that rule.**

`.gitignore` also now carries `=*`, which catches files created by unquoted shell redirects —
the origin of `=2.31.0` (it held captured `pip install requests>=2.31.0` output, from a
`c:\users\b3nj1\` Python install, not this repo).

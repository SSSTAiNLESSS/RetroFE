# Changelog: Feature/Layout-Hot-Reload

This branch makes theme editing a live loop instead of an edit-restart-navigate-back cycle.
Pressing **F5** re-reads `layout.xml` and adopts its animations onto the page already on screen,
at any menu depth, without losing the collection, playlist, scroll position or playing video.

It is slice 1 of a larger direction: make RetroFE itself the theme-editing surface rather than
building an external WYSIWYG editor that would have to reimplement RetroFE's renderer. Full
reasoning and the survey behind it: `docs/RetroFE/Layout-Hot-Reload-Blueprint.md`.

## [feature/layout-hot-reload]

### Added
- **F5 layout hot-reload** (`RETROFE_RELOAD_LAYOUT_REQUEST`): re-parses `layout.xml` into a
  throwaway page, transplants its `AnimationEvents` onto the live components via the existing
  `setTweens()`, then destroys the throwaway. The live page is never torn down.
- **`Page::reapplyTweensFrom()`** plus `Page::componentKey()`: matches live and freshly-parsed
  components by a **stable structural key** — concrete type (`typeid`) + layer + authored id —
  and consumes them in document order. Anything unmatched keeps its existing tweens.
- **`Component::getTweens()`**: accessor counterpart to the existing `setTweens()`.
- **Layout hot-reload blueprint** (`docs/RetroFE/Layout-Hot-Reload-Blueprint.md`): the survey of
  228 real theme `layout.xml` files and the design it produced.
- **Test rig tooling** (`Scripts/test_fixture.ps1`): snapshot/status/restore for the isolated
  `K:\RetroFE-Testies` fixture, with emulator directories excluded on both sides so a restore
  cannot purge them.

### Design notes
- **The page is deliberately not rebuilt.** A component only changes state when an event fires
  *and* it has a matching animation block at its current `menuIndex`; otherwise the request is
  silently dropped. A page's appearance is therefore the accumulated result of the whole
  navigation, not a function of its final depth — so a rebuilt page leaves everything established
  at a shallower tier at its authored alpha, which is black for most themes, and it gets worse the
  deeper you go. Swapping only the animation data avoids this at any depth.
- **Matching by structural key, not array index.** An earlier guard demanded identical component
  counts and paired tweens by index. `PageBuilder` adds components conditionally, so the count
  legitimately drifts — a missing art file was enough to veto every subsequent reload, and index
  pairing would have scrambled the theme if any component were added or dropped mid-list.

### Known limits
- **Structural edits still need a restart.** Commenting a component in or out changes the
  component set; that component is skipped and the rest still reload.
- **Art and `src`/`type` changes are not picked up** — only animation data is transplanted.
- **Menu per-item scroll-point animations are not transplanted.** `~ScrollingList` deletes the
  `ViewInfo`s in `scrollPoints_` and clones share that vector, so moving them would dangle.
- Highlight animations replay on the next **scroll**, not immediately on F5.

### Status
Slice 1 built and **confirmed working on the test rig** — F5 takes on every press, at depth.
The **file watcher** (auto-reload on save, gated behind `layoutHotReload`, default off) is
specced in the blueprint §2.2 and **not yet started**.

### Note
The spike commit `ad7d78e` ("forced page rebuild on F5") is still in this branch's history. Its
*approach* was abandoned, but the `RETROFE_RELOAD_LAYOUT_REQUEST` enum and `SDLK_F5` trigger it
added are the plumbing this feature sits on — **do not `git revert` it**. Squash it together with
the pivot commit when cleaning the branch for a PR.

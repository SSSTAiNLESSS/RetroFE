---
name: layout-new
description: "Scaffold a fresh RetroFE theme (layout) folder with a documented, known-good starter layout.xml that already passes layout-lint. The starter includes a background image, a vertical game menu, a video preview with screenshot fallback, a selected-item logo with a highlight animation, and year/manufacturer metadata text, all positioned from the chosen virtual resolution. Use when the user wants to start a new theme/layout from scratch, create a blank/starter layout, or asks 'make me a new RetroFE theme'. Runs RetroFE/.claude/skills/layout-new/scripts/new_layout.py. After scaffolding, lint the result with layout-lint and drop in art."
---

# layout-new — start a RetroFE theme from a known-good template

## Why this exists
Starting a layout from a blank file means re-learning the tag structure every
time and risking silent typos. This skill drops a **valid, documented starter
layout.xml** (it passes `layout-lint` with zero errors) into a correctly-named
theme folder, so the user starts from something that already runs and just
customises it.

## How to run it
```
python "K:/RetroFE/.claude/skills/layout-new/scripts/new_layout.py" --name "My Theme"
```
Options:
- `--name` (required) — theme name; becomes the folder name RetroFE loads by.
- `--dest <dir>` — parent `layouts` folder. Defaults to the repo's bundled
  `Package/Environment/Common/layouts/`. For a live install, point it at the
  running frontend's `.../RetroFE/layouts` folder.
- `--width` / `--height` — virtual canvas (default `1920`x`1080`). Element
  positions scale from these, so a `1280x1024` (4:3) canvas still looks sane.
- `--force` — write into an existing folder instead of refusing.

## What it creates
```
<dest>/<name>/
  layout.xml     starter theme (background, vertical menu, video preview,
                 logo + highlight animation, year/manufacturer text)
  fonts/         put font.ttf here (the starter references fonts/font.ttf)
  sounds/        optional UI sounds (commented out in the starter)
  README.txt     what art goes where, and the lint command
```

## Always do this after scaffolding
1. **Lint it** to confirm it's clean:
   `python "K:/RetroFE/.claude/skills/layout-lint/scripts/lint_layout.py" "<dest>/<name>/layout.xml"`
   Expect **0 errors**. The two "file not found" warnings for `bg.png` and
   `fonts/font.ttf` are normal — they're the art the user still needs to add.
2. Have the user drop in `bg.png` and `fonts/font.ttf`.
3. Point RetroFE's `settings.conf` `layout` setting at the theme name and launch.

## Editing tips (share with the user as needed)
- `layer` (0=back … 19=front) controls what draws on top of what.
- `<reloadable...>` components change with the highlighted game; static
  `<image>/<video>` do not.
- Add a per-resolution variant by copying to `layout 4x3.xml` (RetroFE picks the
  ratio-specific file automatically, else falls back to `layout.xml`).
- Re-lint after every change — RetroFE won't warn you about typos, but the linter will.

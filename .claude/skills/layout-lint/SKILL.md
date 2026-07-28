---
name: layout-lint
description: "Static-check a RetroFE layout.xml theme file against what the RetroFE C++ parser ACTUALLY accepts (not just the wiki), catching the silent-failure bugs RetroFE never reports: misspelled or mis-cased attributes, unknown tags, broken animations (missing to/duration, non-animatable types, wrong easing names), bad menu types, bad art modes, and missing static art/font files. Use when the user asks to check/lint/validate/debug a layout or theme, when a theme 'isn't working' or 'nothing shows up', or right after editing any layout.xml / splash.xml. Runs RetroFE/.claude/skills/layout-lint/scripts/lint_layout.py."
---

# layout-lint — catch RetroFE's silent theme failures

## Why this exists
RetroFE **never tells you** when a layout is wrong. A misspelled attribute
(`Layer` instead of `layer`), an unknown tween type, or a wrong easing name
produces **no error** — the element just silently doesn't do what you meant.
This linter checks a layout against the rules the RetroFE C++ parser really
enforces (extracted from `RetroFE/Source/Graphics/PageBuilder.cpp` and
`Animate/Tween.cpp`), so those silent bugs become visible.

It parses as leniently as RetroFE's rapidxml does (default `parse<0>` flags),
so it will **not** false-alarm on the loose XML that real, shipped layouts use
(e.g. `<!----- divider ----->` comments, or `<onMenuJumpEnter>...</onMenuEnter>`
mismatched close tags — RetroFE accepts both).

## How to run it
```
python "K:/RetroFE/.claude/skills/layout-lint/scripts/lint_layout.py" <layout.xml> [more.xml ...]
```
- Accepts one or more files (lint `layout.xml`, `layout 4x3.xml`, `splash.xml` together).
- Exit code `0` = no errors (warnings allowed); `1` = at least one error or an unparseable file.

## What it reports
**Errors** (definitely broken — fix these):
- Unknown tag names, and unknown / mis-cased attributes (with a "did you mean" hint — RetroFE is case-sensitive on attributes).
- `<animate>` missing `type`, or missing `to` when `type` isn't `nop`.
- `<set>` missing the required `duration`.

**Warnings** (works but probably not what you intended):
- `<animate type=...>` that isn't an animatable property (silently ignored).
- `type="fontSize"` — known RetroFE engine bug: it can never match, so it does nothing.
- Easing `algorithm=` that RetroFE doesn't know (falls back to `linear`), including the wiki's `easeInoutquintic`, which the engine actually spells `easeOnOutQuintic`.
- `<menu type=>` other than `vertical`/`custom`; `mode=` outside the five valid art modes.
- Static `src=` / `font=` files that don't exist next to the layout (reloadable media is resolved at runtime and is not path-checked).

## How to use the results
1. Fix **errors** first — they are silent no-ops in RetroFE.
2. Then judge **warnings** in context (a missing-font warning may just mean the
   art isn't populated yet).
3. Re-run until clean, then have the user launch the frontend to confirm visually.

## Keeping it accurate (maintainer note)
The allowlists at the top of `lint_layout.py` are the single source of truth and
mirror the C++ parser. If RetroFE's parser changes, update those sets to match —
`PageBuilder.cpp` / `Tween.cpp` are the real authority, above the wiki.

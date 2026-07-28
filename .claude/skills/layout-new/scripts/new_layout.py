#!/usr/bin/env python3
"""
new_layout.py — Scaffold a fresh RetroFE theme (layout) folder.

Creates a new /layouts/<name>/ folder containing a documented, KNOWN-GOOD
starter layout.xml (it passes layout-lint). The starter shows the common
building blocks a theme needs: a background, a vertical game menu, a video
preview with image fallback, a logo, and a couple of metadata text fields
with a highlight animation. Drop your art into the folder and tweak.

USAGE
    python new_layout.py --name "My Theme"
    python new_layout.py --name "My Theme" --dest "K:/RetroFE/Artifacts/windows/RetroFE/layouts"
    python new_layout.py --name "My Theme" --width 1280 --height 1024

By default it writes to the repo's bundled layouts folder:
    K:/RetroFE/Package/Environment/Common/layouts/<name>/

It refuses to overwrite an existing folder unless you pass --force.
"""

import argparse
import os
import sys


DEFAULT_DEST = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "..", "..",            # scripts -> layout-new -> skills -> .claude -> repo root
    "Package", "Environment", "Common", "layouts",
)

# Starter layout. Tokens @W@ / @H@ are replaced; XML has no curly braces so a
# plain string with token replacement keeps this readable and copy-pasteable.
LAYOUT_TEMPLATE = """<layout width="@W@" height="@H@" font="fonts/font.ttf" loadFontSize="36" fontColor="dedede">

    <!-- Sounds: uncomment and drop wav files in this folder to use them.
    <sound type="load"      src="sounds/load.wav"/>
    <sound type="highlight" src="sounds/scroll.wav"/>
    <sound type="select"    src="sounds/select.wav"/>
    -->

    <!-- Background: put a bg.png in this folder (fills the screen). -->
    <image src="bg.png" x="0" y="0" width="stretch" height="stretch" layer="0"/>

    <!-- System / game logo for the currently selected item.
         type="logo" looks up medium_artwork/logo/<item>.png in the collection. -->
    <reloadableImage type="logo" x="center" y="120" xOrigin="center" yOrigin="top"
                     height="220" maxWidth="900" layer="7">
        <onHighlightEnter>
            <set duration="0.25">
                <animate type="alpha" from="0" to="1" algorithm="easeoutcubic"/>
            </set>
        </onHighlightEnter>
        <onHighlightExit>
            <set duration="0.15">
                <animate type="alpha" to="0" algorithm="easeincubic"/>
            </set>
        </onHighlightExit>
    </reloadableImage>

    <!-- Video preview of the selected game, with a screenshot as fallback. -->
    <reloadableVideo type="video" imageType="screenshot"
                     x="center" y="center" xOrigin="center" yOrigin="center"
                     height="540" maxWidth="960" volume="0" layer="5"/>

    <!-- Vertical scrolling list of the game names in the current collection. -->
    <menu type="vertical" orientation="vertical" scrollTime="0.2"
          scrollAcceleration="0.02" minScrollTime="0.05"
          x="80" y="@LISTY@" width="520" height="@LISTH@" layer="6">
        <itemDefaults fontSize="30" fontColor="9aa4b2" spacing="8"/>
        <item index="start"    fontColor="3a4250"/>
        <item index="selected" fontSize="40" fontColor="ffffff"/>
        <item index="end"      fontColor="3a4250"/>
    </menu>

    <!-- A couple of metadata fields for the selected game. -->
    <reloadableText type="year"         x="80"  y="@METAY@" xOrigin="left" yOrigin="top" fontSize="26" layer="7"/>
    <reloadableText type="manufacturer" x="80"  y="@META2Y@" xOrigin="left" yOrigin="top" fontSize="26" maxWidth="500" layer="7"/>

</layout>
"""

README_TEXT = """This is a RetroFE layout (theme) folder.

Files RetroFE looks for here:
  layout.xml          - main theme (loaded when the frontend runs)
  layout <ratio>.xml  - optional per-resolution variant, e.g. "layout 4x3.xml"
  splash.xml          - optional startup splash screen

Art you provide in THIS folder (referenced by <image>/<video>/<sound> src=):
  bg.png              - full-screen background (referenced by the starter)
  fonts/font.ttf      - the UI font (referenced by the starter <layout font=>)
  sounds/*.wav        - optional UI sounds (commented out in the starter)

Per-game art (logos, videos, screenshots for <reloadable...> components) does
NOT live here - RetroFE loads it from each collection's medium_artwork/ folder
at runtime. See the wiki "Mode Attribute" section for the exact lookup paths.

After editing layout.xml, lint it:
  python K:/RetroFE/.claude/skills/layout-lint/scripts/lint_layout.py layout.xml
"""


def build_layout(width, height):
    # A few positions are derived from the canvas so the starter looks sane at
    # any resolution (single source of truth: width/height).
    list_y = int(height * 0.28)
    list_h = int(height * 0.60)
    meta_y = int(height * 0.90)
    meta2_y = int(height * 0.94)
    return (LAYOUT_TEMPLATE
            .replace("@W@", str(width))
            .replace("@H@", str(height))
            .replace("@LISTY@", str(list_y))
            .replace("@LISTH@", str(list_h))
            .replace("@METAY@", str(meta_y))
            .replace("@META2Y@", str(meta2_y)))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Scaffold a new RetroFE layout folder.")
    ap.add_argument("--name", required=True, help='Theme name, e.g. "Neon 16x9".')
    ap.add_argument("--dest", default=os.path.normpath(DEFAULT_DEST),
                    help="Parent layouts folder to create the theme in.")
    ap.add_argument("--width", type=int, default=1920, help="Virtual canvas width.")
    ap.add_argument("--height", type=int, default=1080, help="Virtual canvas height.")
    ap.add_argument("--force", action="store_true",
                    help="Allow writing into an existing theme folder.")
    args = ap.parse_args(argv)

    theme_dir = os.path.join(args.dest, args.name)
    if os.path.exists(theme_dir) and not args.force:
        print(f"[ERROR] {theme_dir} already exists. Use --force to write into it.")
        return 1

    os.makedirs(os.path.join(theme_dir, "fonts"), exist_ok=True)
    os.makedirs(os.path.join(theme_dir, "sounds"), exist_ok=True)

    layout_path = os.path.join(theme_dir, "layout.xml")
    with open(layout_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(build_layout(args.width, args.height))
    with open(os.path.join(theme_dir, "README.txt"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(README_TEXT)

    print(f"Created theme: {theme_dir}")
    print(f"  layout.xml   ({args.width}x{args.height} virtual canvas)")
    print(f"  fonts/  sounds/  README.txt")
    print("\nNext steps:")
    print(f"  1. Drop bg.png and fonts/font.ttf into the folder.")
    print(f'  2. Lint it: python "K:/RetroFE/.claude/skills/layout-lint/scripts/lint_layout.py" "{layout_path}"')
    print(f"  3. Point RetroFE's settings.conf 'layout' at \"{args.name}\" and launch.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

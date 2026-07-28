#!/usr/bin/env python3
"""
lint_layout.py — Static checker for RetroFE layout.xml theme files.

WHY THIS EXISTS
---------------
RetroFE fails *silently* on bad layouts: a misspelled attribute, an unknown
tween type, or a wrong easing name produces NO error — the element just doesn't
do what you meant. That single behaviour is the #1 time-sink when authoring
themes. This linter checks a layout against what the RetroFE C++ parser
ACTUALLY accepts (extracted from PageBuilder.cpp / Tween.cpp), not just the wiki.

USAGE
    python lint_layout.py <path-to-layout.xml> [more.xml ...]
    python lint_layout.py "K:/RetroFE/Package/.../layouts/Aeon Nox/layout.xml"

EXIT CODE
    0 = no errors (warnings are allowed)
    1 = at least one ERROR found, or a file could not be parsed

The allowlists below are the single source of truth. If RetroFE's parser
changes, update these to match the C++ — that is the real authority.
"""

import bisect
import os
import re
import sys


# --------------------------------------------------------------------------
# GROUND TRUTH — mirrors RetroFE/Source/Graphics/PageBuilder.cpp + Tween.cpp
# --------------------------------------------------------------------------

# Element names the parser understands anywhere in a layout.
ACTION_TAGS = {
    "onEnter", "onExit", "onIdle", "onMenuIdle", "onMenuScroll",
    "onHighlightEnter", "onHighlightExit", "onMenuEnter", "onMenuExit",
    "onGameEnter", "onGameExit", "onPlaylistEnter", "onPlaylistExit",
    "onMenuJumpEnter", "onMenuJumpExit", "onAttractEnter", "onAttract",
    "onAttractExit", "onJukeboxJump",
    "onMenuActionInputEnter", "onMenuActionInputExit",
    "onMenuActionSelectEnter", "onMenuActionSelectExit",
}

COMPONENT_TAGS = {
    "image", "video", "text", "sound", "menu", "container", "statusText",
    "reloadableImage", "reloadableVideo", "reloadableAudio",
    "reloadableText", "reloadableScrollingText",
}

KNOWN_TAGS = (
    {"layout", "itemDefaults", "item", "set", "animate"}
    | COMPONENT_TAGS
    | ACTION_TAGS
)

# Every attribute the parser reads (buildViewInfo geometry + all
# first_attribute() calls across PageBuilder.cpp). CASE-SENSITIVE on purpose:
# rapidxml matches exact case, so `Layer` silently does nothing.
KNOWN_ATTRS = {
    # geometry / general (buildViewInfo)
    "x", "y", "xOffset", "yOffset", "xOrigin", "yOrigin", "height", "width",
    "fontSize", "fontColor", "minHeight", "minWidth", "maxHeight", "maxWidth",
    "alpha", "angle", "layer", "backgroundColor", "backgroundAlpha",
    "reflection", "reflectionDistance", "reflectionScale", "reflectionAlpha",
    "containerX", "containerY", "containerWidth", "containerHeight",
    "monitor", "volume",
    # component / menu / reloadable / animation attributes
    "algorithm", "alignment", "direction", "duration", "endTime", "font",
    "from", "id", "imageType", "index", "jukebox", "jukeboxNumLoops",
    "loadFontSize", "menuIndex", "menuScrollReload", "minScrollTime",
    "minShowTime", "mode", "numLoops", "orientation", "pluralPostfix",
    "pluralPrefix", "scrollAcceleration", "scrollingSpeed", "scrollTime",
    "selected", "selectedOffset", "singlePostfix", "singlePrefix", "spacing",
    "src", "startPosition", "startTime", "textFallback", "textFormat",
    "timeFormat", "to", "type", "value", "videoType",
}

# Valid <animate type="..."> tween properties (matched lowercased by engine).
# NOTE: "fontsize" is deliberately absent — the engine stores the map key as
# "fontSize" but lowercases the lookup to "fontsize", so it can NEVER match.
TWEEN_PROPERTIES = {
    "x", "y", "angle", "alpha", "width", "height", "xorigin", "yorigin",
    "xoffset", "yoffset", "backgroundalpha", "maxwidth", "maxheight", "layer",
    "containerx", "containery", "containerwidth", "containerheight",
    "volume", "nop",
}

# Valid easing algorithms (matched lowercased). "easeonoutquintic" is the
# engine's actual (misspelled) key for the in-out quintic curve.
TWEEN_ALGORITHMS = {
    "easeinquadratic", "easeoutquadratic", "easeinoutquadratic",
    "easeincubic", "easeoutcubic", "easeinoutcubic",
    "easeinquartic", "easeoutquartic", "easeinoutquartic",
    "easeinquintic", "easeoutquintic", "easeonoutquintic",
    "easeinsine", "easeoutsine", "easeinoutsine",
    "easeinexponential", "easeoutexponential", "easeinoutexponential",
    "easeincircular", "easeoutcircular", "easeinoutcircular",
    "linear",
}

MENU_TYPES = {"vertical", "custom"}
ART_MODES = {"system", "common", "layout", "systemlayout", "commonlayout"}

# Attributes whose value is a file path resolved relative to the layout folder.
PATH_ATTRS = {"src", "font"}


# --------------------------------------------------------------------------
# Tolerant scanner — mirrors how RetroFE's rapidxml (doc.parse<0>) reads XML
# --------------------------------------------------------------------------
# RetroFE parses with rapidxml's DEFAULT flags, which do NOT validate that a
# closing tag's name matches its opening tag. Shipped layouts rely on this
# (e.g. <onMenuJumpEnter>...</onMenuEnter> works fine). A strict XML parser
# would reject those real, working files, so we scan with the same leniency:
# any </...> simply closes the current element. We still get accurate line
# numbers for every element.

class Node:
    __slots__ = ("tag", "attrs", "line", "children", "parent")

    def __init__(self, tag, attrs, line, parent):
        self.tag = tag
        self.attrs = attrs          # dict, in document order (py3.7+)
        self.line = line
        self.children = []
        self.parent = parent


def _blank_comments(text):
    """Strip <!-- ... --> comments but keep line numbers intact.

    RetroFE tolerates the `<!------ divider ------>` style comments (repeated
    dashes) that strict XML forbids. Each comment is replaced by the same
    number of newlines it spanned so reported line numbers stay accurate.
    """
    def repl(m):
        return "\n" * m.group(0).count("\n")
    return re.sub(r"<!--.*?-->", repl, text, flags=re.DOTALL)


# One tag: opening/closing marker, name, attribute blob, self-close marker.
# The attribute blob uses quoted-value sub-patterns so a '>' inside a value
# (e.g. menuIndex=">1") does not prematurely end the tag.
_TAG_RE = re.compile(
    r"""<(?P<close>/?)\s*(?P<name>[\w:.\-]+)
        (?P<attrs>(?:\s+[\w:.\-]+\s*=\s*"[^"]*"
                   |\s+[\w:.\-]+\s*=\s*'[^']*'
                   |\s+[\w:.\-]+)*)
        \s*(?P<selfclose>/?)\s*>""",
    re.VERBOSE | re.DOTALL,
)

_ATTR_RE = re.compile(
    r"""([\w:.\-]+)\s*=\s*(?:"([^"]*)"|'([^']*)')""",
)


def _parse_attrs(blob):
    attrs = {}
    for m in _ATTR_RE.finditer(blob):
        name = m.group(1)
        value = m.group(2) if m.group(2) is not None else (m.group(3) or "")
        attrs[name] = value
    return attrs


def parse_tree(path):
    """Return (root_node, None) or (None, error_string). Never raises on the
    kinds of looseness rapidxml accepts."""
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        text = _blank_comments(fh.read())

    # offset -> line number lookup
    line_starts = [0]
    for i, ch in enumerate(text):
        if ch == "\n":
            line_starts.append(i + 1)

    def line_of(offset):
        return bisect.bisect_right(line_starts, offset)

    root = None
    stack = []
    for m in _TAG_RE.finditer(text):
        name = m.group("name")
        # Skip processing instructions / doctype (names starting with ? or !
        # never match [\w...], so they simply don't appear here).
        if m.group("close"):
            if stack:
                stack.pop()
            continue
        node = Node(name, _parse_attrs(m.group("attrs")),
                    line_of(m.start()), stack[-1] if stack else None)
        if stack:
            stack[-1].children.append(node)
        elif root is None:
            root = node
        if not m.group("selfclose"):
            stack.append(node)

    if root is None:
        return None, "no XML elements found (is this a layout file?)"
    return root, None


# --------------------------------------------------------------------------
# Linting
# --------------------------------------------------------------------------

class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, line, msg):
        self.errors.append((line, msg))

    def warn(self, line, msg):
        self.warnings.append((line, msg))


def check_node(node, layout_dir, rep):
    line = node.line

    # 1. Unknown element name (typo'd or unsupported tag → silently ignored).
    if node.tag not in KNOWN_TAGS:
        rep.error(line, f"<{node.tag}> is not a tag RetroFE understands "
                        f"(it will be ignored). Check the spelling.")

    # 2. Unknown / mis-cased attributes (the classic silent failure).
    for name in node.attrs:
        if name not in KNOWN_ATTRS:
            hint = ""
            lowered = {a.lower(): a for a in KNOWN_ATTRS}
            if name.lower() in lowered:
                hint = f' Did you mean "{lowered[name.lower()]}"? (case matters)'
            rep.error(line, f'<{node.tag}> attribute "{name}" is not recognised '
                            f'and will be ignored.{hint}')

    # 3. Tag-specific rules.
    if node.tag == "animate":
        _check_animate(node, rep)
    if node.tag == "set" and "duration" not in node.attrs:
        rep.error(line, '<set> is missing the required "duration" attribute '
                        "(the whole set is skipped without it).")
    if node.tag == "menu":
        t = node.attrs.get("type")
        if t is not None and t not in MENU_TYPES:
            rep.warn(line, f'<menu type="{t}"> is unusual; expected '
                           f'"vertical" or "custom".')

    # 4. mode= attribute value check (any tag that carries it).
    mode = node.attrs.get("mode")
    if mode is not None and mode not in ART_MODES:
        rep.warn(line, f'mode="{mode}" is not one of {sorted(ART_MODES)}; '
                       "RetroFE will treat it as no mode.")

    # 5. Static path attributes point at files that should exist.
    for attr in PATH_ATTRS:
        if attr in node.attrs and node.tag in {"image", "video", "sound", "layout",
                                               "text", "menu", "item", "itemDefaults",
                                               "reloadableImage", "reloadableVideo",
                                               "reloadableAudio", "reloadableText",
                                               "reloadableScrollingText"}:
            val = node.attrs[attr]
            # reloadable* resolve their media at runtime from collections; only
            # a literal font/src that lives in the layout folder is checkable.
            if attr == "src" and node.tag.startswith("reloadable"):
                continue
            rel = val.replace("\\", "/")
            full = os.path.normpath(os.path.join(layout_dir, rel))
            if not os.path.exists(full):
                rep.warn(line, f'{node.tag} {attr}="{val}" — file not found '
                               f'relative to the layout folder ({full}).')

    for child in node.children:
        check_node(child, layout_dir, rep)


def _check_animate(node, rep):
    line = node.line
    t = node.attrs.get("type")
    if t is None:
        rep.error(line, '<animate> is missing the required "type" attribute.')
        return
    tl = t.lower()
    if tl == "nop":
        return
    if "to" not in node.attrs:
        rep.error(line, f'<animate type="{t}"> needs a "to" attribute '
                        "(only nop may omit it).")
    if tl not in TWEEN_PROPERTIES:
        if tl == "fontsize":
            rep.warn(line, '<animate type="fontSize"> does NOT work in RetroFE '
                           "(an engine bug makes the lookup always miss). "
                           "Animate a different property.")
        else:
            rep.warn(line, f'<animate type="{t}"> is not an animatable property; '
                           "this animation will be silently ignored.")
    alg = node.attrs.get("algorithm")
    if alg is not None and alg.lower() not in TWEEN_ALGORITHMS:
        hint = ""
        if alg.lower() == "easeinoutquintic":
            hint = ' The engine spells it "easeOnOutQuintic" (a typo in RetroFE).'
        rep.warn(line, f'algorithm="{alg}" is unknown; RetroFE will fall back '
                       f"to linear.{hint}")


def lint_file(path):
    print(f"\n=== {path} ===")
    if not os.path.isfile(path):
        print(f"  [ERROR] file not found")
        return 1

    root, err = parse_tree(path)
    if err:
        print(f"  [ERROR] {err}")
        return 1

    if root.tag != "layout":
        print(f"  [WARN] root element is <{root.tag}>, expected <layout>.")

    rep = Report()
    layout_dir = os.path.dirname(os.path.abspath(path))
    check_node(root, layout_dir, rep)

    for line, msg in sorted(rep.errors):
        print(f"  [ERROR] line {line}: {msg}")
    for line, msg in sorted(rep.warnings):
        print(f"  [WARN]  line {line}: {msg}")

    print(f"  -> {len(rep.errors)} error(s), {len(rep.warnings)} warning(s)")
    return 1 if rep.errors else 0


def main(argv):
    try:                                    # keep unicode safe on Windows consoles
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    if len(argv) < 2:
        print(__doc__)
        return 2
    worst = 0
    for path in argv[1:]:
        worst = max(worst, lint_file(path))
    return worst


if __name__ == "__main__":
    sys.exit(main(sys.argv))

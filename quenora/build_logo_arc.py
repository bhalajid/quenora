#!/usr/bin/env python3
"""
build_logo_arc.py — put the nine circles back on their own arc.

RUN BEFORE build_brand.py. It rewrites the supplied brand SVGs in place.

THE PROBLEM

The alternate set draws its nine spheres on an arc stretched about 1.6x
horizontally. The radii are right — 9x from first to last, ratio 9^(1/8) —
but the path they sit on is not the mark's. Spread that wide the arc stops
reading as a quarter turn and starts reading as a tail trailing off to the
right, which is exactly what it looked like in the header.

  supplied   x 432 -> 983  (551 wide)   y 378 -> 73  (305 tall)   1.80 : 1
  the mark   x  12 -> 152  (140 wide)   y 162 -> 36 (126 tall)   1.11 : 1

THE FIX

CLAUDE.md fixes the geometry: nine circles on a 90 degree arc in the viewBox
0 0 187.71 174.29, and those coordinates must be byte-identical everywhere —
nav, footer, favicon, hero canvas and the chapter diagram all derive from the
same nine triples. The hero has been drawing them correctly all along; only
the supplied file disagreed. So the triples are taken from the mark and
mapped into the lockup, anchored on the largest sphere so the arc keeps the
position and size it already had at its top end and tightens below it.

The spherical shading is kept. Each sphere is a base circle, a rim circle and
a highlight ellipse, and the highlight sits at a fixed fraction of the radius
— measured off the supplied file rather than guessed:

    offset  (-0.330r, -0.401r)      radii  (0.260r, 0.170r)      rotate -31.5

COLOUR

The Q is flat ember and the spheres fell away to near-black at the rim, so
side by side they read as two different oranges. The gradient now bottoms out
in a dark ember rather than a brown, which keeps them the same colour while
still reading as spheres and not as flat dots.

RETIRED
=======

Not run by build.sh any more, and it should not be run by hand.

It was right while the site carried the alternate squared-Q set: those dots
were on a 37-degree scatter that did not match the mark, and this put them
back on the canonical 90-degree arc. The lockup is now the supplied artwork,
whose dots were drawn for its own 2.41:1 shape. Run against that, this
rewrites them and takes the box with it — verified in a scratch worktree,
primary.svg went from viewBox "8 9 1421 590" to "8 -199 1421 798".

Kept rather than deleted because the geometry and the measured highlight
offsets in it are the reference for the standalone mark, which build_favicon
still uses. Pass --force if you genuinely mean it.
"""
import os, re, sys

if "--force" not in sys.argv:
    sys.exit("  build_logo_arc is retired; it rewrites the supplied lockup. "
             "Pass --force if you mean it.")

ROOT = os.path.dirname(os.path.abspath(__file__))
BRAND = os.path.join(ROOT, "assets", "brand")

# The mark, in arc units. Identical to index.html's MARK and to CLAUDE.md.
MARK = [(12, 161.71, 3), (21.64, 161.34, 3.95), (33.39, 159.88, 5.2),
        (47.73, 156.52, 6.84), (65.05, 149.97, 9), (85.34, 138.1, 11.84),
        (107.49, 117.76, 15.59), (127.81, 84.89, 20.52), (151.71, 36, 27)]

# Measured off the supplied file, not invented.
HX, HY, HRX, HRY, HROT = -0.330, -0.401, 0.260, 0.170, -31.5

# Copper, not ember. Nora's button and the "Start a conversation" CTA are both
# --copper #C97A3C (the CTA hovers to --copper-lt #E9A063); the lockup was the
# only ember thing beside them. The Q moves with the spheres, so the mark stays
# one colour shaded rather than two oranges side by side.
COPPER, COPPER_LT = '#C97A3C', '#E9A063'
GRADIENT = ('<radialGradient id="%s" cx="0.5" cy="0.5" r="0.53" fx="0.32" fy="0.29">'
            '<stop offset="0" stop-color="#F7DCC2"/>'
            '<stop offset="0.18" stop-color="#E9A063"/>'
            '<stop offset="0.50" stop-color="#C97A3C"/>'
            '<stop offset="0.85" stop-color="#A55F2A"/>'
            '<stop offset="1" stop-color="#7E4620"/>'
            '</radialGradient>')
# the rim light, warmed to match
RIM = ('<radialGradient id="%s" cx="0.5" cy="0.5" r="0.52" fx="0.76" fy="0.79">'
       '<stop offset="0" stop-color="#F2CDA4" stop-opacity="0.42"/>'
       '<stop offset="0.5" stop-color="#F2CDA4" stop-opacity="0.06"/>'
       '<stop offset="1" stop-color="#F2CDA4" stop-opacity="0"/>'
       '</radialGradient>')

# Where the arc's foot and head sit, in lockup units. The wordmark glyphs are
# at  u 243-363 · e 417-534 · n 584-701 · o 752-872 · r 920-998 · a 1031-1147,
# and a 90 degree arc is locked at 1.11:1 — so moving the foot to the u and
# keeping the rise means the whole arc scales, and the box grows with it.
SPANS = {
    'compact': (270, 528),    # u -> e/n     arc 258 wide, box 1166x554
    'mid':     (270, 900),    # u -> o       arc 630 wide, box 1166x961
    'full':    (270, 1008),   # u -> the r   arc 738 wide, box 1166x1077
}

# WHICH SPAN GOES WHERE, and why it is not one answer.
#
# The arc must start above the u. A 90 degree arc is locked at 1.11:1, so a
# longer arc is a proportionally taller lockup, and the wordmark inside it
# shrinks to match. The site header bar is 85px, which caps the logo at about
# 60px, and at 60px:
#
#     compact   wordmark 18.6px      mid   10.7px      full   8.8px
#
# Only one of those is readable. So the header takes the compact arc — which
# still reads better than the 15.2px it had before — and the footer, which is
# a stacked block with vertical room to spare, takes the long rise. Same mark,
# two crops, which is what the .brand.lg class already existed for.
FILE_SPAN = {'quenora-primary.svg': 'compact',
             'quenora-primary-light-background.svg': 'compact',
             'quenora-full.svg': 'mid',
             'quenora-full-light-background.svg': 'mid'}
OVERRIDE = os.environ.get('QUENORA_ARC')


def spheres(anchor_cx, anchor_cy, anchor_r, ids):
    """The nine, mapped so the LAST one keeps the place and size it had.

    `ids` is (base, rim, highlight) and is READ FROM THE FILE. Each file in the
    supplied set was exported with its own random gradient id prefix — q79d4*
    in primary, qdb76* in full — so hardcoding one prefix wrote nine circles
    into the full lockup that referenced a gradient it did not contain, and
    they painted nothing at all."""
    B, R, H = ids
    ax, ay, ar = MARK[-1]
    s = anchor_r / ar
    out = []
    for mx, my, mr in MARK:
        cx = anchor_cx + (mx - ax) * s
        cy = anchor_cy + (my - ay) * s
        r = mr * s
        hx, hy = cx + HX * r, cy + HY * r
        out.append(
            f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="url(#{B})"/>'
            f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="url(#{R})"/>'
            f'<ellipse cx="{hx:.2f}" cy="{hy:.2f}" rx="{HRX * r:.2f}" ry="{HRY * r:.2f}"'
            f' transform="rotate({HROT} {hx:.2f} {hy:.2f})" fill="url(#{H})"/>')
    return "".join(out)


def ink_top(svg):
    """Topmost y of the lettering, so the arc can be seated just above it."""
    ys = []
    for m in re.finditer(r'<path\b[^>]*?d="([^"]+)"', svg):
        n = [float(v) for v in re.findall(r'-?\d+\.?\d*', m.group(1))]
        if n[1::2]:
            ys.append(min(n[1::2]))
    return min(ys) if ys else 440.0


def rewrite(path):
    s = open(path, encoding="utf-8").read()
    g = re.search(r'(<g class="quenora-rise">)(.*?)(</g>)', s, re.S)
    if not g:
        return None
    circles = re.findall(r'<circle[^>]*?cx="([\d.]+)" cy="([\d.]+)" r="([\d.]+)"',
                         g.group(2))
    if len(circles) < 2:
        return None
    old = (float(circles[0][0]), float(circles[-1][0]))
    r = float(circles[-1][2])                      # keep the size it already had
    scale = r / MARK[-1][2]

    """Seat the arc rather than leave it where the stretched one ended up.
    Its foot sits a fixed gap above the lettering, and its head stops short
    of the right edge — otherwise a 90 degree arc, which is much taller than
    the flat one it replaces, either collides with the word or runs out of
    the box."""
    top = ink_top(s)
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', s).group(1).split()]
    span = OVERRIDE or FILE_SPAN.get(os.path.basename(path), 'compact')
    foot_x, head_x = SPANS[span]
    scale = (head_x - foot_x) / (MARK[-1][0] - MARK[0][0])
    r = MARK[-1][2] * scale
    foot_y = top - 48                              # smallest sphere's centre
    head_y = foot_y - (MARK[0][1] - MARK[-1][1]) * scale

    ids = re.findall(r'<radialGradient id="([^"]+)"', s)[:3]
    if len(ids) < 3:
        return None
    B, R, H = ids
    s = s[:g.start(2)] + spheres(head_x, head_y, r, (B, R, H)) + s[g.end(2):]
    s = re.sub(r'<radialGradient id="%s".*?</radialGradient>' % B, GRADIENT % B, s, flags=re.S)
    s = re.sub(r'<radialGradient id="%s".*?</radialGradient>' % R, RIM % R, s, flags=re.S)
    # the Q moves with them
    s = s.replace('fill="#FF7043"', 'fill="%s"' % COPPER)

    """Then crop the dead space the taller arc left above it. The box used to
    be sized for an arc that sprawled sideways; keeping that height would put
    a third of the lockup's height into empty sky and shrink everything else
    to fit a header."""
    """The box follows the arc in BOTH directions. An earlier version only
    ever cropped downward — `if new_top > vb[1]` — so the two wider spans,
    whose arcs rise well above the original top edge, kept a box that stopped
    at y=0 and had their largest sphere sliced flat by it."""
    new_top = round(head_y - r - 18)
    s = s.replace('viewBox="%s"' % re.search(r'viewBox="([^"]+)"', s).group(1),
                  'viewBox="%g %g %g %g"' % (vb[0], new_top, vb[2], vb[1] + vb[3] - new_top))
    open(path, "w", encoding="utf-8").write(s)
    return old, (foot_x, head_x), (vb[3], vb[1] + vb[3] - new_top), span


def main():
    n = 0
    for name in sorted(os.listdir(BRAND)):
        if not name.endswith(".svg"):
            continue
        res = rewrite(os.path.join(BRAND, name))
        if res:
            (b0, b1), (a0, a1), (h0, h1), span = res
            print(f"  {name}: {span:8} arc {b1 - b0:.0f} -> {a1 - a0:.0f}, "
                  f"box {h0:.0f} -> {h1:.0f}")
            n += 1
    if not n:
        sys.exit("  no brand SVG carried a .quenora-rise group")
    print(f"  nine circles back on the mark's own arc in {n} file(s)")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
build_favicon.py — the tab icon is the nine circles, and nothing else.

RUN AFTER build_logo_arc.py, whose colours this matches.

WHAT CHANGES

The supplied set's icon is the Q. The mark is the nine circles, so the tab
now carries the nine circles: the same triples the hero canvas, the header
lockup and the chapter diagram are all drawn from, at the crop CLAUDE.md
already names for the mark on its own — viewBox 9 9 169.71 155.71 — squared
up by centring that box vertically.

  quenora-icon.svg        the nine, as vector
  quenora-icon-32.png     tab, retina tab
  quenora-icon-64.png
  quenora-icon-180.png    apple-touch
  quenora-icon-192.png    installed icon
  quenora-icon-512.png    installed icon, splash
  favicon.ico             16 / 32 / 48, for anything old

A NOTE ON HOW SMALL THIS GOES

The mark spans 9x from first circle to last. Squeezed into 16 physical
pixels the smallest circle lands under a quarter of a pixel and is simply
not there — at that size the icon reads as four or five dots rising, not
nine. That is the mark behaving as designed rather than a defect, but it is
the reason the supplied set offered a Q instead. Rendered at each size
rather than downsampled from one big one, so every size is as crisp as the
rasteriser can make it.

RASTERISING

Chromium, through the same Playwright the release gate already depends on —
no new dependency, and it is the renderer the icons will actually be viewed
in. The .ico container is written here directly: it is a header, one 16-byte
directory entry per frame and then the frames, and doing it by hand is what
lets all three sizes keep the render made against their own pixel grid.
"""
import json, os, struct, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
BRAND = os.path.join(ROOT, "assets", "brand")
TEST = os.path.join(ROOT, "test")

# The mark, in arc units. Identical to build_logo_arc.MARK, index.html's MARK
# and CLAUDE.md. Nine circles on a 90 degree arc, growing 9x, ratio 9^(1/8).
MARK = [(12, 161.71, 3), (21.64, 161.34, 3.95), (33.39, 159.88, 5.2),
        (47.73, 156.52, 6.84), (65.05, 149.97, 9), (85.34, 138.1, 11.84),
        (107.49, 117.76, 15.59), (127.81, 84.89, 20.52), (151.71, 36, 27)]

# Measured off the supplied set, same as build_logo_arc.
HX, HY, HRX, HRY, HROT = -0.330, -0.401, 0.260, 0.170, -31.5

# The mark's own crop, squared. 169.71 wide by 155.71 tall, so the box is
# widened to 169.71 on both sides and the ink centred in it.
VB = (9, 9 - (169.71 - 155.71) / 2, 169.71, 169.71)

PNGS = [32, 64, 180, 192, 512]
ICO = [16, 32, 48]


def svg():
    body = []
    for cx, cy, r in MARK:
        hx, hy = cx + HX * r, cy + HY * r
        body.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#qb)"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#qr)"/>'
            f'<ellipse cx="{hx:.2f}" cy="{hy:.2f}" rx="{HRX * r:.2f}" ry="{HRY * r:.2f}"'
            f' transform="rotate({HROT} {hx:.2f} {hy:.2f})" fill="url(#qh)"/>')
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="{VB[0]:g} {VB[1]:g} {VB[2]:g} {VB[3]:g}" '
        f'role="img" aria-label="Quenora">'
        '<defs>'
        '<radialGradient id="qb" cx="0.5" cy="0.5" r="0.53" fx="0.32" fy="0.29">'
        '<stop offset="0" stop-color="#F7DCC2"/><stop offset="0.18" stop-color="#E9A063"/>'
        '<stop offset="0.50" stop-color="#C97A3C"/><stop offset="0.85" stop-color="#A55F2A"/>'
        '<stop offset="1" stop-color="#7E4620"/></radialGradient>'
        '<radialGradient id="qr" cx="0.5" cy="0.5" r="0.52" fx="0.76" fy="0.79">'
        '<stop offset="0" stop-color="#F2CDA4" stop-opacity="0.42"/>'
        '<stop offset="0.5" stop-color="#F2CDA4" stop-opacity="0.06"/>'
        '<stop offset="1" stop-color="#F2CDA4" stop-opacity="0"/></radialGradient>'
        '<radialGradient id="qh" cx="0.5" cy="0.5" r="0.5">'
        '<stop offset="0" stop-color="#FFFFFF" stop-opacity="0.92"/>'
        '<stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></radialGradient>'
        '</defs>' + "".join(body) + '</svg>')


RASTER = r"""
const {chromium} = require('playwright');
const fs = require('fs');
const [svgPath, outDir, sizesJson] = process.argv.slice(2);
const svg = fs.readFileSync(svgPath, 'utf8');
(async () => {
  const b = await chromium.launch();
  for (const s of JSON.parse(sizesJson)) {
    /* deviceScaleFactor 1 and a viewport of exactly s: the SVG is rendered AT
       the target size rather than downsampled from a larger one, so the
       rasteriser antialiases against the real pixel grid. */
    const c = await b.newContext({viewport: {width: s, height: s},
                                  deviceScaleFactor: 1});
    const pg = await c.newPage();
    await pg.setContent('<style>html,body{margin:0;padding:0;background:transparent}' +
      'svg{display:block;width:' + s + 'px;height:' + s + 'px}</style>' + svg);
    await pg.waitForTimeout(60);
    await pg.screenshot({path: outDir + '/_raster-' + s + '.png', omitBackground: true});
    await c.close();
  }
  await b.close();
  console.log('rendered ' + JSON.parse(sizesJson).join(', '));
})();
"""


def main():
    open(os.path.join(BRAND, "quenora-icon.svg"), "w").write(svg())
    print("  quenora-icon.svg: the nine circles, %d bytes" % len(svg()))

    tmp = os.path.join(TEST, "_raster.js")
    open(tmp, "w").write(RASTER)
    sizes = sorted(set(PNGS + ICO))
    try:
        r = subprocess.run(
            ["node", tmp, os.path.join(BRAND, "quenora-icon.svg"), BRAND, json.dumps(sizes)],
            cwd=TEST, capture_output=True, text=True)
        if r.returncode:
            sys.exit("  rasteriser failed:\n" + (r.stderr or r.stdout)[:600])
        print("  " + r.stdout.strip())
    finally:
        os.path.exists(tmp) and os.remove(tmp)

    """The .ico, written by hand from the three separate renders.

    Pillow's ICO writer takes ONE image and downsamples it to whatever sizes
    you list, so saving from the 16px frame produced a one-frame icon and
    saving from the 48px one would have thrown away the 16 and 32 renders
    that were made against their own pixel grid. The container is trivial —
    a 6-byte header, a 16-byte directory entry per frame, then the frames —
    and PNG-encoded frames inside an .ico are understood by every browser
    and by Windows since Vista."""
    ico_png = {}
    for s in ICO:
        with open(os.path.join(BRAND, "_raster-%d.png" % s), "rb") as fh:
            ico_png[s] = fh.read()

    header = struct.pack("<HHH", 0, 1, len(ICO))
    offset = len(header) + 16 * len(ICO)
    entries, blobs = b"", b""
    for s in ICO:
        data = ico_png[s]
        entries += struct.pack("<BBBBHHII",
                               0 if s >= 256 else s,   # width, 0 means 256
                               0 if s >= 256 else s,   # height
                               0,                      # palette, 0 = truecolour
                               0,                      # reserved
                               1,                      # colour planes
                               32,                     # bits per pixel
                               len(data), offset)
        blobs += data
        offset += len(data)
    with open(os.path.join(BRAND, "favicon.ico"), "wb") as fh:
        fh.write(header + entries + blobs)

    for s in PNGS:
        os.replace(os.path.join(BRAND, "_raster-%d.png" % s),
                   os.path.join(BRAND, "quenora-icon-%d.png" % s))
    for s in ICO:
        p = os.path.join(BRAND, "_raster-%d.png" % s)
        os.path.exists(p) and os.remove(p)

    for name in ["quenora-icon-%d.png" % s for s in PNGS] + ["favicon.ico"]:
        print("  %-24s %6d bytes" % (name, os.path.getsize(os.path.join(BRAND, name))))


if __name__ == "__main__":
    main()

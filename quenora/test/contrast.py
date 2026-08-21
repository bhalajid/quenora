#!/usr/bin/env python3
"""WCAG AA contrast check, computed from the CSS the pages actually declare.

Two palettes ship side by side: the editorial homepage (--void / --t1 / --ember)
and the legacy inner pages (--ink / --white / --grey). Rather than assume one
naming scheme, this reads whichever ground and foreground tokens each file
declares and checks every pair it finds.

Thresholds:  4.5:1 body text   ·   3.0:1 large display accents
"""
import glob
import os
import re
import sys


def lum(hex_colour):
    h = hex_colour.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return .2126 * f(r) + .7152 * f(g) + .0722 * f(b)


def ratio(a, b):
    l = sorted([lum(a), lum(b)], reverse=True)
    return (l[0] + .05) / (l[1] + .05)


GROUNDS = ("--void", "--ink")
FOREGROUNDS = ("--t1", "--t2", "--t3", "--copper", "--copper-lt", "--ember",
               "--signal", "--white", "--grey", "--grey-d")
# accents used only at display size are held to the large-text threshold
LARGE_ONLY = {"--copper", "--ember"}


def main(root="."):
    failures, checked = [], 0
    for path in sorted(glob.glob(os.path.join(root, "*.html"))):
        html = open(path, encoding="utf-8").read()
        name = os.path.basename(path)

        ground = None
        for token in GROUNDS:
            m = re.search(re.escape(token) + r":\s*(#[0-9A-Fa-f]{6})", html)
            if m:
                ground = m.group(1)
                break
        if not ground:
            continue

        for token in FOREGROUNDS:
            m = re.search(re.escape(token) + r":\s*(#[0-9A-Fa-f]{6})", html)
            if not m:
                continue
            c = ratio(m.group(1), ground)
            checked += 1
            minimum = 3.0 if token in LARGE_ONLY else 4.5
            if c < minimum:
                failures.append("   %-16s %-12s %-8s %5.2f:1  (min %.1f)"
                                % (name, token, m.group(1), c, minimum))

    print("   %d token pairs checked across the deployed palettes" % checked)
    if failures:
        print("\n".join(failures))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))

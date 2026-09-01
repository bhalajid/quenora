#!/usr/bin/env python3
"""One site, one palette and one wordmark.

Two design generations live in this repo. Pages from the older one carry their
own token block and their own lockup — a cool #F8FAFC where the rest of the
site is a warm #F2EFE8, a slightly different black, neutral hairlines instead
of warm ones, and a wordmark with a copper initial and a glow behind the mark.

Each time one of those pages was reached from the current header it read as a
different company, and each time it was a person who noticed rather than a
test: capabilities, then work, then approach. This checks the palette and the
lockup mechanically so the next one fails the build instead.
"""
import os
import re
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = ("test", "node_modules", "api", "assets", "study")
SKIP_FILES = {"index-old-backup.html"}

# The ground and the ink, whatever a page calls its tokens.
GROUND = "#07070A"
INK = "#F2EFE8"
GROUND_ALIASES = ("--void", "--ink")
INK_ALIASES = ("--t1", "--white")

# Things that belonged to the previous generation and must not come back.
BANNED = [
    (re.compile(r"--white:\s*#F8FAFC", re.I),
     "cool #F8FAFC text — the site sets a warm #F2EFE8"),
    (re.compile(r"--ink:\s*#0A0A0B", re.I),
     "#0A0A0B ground — the site sets #07070A"),
    (re.compile(r"--line(?:-2)?:\s*rgba\(255,\s*255,\s*255", re.I),
     "neutral white hairlines — the site tints them warm"),
    (re.compile(r"\.brand\s+b\s+em\s*\{[^}]*color:\s*var\(--copper\)", re.I),
     "the copper initial in the wordmark — the lockup is one colour"),
    (re.compile(r"\.brand\s+svg\s*\{[^}]*drop-shadow", re.I),
     "a glow behind the mark — the home page lockup has none"),
    (re.compile(r"\.navcta\s*\{\s*display:\s*none", re.I),
     "the header CTA hidden on small screens — every other page keeps it"),
]


def pages():
    out = []
    for d, dirs, fs in os.walk(ROOT):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS and not x.startswith(".")]
        for f in fs:
            if f.endswith(".html") and f not in SKIP_FILES:
                out.append(os.path.relpath(os.path.join(d, f), ROOT))
    return sorted(out)


def token(css, names):
    for n in names:
        m = re.search(re.escape(n) + r":\s*(#[0-9A-Fa-f]{6})", css)
        if m:
            return m.group(1).upper()
    return None


bad, checked = [], 0
for rel in pages():
    html = open(os.path.join(ROOT, rel), encoding="utf-8").read()
    styles = " ".join(re.findall(r"<style[^>]*>(.*?)</style>", html, re.S))
    if not styles:
        continue
    checked += 1

    g = token(styles, GROUND_ALIASES)
    i = token(styles, INK_ALIASES)
    if g and g != GROUND:
        bad.append("%s: ground is %s, the site is %s" % (rel, g, GROUND))
    if i and i != INK:
        bad.append("%s: body text is %s, the site is %s" % (rel, i, INK))

    for pat, why in BANNED:
        if pat.search(styles):
            bad.append("%s: %s" % (rel, why))

    # every page that shows the wordmark must load the serif the site sets
    # emphasis in, so a heading with <em> does not fall back to italic Inter
    if re.search(r"<h[1-3][^>]*>[^<]*<em>", html) and "Playfair" not in html:
        bad.append("%s: a heading uses <em> but the serif is not loaded" % rel)

print("  %d page(s) checked for design drift" % checked)
if bad:
    for b in bad:
        print("   " + b)
    print("  %d drift(s)" % len(bad))
    sys.exit(1)
print("  one palette, one wordmark, everywhere")

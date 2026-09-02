#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quenora — build the contact QR.

The code encodes a URL rather than the vCard itself. A vCard is ~300 bytes,
which makes a dense code that scans badly from a printed card at a distance,
and a code carrying the card directly can never be counted or corrected. A
short URL gives a sparse, forgiving code, one number to change when a number
changes, and a scan count.

    quenora.ai/c        the card on the site and in the footer
    quenora.ai/c?k=<id> a printed instance — a business card, an event stand

The id says which printed run was scanned. It does not say who scanned it:
there is no cookie, no IP stored and no user agent stored, because the privacy
notice says this site does not track and that stays true.

Run:  python3 build_qr.py
"""
import os
import sys

try:
    import segno
except ImportError:
    sys.exit("needs segno — /tmp/qvenv/bin/pip install segno")

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "assets")

# error correction H tolerates roughly 30% damage, which is what a card that
# has been in a wallet for six months actually needs
CODES = [
    ("qr-card",  "https://quenora.ai/c",            "the site and the footer"),
    ("qr-print", "https://quenora.ai/c?k=card",     "printed business cards"),
    ("qr-event", "https://quenora.ai/c?k=event",    "trade stands and events"),
]

os.makedirs(OUT, exist_ok=True)
print("contact QR")
for name, url, why in CODES:
    qr = segno.make(url, error="h", micro=False)
    path = os.path.join(OUT, name + ".svg")
    # dark on transparent so it sits on either theme; the quiet zone is part
    # of the spec, not padding — scanners need it
    qr.save(path, kind="svg", scale=1, border=4,
            dark="#07070A", light=None, svgclass=None, lineclass=None,
            omitsize=True, xmldecl=False, svgns=True)
    kb = os.path.getsize(path) / 1024
    print("  %-9s %-32s %2d modules  %4.1f KB  · %s"
          % (name, url, qr.symbol_size(scale=1, border=0)[0], kb, why))

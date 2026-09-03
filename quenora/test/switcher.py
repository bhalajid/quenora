#!/usr/bin/env python3
"""The language switcher must have exactly one click handler.

It had two. build_i18n.py appends the switcher script on every run and removes
the previous copy first; that removal matched on the script's *contents* until
it was changed to match a data-generated marker — and the scripts already in
the source pages predated the marker, so they were never removed and a second
tagged copy was appended on top.

Two handlers both call classList.toggle('open') on the same click. The menu
opened and closed in the same event, so the dropdown could not be used at all
on any page in any language, and nothing in the gate noticed.

This counts handlers and checks the parts are present and wired together.
"""
import os
import re
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = ("test", "node_modules", "api", "assets", "study")
SKIP_FILES = {"index-old-backup.html"}


def pages():
    out = []
    for d, dirs, fs in os.walk(ROOT):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS and not x.startswith(".")]
        for f in fs:
            if f.endswith(".html") and f not in SKIP_FILES:
                out.append(os.path.relpath(os.path.join(d, f), ROOT)
                           .replace(os.sep, "/"))
    return sorted(out)


bad, checked = [], 0
for rel in pages():
    html = open(os.path.join(ROOT, rel), encoding="utf-8").read()

    has_btn = 'id="langBtn"' in html
    has_menu = 'id="langMenu"' in html
    handlers = len(re.findall(r"getElementById\('langBtn'\)", html))

    if not has_btn and not has_menu and handlers == 0:
        continue                      # English-only page, no switcher by design
    checked += 1

    if handlers != 1:
        bad.append("%s: %d click handler(s) on the switcher — %s"
                   % (rel, handlers,
                      "two both toggle, so it opens and closes on one click"
                      if handlers > 1 else "the button does nothing"))
    if has_btn != has_menu:
        bad.append("%s: button and menu are not both present" % rel)
    if has_btn and 'aria-controls="langMenu"' not in html:
        bad.append("%s: the button does not point at the menu it controls" % rel)
    if has_menu:
        langs = re.findall(r'<li><a[^>]*hreflang="([^"]+)"', html)
        if sorted(langs) != ["de", "en", "fr"]:
            bad.append("%s: menu offers %s, expected de/en/fr" % (rel, langs or "nothing"))
        cur = re.findall(r'aria-current="true"[^>]*hreflang="([^"]+)"'
                         r'|hreflang="([^"]+)"[^>]*aria-current="true"', html)
        flat = [a or b for a, b in cur]
        lang = rel.split("/")[0] if "/" in rel else "en"
        # es/ and it/ are built but not offered, so the page's own language is
        # not in the menu and nothing there can be marked current. That is
        # correct for a language nobody can navigate to.
        want = 0 if lang in ("es", "it") else 1
        if len(flat) != want:
            bad.append("%s: %d entries marked as the current language, expected %d"
                       % (rel, len(flat), want))

print("  %d page(s) with a language switcher checked" % checked)
if bad:
    for b in bad:
        print("   " + b)
    print("  %d problem(s)" % len(bad))
    sys.exit(1)
print("  one handler, button and menu wired, three languages, one marked current")

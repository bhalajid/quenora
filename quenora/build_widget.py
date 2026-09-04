#!/usr/bin/env python3
"""
build_widget.py — put Nora on every page, from one source.

RUN THIS FIRST, BEFORE build_i18n.py. It writes into the English pages, and
build_i18n regenerates de/ and fr/ from those, so the order carries the widget
into every language for free. build.sh enforces it.

────────────────────────────────────────────────────────────────────────
WHY

The assistant was built into the home page and lived only there. A visitor who
arrived on capabilities or engineering — which is most of them, because those
are the pages that rank and the pages we link to — had no way to ask anything.
The one thing on this site that demonstrates what the firm does was reachable
from one page in eleven.

It is now injected into all of them from widget/, so there is exactly one copy
to change and no way for ten pages to drift away from it.

WHY MARKERS RATHER THAN APPENDING

Each injection is delimited, so a second run replaces what the first run wrote
instead of stacking another copy. The site has already shipped a bug of exactly
that shape: two language-switcher handlers both toggling the same menu, so it
opened and closed on one click, on every page, in every language, for four
commits. An injector that is not idempotent is that bug waiting to happen.
────────────────────────────────────────────────────────────────────────
"""
import os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))

# Every page a visitor can land on. products is unlisted but still generated,
# and someone holding its URL should get the same assistant.
PAGES = ["index.html", "engineering.html", "capabilities.html", "products.html",
         "approach.html", "work.html", "contact.html", "about.html",
         "impressum.html", "privacy.html"]

CSS_M  = ("/*WIDGET:CSS*/",  "/*/WIDGET:CSS*/")
HTML_M = ("<!--WIDGET:HTML-->", "<!--/WIDGET:HTML-->")
JS_M   = ("<!--WIDGET:JS-->", "<!--/WIDGET:JS-->")


def read(name):
    return open(os.path.join(ROOT, "widget", name), encoding="utf-8").read().strip()


def splice(s, marks, body):
    """Replace between the markers, or insert markers around a first write."""
    a, b = marks
    if a in s and b in s:
        i, j = s.index(a), s.index(b) + len(b)
        return s[:i] + a + "\n" + body + "\n" + b + s[j:], True
    if a in s:                      # first run: only the opening marker exists
        i = s.index(a) + len(a)
        return s[:i] + "\n" + body + "\n" + b + s[i:], True
    return s, False


def place(s, marks, body, before):
    """Put a first-time block immediately before `before`."""
    a, b = marks
    if a in s:
        return splice(s, marks, body)
    if before not in s:
        return s, False
    i = s.rindex(before)
    return s[:i] + a + "\n" + body + "\n" + b + "\n" + s[i:], True


def main():
    css, html, js = read("assistant.css"), read("assistant.html"), read("assistant.js")
    js_block = "<script>\n" + js + "\n</script>"

    done = 0
    for page in PAGES:
        p = os.path.join(ROOT, page)
        if not os.path.exists(p):
            print("  skip %-20s (not in the repo)" % page)
            continue
        s = open(p, encoding="utf-8").read()
        before = len(s)

        s, ok1 = place(s, CSS_M, css, "</style>")
        s, ok2 = place(s, HTML_M, html, "</body>")
        s, ok3 = place(s, JS_M, js_block, "</body>")

        if not (ok1 and ok2 and ok3):
            print("  FAIL %-20s no </style> or </body> to anchor to" % page)
            return 1
        open(p, "w", encoding="utf-8").write(s)
        done += 1
        print("  %-22s %+6d bytes" % (page, len(s) - before))

    print("  Nora on %d English page(s); build_i18n carries her into de/ and fr/" % done)
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Resolve every internal link the way a browser does, from the URL that
Vercel actually serves — not from the path on disk.

vercel.json sets cleanUrls, so /de/index.html is 308-redirected to /de, with
no trailing slash. A browser resolves a relative href against the *directory*
of the current URL, and the directory of "/de" is "/". Every relative link on
the German and French home pages therefore resolved to the English site in
production: href="engineering.html" fetched /engineering.html.

Every earlier link check read the filesystem, where the same links are
correct, so none of them could see it. This one models the deployed URL shape
and fails if a link 404s or crosses out of its language.
"""
import io, os, re, sys
from urllib.parse import urljoin, urlparse

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))
DOMAIN = "https://quenora.ai"
CLEAN_URLS = True          # mirrors vercel.json
LEGAL = {"impressum.html", "privacy.html"}   # English-only by design


def landing(rel):
    """The URL a visitor ends up on after Vercel's redirects."""
    u = "/" + rel.replace(os.sep, "/")
    if CLEAN_URLS:
        if u.endswith("/index.html"):
            u = u[: -len("/index.html")] or "/"
        elif u.endswith(".html"):
            u = u[: -len(".html")]
    return DOMAIN + u


def to_file(url):
    p = urlparse(url).path
    if p.endswith("/"):
        p += "index.html"
    if not p.endswith(".html"):
        for c in (p.lstrip("/") + ".html",
                  os.path.join(p.lstrip("/"), "index.html")):
            if os.path.exists(os.path.join(ROOT, c)):
                return c
        return p.lstrip("/") + ".html"
    return p.lstrip("/")


def pages():
    out = []
    for d, _, fs in os.walk(ROOT):
        if any(x in d for x in (os.sep + "test", os.sep + "node_modules",
                                os.sep + "api", os.sep + "assets")):
            continue
        for f in fs:
            if f.endswith(".html") and "backup" not in f:
                out.append(os.path.relpath(os.path.join(d, f), ROOT))
    return sorted(out)


bad, n = [], 0
for pg in pages():
    src = pg.split("/")[0] if "/" in pg else "en"
    if src.endswith(".html"):
        src = "en"
    base = landing(pg)
    s = io.open(os.path.join(ROOT, pg), encoding="utf-8").read()
    for tag in re.findall(r"<a\s[^>]*>", s):
        m = re.search(r'href="([^"]+)"', tag)
        if not m:
            continue
        h = m.group(1)
        if h.startswith(("http", "mailto:", "tel:", "#")) or h.startswith("'"):
            continue
        f = to_file(urljoin(base, h))
        n += 1
        if not os.path.exists(os.path.join(ROOT, f)):
            bad.append("%s: %s -> 404 %s" % (pg, h, f))
            continue
        tgt = f.split("/")[0] if "/" in f else "en"
        if tgt.endswith(".html"):
            tgt = "en"
        if tgt != src and f not in LEGAL and "hreflang=" not in tag:
            bad.append("%s: %s leaves %s for %s (%s)" % (pg, h, src, tgt, f))

print("  %d internal links resolved against the deployed URL shape" % n)
if bad:
    for b in bad:
        print("   " + b)
    print("  %d broken" % len(bad))
    sys.exit(1)
print("  no 404s, no link leaves its language")

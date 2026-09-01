#!/usr/bin/env python3
"""The site declares one address, and it is the one it is launching on.

Two failures this guards against:

  * a *.vercel.app URL reaching a visitor. The deployment host is an
    implementation detail; end users should never see it in the address bar,
    in a canonical, in a share card or in a link. vercel.json redirects the
    host permanently, and this makes sure nothing in the markup sends anyone
    back to it.

  * a canonical, hreflang, og:url or sitemap entry written in the .html form.
    vercel.json sets cleanUrls, so /services.html is 308-redirected to
    /services. Declaring the redirecting form means every canonical points at
    a redirect rather than at the page.

Naming Vercel Inc. in the privacy notice is required by Article 13 GDPR and is
explicitly allowed — this checks URLs, not prose.
"""
import os
import re
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))
DOMAIN = "https://quenora.ai"
SKIP_DIRS = ("test", "node_modules", "api", "assets", "study")
SKIP_FILES = {"index-old-backup.html"}

HOST_URL = re.compile(r'(?:href|src|content)="(https?://[^"]*vercel\.app[^"]*)"', re.I)
DECLARED = re.compile(
    r'<link[^>]+rel="canonical"[^>]+href="([^"]+)"'
    r'|<link[^>]+href="([^"]+)"[^>]+rel="canonical"'
    r'|<link[^>]+rel="alternate"[^>]+href="([^"]+)"'
    r'|<link[^>]+href="([^"]+)"[^>]+rel="alternate"'
    r'|<meta[^>]+property="og:url"[^>]+content="([^"]+)"'
    r'|<meta[^>]+content="([^"]+)"[^>]+property="og:url"')


def files():
    out = []
    for d, dirs, fs in os.walk(ROOT):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS and not x.startswith(".")]
        for f in fs:
            if (f.endswith(".html") or f.endswith(".xml") or f == "robots.txt") \
               and f not in SKIP_FILES:
                out.append(os.path.relpath(os.path.join(d, f), ROOT))
    return sorted(out)


bad, n = [], 0
for rel in files():
    text = open(os.path.join(ROOT, rel), encoding="utf-8").read()

    for m in HOST_URL.finditer(text):
        bad.append("%s: a visitor-facing URL on the deployment host — %s"
                   % (rel, m.group(1)))

    urls = []
    if rel.endswith(".xml"):
        urls = re.findall(r"<loc>([^<]+)</loc>", text) + \
               re.findall(r'<xhtml:link[^>]+href="([^"]+)"', text)
    else:
        for g in DECLARED.findall(text):
            u = next((x for x in g if x), None)
            if u:
                urls.append(u)
    for u in urls:
        n += 1
        if not u.startswith(DOMAIN):
            bad.append("%s: declares %s, not %s" % (rel, u, DOMAIN))
        elif u.endswith(".html") or (u.endswith("/") and u != DOMAIN + "/"):
            bad.append("%s: %s is the redirecting form under cleanUrls" % (rel, u))

print("  %d declared URL(s) checked across %d file(s)" % (n, len(files())))
if bad:
    for b in sorted(set(bad)):
        print("   " + b)
    print("  %d problem(s)" % len(set(bad)))
    sys.exit(1)
print("  every declared URL is quenora.ai, in the form the site actually serves")

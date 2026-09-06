#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_footer.py — one footer map, written into every English page.

WHY THIS EXISTS

The site had two footer systems. index.html used a .fgrid of plain divs with
<h3> headings; the inner pages used .foot-row / .foot-col with <h5>. The three
link columns were maintained separately in both, so every footer change had to
be made twice and the two drifted — which is how the audit found a footer
sending Approach, Capabilities and Work to a previous design generation while
the header sent the same three words somewhere else.

This generator owns the three link columns — the map, the legal links and the
social row — and writes the same ones into every page. It deliberately does
NOT touch the brand column or the bottom bar: those carry each generation's
own markup (an <img> lockup on the home page, an inline <use href="#mark9">
on the inner pages), and unifying them means re-theming the inner pages, which
is scope-2 work and not this.

So: the footer NAVIGATION is identical everywhere by construction. The
surrounding shell still belongs to whichever generation the page is on.

The heading level follows the page's own system rather than being forced, so
the existing stylesheet keeps applying.

ORDER: this must run BEFORE build_nav.py. build_nav re-points header and
footer links from one destination map and marks the current page; if it ran
first, everything it did here would be overwritten.
"""
import os
import re
import sys

from bs4 import BeautifulSoup as BS

ROOT = os.path.dirname(os.path.abspath(__file__))
SKIP = {"index-old-backup.html", "story.html"}

# Pricing has no page yet. The client is writing one; until it exists this
# points at the pricing chapter on the home page, which is where that content
# lives today. A footer link to a page that does not exist is a 404 on every
# page of the site, and stage 4c fails the build on it. One line to switch.
MAP = [
    ("Approach",     "approach.html"),
    ("Capabilities", "capabilities.html"),
    ("Pricing",      "index.html#commercial"),
    ("Work",         "work.html"),
    ("About",        "about.html"),
    ("Contact",      "index.html#climax"),
]

LEGAL = [
    ("Legal notice · Impressum", "impressum.html"),
    ("Privacy notice",           "privacy.html"),
]

# Verified reachable before being linked, which is the rule this footer earned
# the hard way: it once shipped three dead "#" anchors. YouTube is absent on
# purpose — the URL supplied 404s, and youtube.com/@quenora is a different
# account ("QUENORA — Honour Thy Self"), so linking it would send visitors to
# a stranger's channel. It goes in the moment there is a real one.
SOCIAL = [
    ("LinkedIn", "https://www.linkedin.com/company/quenora",
     '<path d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9h4v12H3zM9 9h3.8v1.7h.1c.5-1 '
     '1.8-2.1 3.7-2.1 4 0 4.4 2.4 4.4 5.5V21h-4v-6.1c0-1.5 0-3.3-2-3.3s-2.3 1.6-2.3 3.2V21H9z"/>'),
    ("Instagram", "https://www.instagram.com/quenora.ai/",
     '<rect x="3" y="3" width="18" height="18" rx="5" fill="none" stroke="currentColor" '
     'stroke-width="2"/><circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" '
     'stroke-width="2"/><circle cx="17.3" cy="6.7" r="1.3"/>'),
    ("Facebook", "https://www.facebook.com/people/Quenora-Consulting/61593930577480/",
     '<path d="M22 12.1a10 10 0 1 0-11.6 9.9v-7H7.9v-2.9h2.5V9.9c0-2.5 1.5-3.9 3.8-3.9 1.1 0 2.2.2 '
     '2.2.2v2.5h-1.2c-1.3 0-1.7.8-1.7 1.6v1.9h2.8l-.4 2.9h-2.4v7A10 10 0 0 0 22 12.1z"/>'),
    ("X", "https://x.com/quenora_ai",
     '<path d="M17.5 3h3l-6.6 7.5L21.8 21h-5.9l-4.6-6-5.3 6H3l7-8L2.5 3h6l4.2 5.5zm-1 16.2h1.7L7.6 '
     '4.7H5.8z"/>'),
]


CSS = """/*FOOTER:CSS*/
/* the social row is a row of marks, not a stack of words */
.f-social{display:flex;flex-wrap:wrap;gap:14px;align-items:center}
.f-social a{display:inline-flex;align-items:center;justify-content:center;
  width:34px;height:34px;border:1px solid var(--line,rgba(242,239,232,.09));
  border-radius:2px;color:var(--t2,#A8AEBB);
  transition:color .25s ease,border-color .25s ease}
.f-social a:hover,.f-social a:focus-visible{color:var(--copper-lt,#E9A063);
  border-color:var(--copper-lt,#E9A063)}
.f-social svg{width:17px;height:17px;display:block}
/*/FOOTER:CSS*/"""


def cols(footer):
    """the four footer columns, whichever system this page is on"""
    row = footer.select_one(".fgrid") or footer.select_one(".foot-row")
    if row is None:
        return None, None
    kids = [c for c in row.find_all(recursive=False)]
    return row, kids


def build(path, page):
    html = open(path, encoding="utf-8").read()
    soup = BS(html, "html.parser")
    footer = soup.find("footer")
    if footer is None:
        return 0
    row, kids = cols(footer)
    if not kids or len(kids) < 2:
        return 0

    # keep whatever this page's system uses, so the stylesheet still applies
    heading = "h3"
    for k in kids[1:]:
        h = k.find(re.compile("^h[1-6]$"))
        if h is not None:
            heading = h.name
            break
    col_cls = kids[1].get("class") if len(kids) > 1 else None

    def col(title, links, nav_label, social=False):
        d = soup.new_tag("div")
        if col_cls:
            d["class"] = col_cls
        h = soup.new_tag(heading)
        h.string = title
        d.append(h)
        nav = soup.new_tag("nav")
        nav["aria-label"] = nav_label
        if social:
            nav["class"] = ["f-social"]
            for name, href, inner in links:
                a = soup.new_tag("a", href=href)
                a["rel"] = "noopener me"
                a["target"] = "_blank"
                # aria-label already names the link, so a visually hidden
                # duplicate of the name adds bytes and a second announcement.
                # The mark is inline SVG: it cannot fail to arrive the way a
                # linked image can, so there is nothing for it to fall back to.
                a["aria-label"] = name
                a.append(BS('<svg viewBox="0 0 24 24" aria-hidden="true" '
                            'fill="currentColor">' + inner + '</svg>',
                            "html.parser"))
                nav.append(a)
        else:
            for label, href in links:
                if page == "index.html" and href.startswith("index.html#"):
                    href = href[len("index.html"):]
                a = soup.new_tag("a", href=href)
                a.string = label
                nav.append(a)
        d.append(nav)
        return d

    new_cols = [
        col("Site map", MAP, "Footer"),
        col("Legal", LEGAL, "Legal"),
        col("Follow", SOCIAL, "Social", social=True),
    ]
    for k in kids[1:]:
        k.extract()
    for c in new_cols:
        row.append(c)

    s = str(soup)
    if "/*FOOTER:CSS*/" in s:
        s = re.sub(r"/\*FOOTER:CSS\*/.*?/\*/FOOTER:CSS\*/", lambda _m: CSS, s, flags=re.S)
    elif "</style>" in s:
        i = s.rindex("</style>")
        s = s[:i] + CSS + "\n" + s[i:]
    open(path, "w", encoding="utf-8").write(s)
    return 1


def main():
    pages = sorted(f for f in os.listdir(ROOT)
                   if f.endswith(".html") and f not in SKIP)
    n = 0
    for page in pages:
        n += build(os.path.join(ROOT, page), page)
    print("footer")
    print("  one map, one legal column, %d social marks — %d page(s)"
          % (len(SOCIAL), n))
    return 0


if __name__ == "__main__":
    sys.exit(main())

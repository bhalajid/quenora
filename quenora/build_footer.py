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

This generator owns the WHOLE footer — the brand column, the three link
columns and the bottom bar — and writes the same one into every page. The home
page's version is the one that wins.

It has to be self-contained to do that. The inner pages are still on the older
design generation and define neither the tokens the home page footer uses
(--sp3, --t2, --t3) nor its classes (.lockup, .desc, .fbot, .fgrid); all they
share is .brandimg. So the markup uses its own f- prefixed classes and the
stylesheet below carries every value with a var() fallback, rather than
borrowing whatever each page happens to define. A custom property with no
fallback is invalid at computed-value time and silently takes the initial
value, which is how the language menu once rendered with no panel at all.

The heading level still follows the page's own system, so an inner page's
existing footer heading styles keep applying.

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

# The footer maps the HOME PAGE, chapter by chapter; the header routes to the
# standalone pages. That is why the two use different words for the same
# subject — "Approach" here against "Phased Approach" in the header. One label
# meaning two different places on one page is the defect stage 4d exists to
# catch, and it is a bug this footer actually shipped once.
MAP = [
    ("Approach",     "index.html#journey"),      # chapter 04
    ("Capabilities", "index.html#solution"),     # chapter 05
    ("Pricing",      "index.html#commercial"),   # chapter 09
    ("Work",         "index.html#problem"),      # chapter 01
    ("About",        "index.html#who"),          # chapter 06
    ("Contact",      "index.html#climax"),
]

LEGAL = [
    ("Legal notice · Impressum", "impressum.html"),
    ("Privacy notice",           "privacy.html"),
]

# Verified reachable before being linked, which is the rule this footer earned
# the hard way: it once shipped three dead "#" anchors. YouTube took two
# tries: the first URL 404d and youtube.com/@quenora turned out to be a
# different account ("QUENORA — Honour Thy Self"). @quenora-ai is the real one
# — "Quenora Consulting - YouTube" — and was checked before being linked.
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
    # Outline body plus a solid triangle, the same construction as the
    # Instagram mark. The first attempt was a single path whose arc command
    # read "a3 3 0 0 2.1-2.1" — five numbers where an arc needs seven, so the
    # sweep flag got 2.1 and the browser rejected the whole path. It rendered
    # as an empty rounded box and only the console said why.
    ("YouTube", "https://www.youtube.com/@quenora-ai",
     '<rect x="1.6" y="4.6" width="20.8" height="14.8" rx="4" fill="none" '
     'stroke="currentColor" stroke-width="2"/><path d="M10.2 9.1v5.8l5-2.9z"/>'),
    ("X", "https://x.com/quenora_ai",
     '<path d="M17.5 3h3l-6.6 7.5L21.8 21h-5.9l-4.6-6-5.3 6H3l7-8L2.5 3h6l4.2 5.5zm-1 16.2h1.7L7.6 '
     '4.7H5.8z"/>'),
]


BLURB = ("Enterprise AI, engineered to operate. Built into what you already "
         "run, then handed over.")

CSS = """/*FOOTER:CSS*/
/* Self-contained on purpose — see the module docstring. Every value carries a
   fallback so this renders the same on a page that defines the new tokens and
   on one that does not. */
/* The two generations framed the footer differently: the home page's .wrap
   runs full width with a 20px margin and no padding, the inner pages' has
   max-width:1240px and 40px of padding — so the same footer started at a
   different place depending on the page. One frame for both. */
footer .wrap{max-width:1240px;margin-inline:auto;padding-inline:24px;width:100%}
footer .f-grid{display:grid;gap:38px;
  grid-template-columns:minmax(0,1.4fr) repeat(3,minmax(0,1fr))}
@media(max-width:900px){footer .f-grid{grid-template-columns:minmax(0,1fr) minmax(0,1fr)}}
@media(max-width:560px){footer .f-grid{grid-template-columns:minmax(0,1fr)}}
footer .f-lockup{display:flex;align-items:baseline;gap:9px;margin-bottom:20px}
footer .f-lockup img{display:block;width:118px;height:auto}
footer .f-lockup .f-desc{font-family:'JetBrains Mono',ui-monospace,monospace;
  font-size:10px;letter-spacing:.24em;text-transform:uppercase;
  color:var(--t3,#7C8290)}
footer .f-blurb{max-width:35ch;font-size:.96rem;color:var(--t2,#A8AEBB);margin:0}
footer .f-where{font-family:'JetBrains Mono',ui-monospace,monospace;
  font-size:11px;letter-spacing:.18em;text-transform:uppercase;
  color:var(--t3,#7C8290);margin:14px 0 0}
/* The column headings. The home page styled them copper at 10px; the inner
   pages styled the same headings grey at 11px, because each page's own
   stylesheet was deciding. Stated here, so "SITE MAP" reads the same on all
   eleven. The heading LEVEL still follows the page — h3 here, h5 there — so
   nothing else that targets those elements is disturbed. */
footer .f-grid h3,footer .f-grid h4,footer .f-grid h5{
  font-family:'JetBrains Mono',ui-monospace,monospace;font-size:10px;
  font-weight:500;letter-spacing:.24em;text-transform:uppercase;
  color:var(--copper-lt,#E9A063);margin:0 0 16px}
/* The link columns stack. impressum.html and privacy.html style footer navs
   as flex ROWS, so the site map ran across the page and straight through the
   Legal column — one page's stylesheet deciding the shape of a footer this
   file is supposed to own. Stated here, it is the same on all eleven. */
footer nav[aria-label="Footer"],
footer nav[aria-label="Legal"]{display:flex;flex-direction:column;
  align-items:flex-start;gap:14px}
/* the social row is a row of marks, not a stack of words */
.f-social{display:flex;flex-wrap:wrap;gap:14px;align-items:center}
.f-social a{display:inline-flex;align-items:center;justify-content:center;
  width:34px;height:34px;border:1px solid var(--line,rgba(242,239,232,.09));
  border-radius:2px;color:var(--t2,#A8AEBB);
  transition:color .25s ease,border-color .25s ease}
.f-social a:hover,.f-social a:focus-visible{color:var(--copper-lt,#E9A063);
  border-color:var(--copper-lt,#E9A063)}
.f-social svg{width:17px;height:17px;display:block}
footer .f-bot{display:flex;flex-wrap:wrap;gap:10px 24px;
  justify-content:space-between;margin-top:56px;padding-top:22px;
  border-top:1px solid var(--line,rgba(242,239,232,.09));
  font-size:.84rem;color:var(--t3,#7C8290)}
/*/FOOTER:CSS*/"""



def emit(css):
    """The stylesheet without its commentary.

    The rationale for each rule belongs in this file, where someone changing it
    will read it. Shipped, it is bytes on every page of the site that nobody
    sees — and stage 8 caps the home page at 220 KB, which those comments were
    quietly eating into. The delimiters stay: they are how the block is found
    and replaced on the next run.
    """
    body = re.sub(r"/\*(?!/?FOOTER:CSS\*/).*?\*/", "", css, flags=re.S)
    return re.sub(r"\n\s*\n+", "\n", body)



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
    if col_cls and "foot-col" not in col_cls:
        col_cls = None

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

    def brand():
        d = soup.new_tag("div")
        lock = soup.new_tag("div")
        lock["class"] = ["f-lockup"]
        img = soup.new_tag("img", src="/assets/brand/quenora-primary.svg")
        img["alt"] = "Quenora"
        img["width"] = "1439"
        img["height"] = "525"
        img["decoding"] = "async"
        img["class"] = ["brandimg"]
        lock.append(img)
        desc = soup.new_tag("span")
        desc["class"] = ["f-desc"]
        desc.string = "Consulting"
        lock.append(desc)
        d.append(lock)
        p = soup.new_tag("p")
        p["class"] = ["f-blurb"]
        p.string = BLURB
        d.append(p)
        w = soup.new_tag("p")
        w["class"] = ["f-where"]
        w.string = "Working internationally"
        d.append(w)
        return d

    new_cols = [
        brand(),
        col("Site map", MAP, "Footer"),
        col("Legal", LEGAL, "Legal"),
        col("Follow", SOCIAL, "Social", social=True),
    ]
    for k in kids:
        k.extract()
    cls = row.get("class") or []
    if "f-grid" not in cls:
        row["class"] = cls + ["f-grid"]
    for c in new_cols:
        row.append(c)

    # the bottom bar, same one everywhere. .fbot on the home page,
    # .foot-line on the inner pages — one class now, and one set of contents.
    bot = footer.select_one(".fbot, .foot-line, .f-bot")
    nb = soup.new_tag("div")
    nb["class"] = ["f-bot"]
    left = soup.new_tag("span")
    left.string = "© 2026 Quenora Consulting"
    right = soup.new_tag("span")
    right.append("Bad Friedrichshall, Germany · ")
    a1 = soup.new_tag("a", href="impressum.html")
    a1.string = "Legal notice"
    right.append(a1)
    right.append(" · ")
    a2 = soup.new_tag("a", href="privacy.html")
    a2.string = "Privacy"
    right.append(a2)
    nb.append(left)
    nb.append(right)
    if bot is not None:
        bot.replace_with(nb)
    else:
        row.insert_after(nb)

    s = str(soup)
    if "/*FOOTER:CSS*/" in s:
        s = re.sub(r"/\*FOOTER:CSS\*/.*?/\*/FOOTER:CSS\*/", lambda _m: emit(CSS), s, flags=re.S)
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

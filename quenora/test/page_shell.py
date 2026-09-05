#!/usr/bin/env python3
"""
4i — every page is built from the same shell.

This stage exists because a whole class of defect was reported from the live
site that no existing stage looked for, and that I had repeatedly claimed to
have checked. Every one of these was true at once:

  · the home page's logo sat 160px to the right of its own headline, because
    the hero kept a wider container than the header
  · engineering.html indented its body 20px less than every other page and
    opened its headline 60px lower
  · four of eight pages had no ember emphasis in the headline at all —
    capabilities, work, contact and products were missing the one typographic
    signature the brand has

None of it was visible to a link checker, a contrast checker or a translation
checker. It is visible to a reader in a second, which is the wrong way round.

What is checked here is only what can be checked from the markup with
certainty. Geometry that needs a layout engine is asserted through the shared
container instead: if every page carries the generated container block and
none of them override it afterwards, they cannot drift apart.
"""
import os, re, sys
from bs4 import BeautifulSoup as BS

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "..")

PAGES = ["index.html", "engineering.html", "capabilities.html", "products.html",
         "approach.html", "work.html", "contact.html"]
LANGS = ["", "de", "fr"]

fail, checked = [], 0

for lang in LANGS:
    for page in PAGES:
        p = os.path.join(ROOT, lang, page) if lang else os.path.join(ROOT, page)
        if not os.path.exists(p):
            continue
        checked += 1
        where = ("%s/%s" % (lang, page)).lstrip("/")
        raw = open(p, encoding="utf-8").read()
        soup = BS(raw, "html.parser")
        main = soup.find("main")

        if main is None:
            fail.append("%s: no <main>" % where)
            continue

        h1 = main.find("h1")
        if h1 is None:
            fail.append("%s: no headline" % where)
            continue

        # 1 — the brand's one typographic signature
        ems = h1.find_all("em")
        if len(ems) != 1:
            fail.append("%s: headline carries %d <em>, expected exactly 1 — "
                        "the ember word is the brand's signature"
                        % (where, len(ems)))
        elif not ems[0].get_text(strip=True):
            fail.append("%s: the <em> in the headline is empty" % where)

        # 2 — the emphasis has to be a word, not the whole sentence. An <em>
        #     wrapping everything is the same as no emphasis at all.
        if len(ems) == 1:
            whole = len(h1.get_text(strip=True))
            part = len(ems[0].get_text(strip=True))
            if whole and part / whole > 0.6:
                fail.append("%s: the <em> covers %d%% of the headline — that is "
                            "not emphasis" % (where, round(100 * part / whole)))

        # 3 — the shared container, so the logo and the body start at the same x
        if "/*NAV:CSS*/" not in raw:
            fail.append("%s: no generated container block — run build_nav.py"
                        % where)
        else:
            tail = raw.split("/*/NAV:CSS*/", 1)[-1]
            head = tail.split("</style>", 1)[0] if "</style>" in tail else ""
            # a later .wrap rule with padding would silently win on order
            if re.search(r"(^|[},])\s*\.wrap\s*\{[^}]*padding", head):
                fail.append("%s: a .wrap rule after the generated block "
                            "overrides the shared container" % where)

        # 4 — one language switcher, so a visitor is never stranded
        if lang or page not in ("about.html",):
            if soup.find(class_="langsel") is None:
                fail.append("%s: no language switcher in the header" % where)

print("  %d page(s) checked against the shared shell" % checked)
if fail:
    for f in fail[:25]:
        print("   " + f)
    if len(fail) > 25:
        print("   ... and %d more" % (len(fail) - 25))
    print("FAIL")
    sys.exit(1)
print("  every headline carries its ember word; every page shares one container")
print("PASS")

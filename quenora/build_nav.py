#!/usr/bin/env python3
"""
build_nav.py — the header tells you where you are, and goes straight there.

Runs after build_widget.py and before build_i18n.py, on the English pages
only; build_i18n carries the result into every language.

────────────────────────────────────────────────────────────────────────
FOUR THINGS, ALL REPORTED FROM THE LIVE SITE

1  NOTHING SAID WHICH PAGE YOU WERE ON

   Exactly one page carried an "on" class, hand-written, on Capabilities.
   Every other page's header looked identical to every other page's header.
   The style for it already existed and was simply never applied, which is
   the easiest kind of defect to walk past. It is generated now, for the
   header and the footer, from the page's own filename.

2  APPROACH WENT TO THE HOME PAGE

   The nav sent "Approach" to index.html#journey — the chapter on the home
   page — while approach.html sat there unlinked from the navigation. So the
   home page loaded, painted, and then jumped. Capabilities, Engineering and
   Work all went straight to their own pages; only Approach did not.

   One label now means one destination, from every page.

3  THE LINKS MOVED WHEN YOU LEFT THE HOME PAGE

   The inner pages lay the header out with justify-content:space-between over
   five children, so the links sat in the middle of the bar. The home page
   gives .navlinks margin-left:auto, which pushes them right, against the
   language button and the call to action. Two different headers on one site,
   and the links visibly jumped as soon as you clicked anything.

4  A RELOAD PUT YOU BACK IN THE MIDDLE OF A CHAPTER

   The browser restores scroll position by default. On a chaptered page whose
   sections reveal on scroll, that drops the reader into the middle of a
   narrative with the reveals already spent — it reads as a broken page rather
   than as a convenience. A reload now returns to the top, unless the URL
   carries an anchor, which is an explicit request for a place.
────────────────────────────────────────────────────────────────────────
"""
import os, re, sys
from bs4 import BeautifulSoup as BS

ROOT = os.path.dirname(os.path.abspath(__file__))

PAGES = ["index.html", "engineering.html", "capabilities.html", "products.html",
         "approach.html", "work.html", "contact.html", "story.html",
         "impressum.html", "privacy.html"]

# One label, one destination. About has no page of its own, so it stays a
# chapter on the home page — stated here rather than left to look like an
# oversight.
DEST = {
    "Approach":     "approach.html",
    "Capabilities": "capabilities.html",
    "Engineering":  "engineering.html",
    "Work":         "work.html",
    "About":        "index.html#who",
    # The enquiry form lives in the home page's closing chapter. contact.html
    # exists but carries no form, so sending "Contact" there would land a
    # visitor on a page with nothing to fill in — the CTA and the footer both
    # point at the form itself.
    "Contact":      "index.html#climax",
    "Home":         "index.html",
}

CSS_M = ("/*NAV:CSS*/", "/*/NAV:CSS*/")
JS_M  = ("<!--NAV:JS-->", "<!--/NAV:JS-->")

NAV_CSS = """/* The inner pages spread five header children with space-between, which put
   the links in the middle of the bar while the home page pushed them right.
   Same rule on every page now, so nothing moves when you navigate. */
.navlinks{margin-left:auto}"""

NAV_JS = """<script>
/* A reload used to drop the reader back into the middle of a chapter with its
   scroll-triggered reveals already spent, which reads as a broken page rather
   than as a convenience. Returning to the top is the honest default; an anchor
   in the URL is an explicit request for a place and is left alone. */
(function(){
  /* The work page's field figure is verified by a headless harness with no
     history and no window; this must not throw there. */
  if(typeof history==='undefined'||typeof window==='undefined') return;
  if(!('scrollRestoration' in history)) return;
  history.scrollRestoration = 'manual';
  addEventListener('load', function(){
    if(location.hash) return;
    window.scrollTo(0, 0);
  });
})();
</script>"""


def splice(s, marks, body, before):
    a, b = marks
    if a in s and b in s:
        i, j = s.index(a), s.index(b) + len(b)
        return s[:i] + a + "\n" + body + "\n" + b + s[j:], True
    if before not in s:
        return s, False
    i = s.rindex(before)
    return s[:i] + a + "\n" + body + "\n" + b + "\n" + s[i:], True


def retarget_and_mark(soup, page):
    """Point every nav label at its one destination, and flag the current
    page. Both the header and the footer, because the release gate requires
    them to agree and a visitor reads whichever is nearer."""
    changed = marked = 0
    for root in (soup.find("header"), soup.find("footer")):
        if root is None:
            continue
        for a in root.find_all("a"):
            label = a.get_text(" ", strip=True)
            want = DEST.get(label)
            if not want:
                continue
            # On the home page the two anchor destinations are in-page, and
            # the header CTA has always written them relatively. Keeping the
            # same form means the header and the footer agree by destination.
            if page == "index.html" and want.startswith("index.html#"):
                want = want[len("index.html"):]
            if a.get("href") != want:
                a["href"] = want
                changed += 1
            cls = [c for c in (a.get("class") or []) if c != "on"]
            # "on" means this link points at the page you are reading. The
            # brand and the call to action are excluded: they are controls,
            # not a position in the navigation.
            # An exact match only. "About" resolves to index.html#who, which
            # shares a filename with the home page but is a chapter inside it,
            # not the page's identity — matching on the filename alone lit
            # About up as the current tab on the home page.
            if want == page and "navcta" not in cls and "brand" not in cls:
                cls.append("on")
                a["aria-current"] = "page"
                marked += 1
            elif a.get("aria-current"):
                del a["aria-current"]
            # Assign unconditionally. Stripping "on" from a link whose only
            # class was "on" left cls empty, and an empty list was silently
            # skipped — so a marker written by a previous run never came off.
            if cls:
                a["class"] = cls
            elif a.get("class") is not None:
                del a["class"]
    return changed, marked


def main():
    total_c = total_m = 0
    for page in PAGES:
        p = os.path.join(ROOT, page)
        if not os.path.exists(p):
            continue
        s = open(p, encoding="utf-8").read()

        soup = BS(s, "html.parser")
        c, m = retarget_and_mark(soup, page)
        s = str(soup)

        s, ok1 = splice(s, CSS_M, NAV_CSS, "</style>")
        s, ok2 = splice(s, JS_M, NAV_JS, "</body>")
        if not (ok1 and ok2):
            print("  FAIL %s: nowhere to anchor" % page)
            return 1

        open(p, "w", encoding="utf-8").write(s)
        total_c += c
        total_m += m
        print("  %-22s %d link(s) retargeted, %d marked current" % (page, c, m))

    print("  %d retargeted, %d current-page markers across the English pages"
          % (total_c, total_m))
    return 0


if __name__ == "__main__":
    sys.exit(main())

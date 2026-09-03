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
# One label, one destination, from every page — including the home page.
#
# The reasoning, because this was argued both ways and reversed once. The home
# page chapters are the argument; the pages are the evidence, and they share no
# sentences — the chapter/page pairs run 178 words against 684, 239 against
# 1824, 165 against 2353. Nothing is being duplicated or moved.
#
# What changes is only where a MENU click lands. A visitor scrolling the home
# page meets each chapter in order and takes its "in full" link in context —
# that path is untouched and is the one that converts. A visitor who reaches
# for the nav has already opted out of reading in sequence: they want the
# reference, and handing them a 178-word teaser plus another click answers a
# question they did not ask.
#
# It is also the only model under which the current-tab marker can ever fire
# from the home page: routing Capabilities to #solution keeps you on
# index.html, so no tab is ever the current one.
#
# About is the exception, and it is a translation exception rather than a
# design one. story.html is English-only and carries a different header with
# no language switcher, so linking it would strand a German or French visitor
# on an English page with no way back. Until it is translated, About stays the
# home page chapter, which does exist in all three languages.
DEST_HOME = {
    "Approach": "approach.html", "Capabilities": "capabilities.html",
    "Engineering": "engineering.html", "Work": "work.html",
    "About": "#who", "Contact": "#climax", "Home": "index.html",
}
DEST_INNER = {
    "Approach": "approach.html", "Capabilities": "capabilities.html",
    "Engineering": "engineering.html", "Work": "work.html",
    "About": "index.html#who", "Contact": "index.html#climax",
    "Home": "index.html",
}

CURRENT = {
    "approach.html":     "Approach",
    "capabilities.html": "Capabilities",
    "engineering.html":  "Engineering",
    "work.html":         "Work",
    "contact.html":      "Contact",
}

CSS_M = ("/*NAV:CSS*/", "/*/NAV:CSS*/")
JS_M  = ("<!--NAV:JS-->", "<!--/NAV:JS-->")

NAV_CSS = """/* ── one header, on every page ──────────────────────────────────────────
   This site grew two header systems. The home page and engineering.html
   space the links with var(--sp3) and mark the current page by turning it
   copper, through a bare [aria-current=page] rule. approach, capabilities,
   work and contact use a 30px gap, a smaller type size, and mark the current
   page white with a growing underline. Same nav, same words, three different
   treatments depending on where you happened to be standing — and the links
   sat at a different x on each page, so they visibly jumped as you clicked
   through.

   Everything below is the single treatment. It is injected last, so it wins
   on order rather than on !important, and the desktop metrics are scoped
   above the 880px breakpoint that both families already use for the burger,
   so the mobile drawer keeps its own larger tap targets. */

/* The inner pages spread five header children with space-between, which put
   the links in the middle of the bar while the home page pushed them right. */
.navlinks{margin-left:auto}

/* Same container, so the header sits at the same x on every page. The three
   families each defined .wrap differently — width:min(100% - 40px, W) with no
   padding, max-width with 20px of padding, and max-width with 40px — so even
   after the max-width was unified the CONTENT box was 1240, 1200 and 1160.
   That is the last of the shifting. Scoped to desktop so each page keeps the
   mobile gutter it was designed with. */
@media(min-width:881px){
  header .wrap{width:auto;max-width:1240px;margin-inline:auto;
    padding-left:40px;padding-right:40px}
}

@media(min-width:881px){
  /* The header's own flex container: a div.wrap on the home page and inner
     engineering, a nav on the rest. Their gaps were 24px and 30px, and with
     three items to the right of the links that is a 12px difference in where
     the links end — the last of the movement between pages. */
  header > .wrap, header nav{gap:26px}
  .navlinks{gap:26px;align-items:center}
  .navlinks a,.navlinks>a{font-size:14px;padding:4px 0;border-bottom:0}
  .navcta{padding:9px 16px;font-size:12.5px}
}

/* The current page: white, over a copper rule. Drawn as a background image
   rather than a border or an ::after, because one family already owns the
   ::after for its hover underline and a border-bottom is taken by the mobile
   drawer — this collides with neither. */
header .navlinks a.on,
header .navlinks a[aria-current="page"]{
  color:#F2EFE8;
  background-image:linear-gradient(#C97A3C,#C97A3C);
  background-size:100% 2px;
  background-repeat:no-repeat;
  background-position:0 100%;
}
/* and suppress the other family's underline, so the active tab never wears
   two of them at once */
header .navlinks a.on::after,
header .navlinks a[aria-current="page"]::after{width:0}"""


NAV_JS = """<script>
/* Two things about arriving at this page, both about scroll.

   ONE — ARRIVING AT AN ANCHOR FROM ANOTHER PAGE

   html{scroll-behavior:smooth} is right for a nav click inside the page: the
   reader keeps their bearings while the page glides. It is wrong on arrival.
   Following Approach from an inner page loads the home page at the top and
   then smooth-scrolls all the way down to the chapter — so the reader watches
   the chapter numbers count past, 01, 02, 03, before the page settles. It
   looks like the site loaded the wrong page and corrected itself.

   The fix is to make only the first jump instant, then hand smooth back, so
   every later click behaves as before.

   TWO — A RELOAD

   The browser restores scroll position by default. On a chaptered page whose
   sections reveal on scroll, that drops the reader into the middle of a
   narrative with the reveals already spent. A reload returns to the top —
   unless the URL carries an anchor, which is an explicit request for a place.

   The work page's field figure is verified by a headless harness with no
   history and no window, so this must not throw there. */
(function(){
  if(typeof window==='undefined'||typeof document==='undefined') return;
  /* The harness defines window and document but not the bare globals a page
     normally inherits from window, so reach for them explicitly and check. */
  if(typeof window.addEventListener!=='function'
     || typeof window.requestAnimationFrame!=='function') return;
  var root = document.documentElement;
  if(!root||!root.style) return;

  function instantly(fn){
    var had = root.style.scrollBehavior, done = false;
    root.style.scrollBehavior = 'auto';
    fn();
    /* Give the jump a frame to land before smooth is allowed back, or the
       browser applies the restored value to the scroll still in flight.
       The timer is not belt and braces: requestAnimationFrame does not run in
       a background tab, and a page opened in one would have kept smooth
       scrolling switched off until it was looked at. */
    function restore(){
      if(done) return;
      done = true;
      root.style.scrollBehavior = had;
    }
    window.requestAnimationFrame(function(){
      window.requestAnimationFrame(restore);
    });
    setTimeout(restore, 400);
  }

  if(typeof history!=='undefined' && 'scrollRestoration' in history){
    history.scrollRestoration = 'manual';
  }

  window.addEventListener('load', function(){
    var hash = location.hash;
    if(!hash || hash === '#'){
      instantly(function(){ window.scrollTo(0, 0); });
      return;
    }
    var target;
    try { target = document.querySelector(hash); } catch(e){ target = null; }
    if(!target) return;
    instantly(function(){
      target.scrollIntoView({behavior: 'auto', block: 'start'});
    });
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
    """Put every nav label back on its one destination for this page, and flag
    the label this page IS. Header and footer both, because the release gate
    requires them to agree and a visitor reads whichever is nearer."""
    dest = DEST_HOME if page == "index.html" else DEST_INNER
    here = CURRENT.get(page)
    changed = marked = 0
    for root in (soup.find("header"), soup.find("footer")):
        if root is None:
            continue
        for a in root.find_all("a"):
            label = a.get_text(" ", strip=True)
            want = dest.get(label)
            if want and a.get("href") != want:
                a["href"] = want
                changed += 1
            cls = [c for c in (a.get("class") or []) if c != "on"]
            # The brand and the call to action are controls, not a position
            # in the navigation, so neither is ever the current tab.
            if label == here and "navcta" not in cls and "brand" not in cls:
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

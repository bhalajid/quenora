#!/usr/bin/env python3
"""One page, one map.

The header and the footer of a page must send the same word to the same place.
This has broken three times, each time found by a person rather than a test:

  * the footer's Approach / Capabilities / Work went to the previous design
    generation while the header's went to sections on the home page;
  * services.html and work.html carried a seven-item header nav against the
    five-item map every other page agreed on;
  * their footers ran a map of their own — "Core capabilities", "Firm", four
    separate links that all resolved to the same page.

Every one of those is the same defect: a label with two destinations. This
checks it mechanically, per page and per language, so it stops being something
somebody has to notice.
"""
import os
import re
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))

SKIP_DIRS = ("test", "node_modules", "api", "assets", "study")
SKIP_FILES = {"index-old-backup.html"}
# Legal pages carry a cut-down footer by design and no main nav.
NAV_EXEMPT = {"impressum.html", "privacy.html"}

TAG = re.compile(r"<a\s[^>]*>.*?</a>", re.S)
HREF = re.compile(r'href="([^"]+)"')
TEXT = re.compile(r"<[^>]+>")


LANGSEL = re.compile(r'<div[^>]*class="langsel".*?</div>\s*</div>|<ul[^>]*class="langmenu".*?</ul>', re.S)


CTA = re.compile(r'<a[^>]*class="[^"]*\bnavcta\b[^"]*"[^>]*>.*?</a>', re.S)


def strip_cta(fragment):
    """The CTA is compared by destination, not by wording.

    Its label is a sentence ("Start a conversation") where the footer names the
    same destination "Contact", and on some pages it carries a long and a short
    label in two spans that concatenate into "Start a conversationContact". It
    sits inside .navlinks on some pages and beside it on others. Comparing the
    text was never going to work; comparing where it goes is the actual rule."""
    return CTA.sub("", fragment or "")


def strip_switcher(fragment):
    """The language menu is not the site map. It lives next to the nav and its
    items are language names, so counting them as navigation reported English,
    Deutsch and Francais as header entries missing from the footer."""
    return LANGSEL.sub("", fragment or "")


def links(fragment):
    out = []
    for tag in TAG.findall(fragment or ""):
        h = HREF.search(tag)
        if not h:
            continue
        label = TEXT.sub("", tag).strip()
        label = " ".join(label.split())
        if label:
            out.append((label, h.group(1)))
    return out


def block(html, start_pat, end_tag):
    m = re.search(start_pat, html)
    if not m:
        return None
    end = html.find(end_tag, m.end())
    return html[m.end():end] if end > 0 else None


def pages():
    out = []
    for d, dirs, fs in os.walk(ROOT):
        # widget/ holds the assistant's source fragments, not pages. They are
        # injected into every page by build_widget.py and have no header of
        # their own to agree with a footer.
        dirs[:] = [x for x in dirs if x not in ("widget", "test", "api", "node_modules")]
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS and not x.startswith(".")]
        for f in fs:
            if f.endswith(".html") and f not in SKIP_FILES:
                out.append(os.path.relpath(os.path.join(d, f), ROOT))
    return sorted(out)


bad, checked = [], 0
HEADERS = {}
for rel in pages():
    html = open(os.path.join(ROOT, rel), encoding="utf-8").read()
    name = os.path.basename(rel)

    header = block(html, r'<nav[^>]*class="navlinks"[^>]*>|<div[^>]*class="navlinks"[^>]*>', "</nav>")
    if header is None:
        header = block(html, r'<div[^>]*class="navlinks"[^>]*>', "</div>")
    foot_all = block(html, r"<footer[^>]*>", "</footer>")
    site = None
    if foot_all:
        site = block(foot_all, r'<nav aria-label="Footer"[^>]*>', "</nav>")

    if name in NAV_EXEMPT:
        continue
    if header is None:
        bad.append("%s: no header nav found" % rel)
        continue
    if site is None:
        bad.append("%s: footer has no <nav aria-label=\"Footer\"> site map" % rel)
        continue

    checked += 1
    h = dict(links(strip_cta(strip_switcher(header))))
    HEADERS[rel] = list(h)
    f = dict(links(site))

    # the CTA lives outside .navlinks; fold it in under its own label
    # the CTA and the footer's Contact entry must lead to the same place
    cta = re.search(r'<a[^>]*class="[^"]*\bnavcta\b[^"]*"[^>]*href="([^"]+)"', html)
    contact = [t for l, t in links(site)
               if l in ("Contact", "Kontakt", "Contacto", "Contatti")]
    if cta and contact and cta.group(1) != contact[0]:
        bad.append("%s: the header CTA goes to %s but the footer's Contact goes to %s"
                   % (rel, cta.group(1), contact[0]))

    for label, target in h.items():
        if label in f and f[label] != target:
            bad.append('%s: "%s" -> header %s but footer %s'
                       % (rel, label, target, f[label]))

    # a footer entry that duplicates a header word must not disagree either way
    for label, target in f.items():
        if label in h and h[label] != target:
            continue  # already reported above
    # every header destination should be reachable from the footer too
    missing = [l for l in h if l not in f and l not in ("Home",)]
    # Home and Contact live in the footer by design: the brand mark is the
    # header's Home, and the header's CTA is its Contact.
    FOOT_ONLY = {"Home", "Start", "Startseite", "Accueil", "Inicio", "Home page",
                 "Contact", "Kontakt", "Contacto", "Contatti"}
    strays = [l for l in f if l not in h and l not in FOOT_ONLY]
    if missing:
        bad.append("%s: in the header but not the footer: %s" % (rel, ", ".join(sorted(missing))))
    if strays:
        bad.append("%s: in the footer but not the header: %s" % (rel, ", ".join(sorted(strays))))

# ── and the same header on every page, not just a self-consistent one ──
#
# The checks above compare a page's header against its own footer. That let
# approach, contact and products carry a six-item header with "Home" in it
# while every other page had five — self-consistent, and different from the
# rest of the site. A visitor moving between them saw the nav change shape.
per_lang = {}
for rel, labels in HEADERS.items():
    lang = rel.split("/")[0] if "/" in rel else "en"
    if rel.split("/")[-1] in NAV_EXEMPT:
        continue
    per_lang.setdefault(lang, {})[rel] = labels

for lang, pages_in in sorted(per_lang.items()):
    if len(pages_in) < 2:
        continue
    counts = {}
    for rel, labels in pages_in.items():
        counts.setdefault(tuple(labels), []).append(rel)
    if len(counts) > 1:
        common = max(counts.items(), key=lambda kv: len(kv[1]))[0]
        for shape, rels in counts.items():
            if shape == common:
                continue
            for rel in rels:
                bad.append("%s: header is %s; every other %s page is %s"
                           % (rel, " / ".join(shape), lang, " / ".join(common)))

print("  %d page(s) checked for header/footer agreement" % checked)
if bad:
    for b in bad:
        print("   " + b)
    print("  %d disagreement(s)" % len(bad))
    sys.exit(1)
print("  every page sends the same word to the same place")

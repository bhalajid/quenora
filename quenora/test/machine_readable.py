#!/usr/bin/env python3
"""
4h — what a machine reads when it reads this site.

This stage exists because of a defect that was live and invisible: the
homepage's JSON-LD was hand-written, build_i18n copied it verbatim into every
language, and so /de and /fr each declared inLanguage "en-GB" and the English
canonical URL. Both German pages were telling every crawler and every agent
that they were the English homepage. Nothing on screen was wrong, which is
exactly why it survived.

The failure mode this guards is narrow and specific: structured data drifting
away from the page it sits on. So every assertion here compares the graph
against the page's own served URL and its own language, never against a list
kept somewhere else.
"""
import json, os, re, sys
from bs4 import BeautifulSoup as BS

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "..")
DOMAIN = "https://quenora.ai"
LOCALE = {"en": "en-GB", "de": "de-DE", "fr": "fr-FR"}
PAGES = ["index.html", "engineering.html", "capabilities.html", "products.html",
         "approach.html", "work.html", "contact.html"]

fail, checked = [], 0


def served(lang, page):
    path = "" if lang == "en" else "/" + lang
    if page == "index.html":
        return DOMAIN + (path or "/")
    return DOMAIN + path + "/" + page[: -len(".html")]


for lang in ("en", "de", "fr"):
    for page in PAGES:
        p = os.path.join(ROOT, "" if lang == "en" else lang, page)
        if not os.path.exists(p):
            continue
        checked += 1
        where = ("%s/%s" % (lang, page)).lstrip("/")
        soup = BS(open(p, encoding="utf-8").read(), "html.parser")
        tags = soup.find_all("script", attrs={"type": "application/ld+json"})

        if len(tags) != 1:
            fail.append("%s: %d JSON-LD blocks, expected exactly 1"
                        % (where, len(tags)))
            continue
        try:
            g = json.loads(tags[0].string)["@graph"]
        except Exception as e:
            fail.append("%s: JSON-LD does not parse — %s" % (where, e))
            continue

        wp = [x for x in g if x.get("@type") == "WebPage"]
        if not wp:
            fail.append("%s: no WebPage node" % where)
            continue
        wp = wp[0]

        want_url, want_lang = served(lang, page), LOCALE[lang]
        if wp.get("url") != want_url:
            fail.append("%s: WebPage url is %s, page is served at %s"
                        % (where, wp.get("url"), want_url))
        if wp.get("inLanguage") != want_lang:
            fail.append("%s: declares inLanguage %s, page is %s"
                        % (where, wp.get("inLanguage"), want_lang))

        # every @id the page points at must exist in its own graph
        ids = {x.get("@id") for x in g}
        for node in g:
            for k, v in node.items():
                if isinstance(v, dict) and set(v) == {"@id"} \
                   and v["@id"] not in ids:
                    fail.append("%s: %s.%s points at %s, which is not in the "
                                "graph" % (where, node.get("@type"), k, v["@id"]))

        # a URL in the graph must never leave this page's language
        for m in re.findall(r'"(https://quenora\.ai[^"]*)"', tags[0].string):
            seg = m[len(DOMAIN):].strip("/").split("/")[0]
            other = {"de", "fr", "es", "it"} - {lang}
            if seg in other:
                fail.append("%s: graph links to %s, another language" % (where, m))

        if page == "capabilities.html":
            il = [x for x in g if x.get("@type") == "ItemList"]
            n = len(il[0]["itemListElement"]) if il else 0
            if n != 9:
                fail.append("%s: %d Service entries, the page offers 9"
                            % (where, n))
        if page == "index.html":
            fq = [x for x in g if x.get("@type") == "FAQPage"]
            n = len(fq[0]["mainEntity"]) if fq else 0
            want = len(soup.find_all("details"))
            if n != want:
                fail.append("%s: FAQPage declares %d questions, the page asks "
                            "%d" % (where, n, want))

# the two text files
for name, must in (("llms.txt", ["# Quenora Consulting", "## What the firm does",
                                 "info@quenora.ai"]),
                   ("llms-full.txt", ["Quenora"])):
    p = os.path.join(ROOT, name)
    if not os.path.exists(p):
        fail.append("%s is missing — run build_seo.py" % name)
        continue
    body = open(p, encoding="utf-8").read()
    checked += 1
    for m in must:
        if m not in body:
            fail.append("%s: does not contain %r" % (name, m))
    if "vercel.app" in body:
        fail.append("%s: names vercel.app; the site launches on quenora.ai" % name)
    # the artefact that started this: a space before a full stop, left by
    # joining the text nodes an <em> splits a heading into
    if re.search(r"\S \.", body):
        fail.append("%s: ' .' — a heading was joined across its <em>" % name)

print("  %d page(s) and file(s) checked for machine-readable structure" % checked)
if fail:
    for f in fail[:25]:
        print("   " + f)
    if len(fail) > 25:
        print("   ... and %d more" % (len(fail) - 25))
    print("FAIL")
    sys.exit(1)
print("  every page declares its own URL, its own language, and a whole graph")
print("PASS")

#!/usr/bin/env python3
"""Quenora — translation quality gate.

Mechanical checks only. This catches the classes of error that survive a
careless translation pass; it does NOT replace a native-speaker review, and
it says so at the end.

Checks, per language:
  1  coverage          every visible string is translated
  2  english residue   no untranslated English left in the body copy
  3  placeholders      brand, domain, email, product names preserved exactly
  4  symbols           arrows and typographic dashes preserved
  5  capitalisation    English Title Case not carried into FR/ES/IT;
                       German nouns capitalised in known cases
  6  punctuation       FR narrow no-break space before ; : ! ? and « »
                       ES inverted ¿ ¡ opening marks present
  7  orthography       DE uses ß not Swiss ss; no stray double spaces
  8  html integrity    tag count and structure identical to the English source
  9  metadata          lang, canonical, hreflang, og:locale correct
 10  length            translated strings not absurdly longer (layout risk)
"""
import json
import os
import re
import sys
from collections import defaultdict

from bs4 import BeautifulSoup, Comment

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
PAGES = ["index.html", "services.html", "products.html",
         "approach.html", "work.html", "contact.html"]
LANGS = ["de", "fr", "es", "it"]
# es and it are built but deliberately unlisted: noindex, absent from the
# sitemap and not offered in the switcher. Advertising them in hreflang while
# telling crawlers not to index them is a contradiction, so build_i18n.py
# emits alternates for the LISTED languages only. This test predates that
# decision and required all four, which failed a correct build.
UNLISTED_LANGS = {"es", "it"}
LISTED_LANGS = [l for l in LANGS if l not in UNLISTED_LANGS]
LOCALE = {"de": "de_DE", "fr": "fr_FR", "es": "es_ES", "it": "it_IT"}

KEEP = ["Quenora Technology Consulting", "quenora.ai", "hello@quenora.ai",
        "EU AI Act", "GDPR", "Platform Engineering"]

# common English words that should never survive in translated body copy
EN_RESIDUE = re.compile(
    r"\b(the|and|with|from|your|our|that|this|which|because|without|"
    r"team|engagement|capabilities|approach|delivered|built|running)\b")

# words that are legitimately English in every language (product/tech terms)
EN_ALLOWED = re.compile(
    r"^(Platform Engineering|MLOps|RAG systems|ETL pipelines|IaC|API "
    r"orchestration|Human-in-the-loop|SLA-backed|Model-agnostic|"
    r"Cloud-agnostic|Self-deployable|Vendor-neutral|BI & reporting|"
    r"Board-ready|Audit-ready|No lock-in|Fixed price|Ongoing|Monitoring|"
    r"Documentation|Scope|Build|Integrate|Diagnose|Transfer|Sustain)$")

TITLE_CASE = re.compile(r"^(?:[A-ZÀ-Þ][a-zà-ÿ]+\s+){2,}[A-ZÀ-Þ][a-zà-ÿ]+$")

fails, warns = [], []


def fail(lang, check, msg):
    """A shortfall in a language nobody is offered is a note, not a blocker.

    es/ and it/ are built and kept in the repo but are absent from the
    switcher, the hreflang set and the sitemap, and are served noindex. No
    visitor can reach them, so an untranslated string there cannot reach a
    visitor either. Blocking the release on it stops work on the languages
    that are actually published — which is what it did the first time the
    engineering page was localised."""
    if lang in UNLISTED_LANGS:
        warns.append((lang, check, msg + " (language not offered — not blocking)"))
        return
    fails.append((lang, check, msg))


def warn(lang, check, msg):
    warns.append((lang, check, msg))


def visible_strings(path):
    soup = BeautifulSoup(open(path, encoding="utf-8").read(), "html.parser")
    out = []
    for n in soup.find_all(string=True):
        if isinstance(n, Comment) or n.parent.name in ("script", "style"):
            continue
        t = str(n).strip()
        if len(t) >= 2:
            out.append(t)
    return soup, out


def tag_profile(path):
    soup = BeautifulSoup(open(path, encoding="utf-8").read(), "html.parser")
    prof = defaultdict(int)
    for t in soup.find_all(True):
        prof[t.name] += 1
    return prof


print()
print("=" * 62)
print("  QUENORA — TRANSLATION QUALITY GATE")
print("=" * 62)

untranslated = {}
p = os.path.join(ROOT, "_untranslated.json")
if os.path.exists(p):
    untranslated = json.load(open(p, encoding="utf-8"))

for lang in LANGS:
    d = os.path.join(ROOT, lang)
    if not os.path.isdir(d):
        fail(lang, "build", "directory %s/ does not exist" % lang)
        continue

    tr = {}
    tp = os.path.join(ROOT, "i18n", lang + ".json")
    if os.path.exists(tp):
        tr = json.load(open(tp, encoding="utf-8"))
        tr.pop("_meta", None)

    # ---- 1 coverage -------------------------------------------------
    miss = untranslated.get(lang, [])
    if miss:
        fail(lang, "coverage", "%d string(s) still English" % len(miss))

    for page in PAGES:
        src = os.path.join(ROOT, page)
        dst = os.path.join(d, page)
        if not os.path.exists(dst):
            fail(lang, "build", "%s/%s missing" % (lang, page))
            continue
        soup, strings = visible_strings(dst)
        body = " ".join(strings)

        # ---- 3 placeholders preserved --------------------------------
        raw = open(dst, encoding="utf-8").read()
        en_raw = open(src, encoding="utf-8").read()
        for k in KEEP:
            # only require a term where the English page actually uses it —
            # the two homepage layouts do not share the same vocabulary
            if k in en_raw and k not in raw:
                fail(lang, "placeholder", "%s: '%s' lost in translation"
                     % (page, k))

        # ---- 4 symbols preserved -------------------------------------
        src_raw = open(src, encoding="utf-8").read()
        for sym in ("→", "↓", "—"):
            if src_raw.count(sym) and not raw.count(sym):
                fail(lang, "symbols", "%s: '%s' dropped" % (page, sym))

        # ---- 5 capitalisation ----------------------------------------
        if lang in ("fr", "es", "it"):
            for s in strings:
                if EN_ALLOWED.match(s) or s in KEEP:
                    continue
                if TITLE_CASE.match(s):
                    warn(lang, "capitalisation",
                         "%s: English Title Case survives — '%s'" % (page, s[:52]))

        # ---- 6 punctuation -------------------------------------------
        if lang == "fr":
            for s in strings:
                if not re.search(r"[A-Za-zÀ-ÿ]", s):
                    continue                     # clock times, numbers
                for mark in (";", ":", "!", "?"):
                    for m in re.finditer(r"\S" + re.escape(mark), s):
                        if m.group(0)[0] not in (" ", " ", mark):
                            warn(lang, "punctuation",
                                 "%s: missing narrow no-break space before "
                                 "'%s' — '%s'" % (page, mark, s[:46]))
                            break
        if lang == "es":
            for s in strings:
                if s.rstrip().endswith("?") and "¿" not in s:
                    fail(lang, "punctuation",
                         "%s: question without opening ¿ — '%s'" % (page, s[:46]))
                if s.rstrip().endswith("!") and "¡" not in s:
                    fail(lang, "punctuation",
                         "%s: exclamation without opening ¡ — '%s'" % (page, s[:46]))

        # ---- 7 orthography -------------------------------------------
        if lang == "de":
            for bad, good in (("anschliessend", "anschließend"),
                              ("Massstab", "Maßstab"),
                              ("grösse", "größe"), ("schliessen", "schließen"),
                              ("heisst", "heißt"), ("Strasse", "Straße")):
                if bad in raw:
                    fail(lang, "orthography",
                         "%s: Swiss '%s' — Germany uses '%s'" % (page, bad, good))
        for s in strings:
            # collapse newline+indent first: that is HTML source formatting,
            # not a real double space in the rendered sentence
            flat = re.sub(r"\n\s*", " ", s)
            if "  " in flat:
                warn(lang, "orthography", "%s: double space — '%s'"
                     % (page, flat[:46]))

        # ---- 8 html integrity ----------------------------------------
        a, b = tag_profile(src), tag_profile(dst)
        for tag in set(a) | set(b):
            # the switcher legitimately adds div/ul/li/a/button/svg/path/circle/span
            if tag in ("div", "ul", "li", "a", "button", "svg", "path",
                       "circle", "span", "link", "script", "meta"):
                continue
            if a[tag] != b[tag]:
                fail(lang, "html", "%s: <%s> %d in EN vs %d in %s"
                     % (page, tag, a[tag], b[tag], lang))

        # ---- 9 metadata ----------------------------------------------
        if soup.html.get("lang") != lang:
            fail(lang, "metadata", "%s: html lang is '%s'"
                 % (page, soup.html.get("lang")))
        can = soup.find("link", rel="canonical")
        if not can or ("/%s/" % lang) not in can.get("href", ""):
            fail(lang, "metadata", "%s: canonical missing or wrong" % page)
        hl = {l.get("hreflang") for l in soup.find_all("link", rel="alternate")}
        for need in ["en"] + LISTED_LANGS + ["x-default"]:
            if need not in hl:
                fail(lang, "metadata", "%s: hreflang '%s' missing" % (page, need))
        ol = soup.find("meta", attrs={"property": "og:locale"})
        if not ol or ol.get("content") != LOCALE[lang]:
            fail(lang, "metadata", "%s: og:locale should be %s"
                 % (page, LOCALE[lang]))

    # ---- 2 english residue ------------------------------------------
    for en, loc in tr.items():
        if EN_ALLOWED.match(loc.strip()) or loc.strip() in KEEP:
            continue
        if loc.strip().startswith("©"):
            continue
        if len(loc.split()) > 4 and loc.strip() == en.strip():
            warn(lang, "residue", "identical to English — '%s'" % en[:50])

    # ---- 10 length ---------------------------------------------------
    for en, loc in tr.items():
        if len(en) > 40 or "\n" in en:
            continue                             # body copy reflows, labels do not
        if len(loc) > len(en) * 1.85:
            warn(lang, "length", "button/label %d%% longer — check it does not "
                 "wrap: '%s' -> '%s'"
                 % (100 * len(loc) // len(en), en[:30], loc[:34]))

# ---------------------------------------------------------------- report
by_lang = defaultdict(lambda: defaultdict(list))
for lang, check, msg in fails:
    by_lang[lang][check].append(msg)

if fails:
    print("\nFAILURES\n")
    for lang in sorted(by_lang):
        print("  %s" % lang.upper())
        for check in sorted(by_lang[lang]):
            msgs = by_lang[lang][check]
            print("    %-14s %d" % (check, len(msgs)))
            for m in msgs[:4]:
                print("      · %s" % m)
            if len(msgs) > 4:
                print("      · ... and %d more" % (len(msgs) - 4))
        print()

wl = defaultdict(lambda: defaultdict(list))
for lang, check, msg in warns:
    wl[lang][check].append(msg)
if warns:
    print("WARNINGS (review, do not block)\n")
    for lang in sorted(wl):
        print("  %s: %s" % (lang.upper(), ", ".join(
            "%s ×%d" % (c, len(v)) for c, v in sorted(wl[lang].items()))))
    print()

print("=" * 62)
print("  %d failure(s), %d warning(s)" % (len(fails), len(warns)))
print()
print("  NOTE: these are mechanical checks. Idiom, tone and register still")
print("  need a native-speaker review before this goes in front of a client.")
print("=" * 62)
print()
sys.exit(1 if fails else 0)

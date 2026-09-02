#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Every synonym must point at a word the index actually contains.

The assistant bridges the words buyers type to the words the site uses. That
map is hand-written, and the first version pointed French "coûte" at "prix"
and German "kostet" at "Preis" — neither of which appears anywhere in the
localised copy. A synonym aimed at a missing word is worse than none: it adds
nothing and dilutes the real terms, and nothing failed to say so.

This reads the alias tables out of index.html, tokenises each language's built
index the same way the browser does, and fails on any target that is absent.
"""
import json
import os
import re
import sys
import unicodedata

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))


def fold(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def vocab(path):
    if not os.path.exists(path):
        return None
    docs = json.load(open(path, encoding="utf-8"))["docs"]
    out = set()
    for d in docs:
        for t in re.split(r"[^a-z0-9]+", fold(d["h"] + " " + d["t"])):
            if len(t) > 2:
                out.add(t)
    return out


def tables(html):
    """pull ALIAS / ALIAS_DE / ALIAS_FR out of the page without running it"""
    found = {}
    for name, lang in (("ALIAS", "en"), ("ALIAS_DE", "de"), ("ALIAS_FR", "fr")):
        m = re.search(r"var " + name + r" = \{(.*?)\n  \};", html, re.S)
        if not m:
            continue
        pairs = {}
        for km in re.finditer(r"(\w+)\s*:\s*\[([^\]]*)\]", m.group(1)):
            pairs[km.group(1)] = [x.strip().strip("'\"")
                                  for x in km.group(2).split(",") if x.strip()]
        found[lang] = pairs
    return found


html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
maps = tables(html)
paths = {"en": "assistant.json", "de": "de/assistant.json", "fr": "fr/assistant.json"}

bad, checked = [], 0
for lang, pairs in maps.items():
    words = vocab(os.path.join(ROOT, paths[lang]))
    if words is None:
        bad.append("%s: %s has not been built" % (lang, paths[lang]))
        continue
    for key, targets in pairs.items():
        for t in targets:
            checked += 1
            if fold(t) not in words:
                bad.append("%s: %s -> %s, which appears nowhere in the index"
                           % (lang, key, t))

print("  %d synonym target(s) checked across %d language(s)" % (checked, len(maps)))
if bad:
    for b in bad:
        print("   " + b)
    print("  %d dead synonym(s)" % len(bad))
    sys.exit(1)
print("  every synonym points at a word the site actually uses")

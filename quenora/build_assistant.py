#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quenora — build the assistant's index.

The assistant answers from what the site actually says. Not a model: a
retrieval index over this site's own sentences, built here and ranked in the
browser with BM25. That is a deliberate choice rather than a cheap one —

  * it cannot invent a capability the firm does not have, which is the exact
    failure the site spends nine chapters arguing against;
  * no third party sees a visitor's question, so the privacy notice's "no
    cookies, no tracking" stays true as written;
  * it works on the locked-down corporate networks the hero was rebuilt for;
  * and it costs nothing per question, so it cannot be rate-limited at a
    trade stand.

Every answer is a passage a person wrote, with a link to where it sits.

Run:  python3 build_assistant.py      (after build_i18n.py)
"""
import json
import math
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.abspath(__file__))
LANGS = {"en": "", "de": "de", "fr": "fr"}
PAGES = ["index.html", "engineering.html", "capabilities.html",
         "work.html", "approach.html"]

try:
    from bs4 import BeautifulSoup
except ImportError:
    sys.exit("needs beautifulsoup4 — use the same interpreter as build_i18n.py")

# short words carry no signal at this corpus size, in any of the three languages
STOP = set("""a an and are as at be but by for from has have if in into is it its
of on or that the their then there these this to was were what when which who
will with you your our we us how why can does do not no
der die das den dem des ein eine einer eines und oder aber ist sind war waren
sein ihre ihr wir uns sie ihnen mit von zu im am auf für als auch nicht kein
was wie wer wo wenn dann dass
le la les un une des du de et ou mais est sont était étaient être leur nos
nous vous avec pour dans sur comme aussi ne pas que qui quoi où quand si
""".split())


def fold(s):
    """lowercase, strip accents — so 'Fähigkeiten' and 'fahigkeiten' match"""
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def tokens(s):
    return [t for t in re.split(r"[^a-z0-9]+", fold(s)) if len(t) > 2 and t not in STOP]


def chunks_for(path, page_url):
    """One chunk per heading: the heading plus the prose under it."""
    html = open(path, encoding="utf-8").read()
    soup = BeautifulSoup(html, "html.parser")
    for bad in soup(["script", "style", "nav", "header", "footer"]):
        bad.decompose()
    main = soup.find("main") or soup.body
    if not main:
        return []

    out, cur = [], None
    # A capability's description is a bare <div>, not a <p>, so every one of
    # the nine sections had an empty body and was dropped whole — keywords
    # included. Leaf divs (no element children) are prose here.
    for el in main.find_all(["h1", "h2", "h3", "p", "li", "figcaption", "span", "div"]):
        if el.name == "div" and el.find(True) is not None:
            continue
        cls = el.get("class") or []
        is_chip = el.name == "span" and ("tag" in cls or "chip" in cls)
        if el.name == "span" and not is_chip:
            continue
        text = " ".join(el.get_text(" ").split())
        if not text:
            continue
        # The capability keywords — "RAG systems", "Agent design", "MLOps
        # foundations" — are short list items and chips. The prose filter
        # below drops anything under 60 characters as noise, which silently
        # dropped every one of them: the most searchable words on the site,
        # and the closest thing it has to the vocabulary a buyer types. A
        # capability nobody can find is a capability the firm does not appear
        # to have. They are collected here instead.
        if (is_chip or el.name == "li") and len(text) < 60:
            if cur is not None:
                cur["tags"].append(text)
            continue
        if el.name in ("h1", "h2", "h3"):
            if cur and (cur["body"] or cur["tags"]):
                out.append(cur)
            anchor = ""
            for parent in el.parents:
                if parent.get and parent.get("id"):
                    anchor = "#" + parent["id"]
                    break
            cur = {"h": text, "body": [], "tags": [], "url": page_url + anchor}
        elif cur and len(text) > 40:
            cur["body"].append(text)
    if cur and (cur["body"] or cur["tags"]):
        out.append(cur)

    # One passage per paragraph, carrying its heading for context.
    #
    # The first version made a passage of a whole section, capped at 700
    # characters. Two things went wrong: the cap silently dropped the pricing
    # detail past the lede, and BM25's length normalisation stopped meaning
    # anything when every passage was the same maximum size — so the longest
    # chapter won queries it had no business winning. A paragraph is the unit
    # a person would actually quote back.
    packed = []
    for c in out:
        for para in c["body"]:
            if len(para) < 60:
                continue
            packed.append({"h": c["h"], "t": para[:600], "u": c["url"]})
        # the chips become one passage of their own, so a search for a keyword
        # lands on the capability rather than on nothing
        tags = c.get("tags") or []
        if tags:
            packed.append({"h": c["h"], "t": "Covers: " + ", ".join(tags) + ".",
                           "u": c["url"]})
    return packed


def build(lang, sub):
    docs = []
    for page in PAGES:
        path = os.path.join(ROOT, sub, page) if sub else os.path.join(ROOT, page)
        if not os.path.exists(path):
            continue
        url = ("/" + sub + "/" if sub else "/") + (
            "" if page == "index.html" else page[:-len(".html")])
        docs += chunks_for(path, url)

    # Ship the passages and nothing else. Shipping precomputed term
    # frequencies tripled the file and put a second tokeniser in the browser
    # that had to agree with this one forever. 81 passages take a few
    # milliseconds to index on open, so the browser does it and there is only
    # ever one tokeniser to be wrong.
    index = {"lang": lang, "docs": docs}
    out = os.path.join(ROOT, sub, "assistant.json") if sub else os.path.join(ROOT, "assistant.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(index, fh, ensure_ascii=False, separators=(",", ":"))
    kb = os.path.getsize(out) / 1024
    print("  %-3s %3d passages · %5.1f KB" % (lang, len(docs), kb))


if __name__ == "__main__":
    print("assistant index")
    for lang, sub in LANGS.items():
        build(lang, sub)

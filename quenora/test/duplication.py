#!/usr/bin/env python3
"""
duplication.py — what the site says more than once.

Written after the six phases turned out to be told twice, word for word, on
the home page and on approach.html — and after an earlier check of mine
reported "0 shared sentences" between them. That check split on sentence
boundaries and compared only fragments over 45 characters, so an "Exit
condition" prefix was enough to hide six identical statements.

This one normalises harder and reports three kinds of repetition:

  IDENTICAL   the same sentence, after case, whitespace and punctuation are
              flattened. Two pages making the same claim in the same words.
  NEAR        the same sentence with a few words changed — the variant
              phrasing that is worse than an exact copy, because a reader who
              notices it wonders which one is current.
  HEADING     the same heading on two pages, which usually means the same
              section exists twice.

A chapter on the home page summarising a page is not duplication. Repeating
its sentences is.
"""
import os, re, sys, itertools
from collections import defaultdict
from difflib import SequenceMatcher
from bs4 import BeautifulSoup as BS

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '..')
PAGES = ["index.html", "engineering.html", "capabilities.html", "products.html",
         "approach.html", "work.html", "contact.html", "story.html"]
MIN_WORDS = 6          # below this, repetition is usually a label, not a claim
NEAR = 0.86            # similarity at which two sentences are the same claim


def norm(t):
    t = re.sub(r'\s+', ' ', t).strip().lower()
    t = t.replace('’', "'").replace('—', '-').replace('–', '-')
    t = re.sub(r'[^a-z0-9\' -]', '', t)
    return re.sub(r'\s+', ' ', t).strip()


def sentences(el):
    out = []
    for node in el.find_all(['p', 'li', 'div', 'dd', 'td']):
        if node.find(['p', 'li', 'div', 'dd', 'td']):
            continue
        raw = re.sub(r'\s+', ' ', node.get_text(' ', strip=True))
        for s in re.split(r'(?<=[.?!])\s+', raw):
            if len(s.split()) >= MIN_WORDS:
                out.append(s.strip())
    return out


def chapter_of(node):
    """Which home-page chapter a sentence sits in, for a useful report."""
    p = node
    while p is not None:
        if getattr(p, 'get', None) and p.get('id'):
            return '#' + p.get('id')
        p = p.parent
    return ''


def main():
    sents, heads = {}, {}
    for f in PAGES:
        p = os.path.join(ROOT, f)
        if not os.path.exists(p):
            continue
        m = BS(open(p, encoding='utf-8').read(), 'html.parser').find('main')
        if not m:
            continue
        sents[f] = sentences(m)
        heads[f] = [re.sub(r'\s+', ' ', h.get_text(' ', strip=True))
                    for h in m.find_all(['h1', 'h2', 'h3'])]

    # ── identical sentences ────────────────────────────────────────────
    index = defaultdict(list)
    for f, ss in sents.items():
        for s in ss:
            index[norm(s)].append((f, s))

    ident = {k: v for k, v in index.items()
             if len({f for f, _ in v}) > 1}

    # ── identical headings ─────────────────────────────────────────────
    hindex = defaultdict(set)
    for f, hs in heads.items():
        for h in hs:
            if len(h.split()) >= 2:
                hindex[norm(h)].add(f)
    hdup = {k: v for k, v in hindex.items() if len(v) > 1}

    # ── near-duplicates, pairwise between different pages ──────────────
    near = []
    keys = [(f, s, norm(s)) for f, ss in sents.items() for s in ss]
    for (f1, s1, n1), (f2, s2, n2) in itertools.combinations(keys, 2):
        if f1 == f2 or n1 == n2:
            continue
        if abs(len(n1) - len(n2)) > 40:
            continue
        r = SequenceMatcher(None, n1, n2).ratio()
        if r >= NEAR:
            near.append((round(r, 3), f1, s1, f2, s2))
    near.sort(reverse=True)

    print('  %d page(s) compared' % len(sents))
    print()
    print('  IDENTICAL SENTENCES ON MORE THAN ONE PAGE: %d' % len(ident))
    for k, v in sorted(ident.items(), key=lambda kv: -len(kv[1])):
        where = ', '.join(sorted({f for f, _ in v}))
        print('   [%s]' % where)
        print('      %s' % v[0][1][:104])
    print()
    print('  SAME HEADING ON MORE THAN ONE PAGE: %d' % len(hdup))
    for k, v in sorted(hdup.items()):
        print('   [%s]  %s' % (', '.join(sorted(v)), k[:70]))
    print()
    print('  NEAR-DUPLICATES (>= %.0f%% the same): %d' % (NEAR * 100, len(near)))
    for r, f1, s1, f2, s2 in near[:18]:
        print('   %.0f%%  %s  vs  %s' % (r * 100, f1, f2))
        print('        %s' % s1[:96])
        print('        %s' % s2[:96])
    if len(near) > 18:
        print('   ... and %d more' % (len(near) - 18))
    return 0


if __name__ == '__main__':
    sys.exit(main())

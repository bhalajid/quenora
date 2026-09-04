#!/usr/bin/env python3
"""
build_chapter01.py — chapter 01 stops being the third "three things".

The pinned stage in #problem held a headline, a subtitle and three cards:
"AI programmes fail at the seams" → the data, the integration, the handover.

The home page already opens three other chapters the same way. #fit is "three
situations we are actually called into", #work is "these three recur", and
#solution counts nine capabilities of which three are core. A reader meets
four sets of three before the method, and by the third the shape has stopped
carrying meaning. This one goes.

What takes its place is the counters — nine capabilities, six phases, zero
engagements without an end date. They were sitting under the hub in #solution,
where the "9" restated the hub directly above it and the "6" restated the
whole of chapter 03. Moved here they restate nothing: they are the first
concrete numbers on the page, and they arrive before any of the chapters they
summarise.

THE PIN JS HAS TO BE TOLD

The scroll stage drives #pBig, #pSub and #pSeams > div by id, writing opacity
and transform on every frame. Removing the elements without touching the
script leaves it dereferencing null on the first scroll — the whole rAF loop
dies, and with it the progress bar, the horizontal track and the spotlight.
So the stage guards on what it actually has.
"""
import os, re, sys
from bs4 import BeautifulSoup as BS

ROOT = os.path.dirname(os.path.abspath(__file__))


def main():
    p = os.path.join(ROOT, 'index.html')
    s = open(p, encoding='utf-8').read()

    soup = BS(s, 'html.parser')
    inner = soup.select_one('#problem .inner')
    counters = soup.select_one('.counters')

    if inner is None:
        print('  chapter 01: no pinned stage found'); return 1
    if inner.select_one('.counters'):
        print('  chapter 01: already swapped')
    elif counters is None:
        print('  chapter 01: no counters to move'); return 1
    else:
        for old in list(inner.find_all(recursive=False)):
            old.decompose()
        inner.append(counters.extract())
        s = str(soup)
        print('  chapter 01: the seams panel replaced by the counters')

    # ── the stage must survive the elements going ──────────────────────
    if 'pBig && pSub' not in s:
        s = s.replace(
            "      var a = ease(clamp(p / 0.22, 0, 1));\n"
            "      pBig.style.opacity = 1;",
            "      /* The seams panel was removed from this stage, so the three\n"
            "         elements this choreography writes to are no longer there.\n"
            "         Without this guard the first scroll dereferences null and\n"
            "         takes the whole rAF loop with it — progress bar, horizontal\n"
            "         track and spotlight all stop. */\n"
            "      var a = ease(clamp(p / 0.22, 0, 1));\n"
            "      if (pBig && pSub) {\n"
            "      pBig.style.opacity = 1;", 1)
        s = s.replace(
            "      seams.forEach(function (s, i) {\n"
            "        var c = ease(clamp((p - 0.18 - i * 0.14) / 0.30, 0, 1));\n"
            "        s.style.opacity = 0.12 + c * 0.88;\n"
            "        s.style.transform = 'translate3d(0,' + (1 - c) * 34 + 'px,0)';\n"
            "      });",
            "      seams.forEach(function (s, i) {\n"
            "        var c = ease(clamp((p - 0.18 - i * 0.14) / 0.30, 0, 1));\n"
            "        s.style.opacity = 0.12 + c * 0.88;\n"
            "        s.style.transform = 'translate3d(0,' + (1 - c) * 34 + 'px,0)';\n"
            "      });\n"
            "      }", 1)
        print('  chapter 01: the pin stage guards on what it has')

    # ── the stage was sized for three panels that scroll past ──────────
    # 170vh of pinned scroll existed so a headline, a subtitle and three
    # cards could arrive one after another. What is left is a single row of
    # counters, so most of that height is now scrolling past nothing —
    # measured at 2815px for a chapter whose content is one line tall.
    if '.pinwrap{height:170vh' in s:
        s = s.replace('.pinwrap{height:170vh;position:relative}',
                      '.pinwrap{height:auto;position:relative}'
                      '/* was 170vh, sized for three panels arriving in sequence. '
                      'The stage now holds one row of counters, so the pinned '
                      'scroll had nothing left to reveal and 2815px of chapter '
                      'was mostly empty. */', 1)
        print('  chapter 01: the pinned height released')


    # ── the panel was a full-viewport stage ────────────────────────────
    # .pin is position:sticky with height:100svh and place-items:center —
    # right when it held a headline, a subtitle and three cards arriving in
    # sequence. It now holds one row of counters 321px tall inside 900px of
    # sticky viewport, which is the black gap: 348px above and 231px below.
    if '.pin{position:sticky;top:0;height:100svh' in s:
        s = s.replace('.pin{position:sticky;top:0;height:100svh;display:grid;place-items:center;',
                      '.pin{position:static;height:auto;display:grid;place-items:center;'
                      'padding:var(--sp5) 0;', 1)
        print('  chapter 01: the full-viewport stage released')

    # ── "0 engagements" reads as no engagements ────────────────────────
    # The claim is good and the framing is not: a visitor scanning three big
    # numerals reads 9, 6, 0 and the last one lands as a firm with no work.
    # It is also the one line that is not a count of something — it counts
    # what does NOT happen. One handover counts the thing that does, mirrors
    # approach.html's own "Six phases, fourteen weeks, one handover", and
    # makes the row read 9 · 6 · 1.
    # Parse, do not regex. The sentence wraps across a newline in the source,
    # so a pattern written against the rendered text never matched and the
    # swap silently did nothing.
    soup2 = BS(s, 'html.parser')
    zero = soup2.select_one('.counters b[data-count="0"]')
    if zero is not None:
        zero['data-count'] = '1'
        zero.string = '1'
        span = zero.find_next_sibling('span')
        if span is not None:
            span.string = ('handover, agreed before the work starts and written '
                           'into the statement of work.')
        s = str(soup2)
        print('  chapter 01: "0 engagements" is now "1 handover"')

    # ── the counts that name a page link to it ─────────────────────────
    # Done by parsing, and guarded on the tree rather than on a substring.
    # The first version tested for 'href="x" class="cnt-link"' in the raw
    # HTML while BeautifulSoup writes class before href, so the guard never
    # matched: every build wrapped the numerals again and the row ended up
    # with six anchors, three of them empty.
    soup3 = BS(s, 'html.parser')
    targets = {'9': 'capabilities.html', '6': 'approach.html', '1': 'approach.html'}
    wrapped = 0
    for b in soup3.select('.counters b[data-count]'):
        if b.find_parent('a', class_='cnt-link'):
            continue
        href = targets.get(b.get('data-count'))
        if not href:
            continue
        a = soup3.new_tag('a', href=href)
        a['class'] = 'cnt-link'
        b.wrap(a)
        wrapped += 1
    if wrapped:
        s = str(soup3)
        print('  chapter 01: %d count(s) now link to the page they name' % wrapped)

    open(p, 'w', encoding='utf-8').write(s)
    return 0


if __name__ == '__main__':
    sys.exit(main())

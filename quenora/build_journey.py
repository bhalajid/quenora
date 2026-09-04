#!/usr/bin/env python3
"""
build_journey.py — the six phases, told once.

PREVIEW ONLY, on the `infographics` branch.

WHAT WAS ACTUALLY WRONG, AND IT WAS NOT THE FORMAT

The home page and approach.html both tell the six phases. Not similarly —
identically. All six phase titles and all six exit conditions are word for
word the same on both pages. 432 words on the home page and 586 on approach,
for one idea, told twice.

Two earlier drawings of this chapter — a Gantt, then a spine of six gates —
were both answers to the wrong question. Neither removed the duplication; they
made the second telling prettier.

So:

  approach.html   keeps the detail, because that is the page whose whole job
                  is the method. It gets the spine: six gates, each showing
                  the exit condition, with the description behind a
                  disclosure.

  index #journey  stops retelling it. It keeps the argument — most
                  consultancies are built to continue, this one is built to
                  finish — and shows a rail of six stops with the week span
                  and nothing else, then links onward. 432 visible words
                  become about thirty.

WHY THE RAIL CARRIES NO NEW WORDS

Every label is the phase eyebrow the page already had ("Phase 01 · Frame") and
the week chip it already had. Nothing is retyped, so the German and French
translations still match and the change needs no new dictionary entries.

The last stop is drawn hollow on both pages. That is the handover, and it is
the one place the firm is no longer in the picture.
"""
import os, sys
from bs4 import BeautifulSoup as BS

ROOT = os.path.dirname(os.path.abspath(__file__))


def home_rail(soup, sec):
    """A summary, not a second telling: six stops, names and weeks only."""
    phases = sec.select('.phase')
    if len(phases) != 6:
        print('  index: expected 6 phases, found %d' % len(phases)); return False

    rail = soup.new_tag('ol'); rail['class'] = 'ph wrap rv'
    for i, art in enumerate(phases):
        li = soup.new_tag('li')
        li['class'] = 'ph-stop' + (' last' if i == len(phases) - 1 else '')
        dot = soup.new_tag('span'); dot['class'] = 'ph-dot'; dot['aria-hidden'] = 'true'
        li.append(dot)
        eyebrow = art.select_one('.mono')
        if eyebrow:
            e = eyebrow.extract(); e['class'] = 'ph-name mono'; li.append(e)
        dur = art.select_one('.dur')
        if dur:
            d = dur.extract(); d['class'] = 'ph-dur mono'; li.append(d)
        rail.append(li)

    old = sec.select_one('.hwrap')
    if old is None:
        print('  index: no .hwrap'); return False
    old.replace_with(rail)
    return True


def approach_spine(soup):
    """The detail, on the page whose job it is."""
    main = soup.find('main')
    heads = main.find_all('h3')
    if len(heads) != 6:
        print('  approach: expected 6 headings, found %d' % len(heads)); return False

    ol = soup.new_tag('ol'); ol['class'] = 'ex'
    anchor = heads[0].parent

    for i, h in enumerate(heads):
        li = soup.new_tag('li')
        li['class'] = 'ex-step' + (' last' if i == len(heads) - 1 else '')
        node = soup.new_tag('span'); node['class'] = 'ex-node'; node['aria-hidden'] = 'true'
        li.append(node)

        row = soup.new_tag('details'); row['class'] = 'ex-row'
        summ = soup.new_tag('summary'); summ['class'] = 'ex-sum'

        # everything up to the next h3 belongs to this phase
        block = []
        sib = h.next_sibling
        while sib is not None and getattr(sib, 'name', None) != 'h3':
            nxt = sib.next_sibling
            if getattr(sib, 'name', None):
                block.append(sib)
            sib = nxt

        t = h.extract(); t.name = 'span'; t['class'] = 'ex-title'
        summ.append(t)

        cond = None
        rest = []
        for b in block:
            if b.get_text(strip=True).lower().startswith('exit condition'):
                cond = b
            else:
                rest.append(b)
        if cond is not None:
            c = cond.extract(); c['class'] = 'ex-cond'; summ.append(c)
        row.append(summ)

        det = soup.new_tag('div'); det['class'] = 'ex-detail'
        for b in rest:
            det.append(b.extract())
        row.append(det)
        li.append(row)
        ol.append(li)

    anchor.append(ol)
    return True


def main():
    ok = True
    p = os.path.join(ROOT, 'index.html')
    soup = BS(open(p, encoding='utf-8').read(), 'html.parser')
    sec = soup.find(id='journey')
    if sec is None or sec.select_one('.ph'):
        print('  index: nothing to do')
    elif home_rail(soup, sec):
        open(p, 'w', encoding='utf-8').write(str(soup))
        print('  index #journey is a six-stop rail')
    else:
        ok = False

    p = os.path.join(ROOT, 'approach.html')
    soup = BS(open(p, encoding='utf-8').read(), 'html.parser')
    if soup.select_one('.ex'):
        print('  approach: nothing to do')
    elif approach_spine(soup):
        open(p, 'w', encoding='utf-8').write(str(soup))
        print('  approach.html is six gates on a spine')
    else:
        ok = False
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())

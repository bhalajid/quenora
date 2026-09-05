#!/usr/bin/env python3
"""
build_chapters.py — chapters 02, 04, 05 and 08, minimal and marked.

PREVIEW ONLY, on the `infographics` branch.

The same rule each time: the home page carries the argument and a way in; the
detail lives on the page whose job it is. Where the audit found the detail was
already on that page word for word, the home page stops repeating it.

  02  #fit          three situations, each given a mark. The one-line
                    diagnoses stay — they are how a visitor recognises
                    themselves, which is the whole point of the chapter.

  04  #solution     nine capability names took a full screen as a list, each
                    row about a hundred pixels tall, and 33% of them are
                    repeated on capabilities.html. Now a grid: three core
                    filled, six hollow, names only. The "Core" badges go —
                    once the core three are drawn differently the badge is
                    saying it twice.

  05  #work         the three pattern descriptions match work.html at 94-96%,
                    with tense drift between the copies ("an integration layer
                    that lets" against "we built an integration layer that
                    let"). The home page keeps the sector, the pattern and a
                    mark; the descriptions stay on work.html, which is where
                    the figures and the caveats already are.

  08  #commercial   the pricing stays, compact. The four steps of "what
                    happens when you get in touch" move to contact.html —
                    they describe what happens after you write, so they belong
                    beside the form rather than on the home page.

Every string is moved, never retyped, so the translations follow.
"""
import os, sys
from bs4 import BeautifulSoup as BS

ROOT = os.path.dirname(os.path.abspath(__file__))

# marks in the wordmark's vocabulary: circles and a stroke
# Closed shapes. The first set drew the mark failing three different ways —
# an arc stopping before it closed, a ring drifted off centre, a ring closing
# late. The idea was that the mark itself carried the fault. It did not read
# that way: an unclosed circle reads as a half-loaded spinner, and it was
# reported as "unfinished" twice. A mark that makes the reader wonder whether
# the page is broken has failed whatever it was trying to say.
#
# These are complete forms, and the meaning sits in what is beside the circle
# rather than in what is missing from it.
G = {
 # a circle stopped against a wall — the pilot that went no further
 'stall':  '<circle cx="10" cy="12" r="5.5"/><line x1="19" y1="5" x2="19" y2="19"/>',
 # two circles that should be concentric and are not — confident, and off
 'lie':    '<circle cx="12" cy="12" r="7"/><circle cx="14.6" cy="12" r="2.4"/>',
 # a closed circle and a hand already past the hour — governance, arriving late
 'late':   '<circle cx="12" cy="12" r="7"/><line x1="12" y1="12" x2="12" y2="7.6"/>'
           '<line x1="12" y1="12" x2="15.6" y2="14"/>',
 'erp':    '<circle cx="7" cy="9" r="3"/><circle cx="17" cy="9" r="3"/><circle cx="12" cy="16" r="3"/>',
 'desk':   '<circle cx="12" cy="10" r="4"/><line x1="6" y1="18" x2="18" y2="18"/>',
 'legacy': '<circle cx="9" cy="12" r="5"/><line x1="14" y1="12" x2="20" y2="12"/><circle cx="20" cy="12" r="1.6" fill="currentColor" stroke="none"/>',
}
FIT = ['stall', 'lie', 'late']
WORK = ['erp', 'desk', 'legacy']


def mark(soup, key, cls='ch-mark'):
    return BS('<svg class="%s" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
              'stroke-width="1.4" stroke-linecap="round" aria-hidden="true">%s</svg>'
              % (cls, G[key]), 'html.parser')


def fit(soup, sec):
    cards = sec.select('.shape, .card, .fitcard') or []
    if not cards:
        # the three h3s and their siblings
        hs = sec.find_all('h3')
        if len(hs) != 3:
            print('  #fit: expected 3, found %d' % len(hs)); return False
        holder, at = anchor_for(sec, hs[0])   # while hs[0] is still in the tree
        grid = soup.new_tag('div'); grid['class'] = 'ch3 wrap rv'
        for i, h in enumerate(hs):
            card = soup.new_tag('div'); card['class'] = 'ch-card'
            card.append(mark(soup, FIT[i]))
            tick = h.find_previous(class_='tick')
            if tick:
                t = tick.extract(); t['class'] = 'ch-eyebrow mono'; card.append(t)
            p = card_body(soup, h)          # before extracting h
            hh = h.extract(); hh.name = 'h3'; hh['class'] = 'ch-title'
            card.append(hh)
            if p is not None:
                p['class'] = 'ch-body'
                card.append(p)
            grid.append(card)
        holder = hs[0] if hs else None
        if at is not None:
            at.insert_before(grid)
        else:
            holder.append(grid)
        strip_empties(sec)
        return True
    return False


def anchor_for(sec, first):
    """Where the replaced block used to sit.

    Appending to the wrap put the new grid after everything else in the
    chapter — the nine capabilities landed below the automation figure and the
    counters, which is not where the list was. Insert at the position of the
    top-level ancestor the original content occupied instead."""
    holder = sec.find('div', class_='wrap') or sec
    node = first
    while node is not None and node.parent is not holder:
        node = node.parent
    return holder, node


def strip_empties(sec):
    """The cards were lifted out of their old wrappers; what is left behind is
    empty scaffolding that still takes vertical space."""
    for _ in range(4):
        for el in sec.find_all(['article', 'div', 'li', 'section']):
            if el.select_one('.ch-card, .caps, .ch3'):
                continue
            if not el.get_text(strip=True) and not el.find(['svg', 'img', 'canvas', 'input']):
                el.decompose()


def card_body(soup, h):
    sib = h.next_sibling
    while sib is not None and getattr(sib, 'name', None) is None:
        sib = sib.next_sibling
    if sib is not None and sib.name == 'p':
        return sib.extract()
    return None


def solution(soup, sec):
    """Three core at the centre, six in orbit around them.

    A grid said the same thing as the rail and the card rows: everything on
    this page had become a line or a list. The shape here carries the actual
    claim — three capabilities the work runs through, six that come in when
    the work needs them — which a nine-row list cannot say at all.

    On a phone the ring becomes two columns, filled and hollow. That is a
    different arrangement of the same information, not less of it: the Gantt
    was dropped precisely because its mobile form dropped the axis."""
    hs = sec.find_all('h3')
    if len(hs) != 9:
        print('  #solution: expected 9, found %d' % len(hs)); return False
    holder, at = anchor_for(sec, hs[0])

    fig = soup.new_tag('div'); fig['class'] = 'orb wrap rv'

    core = soup.new_tag('ol'); core['class'] = 'orb-core'
    ring = soup.new_tag('ol'); ring['class'] = 'orb-ring'

    for i, h in enumerate(hs):
        is_core = i < 3
        li = soup.new_tag('li')
        li['class'] = 'orb-item' + (' core' if is_core else '')
        if not is_core:
            li['style'] = '--i:%d' % (i - 3)
        dot = soup.new_tag('span'); dot['class'] = 'orb-dot'; dot['aria-hidden'] = 'true'
        li.append(dot)
        num = h.find_previous(class_='i')
        if num:
            n = num.extract(); n['class'] = 'orb-n mono'; li.append(n)
        t = h.extract(); t.name = 'span'; t['class'] = 'orb-name'
        li.append(t)
        (core if is_core else ring).append(li)

    for tag in sec.select('.tag'):
        tag.decompose()

    fig.append(ring)
    fig.append(core)
    if at is not None:
        at.insert_before(fig)
    else:
        holder.append(fig)
    strip_empties(sec)
    return True


def work(soup, sec):
    hs = sec.find_all('h3')
    if len(hs) != 3:
        print('  #work: expected 3, found %d' % len(hs)); return False
    holder, at = anchor_for(sec, hs[0])   # while hs[0] is still in the tree
    grid = soup.new_tag('div'); grid['class'] = 'ch3 wrap rv'
    for i, h in enumerate(hs):
        card = soup.new_tag('a'); card['class'] = 'ch-card ch-link'
        card['href'] = 'work.html'
        card.append(mark(soup, WORK[i]))
        eb = h.find_previous('p', class_='mono')
        if eb:
            e = eb.extract(); e['class'] = 'ch-eyebrow mono'; card.append(e)
        # the description is on work.html already, at 94-96% the same words.
        # Take it out before detaching the heading, or next_sibling is gone.
        p = card_body(soup, h)
        hh = h.extract(); hh.name = 'h3'; hh['class'] = 'ch-title'
        card.append(hh)
        if p is not None:
            p.decompose()
        grid.append(card)
    if at is not None:
        at.insert_before(grid)
    else:
        holder.append(grid)
    strip_empties(sec)
    return True


def commercial(soup, sec, contact_soup):
    """Pricing stays. The four steps after you get in touch move to contact."""
    steps = sec.select('.steps li') or []
    if not steps:
        # the four <b> + <span> pairs
        holder = None
        lab = sec.find('p', class_='mono')
        if lab is None:
            print('  #commercial: no step list found'); return False
        holder = lab.parent
        moved = soup.new_tag('div')
        moved.append(lab.extract())
        for b in list(holder.find_all('b')):
            wrap = b.parent
            if wrap is holder:
                continue
            moved.append(wrap.extract())
        cmain = contact_soup.find('main')
        sect = contact_soup.new_tag('section'); sect['class'] = 'section-pad'
        w = contact_soup.new_tag('div'); w['class'] = 'wrap'
        w.append(BS(str(moved), 'html.parser'))
        sect.append(w)
        cmain.append(sect)
        return True
    return False


def refresh_marks(soup):
    """Rewrite the glyphs in place on every run.

    The chapter builders are guarded: once a chapter has been rebuilt they
    skip it, which is what makes them safe to run repeatedly. The side effect
    is that changing a glyph changes nothing — the new shapes sat in this file
    for a whole build while the page still drew the old arcs. The marks are
    cheap, so they are re-rendered every time rather than only on first
    build.
    """
    n = 0
    for sec_id, keys in (('fit', FIT), ('work', WORK)):
        sec = soup.find(id=sec_id)
        if sec is None:
            continue
        marks = sec.select('.ch-mark')
        for i, sv in enumerate(marks):
            if i >= len(keys):
                break
            fresh = mark(soup, keys[i]).find('svg')
            sv.clear()
            for child in list(fresh.contents):
                sv.append(child)
            n += 1
    if n:
        print('  %d chapter mark(s) redrawn' % n)
    return n


def main():
    p = os.path.join(ROOT, 'index.html')
    soup = BS(open(p, encoding='utf-8').read(), 'html.parser')
    refresh_marks(soup)
    cp = os.path.join(ROOT, 'contact.html')
    csoup = BS(open(cp, encoding='utf-8').read(), 'html.parser')

    done = []
    if soup.find(id='fit') and not soup.select_one('#fit .ch3'):
        if fit(soup, soup.find(id='fit')): done.append('02 #fit')
    if soup.find(id='solution') and not soup.select_one('#solution .caps'):
        if solution(soup, soup.find(id='solution')): done.append('04 #solution')
    if soup.find(id='work') and not soup.select_one('#work .ch3'):
        if work(soup, soup.find(id='work')): done.append('05 #work')

    open(p, 'w', encoding='utf-8').write(str(soup))
    print('  rebuilt: %s' % (', '.join(done) if done else 'nothing'))
    return 0


if __name__ == '__main__':
    sys.exit(main())

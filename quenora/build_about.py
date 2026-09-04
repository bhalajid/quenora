#!/usr/bin/env python3
"""
build_about.py — a real About page, and story.html deleted.

PREVIEW ONLY, on the `infographics` branch.

WHY

story.html was never an About page. The duplication audit put 52% of its
blocks on the home page as well, with near-duplicates at 91-98% — "We're the
firm you call when the pilot worked" against "We are the firm you call when
the pilot worked". It is an older variant of the home page, unlisted,
English-only, and carrying a different header with no language switcher. A
stale second copy of the home page is the one thing search engines and agents
punish, and the site had just been made agent-readable.

So it goes, and about.html takes its place — built from chapter 07, which is
the actual About content, on the standard page shell so it has the header, the
footer and the language switcher every other page has.

That also removes the last exception in the navigation. "About" pointed at a
home-page chapter because story.html was English-only and could not be linked
without stranding a German visitor. about.html is generated from strings that
are already translated, so About can finally behave like the other four.

The home page keeps a short version of the chapter and links onward, the same
pattern as the method: the argument stays, the detail moves to the page whose
job it is.
"""
import os, re, sys, shutil
from bs4 import BeautifulSoup as BS

ROOT = os.path.dirname(os.path.abspath(__file__))
SHELL = 'capabilities.html'      # a page with the current header and footer


def main():
    home_p = os.path.join(ROOT, 'index.html')
    home = BS(open(home_p, encoding='utf-8').read(), 'html.parser')
    who = home.find(id='who')
    if who is None:
        print('  no #who'); return 1
    # Each step is guarded on its own. An all-or-nothing early exit meant a
    # second run skipped the home-page reduction as well, and #who quietly
    # came back to its full length.
    make_page = not os.path.exists(os.path.join(ROOT, 'about.html'))

    shell = BS(open(os.path.join(ROOT, SHELL), encoding='utf-8').read(), 'html.parser')

    # ── the page ────────────────────────────────────────────────────────
    h2 = who.find('h2')
    lede = who.select_one('.lede')
    facts = who.select('.wfact')
    body = [p for p in who.find_all('p')
            if p is not lede and 'whonote' not in (p.get('class') or [])]
    note = who.select_one('.whonote')

    main_el = shell.find('main')
    main_el.clear()
    main_el['id'] = 'main'

    sec = shell.new_tag('section'); sec['class'] = 'phero'
    wrap = shell.new_tag('div'); wrap['class'] = 'wrap'
    kick = shell.new_tag('div'); kick['class'] = 'kicker'
    kick.string = 'About'
    wrap.append(kick)

    h1 = shell.new_tag('h1'); h1['class'] = 'rv'; h1['data-d'] = '1'
    for c in list(h2.contents):
        h1.append(c.extract())
    wrap.append(h1)
    if lede:
        wrap.append(lede.extract())
    sec.append(wrap); main_el.append(sec)

    sec2 = shell.new_tag('section'); sec2['class'] = 'section-pad'
    wrap2 = shell.new_tag('div'); wrap2['class'] = 'wrap'
    for p in body:
        wrap2.append(p.extract())
    if facts:
        dl = shell.new_tag('dl'); dl['class'] = 'ab-facts'
        for f in facts:
            k = f.find('span'); v = f.find('b')
            if k is None or v is None:
                continue
            dt = shell.new_tag('dt'); dt['class'] = 'mono'
            dt.string = k.get_text(' ', strip=True)
            dd = shell.new_tag('dd')
            dd.string = v.get_text(' ', strip=True)
            dl.append(dt); dl.append(dd)
        wrap2.append(dl)
    if note:
        wrap2.append(note.extract())
    sec2.append(wrap2); main_el.append(sec2)

    # title and description
    t = shell.find('title')
    if t:
        t.string = 'Quenora Consulting — About'
    for m in shell.find_all('meta'):
        if m.get('name') == 'description' or m.get('property') == 'og:description':
            m['content'] = ('Quenora is founder-led, based in Heilbronn and working '
                            'internationally. Who you are actually hiring.')

    if make_page:
        open(os.path.join(ROOT, 'about.html'), 'w', encoding='utf-8').write(str(shell))
        print('  about.html written from chapter 07')

    # ── what the home page keeps ───────────────────────────────────────
    # Guard on what the run produces, not on a flag. Without this the link
    # was appended again on every build — three of them after three builds.
    if who.select_one('a.more[href="about.html"]') is not None:
        print('  index #who already reduced')
        return 0
    keep = home.new_tag('a'); keep['class'] = 'more'
    keep['href'] = 'about.html'
    keep.string = 'Who you’re hiring, in full'
    chead = who.select_one('.chead > div') or who.select_one('.chead')
    if chead is not None:
        chead.append(keep)
    open(home_p, 'w', encoding='utf-8').write(str(home))
    print('  index #who reduced to the argument and a link')

    # ── story.html goes ────────────────────────────────────────────────
    sp = os.path.join(ROOT, 'story.html')
    if os.path.exists(sp):
        os.remove(sp)
        print('  story.html deleted')
    for d in ('de', 'fr', 'es', 'it'):
        q = os.path.join(ROOT, d, 'story.html')
        if os.path.exists(q):
            os.remove(q)
    return 0


if __name__ == '__main__':
    sys.exit(main())

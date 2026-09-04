#!/usr/bin/env python3
"""
build_journey.py — six exits, not a Gantt chart.

PREVIEW ONLY, on the `infographics` branch.

WHY THE FIRST ATTEMPT WAS WRONG

I drew the six phases as bars on a 14-week axis. Two things were wrong with it.

It does not survive a phone. The axis has to be hidden below about 820px or
the ticks collapse to four pixels each, and a bar with no axis behind it is
decoration: measured on an iPhone the six bars were 50 to 175px wide against
nothing at all. Half the traffic would have seen a chart that means nothing.

More importantly it foregrounded the wrong thing. Read the chapter's own lede:
"Most consultancies are designed to keep the engagement going. Ours is designed
to bring it to a clean close — each phase carries an exit condition, agreed and
written into the statement of work." The argument is the exit conditions. A
Gantt puts duration first, which is the least distinctive thing here — every
consultancy has a timeline; almost none of them publish what has to be true
before they are allowed to move on, or leave.

WHAT THIS DRAWS INSTEAD

A vertical spine of six gates. Each one shows the phase, its title and the
exit condition that has to be met to pass it; the description and the three
bullets sit behind a disclosure. Duration becomes a small chip rather than the
organising idea.

Vertical is the point: it is the same shape at 375px and at 1600px, so nothing
is hidden on a phone and there is no scale to lose.

The spine fades as it descends and stops at a terminal mark. The engagement
winds down to nothing, and the last gate — "You own it, you run it, we're
gone" — is drawn hollow, because that is the one where the firm is no longer
in the picture. That is the chapter's claim, made by the drawing rather than
asserted again in a sentence.

Every string is lifted from the existing DOM, so the German and French
translations still match. No number, ratio or proportion is invented anywhere:
the only quantities drawn are the week ranges the page already stated.
"""
import os, re, sys
from bs4 import BeautifulSoup as BS

ROOT = os.path.dirname(os.path.abspath(__file__))


def build(soup, sec):
    phases = sec.select('.phase')
    if len(phases) != 6:
        print('  expected 6 phases, found %d' % len(phases)); return False

    ol = soup.new_tag('ol'); ol['class'] = 'ex wrap rv'

    for i, art in enumerate(phases):
        li = soup.new_tag('li'); li['class'] = 'ex-step' + (' last' if i == len(phases) - 1 else '')

        node = soup.new_tag('span'); node['class'] = 'ex-node'
        node['aria-hidden'] = 'true'
        li.append(node)

        row = soup.new_tag('details'); row['class'] = 'ex-row'
        summ = soup.new_tag('summary'); summ['class'] = 'ex-sum'

        top = soup.new_tag('div'); top['class'] = 'ex-top'
        eyebrow = art.select_one('.mono')
        if eyebrow:
            e = eyebrow.extract(); e['class'] = 'ex-eyebrow mono'; top.append(e)
        dur = art.select_one('.dur')
        if dur:
            d = dur.extract(); d['class'] = 'ex-dur mono'; top.append(d)
        summ.append(top)

        h3 = art.find('h3')
        if h3:
            t = h3.extract(); t.name = 'span'; t['class'] = 'ex-title'
            summ.append(t)

        exit_ = art.select_one('.exit')
        if exit_:
            x = exit_.extract(); x['class'] = 'ex-cond'
            summ.append(x)

        row.append(summ)

        det = soup.new_tag('div'); det['class'] = 'ex-detail'
        body = art.find('p', class_=None)
        if body:
            det.append(body.extract())
        lis = art.find_all('li')
        if lis:
            ul = soup.new_tag('ul'); ul['class'] = 'ex-list'
            for l in lis:
                ul.append(l.extract())
            det.append(ul)
        row.append(det)
        li.append(row)
        ol.append(li)

    old = sec.select_one('.hwrap')
    if old is None:
        print('  no .hwrap'); return False
    old.replace_with(ol)
    return True


def main():
    p = os.path.join(ROOT, 'index.html')
    soup = BS(open(p, encoding='utf-8').read(), 'html.parser')
    sec = soup.find(id='journey')
    if sec is None:
        print('  no #journey'); return 1
    if sec.select_one('.ex'):
        print('  already built'); return 0
    if not build(soup, sec):
        return 1
    open(p, 'w', encoding='utf-8').write(str(soup))
    print('  #journey is six gates on a spine')
    return 0


if __name__ == '__main__':
    sys.exit(main())

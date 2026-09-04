#!/usr/bin/env python3
"""
build_journey.py — the six phases as a timeline instead of 432 words.

PREVIEW ONLY. This lives on the `infographics` branch so the idea can be
looked at without touching the site.

WHAT IT CHANGES

#journey was the heaviest chapter on the home page: 432 words, 8 paragraphs
and 18 bullets, inside a pinned horizontal scroller you had to drag through to
reach phase six. It describes a sequence with durations, which is the one shape
prose is genuinely worse at than a picture.

It also hid something. The week ranges overlap — Integrate runs weeks 4-10
while Foundation runs 3-6, and Prove starts in week 9 while Ship is still
going to week 12. Read as paragraphs that reads as six things one after
another. Drawn on an axis you can see the engagement is concurrent, which is a
more honest picture of how the work actually runs and a better answer to "how
long will this take".

WHY IT IS BUILT FROM THE EXISTING MARKUP

Every sentence is lifted from the current DOM rather than retyped. The strings
therefore still match the translation dictionary exactly, so German and French
survive untouched — retyping even one of them would have silently dropped it
back to English. Only the new furniture needs new words.

WHY CSS GRID AND NOT SVG

The labels stay real text: selectable, translatable by build_i18n, readable by
a screen reader, and present in the assistant index and llms-full.txt. A
diagram that hides its content from a machine would undo the work that just
went into being agent-readable.
"""
import os, re, sys
from bs4 import BeautifulSoup as BS

ROOT = os.path.dirname(os.path.abspath(__file__))
WEEKS = 14


def parse_phases(sec):
    out = []
    for art in sec.select('.phase'):
        eyebrow = art.select_one('.mono')
        dur = art.select_one('.dur')
        h3 = art.find('h3')
        body = art.find('p', class_=None)
        exit_ = art.select_one('.exit')
        bullets = [li for li in art.find_all('li')]
        m = re.search(r'(\d+)\D+(\d+)', dur.get_text() if dur else '')
        out.append({
            'eyebrow': eyebrow, 'title': h3, 'body': body, 'exit': exit_,
            'bullets': bullets, 'dur': dur,
            'from': int(m.group(1)) if m else 1,
            'to': int(m.group(2)) if m else 2,
        })
    return out


def build(soup, sec):
    phases = parse_phases(sec)
    if len(phases) != 6:
        print('  expected 6 phases, found %d — leaving it alone' % len(phases))
        return False

    wrap = soup.new_tag('div'); wrap['class'] = 'tl wrap rv'

    # The axis has to sit in the same two-column grid as every row, or the
    # ticks span the whole width while the bars only span the right-hand
    # column — week 1 then draws under the "6" and the chart lies.
    axis = soup.new_tag('div'); axis['class'] = 'tl-axis'
    axis['aria-hidden'] = 'true'
    lbl = soup.new_tag('p'); lbl['class'] = 'tl-unit mono'
    lbl.string = 'Weeks'
    axis.append(lbl)
    ticks = soup.new_tag('div'); ticks['class'] = 'tl-ticks'
    for w in range(1, WEEKS + 1):
        t = soup.new_tag('span')
        t['class'] = 'tl-w' + (' on' if w % 2 == 0 else '')
        t.string = str(w) if w % 2 == 0 else ''
        ticks.append(t)
    axis.append(ticks)
    wrap.append(axis)

    for i, p in enumerate(phases, 1):
        row = soup.new_tag('details'); row['class'] = 'tl-row'
        summ = soup.new_tag('summary'); summ['class'] = 'tl-sum'

        head = soup.new_tag('div'); head['class'] = 'tl-head'
        if p['eyebrow']:
            e = p['eyebrow'].extract(); e['class'] = 'tl-eyebrow mono'
            head.append(e)
        if p['title']:
            t = p['title'].extract()
            t.name = 'span'; t['class'] = 'tl-title'
            head.append(t)
        summ.append(head)

        track = soup.new_tag('div'); track['class'] = 'tl-track'
        bar = soup.new_tag('div'); bar['class'] = 'tl-bar'
        bar['style'] = ('grid-column:%d / %d' % (p['from'], p['to'] + 1))
        if p['dur']:
            d = p['dur'].extract(); d['class'] = 'tl-dur mono'
            bar.append(d)
        track.append(bar)
        summ.append(track)
        row.append(summ)

        det = soup.new_tag('div'); det['class'] = 'tl-detail'
        if p['body']:
            det.append(p['body'].extract())
        if p['bullets']:
            ul = soup.new_tag('ul'); ul['class'] = 'tl-list'
            for li in p['bullets']:
                ul.append(li.extract())
            det.append(ul)
        if p['exit']:
            det.append(p['exit'].extract())
        row.append(det)
        wrap.append(row)

    old = sec.select_one('.hwrap')
    if old is None:
        print('  no .hwrap to replace')
        return False
    old.replace_with(wrap)
    return True


def main():
    p = os.path.join(ROOT, 'index.html')
    soup = BS(open(p, encoding='utf-8').read(), 'html.parser')
    sec = soup.find(id='journey')
    if sec is None:
        print('  no #journey'); return 1
    if sec.select_one('.tl'):
        print('  already built'); return 0
    if not build(soup, sec):
        return 1
    open(p, 'w', encoding='utf-8').write(str(soup))
    print('  #journey is a timeline')
    return 0


if __name__ == '__main__':
    sys.exit(main())

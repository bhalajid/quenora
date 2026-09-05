#!/usr/bin/env python3
"""
build_pricing.py — pricing stays on the home page, the process moves to contact.

Chapter 08 carried two different things under one heading. The first is
pricing: a fixed fee to frame, fixed scope to build, handover included. That
belongs on the home page — it is the answer to "what will this cost", and a
reader deciding whether to get in touch needs it before they decide.

The second is "What happens when you get in touch": you write two paragraphs,
we reply within a working day, forty-five minutes, a written position. That is
not pricing. It describes what happens AFTER someone writes, which is the
contact page's whole subject, and on the home page it made the chapter run a
screen and a half for a reader who had not yet decided to make contact.

A pricing page was the alternative and it is the wrong shape. Visitors arrive
at one expecting numbers, and this firm prices to outcomes rather than day
rates — so the page would be a paragraph explaining why there are no figures,
which reads as evasion even when it is honesty.

Same split as the six phases: the argument stays where the reader is being
persuaded, the detail goes to the page whose job it is. Every sentence moves
as it is, so the German and French translations follow it across untouched.
"""
import os, sys
from bs4 import BeautifulSoup as BS

ROOT = os.path.dirname(os.path.abspath(__file__))


def main():
    hp = os.path.join(ROOT, 'index.html')
    cp = os.path.join(ROOT, 'contact.html')
    home = BS(open(hp, encoding='utf-8').read(), 'html.parser')
    contact = BS(open(cp, encoding='utf-8').read(), 'html.parser')

    if contact.select_one('.steps'):
        print('  pricing: the process already lives on contact.html')
        return 0

    sec = home.find(id='commercial')
    if sec is None:
        print('  pricing: no chapter 08'); return 1

    steps = sec.select_one('.steps')
    if steps is None:
        print('  pricing: no process list to move'); return 0
    holder = steps.parent
    label = holder.select_one('.mono')

    main_el = contact.find('main')
    if main_el is None:
        print('  pricing: contact.html has no main'); return 1

    block = contact.new_tag('section'); block['class'] = 'section-pad'
    wrap = contact.new_tag('div'); wrap['class'] = 'wrap'
    if label is not None:
        k = contact.new_tag('div'); k['class'] = 'kicker'
        k.string = label.get_text(' ', strip=True)
        wrap.append(k)
    wrap.append(steps.extract())
    block.append(wrap)
    main_el.append(block)

    holder.decompose()

    open(hp, 'w', encoding='utf-8').write(str(home))
    open(cp, 'w', encoding='utf-8').write(str(contact))
    print('  pricing: the four steps moved to contact.html')
    return 0


if __name__ == '__main__':
    sys.exit(main())

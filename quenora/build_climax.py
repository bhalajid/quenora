#!/usr/bin/env python3
"""
build_climax.py — the hero eyebrow, and where "Start a conversation" lands.

THE EYEBROW WAS TWO CLAIMS IN ONE RULE

"Enterprise AI & automation · Working internationally" runs 1160px on a
desktop and is the first line anyone reads. The second half is a fact about
where the firm operates, which the footer already carries and which nothing
above the fold depends on. It goes, and what is left sits centred between two
rules — the shape it always wanted.

THE CALL TO ACTION LANDED ON A HEADLINE AND NOTHING ELSE

Every "Start a conversation" pointed at #climax, the top of the closing
chapter. Measured from that landing point: the QR card sat 955px below the
fold on an 800px-tall laptop, 852px on a 900, and 619px on a 1080 — and the
form was 270px below that again. A visitor who clicked the one button on the
page meant to start a conversation arrived at a sentence, with nothing to
do and no sign there was anything further down.

The fix is not a hint that there is more below. It is landing where the thing
is. The CTAs point at the card now, with scroll-margin-top holding the
headline in view above it, so the reader gets the closing line and the form in
the same screen.
"""
import os, re, sys
from bs4 import BeautifulSoup as BS

ROOT = os.path.dirname(os.path.abspath(__file__))
SHORT = 'Enterprise AI & automation'
LONG = 'Enterprise AI & automation · Working internationally'

CSS = """/*CLIMAX:CSS*/
/* the eyebrow, centred between two rules */
.hook .eyebrow{display:flex;align-items:center;justify-content:center;gap:18px;
  width:100%;max-width:none}
.hook .eyebrow::before,.hook .eyebrow::after{content:'';height:1px;flex:1;
  max-width:180px;background:linear-gradient(90deg,transparent,var(--copper))}
.hook .eyebrow::after{background:linear-gradient(270deg,transparent,var(--copper))}
/* land on the card, with the closing line still above it */
#talk{scroll-margin-top:200px}
@media(max-width:760px){#talk{scroll-margin-top:120px}}
/*/CLIMAX:CSS*/"""


def main():
    p = os.path.join(ROOT, 'index.html')
    s = open(p, encoding='utf-8').read()
    soup = BS(s, 'html.parser')
    changed = []

    eye = soup.select_one('.hook .eyebrow')
    if eye is not None and LONG in eye.get_text(' ', strip=True):
        eye.string = SHORT
        changed.append('eyebrow trimmed to one claim')

    card = soup.select_one('#climax .qrcard')
    if card is not None and not card.get('id'):
        card['id'] = 'talk'
        changed.append('the contact card is the landing point')

    if changed:
        s = str(soup)

    # every route to the conversation lands on the card
    n = s.count('#climax"')
    if n:
        s = s.replace('index.html#climax"', 'index.html#talk"')
        s = s.replace('"#climax"', '"#talk"')
        changed.append('%d call(s) to action repointed' % n)

    if '/*CLIMAX:CSS*/' in s:
        s = re.sub(r'/\*CLIMAX:CSS\*/.*?/\*/CLIMAX:CSS\*/', CSS, s, flags=re.S)
    else:
        i = s.rindex('</style>')
        s = s[:i] + CSS + '\n' + s[i:]

    open(p, 'w', encoding='utf-8').write(s)
    for c in changed:
        print('  climax: ' + c)
    return 0


if __name__ == '__main__':
    sys.exit(main())

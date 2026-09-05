#!/usr/bin/env python3
"""
build_brand.py — the supplied logo set, in the header, the footer and the tab.

PREVIEW ONLY, on the `infographics` branch.

WHAT CHANGES

The site drew its own mark: nine <circle> elements inline in every page, in
copper (#C97A3C), with the wordmark set in Inter beside it. The supplied set
is a finished lockup — an open Q, the nine-dot arc, and "uenora" — in the
brand's own accent, #FF7043. That is ember, the colour the headlines already
use for emphasis, not copper. Adopting the set therefore moves the mark one
step warmer, which is the brand file's decision rather than mine.

  header   quenora-primary.svg, 34px tall
  footer   quenora-primary.svg, 46px tall
  tab      favicon.ico for anything old, a 32px PNG for the rest, a 180px
           apple-touch icon, and 192/512 for an installed icon

WHY <img> AND NOT INLINE SVG

Inline would let the mark inherit currentColor, which is how the old one
worked. But the supplied file is two colours — an ember mark and a white
wordmark — so there is nothing single to inherit, and inlining 12KB into 24
pages to gain nothing costs 288KB. One cached file, referenced everywhere,
with the name in the alt text so it is still read aloud and still indexed.

WHAT IS DELIBERATELY LEFT ALONE

Nora's button keeps the drawn arc. The supplied icon is an ember Q, and an
ember Q on a copper button is a colour clash rather than a logo. That button
also has to read at 24px, which the cropped arc does and a Q with a gap in it
does not.
"""
import os, sys, re
from bs4 import BeautifulSoup as BS

ROOT = os.path.dirname(os.path.abspath(__file__))
PAGES = ["index.html", "engineering.html", "capabilities.html", "products.html",
         "approach.html", "work.html", "contact.html", "about.html",
         "impressum.html", "privacy.html"]

ICONS = """<link href="/assets/brand/favicon.ico" rel="icon" sizes="any"/>
<link href="/assets/brand/quenora-icon.svg" rel="icon" type="image/svg+xml"/>
<link href="/assets/brand/quenora-icon-32.png" rel="icon" sizes="32x32" type="image/png"/>
<link href="/assets/brand/quenora-icon-180.png" rel="apple-touch-icon"/>
<link href="/assets/brand/quenora-icon-192.png" rel="icon" sizes="192x192" type="image/png"/>
<link href="/assets/brand/quenora-icon-512.png" rel="icon" sizes="512x512" type="image/png"/>"""

CSS = """/* ── the supplied lockup ───────────────────────────────────────────────
   One file, referenced everywhere, rather than nine inline circles repeated
   in twenty-four pages. Height is set and width follows the ratio, so the
   mark never distorts and never reflows the header when it loads. */
.brandimg{display:block;height:34px;width:auto;flex:none}
.brand.lg .brandimg{height:46px}
@media(max-width:900px){.brandimg{height:30px}.brand.lg .brandimg{height:40px}}
@media(max-width:560px){.brandimg{height:26px}.brand.lg .brandimg{height:36px}}"""


def lockup(soup, big=False):
    img = soup.new_tag('img')
    img['class'] = 'brandimg'
    img['src'] = '/assets/brand/quenora-primary.svg'
    img['alt'] = 'Quenora'
    img['width'] = '1439'
    img['height'] = '525'
    img['decoding'] = 'async'
    return img


def main():
    done = 0
    for page in PAGES:
        p = os.path.join(ROOT, page)
        if not os.path.exists(p):
            continue
        soup = BS(open(p, encoding='utf-8').read(), 'html.parser')

        brands = soup.select('.brand')
        if not brands:
            continue
        for b in brands:
            if b.select_one('.brandimg'):
                continue
            # clear(), not a selector sweep. The wordmark is a <b> on some
            # pages and a bare text node on others, so removing 'svg, b' left
            # "quenora" sitting next to the new lockup — the name twice.
            b.clear()
            b.append(lockup(soup, 'lg' in (b.get('class') or [])))

        head = soup.find('head')
        if head is not None:
            for link in head.find_all('link', rel=True):
                rels = link.get('rel')
                rels = rels if isinstance(rels, list) else [rels]
                if any('icon' in r for r in rels):
                    link.decompose()
            head.append(BS(ICONS, 'html.parser'))

        html = str(soup)
        if '/*BRAND:CSS*/' in html:
            html = re.sub(r'/\*BRAND:CSS\*/.*?/\*/BRAND:CSS\*/',
                          '/*BRAND:CSS*/\n' + CSS + '\n/*/BRAND:CSS*/', html, flags=re.S)
        elif '</style>' in html:
            i = html.rindex('</style>')
            html = html[:i] + '/*BRAND:CSS*/\n' + CSS + '\n/*/BRAND:CSS*/\n' + html[i:]
        open(p, 'w', encoding='utf-8').write(html)
        done += 1
    print('  the supplied lockup and icon set on %d page(s)' % done)
    return 0


if __name__ == '__main__':
    sys.exit(main())

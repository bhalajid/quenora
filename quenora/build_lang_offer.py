#!/usr/bin/env python3
"""Quenora — the language offer.

Puts /assets/lang-offer.css and /assets/lang-offer.js on every English page.

It OFFERS a language, it does not route to one. Googlebot crawls
predominantly from US addresses, so redirecting on IP can mean /de and /fr are
never crawled at all, and it overrides the hreflang the site already publishes
correctly. The offer reads navigator.language in the visitor's own browser,
stores nothing to decide whether to show itself, and writes a single cookie —
q_lang — only if the visitor clicks. See privacy.html.

ORDER. This must run BEFORE build_asset_versions.py, which stamps ?v= onto
every /assets/ URL, and therefore before build_i18n.py, which copies the
stamped English pages into de/ fr/ es/ it/.

The de/ and fr/ pages get the script by that copy. On those pages it finds the
visitor already reading their language and returns without drawing anything,
which is why it needs no per-language build step.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

# Every page a visitor can land on, matching build_widget.PAGES. A reader who
# arrives on the Impressum from a search result deserves the same offer.
PAGES = ["index.html", "engineering.html", "capabilities.html", "products.html",
         "approach.html", "work.html", "contact.html", "about.html",
         "pricing.html", "impressum.html", "privacy.html"]

# with or without the ?v= stamp — build_asset_versions rewrites these after we
# run, so matching only the bare form appends a second copy on every build.
# That is exactly how Nora's stylesheet reached nine copies on one page.
# Match ANY form of the tag, not the one form we happen to write. BeautifulSoup
# runs over these pages and normalises `defer` to `defer=""` and reorders
# attributes, so a pattern anchored to our own spelling misses on the second
# build and appends a duplicate. That is how Nora's stylesheet reached nine
# copies on one page, and this generator reproduced it on its first run.
CSS_LINK = r'<link\b[^>]*?/assets/lang-offer\.css(?:\?v=[0-9a-f]+)?[^>]*?>\s*'
JS_TAG   = r'<script\b[^>]*?/assets/lang-offer\.js(?:\?v=[0-9a-f]+)?[^>]*?>\s*</script>\s*'


def main():
    for name in ("lang-offer.css", "lang-offer.js"):
        if not os.path.exists(os.path.join(ROOT, "assets", name)):
            print("  FAIL assets/%s is missing" % name)
            return 1

    link = '<link href="/assets/lang-offer.css" rel="stylesheet"/>'
    tag = '<script defer src="/assets/lang-offer.js"></script>'
    done = 0

    for page in PAGES:
        p = os.path.join(ROOT, page)
        if not os.path.exists(p):
            print("  skip %-20s (not in the repo)" % page)
            continue
        s = open(p, encoding="utf-8").read()
        before = len(s)

        # strip every copy, versioned or not, then insert exactly one
        s = re.sub(CSS_LINK, '', s)
        s = re.sub(JS_TAG, '', s)
        if '</head>' not in s or '</body>' not in s:
            print("  FAIL %-20s no </head> or </body> to anchor to" % page)
            return 1
        s = s.replace('</head>', link + '\n</head>', 1)
        s = s.replace('</body>', tag + '\n</body>', 1)

        open(p, "w", encoding="utf-8").write(s)
        done += 1
        print("  %-22s %+6d bytes" % (page, len(s) - before))

    print("  the language offer on %d English page(s); build_i18n carries it onward" % done)
    return 0


if __name__ == "__main__":
    sys.exit(main())

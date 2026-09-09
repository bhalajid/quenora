#!/usr/bin/env bash
# Build the site. The order matters and is the reason this file exists.
#
#   build_brand     the supplied lockup and icon set into header, footer, tab.
#   build_logo_motion  MUST FOLLOW build_brand: inlines the header lockup so
#                   the Q can carry a sweeping reflection and the nine spheres
#                   can animate, and replaces the ring cursor with the mark's
#                   own spheres trailing the pointer.
#   build_widget    injects Nora (the floating assistant) into the English
#                   pages from widget/. Must run FIRST, so the localisation
#                   build carries her into every language.
#   build_nav       one destination per nav label, marks the current page,
#                   and settles the header layout. English pages only.
#   build_i18n      regenerates de/ fr/ es/ it/ from the English source.
#                   It overwrites those directories wholesale.
#   build_assistant reads the built pages and writes one search index per
#                   language, so it has to see the localised pages.
#   build_seo       writes JSON-LD into every page and generates llms.txt.
#                   It writes INTO de/ and fr/, so if build_i18n ran after
#                   it, every localised page would silently lose its
#                   structured data and go back to declaring itself English.
#
# build_qr is separate and deliberate: the printed codes are regenerated
# only when the contact details change, because a code that has been
# printed cannot be reissued.
set -euo pipefail
cd "$(dirname "$0")"

# /tmp/qvenv was the documented interpreter and macOS clears /tmp, so the build
# failed on its own and told you to rebuild the venv in the place it will be
# deleted from again. Prefer one inside the repo (.gitignored); keep the old
# path as a fallback.
if [ -z "${PY:-}" ]; then
  for c in ./.venv/bin/python3 /tmp/qvenv/bin/python3 python3; do
    if "$c" -c 'import bs4' 2>/dev/null; then PY="$c"; break; fi
  done
fi
if [ -z "${PY:-}" ] || ! "$PY" -c 'import bs4' 2>/dev/null; then
  echo "  No python here has beautifulsoup4."
  echo "  Fix with:  python3 -m venv .venv && .venv/bin/pip install beautifulsoup4"
  exit 1
fi
echo "  build interpreter: $PY"

# PREVIEW (branch: infographics) — markup generators, then the stylesheet.
# The CSS is injected between markers rather than pasted in by hand,
# because regenerating the markup means checking the page out from main
# first, and that silently took hand-added styles with it. Twice.
"$PY" build_about.py
"$PY" build_chapter01.py
"$PY" build_form.py
"$PY" build_climax.py
"$PY" build_pricing.py
"$PY" build_journey.py
"$PY" build_ticker.py
"$PY" build_chapters.py
"$PY" build_preview_css.py
"$PY" build_backto.py

# build_logo_arc is RETIRED and deliberately not run. It mapped the nine
# circles onto the canonical 90-degree arc, which was right while the site
# used the alternate squared-Q set. The lockup is now the supplied artwork,
# whose dots were drawn for a 2.41:1 shape, and running it rewrites them:
# verified in a scratch worktree, primary.svg went from viewBox "8 9 1421
# 590" to "8 -199 1421 798" and the mark came apart.
"$PY" build_favicon.py      # ...and the tab icon, derived from the same nine
"$PY" build_brand.py
# ...then the motion, which replaces the flat header image build_brand just
# wrote with an inline copy whose Q can carry a reflection and whose nine
# spheres can move. The other way round and the flat image wins.
"$PY" build_logo_motion.py
# ...and the four easter eggs last, so they sit after every other script.
"$PY" build_easter_eggs.py
# build_widget writes assets/nora.js and assets/nora.css and the tags that
# point at them, so it has to come BEFORE the versioner. It used to sit after
# it and got away with it only because its old guard inserted a tag just once
# and left the stamped URL alone on later builds. Once that guard became a
# strip-and-reinsert — needed, because the old one could never update a tag —
# every build replaced the stamped tag with an unstamped one, after the
# stamping step had already run. The result: /assets/nora.js served with no
# ?v=, and vercel.json caches /assets/ for a year as `immutable`, so returning
# visitors were pinned to whatever copy they first downloaded. An iPad kept
# serving a nora.js from before the launcher learned to avoid the footer.
"$PY" build_widget.py
# build_footer owns the three footer link columns and must run BEFORE
# build_nav, which re-points header and footer links from one map and
# marks the current page. The other way round and build_nav's work is
# thrown away on every build.
"$PY" build_footer.py
"$PY" build_nav.py
# Versioning after every generator that writes an asset URL, and before
# build_i18n so the localised pages inherit the stamped ones. vercel.json
# caches /assets/ for a year as `immutable`, so a changed file only reaches a
# returning visitor if its URL changed too. build_footer writes the footer
# lockup's <img src>, which is why this cannot sit above it.
"$PY" build_asset_versions.py
"$PY" build_i18n.py
"$PY" build_assistant.py
"$PY" build_seo.py

echo
echo "Built. Verify with:  cd test && bash release.sh .."

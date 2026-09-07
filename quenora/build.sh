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

PY=${PY:-/tmp/qvenv/bin/python3}
if ! "$PY" -c 'import bs4' 2>/dev/null; then
  echo "  $PY has no beautifulsoup4."
  echo "  Set PY, or:  python3 -m venv /tmp/qvenv && /tmp/qvenv/bin/pip install beautifulsoup4"
  exit 1
fi

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

"$PY" build_logo_arc.py     # the nine circles back on the mark's own arc
"$PY" build_favicon.py      # ...and the tab icon, derived from the same nine
"$PY" build_brand.py
# ...then the motion, which replaces the flat header image build_brand just
# wrote with an inline copy whose Q can carry a reflection and whose nine
# spheres can move. The other way round and the flat image wins.
"$PY" build_logo_motion.py
# ...and the four easter eggs last, so they sit after every other script.
"$PY" build_easter_eggs.py
# ...and versioning last of all: vercel.json caches /assets/ for a year as
# `immutable`, so a changed file only reaches a returning visitor if its URL
# changed too. This must run after every generator that writes one.
"$PY" build_asset_versions.py
"$PY" build_widget.py
# build_footer owns the three footer link columns and must run BEFORE
# build_nav, which re-points header and footer links from one map and
# marks the current page. The other way round and build_nav's work is
# thrown away on every build.
"$PY" build_footer.py
"$PY" build_nav.py
"$PY" build_i18n.py
"$PY" build_assistant.py
"$PY" build_seo.py

echo
echo "Built. Verify with:  cd test && bash release.sh .."

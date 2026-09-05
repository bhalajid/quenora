#!/usr/bin/env bash
# Build the site. The order matters and is the reason this file exists.
#
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
"$PY" build_journey.py
"$PY" build_ticker.py
"$PY" build_chapters.py
"$PY" build_preview_css.py
"$PY" build_backto.py

"$PY" build_brand.py
"$PY" build_widget.py
"$PY" build_nav.py
"$PY" build_i18n.py
"$PY" build_assistant.py
"$PY" build_seo.py

echo
echo "Built. Verify with:  cd test && bash release.sh .."

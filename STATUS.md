# Status — 25 August 2026

Repo clean, `main` in sync with `origin/main`, release gate green
(9 checks, `RELEASE APPROVED`).

## Where the work is

**English homepage only.** Everything else is deliberately parked. The
decision was to finalise one page in English before touching six pages in
five languages.

| | |
|---|---|
| Live page | `quenora/index.html` — 7 chapters, ~1,500 words of prose |
| Inner pages | `services` `products` `approach` `work` `contact` — not yet reworked to match the new homepage |
| Translations | `de/ fr/ es/ it/` — 24 pages, **frozen and stale**, see `i18n/FROZEN` |
| Tests | `quenora/test/` — 9-stage gate, `bash release.sh ..` |

## Homepage chapters

```
hook · ticker · 01 problem (+ "the gap" diagram) · 02 fit · 03 journey
04 capabilities · 05 objections · 06 pricing · 07 the nine principles · climax
```

## Done

- Hero constellation built on the page's six-column grid; same height as the
  headline, right edge on the wrap's grid line, bottom on the headline's
  bottom. The mark does not move.
- Hover lights exactly one sphere — the nearest, scored against each sphere's
  own reach. 161,877 positions tested, 0 mis-picks.
- Cosmos dust field: drifts, scatters from the cursor, warms to copper, eases
  back.
- Chapter 01 "the gap" diagram — five pilots, one wall, nothing crosses.
- Chapter 07 — the nine principles, with the real mark and rows whose dots
  are the mark's own proportions.
- Blank half-screens fixed at the cause: the sticky stage no longer starts at
  opacity 0, and phase cards are no longer forced to viewport height. Both are
  gate conditions now.
- Logo lockup: mark leads at 40px, wordmark sits back at weight 500, viewBox
  cropped to the arc's bounds. Hover sends a charge up the arc.
- OG image, JSON-LD (Organization / WebSite / WebPage), title carries the
  category and the hook moved to `og:title`.
- `vercel.json` — CSP, HSTS, X-Frame-Options, Permissions-Policy, asset
  immutable caching.

## Open — next session starts here

1. **Hero spacing on small laptops.** Owner's note: the nine circles read as
   "way more away" and the page "not quite aligned for small screen laptops".
   The grid construction is correct at ≥1920 but 1280–1512 has not been
   verified visually.
2. **Full device sweep.** Smoke + appearance across every device category —
   phone, phablet, tablet portrait/landscape, small laptop, desktop,
   ultrawide. Currently modelled numerically, never rendered in a real
   browser (no browser binary in the sandbox).
3. **Chapter 07 integration.** Section is in and passing, but has not been
   reviewed on screen at any width.
4. Inner pages still carry the old design.
5. Translations: `rm i18n/FROZEN && python3 build_i18n.py`, then re-run the
   gate — it will fail until every localised page matches the new structure.

## Blocking launch

- **Impressum** — legally required in Germany, does not exist yet
- **Privacy notice** — does not exist yet
- Contact form still opens a mail client; needs a real backend
- Native-speaker review of all four languages (every `i18n/*.json` carries
  `"reviewed_by_native_speaker": false`)
- Trademark clearance for "Quenora"

## Housekeeping

- `.git/` holds ~14 `*.stale` lock files and some `tmp_obj_*` left by commits
  made from a sandbox that can write but not delete. Harmless. Clear with
  `git gc --prune=now`.
- `quenora/index-old-backup.html` is the superseded homepage, linked from
  nothing. Kept on purpose. It is the main source of misleading search hits —
  see `CLAUDE.md`.

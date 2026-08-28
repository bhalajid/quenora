# Status — 28 August 2026

Repo clean, `main` in sync with `origin/main`, release gate green
(9 checks, `RELEASE APPROVED`).

## Where the work is

**English homepage only.** Everything else is deliberately parked. The
decision was to finalise one page in English before touching six pages in
five languages.

| | |
|---|---|
| Live page | `quenora/index.html` — 9 chapters + hidden `#build`, enquiry form, assistant |
| Inner pages | `services` `products` `approach` `work` `contact` — not yet reworked to match the new homepage |
| Translations | `de/ fr/ es/ it/` — 24 pages, **frozen and stale**, see `i18n/FROZEN` |
| Tests | `quenora/test/` — 9-stage gate, `bash release.sh ..` |

## Homepage chapters

```
hook · ticker · 01 problem (+ "the gap" diagram, 3 beats, loops)
02 fit · 03 journey · 04 capabilities (+ automation figure)
05 work · [06 build — HIDDEN] · 06 objections · 07 who/about
08 pricing · 09 principles · climax (+ enquiry form)
```

Headline is now "Most enterprise AI never reaches **the work**."
See `DESIGN-BRIEF.md` for the design system and the outstanding UI/UX list.

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
- **Rendered in a real browser at last** (local static server, in-app browser).
  Swept 375 / 430 / 710 / 768 / 1280 / 1366 / 1440 / 1512 / 1920 / 2560.
  Hero spacing at 1280–1512 was the open worry — it is correct, the grid
  construction holds proportionally, no overflow at any width. Two genuine
  defects that only rendering could reveal were found and fixed:
  - the nav CTA wrapped to two lines below ~560px and pushed the header out of
    its band; it now swaps to a short "Contact" label
  - the constellation lay across the hook-foot paragraph on every phone and
    tablet. The `narrow` threshold dropped 900 → 700 so tablets take the
    grid-snapped path, and the phone fallback now sits in the empty band
    between the nav and the eyebrow instead of centred low over the type.

## Open — next session starts here

0. **`#build` is written but hidden.** Projects & products section, in
   `index.html` right after chapter 05. To release it, two things must happen
   *together* or the page numbers itself wrongly:
   - remove the `hidden` attribute on `<section hidden id="build">`
   - renumber `#honest` `#who` `#commercial` `#principles` from 06/07/08/09
     to 07/08/09/10
   Ongoing-project rows are amber placeholders: title, tech stack, use case.
   No client is named and none should be without written permission.

1. **The five inner pages still carry the old design.** Biggest visible
   inconsistency on the site. They also hard-code the long nav CTA label, so
   they show the phone header overflow the homepage no longer has.
2. **Mobile pass** on the newer sections — work, about, the enquiry form and
   the assistant panel were built desktop-first.
3. Translations: `rm i18n/FROZEN && python3 build_i18n.py`, then re-run the
   gate. They now also predate the new headline, the About chapter and the
   renamed capabilities, and render `l'IA AI` in three languages.

## Blocking launch

- **Impressum** — legally required in Germany, does not exist yet
- **Privacy notice** — does not exist yet
- Enquiry form is built and posts to `/api/enquiry` (Vercel + Resend), but
  **is not sending**: set `RESEND_API_KEY`, `ENQUIRY_TO`, `ENQUIRY_FROM` as
  Vercel env vars. Until then it falls back to the visitor's mail client.
- The form asks for consent to store personal data and has no privacy notice
  to link to. That pairing is the real launch blocker, not the keys.
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

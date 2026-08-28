# Status — 28 August 2026

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

1. **Chapter 07 integration.** Section is in and passing, but has not been
   reviewed on screen at any width.
2. Inner pages still carry the old design — and they still hard-code the long
   nav CTA label, so they show the same overflowing header on phones that the
   homepage just had.
5. Translations: `rm i18n/FROZEN && python3 build_i18n.py`, then re-run the
   gate — it will fail until every localised page matches the new structure.

## Blocking launch

- **The Impressum has no address or telephone number.** The page exists and is
  linked from every footer, but renders `{{TODO:STREET_AND_NUMBER}}`,
  `{{TODO:POSTCODE}}` and `{{TODO:TELEPHONE}}`. § 5 DDG requires a
  *ladungsfähige Anschrift* — an address where documents can be served, so not
  a PO box — and a second rapid-contact channel alongside email. Release gate
  stage 4b fails on these five tokens and **they are the only thing it fails
  on**. Only Balaji can supply the values.
- Native-speaker review of all four languages (every `i18n/*.json` carries
  `"reviewed_by_native_speaker": false`)
- Trademark clearance for "Quenora"

## Done since this file was last written

- **Impressum and privacy notice exist**, at `impressum.html` and
  `privacy.html`, linked from every footer in all five languages. § 5 DDG and
  GDPR Art. 13. Registration status is stated honestly: a sole proprietorship
  not yet in the Handelsregister, so no HRB number or VAT ID is invented.
- **The contact form is wired.** `api/enquiry.js` posts through Resend,
  consent-gated, and falls back to the mail client only when no API key is
  configured.
- The company name is settled as **Quenora Consulting** — no `GmbH` until it is
  registered. Contact address is **info@quenora.ai**, not `hello@`.
- Release gate: **8 of 9 stages green**. Node is installed and
  `test/node_modules` is populated, so the gate actually runs; a fresh clone
  still needs `npm install` in `quenora/test`.

## Where the detail lives

Remediation against the website audit is tracked item by item — 27 closed, 27
open, with file paths, measurements and the reasoning behind each decision — in
a ledger outside this repo, because it contains internal criticism and
`vercel.json` serves this directory wholesale. Ask Abinaya for the link.

Deliberate decisions recorded there, so they are not re-litigated:
`products.html` stays in the repo unlinked and `noindex`; the inner pages keep
the old design until the homepage is finished; the four localised builds are
deferred until then, and their rebuild has to cover country-specific legal
content, not just translation.

## Housekeeping

- `.git/` holds ~14 `*.stale` lock files and some `tmp_obj_*` left by commits
  made from a sandbox that can write but not delete. Harmless. Clear with
  `git gc --prune=now`.
- `quenora/index-old-backup.html` is the superseded homepage, linked from
  nothing. Kept on purpose. It is the main source of misleading search hits —
  see `CLAUDE.md`.

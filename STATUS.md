# Status — 28 August 2026
# Status — 30 August 2026

Working on branch **`quenora-test-claude`**, tip `a49961b`, synced with origin,
working tree clean. **`main` has none of this yet** — the merge happens once the
bug list is worked through, and Balaji is not editing `main` in the meantime.

Release gate: **8 of 9 green.** Stage 4b is the only failure and it is the
Impressum address. Stage 6 is HELD by design.

```
cd quenora/test && bash release.sh ..
```

## Looking at it

The preview server dies with the session, so start it yourself:

```
python -m http.server 8842 --directory C:/Anu_Software/Git/GitHub/quenora/quenora
```

Then **`http://localhost:8842/index.html?v=50`**. Bump the number every time —
browsers cache this page aggressively and a stale render has cost real time
twice. Versions up to `v=49` are used; **start the next session at `v=50`**.

The quickest tell that you are on a current build: the header CTA is a **solid
copper button**. If it is an outline, the page is stale whatever `?v=` says.

## Where the work is

**English pages.** The four localised builds are frozen and stale.

| | |
|---|---|
| Live page | `quenora/index.html` — 9 chapters + hidden `#build`, enquiry form, assistant |
| Inner pages | `services` `products` `approach` `work` `contact` — not yet reworked to match the new homepage |
| Translations | `de/ fr/ es/ it/` — 24 pages, **frozen and stale**, see `i18n/FROZEN` |
| Tests | `quenora/test/` — 9-stage gate, `bash release.sh ..` |
| Homepage | `quenora/index.html` — 9 visible chapters + a hidden 10th, ~2,400 words, ~23 screens |
| Engineering | `quenora/engineering.html` — **new, 30 Aug**, the evidence page |
| Inner pages | `services` `approach` `work` `contact` — still the previous design generation |
| Unlinked | `products.html` — in the repo, `noindex`, out of the sitemap, deliberately |
| Translations | `de/ fr/` linked · `es/ it/` unlisted and `noindex` — all four frozen, see `i18n/FROZEN` |
| Tests | `quenora/test/` — 9-stage gate |

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
hook · 01 problem · 02 fit · 03 journey · 04 solution · 05 work
[06 build — HIDDEN] · 06 honest · 07 who · 08 commercial · 09 principles · climax
```

`#build` is hidden and carries **06, the same number as `#honest`**. Releasing it
without renumbering the four chapters after it publishes two 06s.

## Done in the 29–30 August passes

- **A CTO audit scored the site 57/100; a rebuild pass took it to 83.** Both are
  written up as artifacts — ask Abinaya for the links, they are in the ledger footer.
- **`engineering.html`** — the firm's only inspectable evidence. Four decisions and
  what each cost, the nine gate stages with real counts, five principles tied to
  phases, a worked problem-to-architecture example labelled illustrative, and the
  evaluation harness explained.
- **The homepage had no mobile navigation.** Below 880px it hid its nav links and
  put nothing in their place, while the older inner pages had a working menu.
  Ported: burger, collapsing panel, header grows to hold it.
- **Three inline CTAs** after chapters 03, 06 and 08. First ask moved from screen
  17.3 to 6.8; the form used to be the only route in.
- **Hero trust block** — the reference-call offer, fixed scope and "you keep the
  code" brought forward from screens 13 and 17. Nothing new is claimed; it is
  stated verbatim elsewhere on the page.
- **`#4` closed** — approach.html now states the same six phases, durations and
  exit conditions as the homepage. Its phase 06 used to read "Sustain · Ongoing".
- **UI6 closed** — the language switcher asked for three tokens the homepage never
  defines, and `.langmenu`'s background resolved to transparent.
- Copy passes across the hook, chapter 01, chapter 02, chapter 03 and phases 01–03.

## Two invariants that are easy to break

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
1. **approach.html mirrors the homepage's method.** Phase names, headings,
   durations and exit conditions must match on both pages — that is what closed
   `#4`. Editing an exit condition on one page and not the other reopens it. It
   has already happened once, caught by parsing both pages rather than reading them.
2. **The hero constellation is measured against the headline box.** Gate stage 7
   fails the build if the arc drifts off the grid. Any change to hook spacing
   moves it, so re-run the gate.

## Blocking launch

- **The Impressum has no address or telephone.** Renders `{{TODO:STREET_AND_NUMBER}}`,
  `{{TODO:POSTCODE}}`, `{{TODO:TELEPHONE}}`. § 5 DDG requires a *ladungsfähige
  Anschrift* — not a PO box — plus a second rapid-contact channel. **The only thing
  the gate fails on. Only Balaji can supply it.**
- **No continuity answer.** The site says the firm is founder-led and never says
  what happens to a client's production system when he is unavailable. The CTO
  audit called this the single biggest unanswered question.
- **No client-side security posture.** Nothing says how credentials, data or
  environment access are handled, from a firm asking for exactly that.
- Native-speaker review of all four languages (`"reviewed_by_native_speaker": false`).
- Trademark clearance for "Quenora".

## Known-live problems in the localised builds

They are frozen, so none of this is fixable in the source — it clears when
`build_i18n.py` runs.

- All four homepages say **six seams over three cards**.
- The German counter renders **0 where it should render 9**.
- The **language switcher is broken on every localised page** — it carries the
  English page's hrefs, so "Deutsch" from `/de/` resolves to `/de/de/` and 404s.
  Cause and fix are recorded in `i18n/FROZEN`.
- A duplicated acronym in every localised H1.

## Environment

- **Node 24.19 is installed**; `test/node_modules` is populated. In bash first:
  `export PATH="/c/Program Files/nodejs:$PATH"`. A fresh clone needs
  `npm install` in `quenora/test`.
- **bs4 is NOT installed**, so `build_i18n.py` cannot run here. Generator-derived
  changes have to be hand-applied to match what it would emit, with the generator
  updated in the same commit.
- **jsdom is available** in `test/node_modules` and is the right tool for any
  question about what the rendered page contains. Set
  `NODE_PATH=.../quenora/test/node_modules`; note node resolves `/tmp` as `C:\tmp`.

## Where the detail lives

Item-by-item remediation — **31 open, 38 closed, 69 rows**, with file paths,
measurements and the reasoning behind every decision — is in a ledger outside this
repo, because it contains internal criticism and `vercel.json` serves this
directory wholesale. **Ask Abinaya for the link.** Two companion pages are linked
from its footer: the CTO audit and the rebuild report.

Decisions recorded there so they are not re-litigated: `products.html` stays
unlinked and `noindex`; Spanish and Italian are unlisted, not deleted; the inner
pages keep the old design until the homepage is finished (`scope-2`); the localised
rebuild must cover country-specific legal content, not just translation.

## Editorial rules, settled 29 August

- **Contractions — use them.** `don't`, `won't`, `it's`.
- **Serial comma — do not use.** "platforms, workflows and decisions".
- **Numbers — words in running prose, digits in labels and statistics.**
- British English throughout; the gate checks spellings but none of the other three.

The site is **half-converted on all three**, because each was settled mid-paragraph
and applied only where it came up. Tracked as the `style` row; run it before any
i18n regeneration, or it is done twice.

## Housekeeping

- `.git/` holds `*.stale` lock files and `tmp_obj_*` from sandboxed commits.
  Harmless. `git gc --prune=now`.
- `quenora/index-old-backup.html` and `story.html` are superseded homepages, linked
  from nothing, kept on purpose, and the main source of misleading search hits.
  See `CLAUDE.md`.
- Three orphaned translation keys have been found by accident so far. Clearing dead
  keys is worth one deliberate pass over `i18n/*.json` before regenerating.

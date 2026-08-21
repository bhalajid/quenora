# Quenora — website

Static marketing site for **Quenora Technology Consulting**.
Domain `quenora.ai`. Five languages, 30 pages, zero runtime dependencies.

## Zero dependencies — deliberately

**No script on this site loads from a CDN.** Verified: `0` external
`<script src>` across all 31 pages.

This is not a style preference. An earlier build loaded Three.js and GSAP from
cdnjs. On a locked-down corporate network, an offline machine, or a file opened
directly from disk, those requests fail — and the hero rendered dead while the
rest of the page looked fine. Enterprise buyers browse on exactly those
machines. Every animation is now hand-written in CSS and native JavaScript.

The only network requests are Google Fonts, and the site renders and animates
correctly if those fail too.

## Structure

```
index.html              Home — canvas hero, automation demo, nine principles
services.html           Nine capabilities
products.html           Frameworks, with honest status badges
approach.html           Six-phase method, four non-negotiables
work.html               Engagement patterns (not named clients)
contact.html            Briefing form
story.html              Alternative editorial scroll-narrative homepage (draft)

de/ fr/ es/ it/         Generated localised copies of all six pages
i18n/*.json             Translation sources — edit these, never the built pages
build_i18n.py           Generator: builds de/ fr/ es/ it/, hreflang, sitemap
assets/                 Generated abstract card artwork
test/                   Six-stage release gate
```

## The hero

Nine nodes on the brand's own 9-9-90 arc, drifting on independent orbits,
wiring themselves together as they come into range, firing cyan signal pulses
along the connections. Particles fall inward and are captured. The pointer
parallaxes the field and lifts the nearest node, revealing its principle name.

Plain 2D canvas. Roughly 1,080 draw operations per frame, no GPU required.
Pauses when scrolled out of view. Under `prefers-reduced-motion` it paints one
static frame and stops.

## Commands

```bash
python3 build_i18n.py          # rebuild de/ fr/ es/ it/ + sitemap
cd test && npm install         # first time only
cd test && ./release.sh ..     # the gate — run before every push
```

## The release gate

Six stages. Any failure blocks the push.

| # | Stage | Checks |
|---|---|---|
| 1 | Syntax + structure | JS parses, tags balanced |
| 2 | Sphere hit-testing | 180 pick cases against real geometry |
| 3 | Smoke (jsdom) | 177 assertions — executes each page's real JS |
| 4 | Accessibility + SEO | Landmarks, alt text, h1 count, focus, links |
| 5 | Contrast | WCAG AA, computed not eyeballed |
| 6 | Translations | Coverage, punctuation, orthography, hreflang |

Stage 3 runs each page in a headless DOM configured like a managed corporate
browser: 2D canvas works, WebGL is blocked. That configuration broke the
predecessor site, so it is the default the tests assume.

## Editing

**Never edit `de/`, `fr/`, `es/`, `it/`** — they are generated and will be
overwritten.

- English copy → the root `.html` files, then `python3 build_i18n.py`
- A translation → `i18n/<lang>.json`, then rebuild

New English copy appears as untranslated in the build report. Coverage below
100% fails the gate. See `TRANSLATIONS.md`.

## Deployment

Vercel, static. `vercel.json` sets `framework: null` and `outputDirectory: "."`
so nothing tries to build it. `/de/`, `/fr/`, `/es/`, `/it/` serve as static
paths with no configuration. Set the domain to `quenora.ai`.

## Before launch

| Item | Where | Status |
|---|---|---|
| Contact email | `i18n/*.json`, page footers | `hello@quenora.ai` — confirm it exists |
| Form backend | `contact.html` | Opens a mail client; needs Formspree or similar |
| **Impressum** | footer | **Legally required in Germany** — placeholder only |
| Privacy notice | footer | Required — placeholder only |
| Registration / VAT | footer | Placeholder |
| Case studies | `work.html` | Placeholders by design |
| Native-speaker review | `i18n/*.json` | `reviewed_by_native_speaker: false` in all four |
| Trademark clearance | — | Not done |

Placeholders render in amber with a dashed underline so none can ship unnoticed.

## Rules

- No client names, logos, metrics or certifications without written sign-off.
  Stages 3 and 6 of the gate enforce this.
- Exactly nine capabilities, three core, one canonical list.
- No CDN scripts. Ever. That is what stage 3 checks.
- Copper is the brand colour; cyan marks live signal only.

# Quenora Technology Consulting — website

Static marketing site. Owner: Balaji "Guru" Durai, Heilbronn, Germany.
Domain `quenora.ai`. Repo `github.com/bhalajid/quenora`. Deployed on Vercel.

**Read `STATUS.md` first.** It is the current state of play and is kept short
on purpose. Do not re-derive it by reading the whole site.

## Read this before searching the repo

These paths are large and will waste your context. Do not grep or read them
unless the task is specifically about them:

- `quenora/test/node_modules/` — 42 MB, all of it dependencies
- `quenora/index-old-backup.html` — the superseded first homepage. Kept
  deliberately as a reference; it is linked from nothing and is NOT the live
  page. Searches for brand words hit it and return stale copy. Ignore it.
- `quenora/story.html` — the same thing again: an *earlier* draft of the
  homepage, not a separate page. Same `<title>`, same `problem`/`journey`/
  `solution` ids, missing the `fit`, `honest`, `commercial` and `principles`
  chapters. Deliberately orphaned and deliberately absent from `sitemap.xml`.
  Do not link it — it would put a stale duplicate homepage in the navigation.
- `quenora/de/ fr/ es/ it/` — 24 generated pages, currently frozen and stale
  (see `quenora/i18n/FROZEN`). Never hand-edit them; they come from
  `build_i18n.py`.

The live homepage is `quenora/index.html` and nothing else.

Useful greps:

```
rg --glob '!test/node_modules' --glob '!index-old-backup.html' --glob '!{de,fr,es,it}/' PATTERN quenora/
```

## Architecture — the one rule that matters

**Zero external dependencies. No CDN scripts anywhere.** Every page is one
self-contained HTML file: CSS in a `<style>` block, JS in a `<script>` block,
no build step, no framework, no bundler.

This is not a preference. GSAP and Three.js were both loaded from cdnjs
earlier and both produced a completely dead hero on networks that block CDNs —
which is exactly the locked-down corporate network this site sells into. Every
animation is now native CSS or 2D canvas. If you are about to add a `<script
src=`, don't; the release gate fails on it.

## The mark

Nine circles on a 90° arc, growing 9× from first to last (ratio 9^(1/8) =
1.3161). Coordinates are hardcoded in the viewBox `0 0 187.71 174.29` space
and **must stay byte-identical everywhere** — nav, footer, favicon, hero
canvas, and the chapter 07 diagram all derive from the same nine triples.

The nine circles map to nine principles, in order: Trustworthy, Human,
Confident, Elegant, Timeless, Enterprise, Premium, Innovative, Intelligent.
Chapter 07 of the homepage is where they are named.

**Never put text inside the mark.** Tried, rejected — it fails at small sizes.

The nav and footer lockups crop the viewBox to `9 9 169.71 155.71` so the ink
fills its box. That is a crop, not a coordinate change.

### Hero geometry — do not "simplify" this

The hero constellation is constructed on the page's own six-column grid
(`.vgrid`, drawn at the wrap's width), against the headline's measured box:

- the arc is exactly as tall as the `h1` block
- its right edge sits on the wrap's right grid line
- its bottom sits on the headline's bottom
- the mark does not move (`SWAY` and `BOB` are both 0)

Earlier versions centred it in arbitrary viewport fractions and gave each
sphere its own orbit. Both are regressions the gate now catches — independent
orbits destroy the logo's spacing, and any motion drifts the arc off the grid
lines it is built on.

## Brand constants — do not change without asking

```
--void   #07070A    --sf1 #0D0E13   --sf2 #14161E
--t1     #F2EFE8    --t2  #A8AEBB   --t3  #7C8290
--copper #C97A3C    --copper-lt #E9A063
--ember  #FF7043    --signal #5BD7F5
fonts: Inter (UI) · JetBrains Mono (labels, numbers) · Playfair Display (italic accents)
```

Copper over blue was deliberate — most European AI firms are blue. Do not
"modernise" it to blue.

## Editorial rules

- **No fabricated clients, logos, metrics, testimonials or certifications.**
  Placeholders render visibly in amber with a dashed underline.
- Illustrative diagrams must say they are illustrative. The chapter 01 "gap"
  figure carries that caption.
- British English throughout — the gate fails on US spellings.
- No filler vocabulary (seamless, world-class, cutting-edge, leverage,
  game-changing…). The gate has the list.
- Sentence case in headings, not Title Case.

## Security — non-negotiable

A private SSL key was once committed to the **AIBoosters** repo and had to be
revoked. This repo was created with no shared history for that reason.
`.gitignore` blocks `*.key *.pem *.crt *.cer *.pfx *.p12 .env*`. Never add a
key, token or secret to this repo under any circumstance.

## Before you claim anything works

```
cd quenora/test && bash release.sh ..
```

Nine checks. It must print `RELEASE APPROVED`. Stage 6 (translations) is
deliberately HELD while the English page is being finalised — that is expected,
not a failure. See `quenora/i18n/FROZEN`.

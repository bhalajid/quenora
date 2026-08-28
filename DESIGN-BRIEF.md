# Quenora — design brief / handoff

Written so this can be picked up cold, in this session, in a design canvas, or
by a human designer. Read `CLAUDE.md` for the engineering rules; this file is
about how the thing looks and why.

---

## What this is

A static marketing site for a founder-led enterprise AI and automation
consultancy. Heilbronn, Germany, working internationally. Founded 2025.
Domain `quenora.ai`. The homepage is finished and good; the five inner pages
are not.

**The single biggest visual problem on the site is not the homepage. It is
that `services` `products` `approach` `work` `contact` still carry the
previous design and look like a different company.**

---

## The design system, as built

### Palette — do not change without a decision

```
--void   #07070A    --sf1 #0D0E13   --sf2 #14161E
--t1     #F2EFE8    --t2  #A8AEBB   --t3  #7C8290
--copper #C97A3C    --copper-lt #E9A063
--ember  #FF7043    --signal #5BD7F5
```

Copper over blue is deliberate — most European AI firms are blue. The greys
are deliberately neutral, with no blue bias, because an earlier palette read
as navy on uncalibrated laptop panels.

### Type

- **Inter** — UI and headlines. Headlines are heavy (800), tight tracking
  (−.045em), sentence case, never Title Case.
- **JetBrains Mono** — labels, eyebrows, numbers, chapter numbers. Uppercase,
  wide letter-spacing (.16–.24em), small (.56–.72rem).
- **Playfair Display italic** — one accent per headline, in `--ember`. This is
  the signature move: a heavy sans headline with one italic serif phrase.

### The mark

Nine circles on a 90° arc, growing 9× from first to last (ratio 9^(1/8)).
Coordinates are hardcoded in viewBox `0 0 187.71 174.29` and **must stay
byte-identical everywhere** — nav, footer, favicon, hero canvas, chapter 09
diagram, the gap figure, the OG image. Never put text inside the mark.

The nine circles map to nine principles: Trustworthy, Human, Confident,
Elegant, Timeless, Enterprise, Premium, Innovative, Intelligent.

Spheres are rendered as lit objects, not flat discs: dark body, lit rim, one
specular highlight up-left. Flat copper fills read as blobs — this was fixed
once already, do not undo it.

### Layout

Six-column grid (`.vgrid`), drawn as faint verticals at the wrap width.
Wrap max-width `--wrap`, 20px gutters. The hero constellation is constructed
on this grid, not on viewport fractions.

Spacing scale: `--sp2:16 --sp3:24 --sp4:40 --sp5:64 --sp6/7` upward.

---

## Page structure (homepage, current)

```
nav (Approach · Capabilities · Work · About · CTA · language)
hook          headline + constellation canvas
ticker        nine capability labels, small
01 problem    + "the gap" canvas diagram (3 beats, loops 11.3s)
02 fit        three situations
03 journey    six phases, horizontal pinned scroll
04 capabilities  nine rows + automation canvas figure
05 work       three engagement shapes
—  build      HIDDEN. projects & products. see STATUS.md before releasing
06 objections
07 who        about, founder, facts panel
08 pricing
09 principles the nine, with the mark
climax        headline + enquiry form
footer
assistant     floating panel, written answers
```

---

## Editorial rules that constrain design

- **No fabricated clients, logos, metrics, testimonials or certifications.**
  Placeholders render visibly in amber with a dashed underline (`.ph`).
- Illustrative diagrams must say they are illustrative.
- British English. The gate fails on US spellings.
- No filler vocabulary (seamless, world-class, cutting-edge, leverage…).
- Sentence case headings.
- Prior-career claims must be attributed to before Quenora existed.

---

## Hard technical constraints

- **Zero external dependencies. No CDN scripts.** GSAP and Three.js were both
  tried and both produced a dead hero on the locked-down corporate networks
  this site sells into. Every animation is native CSS or 2D canvas.
- One self-contained HTML file per page. No build step, no framework.
- CSP is `connect-src 'self'`. Same-origin `/api/*` is allowed; nothing else.
- Everything must pass `cd quenora/test && bash release.sh ..` — 9 checks
  including WCAG AA contrast, a11y, SEO, British English, and hero geometry.

---

## Known UI/UX work, in priority order

1. **The five inner pages.** They carry the old design. This is the largest
   and most visible inconsistency on the site. `services.html` content is
   current; the others need both design and a content pass.
2. **Privacy notice + Impressum.** Legally required in Germany, do not exist,
   and the enquiry form now collects personal data and asks for consent it
   cannot link anywhere.
3. **Translations.** `de/ fr/ es/ it/` are frozen and stale — they predate the
   new headline, the About chapter, the renamed capabilities and the new
   chapter structure. They currently render `l'IA AI` in three languages.
4. **Mobile pass on the new sections.** The work, about and form sections were
   built desktop-first and checked at 375/430 only briefly.
5. `#build` section release — see STATUS.md for the two-step it requires.

## Things that are finished — do not redo

- Hero constellation geometry and the nearest-sphere hover (0 mis-picks
  across 161,877 tested positions, gate-enforced).
- The gap diagram's three beats and the rail notching.
- The lit-sphere rendering treatment.
- Chapter 09's mark-to-principles interaction.
- The nine-capability taxonomy and the automation figure.

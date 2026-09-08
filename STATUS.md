# Quenora — build status and handover

Updated 8 September 2026. Written so a fresh conversation can pick the work up
without reading anything else. **Read this file first.**

---

## 1. What this is

A static marketing site for Quenora Consulting (Bad Friedrichshall), launching
on **quenora.ai**. Deployed at `quenora.vercel.app` from `main`, and that
deployment is live and answering 200.

**The one architectural rule:** no third-party runtime dependency. Every page
is self-contained apart from four first-party files it serves itself —
`/assets/nora.js`, `/assets/nora.css`, `/assets/logo.js`, `/assets/eggs.js`.
Not minimalism for its own sake: an earlier version loaded GSAP and Three.js
from a CDN and the hero was dead on locked-down corporate networks, which is
exactly the audience. **Nothing may reintroduce a CDN dependency.** Same-origin
files are fine and are how Nora has always worked.

Fonts (Google Fonts) are the one exception, and are an open item.

---

## 2. Blocking launch — both yours, neither code

1. **`{{TODO:STREET_AND_NUMBER}}`**, once each in `impressum.html` and
   `privacy.html`. The postcode and town are in — 74117 Bad Friedrichshall —
   so the street is the last of the four. German §5 TMG requires a full postal
   address. **This is the only red stage in the gate.** Send the street and it
   closes in one commit.
2. **DNS.** Verified today: `quenora.ai` still resolves to the parking IP
   192.64.119.248 and HTTPS does not answer. Point it at Vercel. The redirect
   is deliberately **not** in the repo — adding it before the domain answers
   would take the site down. The exact block is in `LAUNCH.md`, to be pasted on
   launch day.

`test/launch_check.sh` runs 20 live assertions afterwards.

---

## 3. How to build and verify

```bash
cd quenora && ./build.sh
cd quenora/test && bash release.sh ..
```

**`build.sh` finds its own interpreter now.** It prefers `./quenora/.venv`,
falls back to `/tmp/qvenv`, then to `python3`, and prints which it picked. It
used to hardcode `/tmp/qvenv/bin/python3`; macOS clears `/tmp`, so the build
failed on its own and printed instructions to rebuild the venv in the place it
gets deleted from. If no python has beautifulsoup4:

```bash
cd quenora && python3 -m venv .venv && .venv/bin/pip install -q beautifulsoup4 pillow
```

**`build.sh` is idempotent — verified.** Run against `main` in a scratch
worktree it changes zero files. It was changing 56 until `build_logo_arc` was
retired (§4). If a build ever produces a diff, that is a finding, not noise.

**Build order is load-bearing.** 21 generators, and `build.sh` enforces the
order. The three rules: `build_i18n` regenerates `de/ fr/ es/ it/` from the
English source, so anything writing into a localised page runs *after* it and
anything editing English content runs *before*; `build_logo_motion` must follow
`build_brand`; and `build_asset_versions` runs **last of all**, because it
rewrites every `/assets/` URL and nothing may write one after it.

### The gate — 19 stages

Every stage exists because a real defect got past someone, and each was
verified to reproduce that defect on the commit before its fix. Notable:

- `4j` **browser_audit.js** — Chromium, 7 pages × 3 language trees × 3
  viewports. No console error, no failed request, no horizontal overflow, an
  italic Playfair ember word in every headline, one current nav tab with
  `aria-current`, Nora present, and logo/header/body geometry identical
  between pages. Then drives Nora in each language.
- `4c deployed_links.py` — resolves links against **the deployed URL shape,
  not the filesystem.** The filesystem lies.
- `7 hero_geometry.js` — the hero's arc on the grid. **Fixed 8 Sep**; see §4.
- `8 qa_english.js` — two size budgets, raw ≤ 225 KB and transfer ≤ 70 KB.
  `index.html` is currently 214.1 KiB raw, 63 KB gzipped.

Playwright is under `test/`. Screenshots: `node browser_audit.js .. --shots`.

---

## 4. Traps that have each cost a production bug

**`immutable` caching on unversioned URLs.** `vercel.json` serves everything
under `/assets/` with `max-age=31536000, immutable`. That is a promise the
bytes at a URL will never change, so browsers keep them for a year and never
revalidate — and they do. A new favicon deployed correctly, was byte-identical
on the live host, and still did not reach anyone who had visited before.
`build_asset_versions.py` now appends `?v=<sha256[:8]>` to every `/assets/`
reference, which is the condition `immutable` is meant to be paired with. **Any
new asset reference must go through it.**

**There are two nine-circle geometries, on purpose.** The drawn mark (1.09:1,
9× over 90°) is `var MARK`, the favicon, the hero canvas, the chapter 07
diagram, Nora's button and the pointer trail — byte-identical within that set.
The lockup carries the supplied artwork's own nine (2.26:1, 10.72× over 37°,
step wandering 1.209–1.571). They cannot be merged: the hero's arc is pinned to
the headline's height, so the lockup's aspect makes it 2.08× wider and it
overlaps the type — verified, six viewports. `build_logo_arc.py` tried to merge
them and is **retired**: out of `build.sh`, and it exits unless passed
`--force`. `CLAUDE.md` § The mark has the full rule.

**cleanUrls means no trailing slash.** `/de/index.html` 308-redirects to `/de`.
Any path match must be `/^\/(de|fr)(?:\/|$)/`. Invisible locally. Has caused
two production bugs: relative links resolving to the English site, and the
assistant answering French visitors in English.

**A page can be missing from a generator's list.** `pricing.html` shipped with
the launch release, was added to `build_logo_motion`'s `PAGES` and not to
`build_brand`'s, and so kept the CSS it was created with — its logo rendered at
34px while every other page was at 62px. A "one logo size" commit did not fix
it, because the cause was the list rather than the values. **A new page must be
added to every generator's list**; grep `^PAGES` across `build_*.py`.

**A width rule beats a height rule.** `.f-lockup img{width:118px}` overrode the
footer logo's height rules, so it rendered 118×49 whatever the CSS said, and
the tagline inside the full lockup came out about two pixels tall.

**The harness lies more often than the page does.** Four times now a "defect"
was the test:

- `hero_geometry.js` took the first nine `<circle>` elements in `index.html`.
  The hero draws its arc on canvas from `var MARK`; the first nine circles are
  `.ch-mark` chapter icons at line 1588. It reported `r9 = 766px` — a
  766-pixel-radius sphere — and passed. It reads `var MARK` now, and takes the
  largest radius from the data instead of a hardcoded 27.
- `hero_hover.js` had the same bug and was fixed the same way.
- `elementFromPoint` can never return an element with `pointer-events:none`,
  and the full-viewport `.aura` sits in front of everything.
- A smoke test asserted `!/<script[^>]*\bsrc=/` with the message "must not
  depend on a CDN". Same-origin is not a CDN.

**Guard scripts on capability, not truthiness.** The headless field-figure
harness runs every page script against a minimal DOM stub where
`getElementById` returns something truthy with no methods, and `matchMedia`,
`location` and `addEventListener` may not exist. Five scripts have been caught
by it, the easter eggs most recently.

**Read the whole gate output.** Filtering it with `head -25` hid a failing size
budget for three commits, each reported as green.

---

## 5. What the site is now

**English only.** `build_i18n.UNLISTED_LANGS = {de, fr, es, it}` — all four
trees still build and are still gate-checked, but nothing links them and
`index.html` declares only `hreflang="en"` and `x-default`. That is the launch
decision; unlisting is one line if it reverses.

Eleven English pages:

| page | what it is |
|---|---|
| `index.html` | the argument, chapters + hero + closing |
| `approach.html` | the phases in full, as a spine of gates |
| `capabilities.html` | the nine capabilities |
| `engineering.html` | five layers, three worked problems |
| `work.html` | engagement patterns + the governed-vs-ungoverned demo |
| `pricing.html` | pricing |
| `about.html` | who you are hiring — see below |
| `contact.html` | contact + what happens when you get in touch |
| `products.html` | unlisted, noindex |
| `impressum.html`, `privacy.html` | legal |

### The five features, all shipped

| # | feature | state |
|---|---|---|
| 1 | **Nora** — site assistant, on every page | done |
| 2 | Contact QR → vCard + scan count | done |
| 3 | `llms.txt` + JSON-LD on every page | done |
| 4 | Wallet pass | **Google done, Apple blocked on a $99/yr cert** |
| 5 | Governed-vs-ungoverned demo, 4 scenarios | done |

**Nora** answers only from sentences already on the site — BM25 over a
pre-built index, no model, no API key, nothing to invent. Says so when she
cannot match.

### The brand, settled 8 September

The lockup is **the supplied artwork** (`Quenora_Web_Logo_Set/quenora-full.svg`)
with two surface changes and nothing else: the nine flat dots are drawn with
the site's sphere treatment at their own centres and radii, and the accent is
copper `#C97A3C` — the token Nora's button and the CTA already use. The Q is
the supplied path, all 390 points, tail whole. The old `primary.svg` had a
viewBox of height 525 and was cropping that tail at 589.

Things tried and reverted, so they are not tried again:

- **Reseating the Q.** It measures 100 units above the wordmark's optical
  centre. That is not a defect — it sits high because the dots sit high and the
  two counterweight each other.
- **Putting the canonical arc in the lockup.** A 1.09:1 square-format mark in a
  2.41:1 lockup reaches neither end; every position only moves the empty space.
- **A speed-driven cursor trail.** Brightening the head as the pointer moved
  produced a bright blob leading the cursor rather than a trail behind it.
- **Ember for the lockup.** It matches the headline accent and stops matching
  the CTA and Nora. The palette has two oranges and no arrangement gives both.

The favicon is the drawn mark alone — nine circles, no letterform — at
16/32/48/64/180/192/512. The `.ico` is written by hand rather than by Pillow,
whose ICO writer downsamples one image and would have discarded the per-size
renders.

### About: one principal

The page that arrived with `develop_release01` described "a firm of senior AI
and platform practitioners", "a team", "between them they have spent years" —
while its own facts block read "Founder-led". There is one person. That copy is
gone. The page now states one principal, names him, claims the capacity limit
as the point, and answers the bus-factor question with what the engagement
already contains — the client keeps the code, the documentation and the
evaluation harness, and the handover phase exists so their own team can run it.
Nothing about availability or employment appears anywhere, deliberately.

**This matters beyond tone.** `CLAUDE.md`'s editorial rule is no fabricated
clients, metrics or testimonials, and the work page's strongest line is that
there are no case studies yet and none will be invented. One invention makes a
reader re-audit everything else.

### Four easter eggs

None fire on their own: a console banner; the Konami code, which lights each
header sphere and names the nine principles; typing `nora`, which opens the
assistant and is guarded so it cannot eat a form entry; and `?grid`, which
draws the six columns the site is measured against — an actual tool.

### Design decisions worth not re-litigating

- **The nav goes to the page**, from every page, so the current-tab marker can
  fire.
- **One container**: header, nav and body start at the same x everywhere. The
  hero keeps 1480 because its mark is tied to the headline height and a grid
  line.
- **The custom cursor ring is gone.** It read as a loading spinner.
- **Chapter marks are closed shapes.** Open arcs read as unfinished.
- **The intro curtain is ~2.4s** — 1250ms counter, 180ms hold, 1000ms slide.
  Deliberate, honours `prefers-reduced-motion`. It is why a screenshot taken
  early comes back black with a number on it.

---

## 6. Open items

**Mine, technical**

- Self-host the fonts. Lighthouse prices Google Fonts as render-blocking at
  **2,050 ms** — the largest remaining performance item.
- `browser_audit.js` still covers 7 pages × 3 language trees × 3 viewports. It
  misses `about`, `impressum`, `privacy` and `pricing`, and the whole tablet
  band between 1280 and 375. A widening was written and lost in a rebase; it
  needs redoing against an English-only site.
- `build_about.py` builds an older About page than the one shipped. It does
  **not** clobber the current copy — verified — but it is stale.
- Nora's twelve canned fallback answers are English in all languages. They only
  appear if `assistant.json` fails to load.
- 15–16 links per inner page are 22px tall on mobile, under the 24×24 of WCAG
  2.2 AA 2.5.8. Mostly footer links; fixing it changes spacing.

**Yours, decisions**

- **The name.** "Quenora" against **Quora** is closer than any logo question,
  and no logo change addresses it. Worth a professional EU word-mark search
  before launch. Not something I can answer.
- **DE/FR have never been read by a native speaker.**
  `reviewed_by_native_speaker: false` in both dictionaries. Moot while they are
  unlisted; blocking if they are ever offered.
- **Apple Wallet** needs the paid developer certificate.
- **"chatbot" appears once, as a negation** — *"Not a chatbot bolted onto a
  homepage."* A buyer searching their own word finds a refusal.
- **Which AI work do you actually take on?** Still open, and needed before the
  work page can claim breadth.
- Terms of Service; accessibility statement.
- The hidden `#build` section — **two chapters both claim 06**. Invisible only
  because `#build` carries `hidden`. Renumber 06–09 → 07–10 in the same change.

---

## 7. Contact details of record

Used by `api/card.js`, `api/pass.js`, `impressum.html`:

- **Quenora Consulting**, 74117 Bad Friedrichshall, Germany
- **+49 152 3392 7436** · **+49 152 5643 3329**
- **info@quenora.ai** · **https://quenora.ai**

---

## 8. Branches and worktrees

```
main                     deployed; everything above is on it and pushed
infographics             worktree at ../Quenora-infographics, merged and far
                         behind main. Safe to delete:
                         git worktree remove ../Quenora-infographics
                         git branch -D infographics
```

**Two people are working on this repo.** Three times on 7–8 September, commits
landed on `origin/main` mid-task — including a parallel About page and a
parallel logo-size fix. **Fetch before you commit, and rebuild on top rather
than merging** when the conflict is in generated markup: reset to
`origin/main`, restore the hand-edited sources, re-run the generators.

Local preview: `cd quenora && python3 -m http.server 8811`, or
`python3 serve-preview.py 8800` for cleanUrls with `/c` and `/w` answered the
way production does.

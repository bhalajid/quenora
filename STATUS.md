# Quenora — status and handover

Updated 13 September 2026. Read this first; it is written so a fresh
conversation needs nothing else.

---

## 1 · Live, and nothing is blocking

The site is up on **https://quenora.ai** and both former blockers are closed.

1. **The address landed** (`1fc9ef1`). `Kleiststr. 12, 74117 Bad
   Friedrichshall` is in `impressum.html`, `privacy.html` and the JSON-LD on
   all 47 pages. The gate has no red stage.
2. **DNS is routed and the apex is primary.** `quenora.ai` serves 200;
   `www.quenora.ai` and `quenora.vercel.app` both 308 to it, paths preserved.
   This was backwards until 13 September — the apex redirected to `www` while
   every canonical, `og:url` and all 26 sitemap URLs declared the apex, so
   Google was being sent to a canonical that refused to serve. It is a Vercel
   dashboard setting, not repo state. `test/launch_check.sh` is **23/23**.

**Indexing.** Google Search Console ownership is verified by DNS TXT and the
sitemap has been submitted. Bing has the IndexNow key at
`/db0e6932619b44a8bcdbfac2be94364c.txt` and a submission has been sent.
Ranking for the bare word "quenora" is contested by an unrelated musician who
already holds that entity in Google's graph; `alternateName` now carries
"Quenora Consulting" and "Quenora AI", which are the names that do not
collide. Google Business Profile is the strongest remaining lever and is
not yet created.

---

## 2 · What this is

Static marketing site for Quenora Consulting, launching on **quenora.ai**,
deployed from `main`. **English, German and French are offered** — `/de` and
`/fr` serve 200 and `index.html` declares `hreflang` for all three plus
`x-default`. `es/` and `it/` still build and are gate-checked but nothing
links them. **Neither DE nor FR has been read by a native speaker**
(`reviewed_by_native_speaker: false` in `i18n/de.json` and `i18n/fr.json`);
that was moot while they were unlisted and is not moot now.

Eleven English pages: `index` `approach` `capabilities` `engineering` `work`
`pricing` `about` `contact` · `products` (unlisted, noindex) · `impressum`
`privacy`.

**The architectural rule: no third-party runtime dependency.** Pages are
self-contained apart from four first-party files they serve themselves —
`/assets/nora.js`, `nora.css`, `logo.js`, `eggs.js`. An earlier version loaded
GSAP and Three.js from a CDN and the hero was dead on locked-down corporate
networks, which is exactly the audience. Same-origin is fine and always was.
Google Fonts is the one exception, and an open item.

**Five features, all shipped.** Nora (BM25 over a prebuilt index — no model, no
key, nothing to invent, says so when she cannot match) · contact QR → vCard +
scan count · `llms.txt` + JSON-LD · wallet pass (Google done, Apple blocked on
a $99/yr cert) · the governed-vs-ungoverned demo.

---

## 3 · Build and verify

```bash
cd quenora && ./build.sh
cd quenora/test && bash release.sh ..
```

`build.sh` finds its own interpreter (`./quenora/.venv`, then `/tmp/qvenv`,
then `python3`) and prints which. If none has bs4:
`python3 -m venv .venv && .venv/bin/pip install -q beautifulsoup4 pillow`.

**`build.sh` is idempotent — verified.** Against `main` it changes zero files.
If a build produces a diff, that is a finding.

**Order is load-bearing.** 21 generators. Three rules: `build_i18n` regenerates
`de/ fr/ es/ it/`, so anything writing into a localised page runs after it and
anything editing English runs before; `build_logo_motion` follows
`build_brand`; `build_asset_versions` runs **last of all** — it rewrites every
`/assets/` URL and nothing may write one after it.

**The gate is 19 stages.** Each exists because a real defect got past someone.
Notable: `4j` browser_audit (Chromium, 7 pages × 3 trees × 3 viewports) ·
`4c` deployed_links (resolves against the deployed URL shape, not the
filesystem — the filesystem lies) · `7` hero_geometry · `8` qa_english (raw
≤ 225 KB, transfer ≤ 70 KB; currently 214 KB / 63 KB).

---

## 4 · Traps, each of which cost a production bug

**`immutable` caching on unversioned URLs.** `/assets/` is served
`max-age=31536000, immutable` — a promise the bytes never change, so browsers
keep them a year and never revalidate. A new favicon deployed correctly, was
byte-identical live, and reached nobody who had visited before.
`build_asset_versions.py` appends `?v=<sha256[:8]>`. **Every new asset
reference must go through it.**

**Two nine-circle geometries, on purpose.** The drawn mark (1.09:1, 9× over
90°) is `var MARK`, the favicon, hero canvas, chapter 07, Nora's button, the
pointer trail — byte-identical within that set. The lockup carries the supplied
artwork's own nine (2.26:1, 10.72× over 37°). They cannot be merged: the hero's
arc is pinned to the headline's height, so the lockup's aspect makes it 2.08×
wider and it overlaps the type. `build_logo_arc.py` tried and is **retired** —
out of `build.sh`, exits unless passed `--force`. Full rule in `CLAUDE.md`.

**cleanUrls means no trailing slash.** `/de/index.html` 308s to `/de`. Any path
match must be `/^\/(de|fr)(?:\/|$)/`. Invisible locally; has caused two
production bugs.

**A page can be missing from one generator's list.** `pricing.html` was in
`build_logo_motion`'s `PAGES` and not `build_brand`'s, so its logo rendered at
34px against 62px everywhere else. A "one logo size" commit missed it because
the cause was the list, not the values. **Grep `^PAGES` across `build_*.py`
when adding a page.**

**A width rule beats a height rule.** `.f-lockup img{width:118px}` overrode the
footer logo's heights, rendering 118×49 whatever the CSS said.

**The harness lies more often than the page does.** Five now:
- `hero_geometry.js` took the first nine `<circle>`s; the hero draws from `var
  MARK` and those circles are `.ch-mark` chapter icons. It reported `r9 =
  766px` and passed. Reads `var MARK` now.
- `hero_hover.js` had the same bug.
- `qa_english.js` split sentences on `textContent`, so six phase headings read
  as one 77-word sentence. Splits on block boundaries now.
- `elementFromPoint` never returns an element with `pointer-events:none`, and
  the full-viewport `.aura` sits in front of everything.
- A smoke test asserted `!/<script[^>]*\bsrc=/` under the message "must not
  depend on a CDN". Same-origin is not a CDN.

**Guard scripts on capability, not truthiness.** The field-figure harness runs
page scripts against a DOM stub where `getElementById` returns something truthy
with no methods and `matchMedia`/`location`/`addEventListener` may be absent.
Five scripts caught.

**Generated markup does not keep a hand edit.** Anything inside
`<script data-generated="ld">` is written by `build_seo.py`. A field added to
`index.html` by hand was deleted by the next build and leaked into `es/` and
`it/`, which mirror the English page. Edit the generator.

**`build_i18n` mirrors English before `build_seo` writes it**, so a change to
a page's `@graph` lands in `es/` and `it/` one build late. `build.sh`
converges on the second run and is idempotent after it — verified over 57
files. A single build after touching `PAGES` is not enough.

**Read the whole gate output.** Filtering with `head -25` hid a failing size
budget for three commits, each reported green.

---

## 5 · Decisions not to re-litigate

**Brand.** The lockup is the supplied artwork with two surface changes: the
nine flat dots drawn with the site's sphere treatment at their own centres and
radii, and copper `#C97A3C` — the token Nora's button and the CTA use. The Q is
the supplied path, 390 points, tail whole (the old `primary.svg` cropped it at
589 with a 525-high viewBox). Tried and reverted: reseating the Q (it sits high
because the dots do, and they counterweight); the canonical arc in the lockup
(a 1.09:1 mark in a 2.41:1 box reaches neither end); a speed-driven cursor
trail (a bright blob leading the pointer); ember (matches the headline, stops
matching the CTA — the palette has two oranges and nothing gives both).

Favicon is the drawn mark alone, 16–512. The `.ico` is written by hand; Pillow
downsamples one image and would discard the per-size renders.

**About: one principal.** The `develop_release01` page claimed "a firm of
senior practitioners", "a team", "between them" while its own facts block said
"Founder-led". There is one person. It now states that, names him, claims the
capacity limit as the point, and answers bus-factor with what the engagement
contains — client keeps code, docs and evaluation harness, handover exists so
their team can run it. Nothing about availability or employment, deliberately.
`CLAUDE.md`'s rule is no fabricated clients, metrics or testimonials; the work
page's strongest line is that there are no case studies and none will be
invented. One invention makes a reader re-audit everything.

**Other.** Nav goes to the page from every page, so the current-tab marker can
fire · one container, header/nav/body share an x; the hero keeps 1480 because
its mark is tied to the headline height and a grid line · the custom cursor
ring is gone, it read as a spinner · chapter marks are closed shapes · the
intro curtain is ~2.4s and honours reduced-motion, which is why an early
screenshot comes back black with a number on it.

**Four easter eggs**, none firing on their own: console banner · Konami (lights
each header sphere, names the nine principles) · typing `nora` (opens the
assistant, guarded against form fields) · `?grid` (draws the six columns).

---

## 6 · Open

**Mine.** Self-host the fonts (Lighthouse: 2,050 ms render-blocking, the
largest perf item, and the last third-party runtime dependency on a site whose
architecture rule is not to have one) · **the container disagrees at 768px**
— `index` renders header and body at 728 where all eight other pages render
768, so the logo sits at x=20 on the home page and x=40 everywhere else, and
jumps the moment you navigate off it on an iPad; `engineering` has the logo at
20 with a full-width container, which is a second variant. Found by the
widened audit, not fixed: fixing it changes rendering · Nora's twelve canned
fallbacks are English in all languages, which now reaches real DE/FR visitors
· 15–16 links per inner page are 22px tall on mobile, under WCAG 2.2 AA
2.5.8's 24×24 · `build_about.py` builds an older page than the one shipped
(does **not** clobber it — verified — but is stale).

**Yours.** **DE/FR have never been read by a native speaker** and are now
offered to visitors — by this file's own earlier standard that moved from moot
to blocking · **the name** — "Quenora" against **Quora** is closer than any
logo question and no logo change addresses it; a EUIPO clearance search
through a German Markenanwalt is the only item here that can force a rename,
so it should not keep waiting · **Google Business Profile**, not yet created,
and the strongest entity signal available against the musician who holds
"Quenora" in Google's graph · Apple Wallet cert ($99/yr, optional — the Google
pass works) · **an accessibility statement**, required of commercial sites in
Germany under the BFSG since June 2025, and absent · ToS · which AI work you
actually take on, needed before the work page can claim breadth · "chatbot"
appears once, as a negation, so a buyer searching their own word finds a
refusal.

**Closed since the last revision.** The street · DNS and the apex/www
direction · `about.html` missing from `build_seo.PAGES`, which left 19 pages
on a stale `@graph` with a partial address · `launch_check.sh` asserting 200
on `/services` after the rename to `/capabilities` · `browser_audit.js`
widened from 7 pages × 3 viewports to 11 × 7, 63 → 203 loads, with the legal
pages exempted from the marketing-shell rules rather than left uncovered · the
`?v=` hashes, which had gone stale on all five first-party assets.

---

## 7 · Facts and branches

Contact of record, used by `api/card.js`, `api/pass.js`, `impressum.html`:
**Quenora Consulting**, 74117 Bad Friedrichshall, Germany ·
**+49 152 3392 7436** · **+49 152 5643 3329** · **info@quenora.ai**

```
main            deployed; everything above is on it and pushed
infographics    worktree at ../Quenora-infographics, merged and far behind.
                Safe to delete: git worktree remove ../Quenora-infographics
                                git branch -D infographics
```

**Two people work on this repo.** Three times on 7–8 September commits landed
on `origin/main` mid-task, including a parallel About page and a parallel
logo-size fix. **Fetch before committing**, and when the conflict is in
generated markup **rebuild on top rather than merge**: reset to `origin/main`,
restore the hand-edited sources, re-run the generators.

Preview: `cd quenora && python3 -m http.server 8811`, or `python3
serve-preview.py 8800` for cleanUrls with `/c` and `/w` answered as production
does.

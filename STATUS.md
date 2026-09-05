# Quenora — build status and handover

Updated 5 September 2026. Written so a fresh conversation can pick the work up
without reading anything else. **Read this file first.**

---

## 1. What this is

A static marketing site for Quenora Consulting (Heilbronn), launching on
**quenora.ai**. Currently deployed at `quenora.vercel.app` from `main`.

**The one architectural rule:** every page is a single self-contained HTML file
— inline `<style>`, inline `<script>`, no framework, no bundler, no
third-party JavaScript. Not minimalism for its own sake: an earlier version
loaded GSAP and Three.js from a CDN and the hero was dead on locked-down
corporate networks, which is exactly the audience. **Nothing may reintroduce a
runtime CDN dependency.**

Fonts (Google Fonts) are the one exception, and are an open item.

---

## 2. Blocking launch — both yours, neither code

1. **Four legal placeholders.** `{{TODO:STREET_AND_NUMBER}}` and
   `{{TODO:POSTCODE}}`, two each in `impressum.html` and `privacy.html`.
   German §5 TMG requires a full postal address. **This is the only red stage
   in the release gate and has been for weeks.** Send the address and it
   closes in one commit.
2. **DNS.** `quenora.ai` still resolves to a parking IP. Point it at Vercel.
   The redirect is deliberately **not** in the repo — adding it before the
   domain answers would take the site down. The exact block is in `LAUNCH.md`,
   to be pasted on launch day.

`test/launch_check.sh` runs 20 live assertions afterwards.

---

## 3. How to build and verify

```bash
cd quenora && ./build.sh          # order matters, see below
cd quenora/test && bash release.sh ..
```

**The build interpreter is `/tmp/qvenv/bin/python3`** — the system Python has
no beautifulsoup4 and is blocked by PEP 668. `/tmp` gets cleaned periodically;
when `bs4` goes missing, rebuild it:

```bash
rm -rf /tmp/qvenv && python3 -m venv /tmp/qvenv && /tmp/qvenv/bin/pip install -q beautifulsoup4
```

**Build order is load-bearing.** `build.sh` enforces it; if running steps by
hand, that is the one rule. `build_i18n` regenerates `de/ fr/ es/ it/` from the
English source, so anything that writes into a localised page must run *after*
it, and anything that edits English content must run *before*.

```
build_about · build_chapter01 · build_form · build_climax · build_pricing
build_journey · build_ticker · build_chapters · build_preview_css
build_backto · build_brand · build_widget · build_nav
build_i18n · build_assistant · build_seo
```

### The gate — 19 stages

Every stage exists because a real defect got past me, and each was verified to
reproduce that defect on the commit before its fix. Notable ones:

- `4j` **browser_audit.js** — 63 page loads in real Chromium, 7 pages × 3
  languages × 3 viewports. Asserts no console error, no failed request, no
  horizontal overflow, an italic Playfair ember word in every headline, the
  logo on the headline, one current nav tab with `aria-current`, Nora present,
  correct `<html lang>`, and that logo/header/body/headline position and size
  do not vary between pages. Then drives Nora in all three languages.
- `4c deployed_links.py` — resolves 835 links against **the deployed URL
  shape, not the filesystem**. The filesystem lies.
- `4h` structured data must match the page's own URL and language.
- `4i` every page shares one shell: ember headline, one container, a switcher.
- `4g` every assistant synonym must resolve, in each language.

Playwright is installed under `test/`. Screenshots: `node browser_audit.js .. --shots`.

---

## 4. Traps that have each cost a production bug

**cleanUrls means no trailing slash.** `/de/index.html` 308-redirects to `/de`.
That is the URL visitors land on; `/de/` is never linked. This has caused two
separate production bugs — relative links resolving to the English site, and
the assistant fetching the English index and answering French visitors in
English. Any path match must be `/^\/(de|fr)(?:\/|$)/`. Invisible locally.

**Every English change must land in DE and FR in the same task.** Standing
instruction. `build_i18n` matches on **exact string equality including
whitespace**, so re-wrapping a line silently drops its translation. Attributes
are translated only for `alt`, `aria-label`, `placeholder`, `title`, `data-q`.
Headings with `<em>` are split into per-language emphasis slots — word order
differs, so a slot can land in the wrong place. No automated check for that.

**The harness lies more often than the page does.** Three times this session a
"defect" was my own test:
- `elementFromPoint` can never return an element with `pointer-events:none`
- a scroll-restore test that forced `.rv` reveals on one side and not the other
  invented a 500px error
- `hero_hover.js` scraped the first nine `<circle>` elements as the sphere arc;
  when the logo became an `<img>` it silently started measuring the language
  button's globe. It reads `var ARC` from the page now and exits loudly.

**Guard scripts on capability, not truthiness.** The headless field-figure
harness runs every page script against a minimal DOM stub where
`getElementById` returns something truthy with no methods, and `location`,
`history` and `addEventListener` may not exist. Four scripts have been caught
by it.

**A check pinned to wording fails when the wording moves.** Two QA checks have
had to be repointed from a heading to the claim. The wording is not the thing
worth protecting.

---

## 5. What the site is now

Ten English pages, fully mirrored into **German and French**; Spanish and
Italian exist at ~45% and are unlisted.

| page | what it is |
|---|---|
| `index.html` | the argument, 9 chapters + hero + closing |
| `approach.html` | the six phases in full, as a spine of gates |
| `capabilities.html` | the nine capabilities |
| `engineering.html` | five layers, three worked problems |
| `work.html` | engagement patterns + the governed-vs-ungoverned demo |
| `about.html` | who you are hiring |
| `contact.html` | contact + what happens when you get in touch |
| `products.html` | unlisted, noindex |
| `impressum.html`, `privacy.html` | legal |

### The five features, all shipped

| # | feature | state |
|---|---|---|
| 1 | **Nora** — site assistant, floating on all 24 pages | done |
| 2 | Contact QR → vCard + scan count | done |
| 3 | `llms.txt` + JSON-LD on every page | done |
| 4 | Wallet pass | **Google done, Apple blocked on a $99/yr cert** |
| 5 | Governed-vs-ungoverned demo, 4 scenarios | done |

**Nora** answers only from sentences already on the site — BM25 over a
pre-built index, no model, no API key, nothing to invent. Says so when she
cannot match.

### Design decisions worth not re-litigating

- **The nav goes to the page**, from every page, so the current-tab marker can
  fire. About is the one exception and it is a translation one.
- **One container**: header, nav and body start at the same x everywhere. The
  hero keeps 1480 because its mark is tied to the headline height and a grid
  line; narrowing it made them collide.
- **The homepage tells the six phases once.** It used to tell them twice, word
  for word, alongside approach.html.
- **The custom cursor ring is gone.** It read as a loading spinner.
- **Chapter marks are closed shapes.** Open arcs read as unfinished — reported
  twice.

---

## 6. Open items

**Mine, technical**

- Self-host the fonts. Lighthouse prices Google Fonts as render-blocking at
  **2,050 ms** — the largest remaining performance item.
- The twelve canned fallback answers inside Nora's script are English in all
  languages. They only appear if `assistant.json` fails to load.
- Spanish and Italian sit at ~45%.
- `test/shots/` and `test/node_modules/` are gitignored.

**Yours, decisions**

- **DE/FR have never been read by a native speaker.**
  `reviewed_by_native_speaker: false` in both dictionaries. Everything is
  machine-checked for consistency, not for whether it sounds right to a German
  buyer. The governed-vs-ungoverned demo is the most legally-flavoured copy on
  the site (BEEG §15, GDPR Art. 28) and raises what that review is worth.
- **Apple Wallet** needs the paid developer certificate before it can be built.
- **"chatbot" appears once on the site, as a negation** — *"Not a chatbot
  bolted onto a homepage."* A buyer searching their own word finds a refusal.
- **Which AI work do you actually take on?** Still open, and needed before the
  work page can claim breadth: vision, forecasting, document processing,
  speech, translation, recommendation, anomaly detection, fine-tuning, LLM
  evaluation, MLOps.
- Terms of Service; accessibility statement.
- The hidden `#build` section — **two chapters both claim 06**. Invisible only
  because `#build` carries `hidden`. Renumber 06–09 → 07–10 in the same change.
- `/index-old-backup` was deleted after being live and reachable for months.
  If you want indexed copies gone faster, add a redirect to `/` in
  `vercel.json`.

---

## 7. Contact details of record

Used by `api/card.js`, `api/pass.js`, `impressum.html`:

- **Quenora Consulting**, Heilbronn, Germany
- **+49 152 3392 7436** · **+49 152 5643 3329**
- **info@quenora.ai** · **https://quenora.ai**

---

## 8. Branches

```
main                     deployed; everything above is on it and pushed
infographics             a worktree at ../Quenora-infographics, now merged
                         and behind main. Safe to delete:
                         git worktree remove ../Quenora-infographics
                         git branch -D infographics
```

Local preview servers, both worktrees: `python3 serve-preview.py 8800`
(cleanUrls, `/c` and `/w` answered the way production does).

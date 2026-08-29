# Quenora — backlog to 95% readiness

Everything found across the structural audit, the content audit, a buyer-side
review (CTO persona, €250M manufacturer, one dead pilot) and a craft-side
teardown (B2B design/content benchmark). Nothing here is speculative — every
item was observed on the live files.

**Goal: every visitor arrives at a logical reason to make contact.**
Today most of them cannot, because the path is broken before the argument
lands.

---

## Readiness model

Scored 0–100 per dimension, weighted by what actually decides a deal.

| Dimension | Weight | Now | Target | Gap |
|---|---|---|---|---|
| Legal compliance | 15 | **0** | 100 | Impressum, privacy notice, VAT all missing |
| Conversion path | 25 | **20** | 95 | one CTA in 19,000px; inner pages feed a dead form |
| Credibility / proof | 20 | **30** | 85 | no photo, no LinkedIn, no sample, two methodologies |
| Content consistency | 15 | **55** | 95 | four contradictions across pages |
| Copy quality | 10 | **80** | 90 | strong, over-negated |
| UI / visual craft | 5 | **72** | 95 | strong taste, unsystematised — 33 type sizes, 9 radii, 14 durations |
| Technical / SEO | 5 | **75** | 95 | no FAQ schema, stale indexed translations |
| Accessibility | 5 | **90** | 95 | homepage clean, inner pages skip headings |
| Responsive / mobile | *folded into UX* | **35** | 95 | journey has no width breakpoint; homepage has no mobile nav |

**Weighted now: 38 / 100. Target: 95.**

The two dimensions carrying 40% of the weight — conversion and legal — are the
two scoring lowest. That is the whole story: the site argues well and converts
badly.

---

## P0 — CRITICAL. Blocking. Fix first.

Nothing else on this list matters until these are done, because every other
improvement drives traffic into a broken funnel or a legal exposure.

| # | Item | Where | Effort |
|---|---|---|---|
| P0-1 | **`contact.html` form is not wired** and says so on screen: *"This prototype form is not yet wired to a backend."* All five inner pages' "Book a briefing" CTA points here. The working form is on the homepage only. | contact.html | 1 h |
| P0-2 | **Impressum does not exist**, link is `href="#"`. Legally required (§5 DDG) and must be reachable from **every** page. Currently reachable from none. | all pages | 3 h |
| P0-3 | **Privacy notice does not exist**, link is `href="#"` — while the homepage form collects name, email, company behind a consent checkbox pointing nowhere. GDPR exposure. | all pages | 4 h |
| P0-4 | **`[PLACEHOLDER]` visible** where Reg / VAT belongs, in the live footer. A German buyer reads this as "not trading yet". | index.html footer | 5 min |
| P0-5 | **LinkedIn link is `href="#"`** — for a firm selling one person, the person has no verifiable profile. | footer | 5 min |
| P0-6 | **Homepage form does not send.** Needs `RESEND_API_KEY`, `ENQUIRY_TO`, `ENQUIRY_FROM` as Vercel env vars. Currently falls back to mail client. | Vercel config | 15 min |
| P0-7 | **No calendar booking anywhere.** Copy promises "Forty-five minutes, no deck" with no way to book it. Buyer review: *"If there were a 'pick a slot' button I would be at 85%"* instead of 65%. | all pages | 2 h |

**P0 total: ~1.5 days. Moves conversion 20 → 70 and legal 0 → 100.**

---

## P1 — CREDIBILITY CONTRADICTIONS

Each of these is a place where the site argues against itself. A procurement
reader who opens two pages finds two firms.

| # | Item | Where |
|---|---|---|
| P1-1 | **Two different methodologies.** Homepage: Frame / Foundation / Integrate / Ship / Prove / Hand over. `approach.html`: Diagnose / Scope / Build / Integrate / Transfer / Sustain. Different names, weeks and exit logic — and the homepage's "The approach in full →" links straight at it. | index + approach |
| P1-2 | **Two evidence standards.** `work.html` publishes "~4 hrs → 38 sec", "20 yrs knowledge indexed" for the same three engagements the homepage presents with no figures and a disclaimer. | index + work |
| P1-3 | **Stale capability names** on four inner pages: "Deployment & Development", "Platform Engineering". Homepage sells "Platform & Deployment Engineering" and "Process & Workflow Automation". | work, approach, products, contact |
| P1-4 | **"Six of them"** — chapter 01 says six seams, shows three (The data, The integration, The handover). | index.html |
| P1-5 | **Fake AI assistant** on five inner pages: *"Preview assistant — illustrative answers"*. Buyer: *"the one thing a technical buyer will screenshot."* Wire it to `/api` or delete it. | 5 inner pages |
| P1-6 | **"Nine capabilities. One team."** against "founder-led, growing" three screens later. One person is not nine capabilities. | index.html |
| P1-7 | **"24/7 monitoring, SLA-backed"** from a one-person firm. Buyer: *"Who is on call at 03:00 in the plant in Poland?"* Not survivable in a first call. | services/products |
| P1-8 | **Footer tagline contradicts positioning.** Inner pages carry *"We don't do it for you. We clear the way."* The rest of the site promises they build and hand over. The homepage never uses this line. | inner footers |
| P1-9 | **Manufacturing pattern is an IT problem.** The manufacturing engagement is service-desk triage. A manufacturing buyer notices there is no shop-floor / OT-IT content. | work.html |

**P1 total: ~2 days. Moves credibility 30 → 60, consistency 55 → 95.**

---

## P2 — UX / CONVERSION

This is the category that decides whether a convinced reader can act.

| # | Item | Detail |
|---|---|---|
| P2-1 | **One CTA in ~19,000px of homepage.** Between hero and the closing form there is not a single conversion element — only four links that send readers *off* the page to pages with a broken form. | Add an enquiry affordance every 2–3 screens |
| P2-2 | **Form sits at ~95% scroll depth.** A reader who consumes 20% of the page never sees pricing, objections, who they are hiring, or a form. | Second form / booking block at ~35% |
| P2-3 | **Hero has no CTA.** First screen offers "Scroll". | Add a primary + secondary action |
| P2-4 | **Nav CTA is an in-page anchor** (`#climax`), so it cannot be measured, cannot be an ad landing target, and drops a cold reader at a form with no context. | Consider a real `/contact` page |
| P2-5 | **No trust signal beside the form.** "We reply within one working day", "no NDA needed", the founder's face — all exist elsewhere or not at all, none adjacent to the input. | Move reassurance next to the form |
| P2-6 | **Reference call buried.** "We will arrange a direct conversation with a reference before you commit" is objection #4. Strongest de-risking asset on the site. | Promote to homepage |
| P2-7 | **AI Readiness Assessment is not purchasable.** Only "Available now" product; no price, no booking, no sample output, fourth card down. Buyer put **60%** on buying it. | Own landing page + price + buy path |
| P2-8 | **Scroll depth ~16–18 viewport heights** across 9 chapters. Craft review recommends 5 sections / ~7 screens; buyer never complained about length. | Compress, do not gut |
| P2-9 | **Horizontal pinned journey ≈280vh** of scroll hijack. Breaks scrollbar meaning, find-in-page and trackpad-less mice. | Move detail to approach.html |

---

## P3 — CONTENT

| # | Item |
|---|---|
| P3-1 | **Pricing chapter has no figures.** 228 words, zero numbers. Either soften the "wastes your quarter" rationale or publish a Frame-phase floor ("from €X"). A floor on one fixed-scope phase is not a price list. |
| P3-2 | **Negation density: 1 per 25.7 words** (90 instances: 42 × "not", 11 × "rather than", 10 × "never"). The site defines itself by what it is not. Halve it. |
| P3-3 | **Nine principles on the homepage.** Both reviewers independently said cut. "Timeless — the exact midpoint of the climb" and "Intelligent — where every prior principle arrives" are brand-book content sitting between the credibility section and the form. Move to About. |
| P3-4 | **"Trustworthy — the foundation everything else stands on"** defines the word with a synonym. First principle, weakest line. |
| P3-5 | **"Nobody's AI programme fails because the model was weak"** — an absolute a technical buyer will counterexample. "Almost none" is equally strong. |
| P3-6 | **"Build what keeps working"** — weak, generic headline directly above the only form. Suggested: *"The pilot worked. Then nothing happened. Start there."* |
| P3-7 | **Ch 02 "situations" and Ch 05 "shapes"** are two three-item problem taxonomies. Second reads as padding. |
| P3-8 | **Ticker is the least differentiated content on the site** and occupies the strip directly below the hero. Duplicates chapter 04. |
| P3-9 | **No dated, authored writing.** For a firm whose proof strategy is "the founder knows what he is doing", published thinking *is* the proof. |
| P3-10 | **No sample deliverable.** Copy promises "a written position — yours to take to your board" and never shows what it looks like. A redacted Frame deliverable would be the most persuasive publishable asset, with zero fabrication. |
| P3-11 | **No security & compliance page** — DPA availability, subprocessors, data residency, model providers, insurance, EU AI Act posture. `products.html` sells a Governance Toolkit while publishing nothing about the firm's own governance. |
| P3-12 | **No key-person / continuity answer.** Buyer: *"What happens to my production system if you are hit by a bus?"* Escrow, second engineer, or documented handover trigger. |
| P3-13 | **No founder photo or bio.** |
| P3-14 | **Voice drift.** Inner pages use contractions and Title Case; homepage does neither. |

---

## P4 — UI / VISUAL

The craft here is genuinely strong. These are items where the interaction
budget is spent on the firm's self-image rather than the buyer's decision.

| # | Item |
|---|---|
| P4-1 | **Custom cursor** — adds hover latency, overrides OS affordances, reads as portfolio site. Both reviewers said cut. |
| P4-2 | **Three canvas animations.** Hero earns it. The gap diagram earns it. The automation figure restates its own caption. |
| P4-3 | **Two competing hover behaviours** on the first screen (nearest-sphere lighting + cursor ring). |
| P4-4 | **Chapter 09 sticky mark** holds a graphic on screen through nine rows of content that should not be on the homepage. |

---

## P4b — POLISH / SYSTEM CONSISTENCY

Measured against the CSS, not eyeballed. Individually invisible; together they
are why the page reads as *very good* rather than *inevitable*. This is the
difference between a site that looks designed and one that looks systematised.

### What is already excellent — do not touch

- **Colour discipline: 375 `var(--token)` uses against 37 raw literals.** Very
  few teams achieve this. The palette is genuinely a system.
- **One easing token** (`--e: cubic-bezier(.16,1,.3,1)`), used 46 times.
- **Reveal choreography** — `.9s` with `.08s` / `.16s` stagger, applied
  consistently across every section.
- **Spacing scale** (16/24/40/64/104/168) is adhered to, with almost no magic
  numbers in section rhythm.
- **Card geometry is exact** — the three engagement cards measure 363px each,
  aligned to the pixel.

### What breaks the system

| # | Item | Measured |
|---|---|---|
| P4b-1 | **No type scale.** 33 distinct rem font sizes. `.83 / .85 / .86 / .88` and `.92 / .94 / .95 / .96 / .98` are visually indistinguishable from one another but arbitrarily different — the reader feels imprecision without being able to name it. Collapse to 7–8 steps. | 33 sizes |
| P4b-2 | **The uppercase mono label is one component wearing 14 different costumes.** Same visual element — eyebrow, chapter label, capability tag, exit condition, footer heading, form label, status pill — across **8 font sizes** (.56–.68rem) and **7 tracking values** (.13em–.34em). This is the single most visible consistency defect on the site, because these labels appear in every chapter. | 14 instances |
| P4b-3 | **No radius scale.** 9 distinct values: 2, 3, 4, 9, 11, 14, 20px and 50%. Cards say 4px, form inputs 4px, buttons 9px, assistant panel 14px, chips 20px. Pick three: sharp (4), soft (9), pill (999). | 9 values |
| P4b-4 | **No motion scale.** 14 distinct transition durations from .2s to .9s (`.2 .25 .3 .35 .38 .4 .45 .5 .55 .9`). Should be three tokens: fast (.2), base (.35), slow (.9). | 14 durations |
| P4b-5 | **Zero section differentiation.** All 11 `<section>`s are `rgba(0,0,0,0)` — pure void from chapter 01 to the footer. `--sf1` and `--sf2` surface tokens are defined and used **only** inside the two pinned stages. Nothing but a numeral and whitespace signals a new chapter, so 9 chapters read as one undifferentiated scroll. Alternating a barely-there surface tone would give the page rhythm at almost no cost. | 11 of 11 |
| P4b-6 | **The assistant panel is visually foreign.** 14px radius and 20px pill chips against a site whose entire language is 4px. It reads as a third-party widget bolted on rather than part of the product. | — |
| P4b-7 | **Card padding drifts.** `.phase` uses `sp5 sp4`; `.shape` and `.build` use `sp4`. Same object, different breathing. | — |
| P4b-8 | **Ragged eyebrow wrapping.** The three engagement-pattern labels wrap to **2, 2 and 1 lines** ("PATTERN 01 · FINANCIAL SERVICES" breaks, "PATTERN 03 · LOGISTICS" does not), so three identical cards have three different internal rhythms. Shorten the sector names or reserve two lines. | 2/2/1 |
| P4b-9 | **Untokenised repeat.** `rgba(242,239,232,.035)` appears 3× as the grid-line colour. Should be `--line0`. | 3× |

---

## P4c — RESPONSIVE / SCROLL / LANDING

Measured live at 320 · 390 · 820 · 1024 · 1280 · 1440 · 1920. **No horizontal
overflow at any width** — that part is clean. Everything below is real.

### The big one

| # | Item |
|---|---|
| **P4c-1** | **There is no mobile breakpoint for the six-phase journey.** The stacking fallback (`.htrack{flex-wrap:wrap;transform:none}` / `.phase{flex:1 1 100%;max-height:none}`) lives inside `@media (prefers-reduced-motion: reduce)` — **not** inside a width query. So on every phone and tablet the journey runs as a horizontal scroll-hijack, with cards clipped and the next card sliced down the middle. This is the "half visible text" problem, and it affects 100% of mobile and tablet visitors who do not have reduced-motion enabled. **Fix: duplicate that rule block into `@media(max-width:900px)`.** One block, ~4 lines. |

**Text actually cut, measured:**

| Viewport | Phase card content clipped |
|---|---|
| 320 × 568 | **125–217px** cut per card |
| 390 × 844 | **65px** cut per card |
| 820 × 1180 (iPad) | **75px** cut per card |
| 1024 × 768 (iPad landscape) | **81px** cut per card |

At 320px the pinned stage also clips 233px of the "AI programmes fail at the
seams" section.

### Scroll length

| Viewport | Total scroll | Journey pin alone |
|---|---|---|
| 320 × 568 | **43.2 screens** | 4.0 screens |
| 390 × 844 | **27.3 screens** | 2.9 screens |
| 820 × 1180 | 18.1 screens | 2.1 screens |
| 1024 × 768 | 22.0 screens | 3.0 screens |

**43 screens on a small phone is not a page, it is a scroll marathon.** The
enquiry form sits at the bottom of all of it.

### Landing / first screen

| # | Item |
|---|---|
| P4c-2 | **Hero does not fit the first screen at small and short viewports.** 320×568: hook is 1001px against 568px of viewport — the headline, the sub-paragraph and the scroll cue cannot coexist. 1024×768 (iPad landscape, and every 768-tall laptop): hook 784px against 768px — overflows by 16px, so the scroll cue is pushed under the fold on the exact screen where it is meant to invite the scroll. |
| P4c-3 | **The homepage has no mobile navigation at all.** Below 880px the nav links are hidden by `display:none` with **no replacement** — a phone visitor to the homepage sees brand + "Contact" + language and cannot reach Approach, Capabilities, Work or About. **Every inner page has a working hamburger menu.** The finished page is the only one that loses its navigation. |

### Verified clean

- **Zero horizontal overflow** at 320, 390, 820, 1024, 1280, 1440, 1920.
- **Headline mask is correct** — `.ln` uses `overflow:hidden` with a matching
  `padding-bottom`, so descenders render complete at every size. Looks like a
  clip in measurement; is not one in rendering.
- Engagement cards equal height and pixel-aligned at every width tested.
- Hero constellation places correctly at every width (gate-enforced).

### Motion pacing

| # | Item |
|---|---|
| P4b-10 | **Three infinite loops run at unrelated tempos.** The ticker marquee (38s), the gap diagram (11.3s cycle) and the automation figure (continuous, ~22-frame spawn) share no rhythmic relationship. Nothing needs to be synchronised exactly, but a shared tempo family would make the page feel composed rather than assembled. |
| P4b-11 | **Motion is entirely front-loaded.** Chapters 01–04 carry all four animated elements; chapters 05–09 and the climax are completely static. The page spends its whole energy budget before it makes its argument, then goes quiet exactly where it should be closing. The climax — the screen that asks for the money — is the least alive on the page. |

---

## P5 — TECHNICAL / SEO

| # | Item |
|---|---|
| P5-1 | **Google Fonts is an external CDN** — contradicts the stated no-CDN rule, whose rationale (locked-down corporate networks) applies identically. Self-host three woff2 files. |
| P5-2 | **No `FAQPage` schema** despite chapter 06 being a literal five-question FAQ. Free rich-result eligibility. |
| P5-3 | **No `Service` schema.** |
| P5-4 | **Inner pages have no `og:image` and no JSON-LD.** Sharing any inner page produces a bare preview. |
| P5-5 | **Heading hierarchy skips** on all five inner pages (h1→h3, h2→h4, h2→h5). Homepage is clean. |
| P5-6 | **24 stale translated pages indexed** in `sitemap.xml`, rendering `l'IA AI` in three languages. De-index until regenerated. |
| P5-7 | **`sitemap.xml` has no `<lastmod>`.** |
| P5-8 | **Inner pages hard-code the long nav CTA label**, so they still show the phone header overflow the homepage no longer has. |
| P5-9 | `index.html` 151KB uncompressed. Fine gzipped; worth watching. |
| P5-10 | **No service × geography landing pages.** A new brand gets zero brand search; five pages is a thin ranking surface. |

---

## P6 — DEFERRED (decided, not forgotten)

| # | Item |
|---|---|
| P6-1 | `#build` section is written and hidden. Releasing needs the `hidden` removed **and** chapters 06–09 renumbered to 07–10, together. |
| P6-2 | Translation regeneration — blocked until English is frozen. |
| P6-3 | `story.html` and `index-old-backup.html` are dead drafts, deliberately orphaned. |

---

## Sequence to 95

**Sprint 1 — make it operational (1.5 days) → readiness 38 → 62**
All of P0. Form wired, legal pages live, VAT filled, LinkedIn real, calendar
link on every page, env vars set.

**Sprint 2 — stop contradicting yourself (2 days) → 62 → 78**
P1-1 through P1-6. One methodology, one evidence standard, one set of
capability names, "six" fixed, fake assistant removed or wired.

**Sprint 3 — give them a reason and a route (2–3 days) → 78 → 88**
P2-1, P2-2, P2-5, P2-6, P2-7. CTAs every few screens, trust signals beside the
form, reference offer promoted, Readiness Assessment made purchasable with a
price.

**Sprint 4 — proof and polish (3–4 days) → 88 → 95**
P3-10 (sample deliverable), P3-11 (security page), P3-12 (continuity), P3-13
(photo), P3-2 (halve negations), P3-3 (principles to About), P5-1, P5-2, P5-6.

**Total ≈ 9–11 working days to 95.**

### Look-and-feel track — can run first and independently

If polish is the priority ahead of legal and conversion, P4b is a
self-contained day and a half that lifts visual craft 72 → 95 and touches
nothing else:

0. **Give the journey a width breakpoint** (15 min) — the single highest-value
   fix in this whole document. Copy the reduced-motion stacking rule into
   `@media(max-width:900px)`. Ends clipped cards and half-visible text on every
   phone and tablet at once.
0b. **Add a mobile nav to the homepage** (1 h) — it is the only page without
   one; the inner pages already have a burger to copy.
1. **Tokenise the system** (½ day) — collapse 33 type sizes to 8, 9 radii to 3,
   14 durations to 3, add `--line0`. Mechanical, low risk, gate-safe.
2. **Fix the mono label** (2 h) — one size, one tracking, one weight, applied
   to all 14 instances. Biggest single visible gain on the page.
3. **Give chapters a surface rhythm** (2 h) — alternate `--sf1` at very low
   opacity so nine chapters stop reading as one scroll.
4. **Bring the assistant into the language** (1 h) — 4px radius, square chips.
5. **Rebalance motion** (2 h) — quiet one front-loaded animation, give the
   climax a reason to feel alive.

Above 95 requires things a website cannot supply: ISO 27001, professional
indemnity cover, a DPA, financial standing, and two contactable references.
Those govern whether the >€50k build is winnable, and no amount of design
changes them.

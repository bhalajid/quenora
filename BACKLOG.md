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

---

## P4d — HERO ANIMATION ON MOBILE, AND SCALE-INVARIANCE

Sampled the hero canvas pixel-by-pixel at 390 × 844 over ~8 seconds.

**The animations are not missing — they are running and invisible.** The
canvas paints, the mark builds, and the cyan signal run does fire (confirmed:
cyan present in 4 of 9 time samples). It reads as missing because the mark is
rendered at roughly **one fifth of its desktop presence**, and because every
motion detail is sized in fixed pixels that do not scale.

### Why it reads as missing

| Measure | Mobile 390×844 | Desktop ~1440 |
|---|---|---|
| Mark height | **63px** | ≈ headline height (~320px) |
| Mark as % of viewport height | **7.5%** | ≈ 35% |
| Mark as % of viewport width | 17.6% | ≈ 24% |
| Canvas coverage (lit pixels) | **0.4–0.7%** | several times that |
| Peak alpha anywhere on canvas | **146 / 255** | full |

| # | Item |
|---|---|
| P4d-1 | **The mobile mark is sized by a leftover gap, not by a design decision.** Below 700px the fallback places it in the band between the nav and the eyebrow. That band is whatever happens to be left over: **83px at 390 wide, 135px at 430.** A 62% difference in the brand's presence between two ordinary phones, driven by nothing but text reflow. On desktop the mark is tied to the headline's measured height — a real relationship. Mobile has no equivalent. |
| P4d-2 | **Nothing in the animation is scale-invariant.** Trail dots (2.6px), run head (3.1px), head glow radius (26px), pulse tails (34–60px), spark velocities and arrival ring radii are all fixed pixel constants tuned on a desktop canvas. On a 390px canvas a 26px glow is **6.7% of the width**; on 1920px the same glow is **1.35%**. The same code produces a different *visual language* at each size — chunky and blobby on phones, delicate on desktop. Everything decorative should be expressed as a fraction of canvas width or of `ms` (the mark scale factor), not in px. |
| P4d-3 | **Dust density varies ~6× across devices.** The field is a fixed 170 particles regardless of canvas area: **511 per million px on a phone, ~88 on a 1920 desktop.** Phones get a dense speckle, large screens get an empty void. Scale the count by area for constant density. |
| P4d-4 | **The best interaction is desktop-only.** Nearest-sphere hover — 161,877 positions tested, 0 mis-picks, the most refined thing on the site — never fires on touch (`hover:none, pointer:coarse`). Mobile visitors get none of it. A tap-to-light, or an auto-cycle that lights each sphere and names its principle, would return that value on the device most visitors use. |
| P4d-5 | **The run is invisible at mobile scale.** The cyan signal is the animation that carries the headline's promise — *AI that reaches the work*. At 63px of arc with a 3px head, it is a flicker. It needs proportionally thicker stroke, longer dwell, and a brighter arrival bloom on small canvases. |

### Room to make it better — concrete

| # | Proposal |
|---|---|
| P4d-6 | **Give the mobile mark a real geometric anchor.** Options, best first: (a) size it to the **headline block height** exactly as desktop does, and place it in the empty band *below* the hook-foot rather than the sliver above the eyebrow; (b) let it bleed off the right edge at ~55% of viewport width — a confident, common premium pattern that turns a constraint into a decision; (c) place it behind the headline at low alpha as a ground rather than an object. Any of the three replaces "whatever gap is left" with a stated relationship. |
| P4d-7 | **Express every constant as a ratio.** Define one `S = W/1440` scale factor at `fit()` and multiply every decorative px through it. Removes an entire class of per-device visual drift, in one pass. |
| P4d-8 | **Tie the three figures to one tempo family.** The ticker (38s), the gap cycle (11.3s) and the automation spawn interval share no rhythmic relationship. Deriving all three from one base beat would make the page feel composed rather than assembled. |
| P4d-9 | **Give the arrival more weight.** The ninth sphere's bloom on arrival is the emotional payoff of the whole hero — the moment the signal *reaches the work*. It currently decays at 0.955/frame with a thin ring. A longer hold and a brief warm flare across the whole arc would land the headline's claim instead of whispering it. |
| P4d-10 | **Reduce motion on small screens deliberately, not accidentally.** If the mark must stay small on phones, then cut the dust, drop the run, and let the mark simply *be* — a still, well-placed brand object beats a busy, illegible one. Choose the reduction; do not inherit it from a leftover band. |

---

## P4e — WHOLE-PAGE HIERARCHY, GRID ALIGNMENT, ANIMATION CEILING

### Where the eye goes first

Measured by salience (type size × contrast against the void) on the first
screen at 1440 × 900:

| Rank | Element | Salience |
|---|---|---|
| 1–5 | the headline words | **107** |
| 6 | *the work.* (italic) | 61 |
| 7 | quenora wordmark | 20 |
| 8 | the sub-paragraph | 11 |
| 9 | EN language switch | 11 |

**The hierarchy is correct and it is the site's real strength** — the headline
owns the screen, the mark supports, nothing competes. Keep it.

| # | Item |
|---|---|
| P4e-1 | **The primary CTA does not appear in the top nine salience items on its own hero.** "Start a conversation" is out-ranked by the language switcher. The first screen's only stated action is the word "Scroll". The eye lands in exactly the right place and then finds nothing to do. |

### Geometric alignment — the site draws a grid it does not sit on

The page renders six visible column rules (`.vgrid`) at the wrap width. At
1440 those lines fall at **20 · 251 · 482 · 713 · 943 · 1174 · 1405**.

**On the grid (0px off):** h1, eyebrow, hook-foot left, chapter numerals, the
gap figure both edges, engagement cards, capability rows. Genuinely precise.

**Off the grid:**

| # | Item | Measured |
|---|---|---|
| **P4e-2** | **The nine chapter headings each start at a different x.** `.chead` is `grid-template-columns: auto 1fr`, so the *auto* column is sized by the numeral glyph — and "01" in italic Playfair is narrower than "08". Heading left edges land at **215, 238, 233, 240, 231, 241, 236, 244, 239** — **29px of drift** across the page's most repeated structural element, and **none of them touches grid line 1 at 251**. Because the grid rules are *visible*, the near-miss is perceptible even when the reader cannot name it. **Fix: a fixed first column (`231px 1fr`, or derive it from the column width) so all nine headings start on the same line.** | 29px drift |
| P4e-3 | **The enquiry form is centred, not aligned.** `max-width:640px; margin:0 auto` puts its edges at 393 and 1033 — **89px off** the nearest column lines on both sides. It is the one block on the page that ignores the grid entirely, and it is the block being asked to convert. | 89px |
| P4e-4 | **Lede right edges are text-determined.** Chapter ledes and the hook-foot paragraph end wherever the `ch` measure runs out — 52–107px short of a column line. Defensible typographically, but it means no section has a right edge the eye can lock onto except the gap figure. | 52–107px |

### Animation — what the ceiling actually is

The spheres are already lit objects: radial body gradient, rim stroke, one
specular highlight. That is well above a flat-disc logo. The realistic upgrades,
all achievable in 2D canvas with zero dependencies:

| # | Option | Gain | Cost / risk |
|---|---|---|---|
| P4e-5 | **Real bloom.** Draw bright pixels to an offscreen canvas, blur, composite additively. Today's glow is stacked radial gradients, which reads flat. True bloom is the single biggest "expensive" upgrade available and would lift the hero, the gap mark and the arrival flare at once. | **Highest** | One offscreen canvas + one blur pass per frame. Watch mobile GPU. |
| P4e-6 | **Fresnel rim light + contact shadow.** A brighter edge on the side away from the light, and a soft occlusion where neighbouring spheres nearly touch. This is what makes CG spheres read as physical rather than drawn. | High | Pure maths, negligible cost. |
| P4e-7 | **Depth of field.** Give each sphere a z, blur the small end slightly via `ctx.filter`. Instantly reads as a photographed object. | High | `filter` is per-draw; batch by depth band. |
| P4e-8 | **True 3D projection with a micro-tilt.** Give the nine circles a z, project with perspective, and let the pointer tilt the arc ±6–8° — depth-sorted, near spheres larger and brighter. **Must return to exact rest**, because the gate asserts `SWAY === 0` and `BOB === 0` and its stated purpose is that the mark never drifts off the grid it is built on. At rest it stays byte-identical to the logo; the tilt is an interaction, not a state. The existing pointer parallax already establishes that precedent. | High | **Gate risk if it does not return to zero.** Never rotate on a timer. |
| P4e-9 | **Chromatic aberration on the glow edge.** A sub-pixel R/B offset on the brightest halos. Very subtle, very film. | Medium | Cheap; easy to overdo. |
| P4e-10 | **Give the mark a ground.** A faint elliptical light spill under the arc, and a barely-there reflection. Turns nine floating circles into an object standing somewhere. | Medium | Cheap. |
| P4e-11 | **Sphere interior life.** A slow, low-amplitude shimmer inside each body so they read as containing something rather than being painted. | Medium | Cheap; must stay under the threshold of noticing. |

**Recommended order: P4e-6 → P4e-10 → P4e-5 → P4e-7.** Rim light and ground
are cheap and immediately physical; bloom is the transformative one; depth of
field is the finish. Leave the 3D tilt (P4e-8) last — it is the most
impressive and the only one that can fail the gate.

---

## P4f — THE TWO MARKS DO NOT COMPOSE

Measured at 1440 × 900 on the first screen.

Both marks are the same object and are correctly scaled — the nav lockup's arc
and the hero constellation share an **identical −42° axis**. That part is
right, and it is why they feel related at all.

What is missing is any *shared line between them*:

| Measure | Value |
|---|---|
| Nav mark arc axis | **−42°** |
| Hero arc axis | **−42°** |
| Line joining the two marks | **+29.8°** |
| Hero arc **right** edge | exactly on grid line 6 (1405) |
| Hero arc **left** end (small circle) | **78px off** the nearest grid line (943) |

| # | Item |
|---|---|
| P4f-1 | **The hero arc is anchored at one end only.** Its right edge sits exactly on the wrap's last grid line and its bottom on the headline's baseline — two real relationships. Its **small end floats**, landing 78px past a column line, because the arc's width falls out of the scale rather than being placed. So the composition is nailed on the right and loose on the left, which is the end nearest the type. |
| P4f-2 | **No line relates the two marks.** They share an axis but sit on a connector running at +29.8° — neither the mark's own 42°, nor 45°, nor any grid diagonal. The eye reads two instances of one object that are not on a common trajectory. Options: (a) drop the hero arc so the nav-to-hero connector runs at **+42°**, mirroring the mark's own axis and putting the whole first screen on one angle; (b) anchor the arc's small circle to grid line 4 so both ends are placed; (c) align the arc's small circle to the headline's **baseline** rather than letting it float. (b) is the cheapest and most defensible — it costs one term in `fit()`. |
| P4f-3 | **Nav mark and hero arc share no vertical either.** The nav mark spans x 20–60 (column 0). Nothing in the hero relates to that column, so the top-left anchor and the right-hand object have no common structure at all. |

---

## P4g — SPHERE RENDERING STUDY (built, viewable)

A working four-panel comparison lives at **`study/sphere-study.html`** — same
nine coordinates, same palette, four treatments, all zero-dependency 2D canvas.
Open it directly in a browser. It is outside `quenora/` so it is not served,
not indexed and not part of the site.

| Panel | Treatment | Verdict |
|---|---|---|
| **A** | Shipping today — body gradient, rim stroke, specular dot | Good. Clearly lit objects, not flat discs. |
| **B** | **+ fresnel rim + contact shadow** | The cheapest real gain. The bright edge reads as light wrapping a curved surface, and the occlusion where spheres nearly touch makes them sit *in front of* each other rather than beside. Pure maths, no cost. |
| **C** | **+ ground plane, reflection, contact spill** | **SHIPPED on the hero.** Nine floating circles become an object standing on a surface. |
| **D** | **+ real bloom + depth of field** | **SHIPPED on the hero** (bloom). Bright pass → blur → additive composite. |

**Status: B, C and D are now live on the hero constellation.** Fresnel rim and
neighbour contact shadow (B), elliptical ground with reflection and contact
spill (C), and half-resolution bloom (D). Measured after: **60.5 fps desktop,
60.1 fps at 390px**, worst frame 19.2ms, and canvas coverage up from 204 to
1,318 lit samples on desktop and 204 to 546 on mobile. Bloom carries a rolling
frame-time guard that disables it permanently on any device averaging worse
than 20ms over its first 90 frames, and is skipped entirely under
`prefers-reduced-motion`.

**Still to do from the study:** apply the same treatment to the gap diagram's
mark (chapter 01) and the automation figure, so all three canvases share one
lighting model. Depth-of-field blur is in the study but not yet on the hero.

The 3D micro-tilt (P4e-8) remains the highest-ceiling option and the only one
that can fail the geometry gate. Do it last, and only returning to exact rest.

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

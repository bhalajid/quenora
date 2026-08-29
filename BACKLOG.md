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
| UI / visual craft | 5 | **85** | 90 | genuinely good, over-invested in brand |
| Technical / SEO | 5 | **75** | 95 | no FAQ schema, stale indexed translations |
| Accessibility | 5 | **90** | 95 | homepage clean, inner pages skip headings |

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
| P4-5 | Keep: typography scale, copper palette, spacing rhythm, reduced-motion discipline, zero-dependency build. **This is top-decile and should not be touched.** |

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

Above 95 requires things a website cannot supply: ISO 27001, professional
indemnity cover, a DPA, financial standing, and two contactable references.
Those govern whether the >€50k build is winnable, and no amount of design
changes them.

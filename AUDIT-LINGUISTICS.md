# Quenora — multilingual language, UX-content and assistant audit

**Pass 1 — audit only. Nothing on the site has been modified.**

Branch `linguistics`, cut from `origin/main` at `b60d4b6`.
Audited 2 September 2026 against the live site at `quenora.vercel.app`, which
was confirmed byte-identical to this commit before any finding was recorded.

Scope: **English, German, French.** Spanish and Italian are ~45% translated and
deliberately unlisted, and were excluded by agreement.

---

## 0. Method, and what it does and does not cover

Stating this first because it determines how much weight each finding carries.

| Surface | How it was checked | Coverage |
|---|---|---|
| Page text, 3 languages | Rendered-DOM extraction with jsdom, 20 pages, 5,051 strings | Complete |
| Translations | 1,003 EN/DE/FR triples read from `i18n/*.json` | Headings and CTAs read in full; body prose sampled |
| Typography | Raw-source scan for U+202F, guillemets, German quotes, ß | Complete |
| Placeholders | All pages plus `llms.txt`, `llms-full.txt`, 3 assistant indexes, sitemap | Complete |
| Assistant | Retrieval replicated exactly in Python, 51 questions × 3 languages | Complete, then verified live |
| Metadata | `lang`, title, description, og, canonical per page | Complete |

**The assistant replication is exact, not approximate.** It reproduces the
site's own `fold`, stopword set, one-suffix strip, BM25 (k1=1.5, b=0.75), the
1.8 heading boost and the 0.42 secondary-passage cutoff. It was validated by
putting the same question to the live widget and getting back the same three
passages in the same order. Every chat finding below is therefore reproducible,
not a sample.

**Two corrections to the brief's assumptions**, both material:

1. **The assistant is not an LLM.** It is BM25 retrieval over an index of
   sentences already on the site. There is no model and no API key. It
   therefore *cannot* hallucinate a price, invent a client or fabricate a
   certification — those are architecturally impossible, not merely unobserved.
   Reporting "no hallucinations found" would be a non-finding. The audit
   instead tests what can actually go wrong: whether retrieval returns the
   *right* passage, whether that passage reads well *in that language*, whether
   the reply language matches the question, and whether it fails honestly.

2. **The site is five languages and seventeen gate stages**, not three and
   nine. ES and IT exist but are unlisted.

---

## 0a. Resolution status — updated 4 September 2026

Pass 2 is applied, built and pushed to `linguistics`. **Gate: 16 of 17.** The
one red stage is 4b, the legal placeholders, which are the client's.

| ID | Finding | Status |
|---|---|---|
| **C1** | Assistant greeted DE/FR visitors in English | **Fixed** — now `UI.greet`, one key per language |
| **C2** | Ungoverned demo's straw-man served as a pricing answer | **Fixed** — excluded from the index; it also left `llms-full.txt` |
| **C3** | "Fixed fee / Festpreis / Forfait" absent from all three indexes | **Fixed** — card labels now indexed; all three questions resolve |
| **C4** | Impressum and privacy placeholders | **Open — Balaji.** The only red gate stage |
| **H1** | "What does Quenora do?" answered with a disclaimer and the QR card | **Fixed** — curated set widened; verified live |
| **H2** | Curated answers English-only; alias tables 45/16/18 | **Partly fixed.** Aliases now 45/35/33. Curated answers stay English-only *by decision* — see 0b |
| **H3** | Failure question matched the case-studies answer | **Fixed** — a failure set now sits above it; bare `about` narrowed |
| **H4** | German `wer` / `wo` aliases were dead code | **Fixed** — both removed from the stopword list |
| **H5** | Every French "Comment…?" dragged to pricing | **Fixed** — `comment` added to the stopword list |
| **§5** | French narrow no-break space missing on 6 of 7 pages | **Fixed** — 78 corrections; **0 plain spaces remain on any page** |
| **§6** | Twelve wording corrections | **Fixed** — all twelve |
| **§7** | Nine principle names inconsistent between DE and FR | **Fixed** — German now translates all nine |
| **§7** | Nav label, footer heading | **Open — two small decisions, see 0b** |
| **§9** | `next year.` dead key; duplicate `where:` | **Open — housekeeping, no visible effect** |

### Found while fixing, not in the original audit

| Finding | Status |
|---|---|
| `RAG systems` sat in `build_i18n.py`'s **do-not-translate list** beside GDPR and MLOps, so `RAG-Systeme` and `Systèmes RAG` — both already written — could never be reached | **Fixed** — removed from DNT |
| `build_i18n.py` wrote `_untranslated.json` through a handle with no encoding while passing `ensure_ascii=False`, so the build **died on Windows** after writing the localised pages but before `build_assistant` and `build_seo` — the half-built state STATUS.md §5 warns about | **Fixed** — `encoding="utf-8"` |
| The release gate reported five red stages here against STATUS.md's one. Three were `rel.split("/")[0] if "/" in rel else "en"` in `nav_map.py`, `switcher.py` and `deployed_links.py`: on Windows `rel` is `de\approach.html`, so **every localised page was classified as English**. The fourth was jsdom having no `fetch` | **Fixed** — separators normalised at the source; `fetch` added to the stub block that already existed |
| French says *retour arrière*, so the English term `rollback` — which a French CTO would still type — matched nothing. Masked until H5 removed the wrong pricing answer that had been covering it | **Fixed** — `ALIAS_FR` bridge |

---

## 0b. Decisions taken, and what they cost

**Curated answers stay English-only.** Writing fourteen answers each in German
and French would add twenty-eight paragraphs of marketing copy that no native
speaker has read — enlarging the exact unreviewed surface this audit says to
shrink. Widening the alias tables was taken as the honest substitute. **The
asymmetry is reduced, not removed:** English still gets curated answers plus
retrieval; German and French get retrieval only, now with roughly three times
the bridging they had.

**The nine principles are translated in German.** `Enterprise` and `Premium`
were the last two left in English while French translated all nine. The German
nine are adjectives, so the replacements are adjectives, sized against the
existing longest (*Vertrauenswürdig*, 16 characters):

| | was | now |
|---|---|---|
| Enterprise | Enterprise | **Unternehmenstauglich** |
| Premium | Premium | **Hochwertig** |

These are brand vocabulary tied to the nine circles of the mark. One line
overrides either.

**Two §7 items are still open, deliberately.** Neither is a defect:

- **Nav label.** German says `KI-Engineering`; English and French say
  `Engineering` / `Ingénierie`. Here German is *more* descriptive, not less —
  aligning it down would make the German worse. Recommendation: leave it.
- **Footer heading.** English says `Site`; both translations say `Navigation`,
  which is better. Recommendation: adopt `Navigation` in English. That is an
  English copy change, so it is the client's voice, not mine.

---

## 0c. Deferred to after launch — native-speaker review

**`reviewed_by_native_speaker` remains `false` in both dictionaries, and stays
false on purpose.**

Agreed 4 September 2026: the native-speaker pass for German and French is
**held until after launch, to be handled from 9 September 2026.**

What that means precisely, so nobody reads more into this audit than it
supports:

- This pass fixed defects a native reviewer would find — mistranslations,
  register, typography, dead terminology. It is **not** a substitute for one.
- Roughly 1,000 strings per language were machine-checked for consistency and
  read selectively for quality. **Headings and CTAs were read in full; body
  prose was sampled.** Anything not quoted in §6 has not been individually
  judged by a human reader of that language.
- The German and French copy is now defensible for launch. It is not certified.
- The flag is the honest marker of that, and flipping it needs a real German
  and a real French reader, not another pass by me.

---

## 0d. Re-verification, 4 September 2026

Every existence claim in Pass 2 was re-checked using the **gate's own**
definition rather than mine, after the gate caught one my checker had accepted.

**The error being hunted:** my tokeniser applies a one-suffix strip, so
`validations` in the page text produced `validation` in my vocabulary, and I
accepted a French synonym pointing at a word that is not literally in the
index. Stage 4g checks the literal token and rejected it.

| Re-checked | Result |
|---|---|
| Alias targets, all three languages, literal tokens | **349 targets, 0 dead** |
| Pricing labels present in each index | en `fixed fee` · de `festpreis` · fr `forfait` — all present |
| Ungoverned demo absent from every surface | 3 indexes + `llms.txt` + `llms-full.txt` — all clean |
| Greeting localised on every built homepage | 0 English literals, 3 `UI.greet` |
| French high punctuation in the built pages | **0 plain spaces on all 7 pages** |

**One false alarm of my own, recorded so it is not repeated.** My first
re-check tested the *English* alias table against the German and French
indexes and reported ~100 dead targets. That is wrong: the gate pairs each
table with its own language. The English table is merged *into* the localised
one at runtime, so its English targets are inert there — a German visitor's
question will never contain "ownership". Inert, not broken. It is also the
clearest measure of why H2 mattered.

---

## 1. Executive summary

| | Score | One-line justification |
|---|---|---|
| **English copy** | **8.5 / 10** | Distinctive, disciplined, British throughout. Zero US spellings. |
| **German copy** | **7.5 / 10** | Competent and largely idiomatic; four genuine mistranslations, one embarrassing. |
| **French copy** | **7 / 10** | Often better than the German, but typography breaches its own declared standard on 6 of 7 pages. |
| **Assistant — English** | **6 / 10** | Fails the most basic question; one curated answer fires on the wrong question. |
| **Assistant — German** | **4 / 10** | English greeting; returns straw-man demo text as a pricing answer. |
| **Assistant — French** | **4.5 / 10** | English greeting; every "Comment…?" question is dragged to pricing. |

### Biggest strengths

- **The English voice is genuinely distinctive** and survives translation more
  often than not. "AI programmes fail at the seams", "And then we leave", "The
  demo was never the hard part" all land in all three languages.
- **The honesty architecture is real, not claimed.** No model means no
  invention. The French failure message — *"Rien sur ce site ne correspond, et
  je préfère vous le dire plutôt que de trouver des mots en commun et d'appeler
  cela une réponse"* — is better French than most agencies write.
- **Typographic conventions that usually break are correct.** German „…"
  and French « » are properly formed everywhere, with zero English-style
  quotes. No US spellings anywhere in the English.
- **No placeholder leakage.** The hidden `#build` chapter's `[Project title]`
  markers do not reach `llms.txt`, `llms-full.txt`, any assistant index, or the
  sitemap. Verified, not assumed.

### Biggest weaknesses

- **The assistant is materially worse in German and French than in English**,
  by design and by omission — see §4. This is the single largest gap in the
  audit.
- **The most basic question a visitor can ask — "What does Quenora do?" —
  is answered badly in all three languages.**
- **French typography breaches the project's own written standard.**
  `fr.json` declares *"Espace fine insécable (U+202F) avant ; : ! ?"*. Six of
  seven French pages have none.

### Overall recommendation

**Do not rewrite the copy.** The prose is better than the average B2B
technology site in all three languages, and the brand voice is intact. The work
is a short list of precise corrections — four of them critical — concentrated
almost entirely in the assistant and in French typography, not in the writing.

---

## 2. Language scorecard

| Category | EN | DE | FR |
|---|---|---|---|
| Grammar | 9 | 8 | 8 |
| Spelling | 10 | 9 | 9 |
| Punctuation / typography | 9 | 9 | **5** |
| Sentence quality | 9 | 8 | 8 |
| Naturalness | 9 | 7 | 8 |
| Business language | 9 | 8 | 8 |
| Technical terminology | 8 | 7 | 7 |
| Brand voice | 9 | 8 | 8 |
| Localisation (not translation) | — | 7 | 7 |
| Cross-language consistency | 7 | 7 | 6 |
| UX writing / microcopy | 8 | 6 | 6 |
| **Overall** | **8.5** | **7.5** | **7** |

---

## 3. Production blockers — CRITICAL

### C1 · The assistant greets German and French visitors in English

**Verified live on `/de`.** Opening the assistant on the German homepage shows,
as its first message:

> Ask anything about Quenora and I will show you what this site says about it,
> in its own words, with a link to where it sits. I do not generate answers —
> if it is not written here, I will tell you that instead of guessing.

This is the paragraph that carries the firm's entire differentiator, and a
German buyer meets it in English.

**Cause, precisely.** The greeting is a bare English string literal inside
`toggle()` in the page script — `bot("Ask anything about Quenora…")`. It never
passes through the `UI` object. The `UI` strings *are* localised correctly:
asking in French returns French. Only the greeting was left outside it.

**The translations already exist**, unused, in both dictionaries:

- DE — *"Fragen Sie alles über Quenora, und ich zeige Ihnen, was diese Website
  dazu sagt — in ihren eigenen Worten, mit einem Link zur Fundstelle. Ich
  erzeuge keine Antworten: Steht es hier nicht, sage ich Ihnen das…"*
- FR — *"Posez n'importe quelle question sur Quenora et je vous montrerai ce
  que ce site en dit, dans ses propres mots, avec un lien vers l'endroit exact.
  Je ne génère pas de réponses : si…"*

**Fix:** move the greeting into the `UI` object beside `none`, `one` and
`many`. `build_i18n.py` cannot reach a string literal inside `<script>`, which
is why a translated key sat unused.

---

### C2 · The German assistant answers a pricing question with the demo's straw-man text

**Verified live on `/de`.** Question: **"Gibt es einen Festpreis?"**
First passage returned:

> **Erfundene Schwelle. Eine Pilot-Ausnahme von Art. 28 gibt es nicht.**
> — attributed to *HABEN SIE EIN PROBLEM, DAS EINEM DAVON ÄHNELT?*

That sentence is an *annotation on the ungoverned side* of the
governed-vs-ungoverned demo. It exists to label a **fabricated** answer as
fabricated. It is now served as Quenora's own answer to a commercial question,
with a source link, to the buyer most likely to be evaluating price.

It is not a hallucination — it is site text. That is what makes it worse: the
honesty architecture is intact and the retrieval still produces a damaging
answer.

**Present in the English and German indexes** (`Invented threshold…`,
`Erfundene Schwelle…`, `Invented figures…`, `Erfundene Zahlen…`), and
**mis-attributed** — filed under a chapter heading from a different section.

**Fix:** exclude the ungoverned panel from `build_assistant.py`'s extraction.
The governed panel can stay; the straw-man must not be retrievable.

---

### C3 · "Fixed fee" is invisible to the assistant in all three languages

The first pricing card on the page is headed **Fixed fee / Festpreis /
Forfait**. That term appears **zero times** in all three assistant indexes:

```
EN  "fixed fee"     0        DE  "festpreis"   0        FR  "forfait"   0
```

Only the card *bodies* are indexed; the card *headings* are not. So:

- FR — **"Y a-t-il un forfait ?"** → **no match at all** (verified live), falls
  through to the honest-failure message.
- DE — **"Gibt es einen Festpreis?"** → returns C2 above.
- EN — **"Is there a fixed fee?"** → no curated trigger either (`fee` is not in
  the pricing keyword set), so it falls to retrieval.

The most common commercial question on any consulting site cannot be answered
in any language.

**Fix:** index the pricing card headings; add `fee`/`forfait`/`festpreis` to
the alias tables.

---

### C4 · Legal placeholders (already known)

`{{TODO:STREET_AND_NUMBER}}` and `{{TODO:POSTCODE}}` render in `impressum.html`
and `privacy.html`. Already the only red stage in the release gate and already
recorded in `STATUS.md` §3 as yours to supply. Listed here only for
completeness — no new finding.

---

## 4. Assistant audit — HIGH severity

### H1 · "What does Quenora do?" is answered badly in all three languages

**Verified live in English.** Every content word is a stopword, so only
`quenora` survives tokenisation. The three passages returned:

1. *"The sector experience and the figure above describe work done before
   Quenora was founded in 2025. They're not Quenora client results…"* — a
   disclaimer
2. *"Scan to save Quenora Consulting to your phone…"* — the QR card
3. *"Illustrative, not a client portfolio…"* — a portfolio caveat

**None answers the question.** The first thing a visitor learns is what Quenora
has *not* done.

German and French behave the same way: *"Wie arbeitet Quenora?"* and *"Was
unterscheidet Quenora?"* both return the same disclaimer-plus-QR-card set.
*"Que fait Quenora ?"* likewise.

**The suggested chip works because it is phrased to hit a curated keyword** —
*"What do you actually do?"* contains the trigger `what do you`. A visitor who
rephrases naturally falls off the curated path entirely. The chips are
therefore hiding the defect rather than mitigating it.

### H2 · The curated answers are English-only, so DE/FR get a weaker assistant

Fourteen hand-written answers exist for the questions buyers actually ask. They
are disabled for German and French by design:

```js
var kq = LANG==='en' ? q.toLowerCase() : '\u0000';
```

The in-code comment explains why, and the reasoning is sound — they were never
translated, so German visitors were getting English prose. Disabling them was
the right *fix*, but it leaves a real asymmetry: **English gets curated answers
plus retrieval; German and French get retrieval only.**

Compounding it, the alias tables are asymmetric too — **45 English entries, 16
German, 18 French** — and the localised tables are merged *into* the English
one rather than replacing it, so most of a German visitor's alias coverage is
English words their question will never contain.

### H3 · One curated answer fires on the wrong question

**"What happens if the project does not work?"** contains `work` and `project`,
which match curated set 7 — *work, case, client, example, project, reference* —
the **case-studies** answer. A high-stakes commercial question about failure
returns marketing copy about engagement examples.

This is a general risk of substring matching: `about` (set 3) matches any
question containing the word "about", so *"What about governance?"* returns the
founder biography.

### H4 · Two German alias bridges are dead code

`ALIAS_DE` defines bridges for **`wer`** (who) and **`wo`** (where):

```js
wer: ['balaji','inhabergefuhrt','firma','gegrundet'],
wo:  ['heilbronn','deutschland','sitz'],
```

Both words are in the shared stopword list (`…wie wer wo wenn dann dass…`), so
`terms()` strips them before `expand()` ever runs. **The two most natural German
question-openers can never trigger their aliases.** French is unaffected —
`qui` is not a stopword.

### H5 · Every French "Comment…?" question is dragged to the pricing chapter

`comment` is not in the stopword list, and it appears in the heading **"Comment
cela est tarifé."**, which earns the 1.8 heading boost. Result:

| Question | Top passage |
|---|---|
| Comment travaille Quenora ? | *Comment cela est tarifé* — "Indiqué ici plutôt qu'après trois rendez-vous…" |
| Comment gérez-vous le rollback ? | *Comment cela est tarifé* — same passage |

Two unrelated questions, one irrelevant answer. **Fix:** add `comment` to the
stopword list, as `how` already is in English.

### Chat findings that came back clean

- **Language matching is correct.** German questions returned German passages,
  French questions French passages. The `/de` and `/fr` indexes load correctly
  (all three return HTTP 200). The production bug recorded in `STATUS.md` §5 —
  French visitors answered in English — did not reproduce.
- **The failure behaviour is honest and well written**, in French especially.
- **Nothing was invented.** As expected from the architecture.

---

## 5. French typography — HIGH

`i18n/fr.json` declares its own standard in `_meta.register`:

> *"Vouvoiement. Espace fine insécable (U+202F) avant ; : ! ? — pas de Title
> Case anglaise."*

Measured against that standard, in raw source:

| Page | Correct U+202F | Plain space (wrong) |
|---|---|---|
| work.html | 27 | 3 |
| index.html | 1 | 20 |
| engineering.html | 0 | 15 |
| capabilities.html | 0 | 5 |
| products.html | 0 | 4 |
| approach.html | 0 | 3 |
| contact.html | 0 | 2 |
| **Total** | **28** | **52** |

**One page was done properly and the other six were not.** Roughly two-thirds
of French high punctuation is typographically wrong. This is the single most
visible "translated by a machine" tell for a French reader, and it is
mechanical to fix.

Guillemets themselves are correct and correctly paired everywhere.

---

## 6. Language quality — MEDIUM

Exact replacements proposed. German and French written as native copy, not as
translations of the English.

### German

| # | Current | Problem | Proposed |
|---|---|---|---|
| M1 | **Fehlverhalten** (for *Failure behaviour*) | *Fehlverhalten* means **misconduct**, of a person. Wrong register and wrong concept in a technical list. | **Fehlerverhalten** — or **Verhalten im Fehlerfall** |
| M2 | **Gegen die vereinbarte Zahl** (*Against the agreed number*, Phase 05 heading) | *Gegen* is adversarial. The English means *measured against*. | **An der vereinbarten Zahl gemessen** |
| M3 | **Die unglamouröse Schicht** (*The unglamorous layer*) | *unglamourös* is a rare, awkward Anglicism no German CTO writes. The French — *la couche ingrate* — is excellent and shows what was available. | **Die unspektakuläre Schicht** |
| M4 | **Die weitere Karte, und die Zahlen** | Literal calque; *weitere Karte* means nothing here. Plus a comma before *und*, which is an English serial-comma habit. | **Das größere Bild und die Zahlen** |
| M5 | **Governance ist eine Menge von Entscheidungen** | *eine Menge von* reads as set theory, or colloquially "a lot of". | **Governance ist eine Reihe von Entscheidungen** |
| M6 | **Organisationen nach dem Piloten** | Reads as "after the pilot *(person)*". | **Organisationen nach der Pilotphase** |
| M7 | **Referenzwahrheit** (*Ground truth*) | Invented compound. German ML practice keeps *Ground Truth* or uses *Grundwahrheit*. | **Ground Truth** (retain), or **Grundwahrheit** |
| M8 | **Was das System nicht entscheiden darf** | *darf nicht* is permission. The English *refuses to decide* is the system's own behaviour — a governance claim, so the distinction matters. French gets this right (*refuse de décider*). | **Was das System nicht entscheidet** |
| M9 | **RAG systems** (in the German capabilities page) | English left inside a German sentence. | **RAG-Systeme** |

### French

| # | Current | Problem | Proposed |
|---|---|---|---|
| M10 | **La carte élargie, et les chiffres** | Same calque and same comma-before-*et* as M4. | **La vue d'ensemble et les chiffres** |
| M11 | **Modernisation du legacy** | Anglicism where French has its own term. | **Modernisation de l'existant** |
| M12 | *méthode* (nav) vs *approche* ("L'approche en détail") | The French uses two words for one concept. German is consistent throughout (*Vorgehen*). | Pick one — **méthode** everywhere |

---

## 7. Cross-language consistency

| Concept | EN | DE | FR | Consistent? | Action |
|---|---|---|---|---|---|
| The nine principles | Trustworthy … Intelligent | 7 of 9 translated; **Enterprise** and **Premium** left in English | All 9 translated (*Entreprise*, *Haut de gamme*) | **No** | Decide once: these are brand vocabulary tied to the mark. Either keep all nine English in all languages, or translate all nine. |
| Ownership (5-layer list) | Ownership | **Verantwortung** (responsibility) | **Propriété** (property) | **No** | German should be **Eigentum** or **Zuständigkeit** — currently a different concept from the French |
| Nav — Engineering | Engineering | **KI-Engineering** | Ingénierie | **No** | German adds a qualifier the others do not |
| Footer heading | Site | Navigation | Navigation | **No** | Both translations improved on the English. Consider adopting "Navigation" in EN |
| Approach | Approach | Vorgehen (consistent) | méthode / approche (**split**) | **No** | See M12 |
| Phase names | Frame … Hand over | Consistent | Consistent | Yes | — |
| Fixed fee | Fixed fee | Festpreis | Forfait | Yes | Correct in copy — but see C3, absent from the assistant |

---

## 8. Terminology glossary — reviewed terms

| Concept | EN | DE now | DE recommended | FR now | FR recommended |
|---|---|---|---|---|---|
| Ground truth | Ground truth | Referenzwahrheit | **Ground Truth** | Vérité terrain | Vérité terrain ✓ |
| Failure behaviour | Failure behaviour | Fehlverhalten | **Fehlerverhalten** | Comportement en cas d'échec | ✓ |
| Evaluation harness | evaluation harness | Evaluations-Harness | ✓ (established on the site) | harnais d'évaluation | ✓ |
| Handover | handover | Übergabe | ✓ | transmission | ✓ |
| Change control | change control | Änderungskontrolle | ✓ | gestion des changements | ✓ |
| Governance | governance | Governance | ✓ (retained, correct) | gouvernance | ✓ |
| Rollback | rollback | Rollback | ✓ | rollback | ✓ |
| Retrieval | retrieval | Retrieval | ✓ | recherche | ✓ |
| Legacy | legacy | Altsysteme | ✓ | legacy | **l'existant** |
| Fixed fee | Fixed fee | Festpreis | ✓ | Forfait | ✓ |
| Estate | your estate | Systemlandschaft | ✓ (strong) | votre parc | ✓ (strong) |

---

## 9. Housekeeping — LOW

- **`next year.`** is a key in `de.json` with an **empty value**. It appears
  nowhere in the current English, so nothing renders wrong — a dead entry.
- **`ALIAS` defines `where:` twice.** The second wins; harmless, but it means
  one of the two was intended to be something else.
- **The hidden `#build` chapter's placeholders now exist in German and French
  too** (`[Project title]`, `[Tech stack]`). They are inside `hidden`, do not
  render, and do not leak into any machine-readable surface — verified. They
  become visible the day `#build` is released.

---

## 10. Keep — do not change

Listed so a later pass does not "improve" them.

- **"Most enterprise AI never reaches the work."** — and its German
  *"Die meiste Unternehmens-KI erreicht nie die Arbeit."* and French rendering.
- **"AI programmes fail at the seams."** / *"KI-Programme scheitern an den
  Nahtstellen."* — the German is arguably better than the English.
- **"And then we leave."** / *"Und dann gehen wir."* / *"Puis nous partons."* —
  all three land.
- **"The unglamorous layer" → "La couche ingrate"** — *ingrate* (thankless) is
  a genuinely superior French choice. This is the standard the German should
  meet, not a candidate for change.
- **"Confident" → "Souverän"** — a strong, native German choice over the
  obvious *selbstbewusst*.
- **The French failure message** — *"Rien sur ce site ne correspond, et je
  préfère vous le dire plutôt que de trouver des mots en commun et d'appeler
  cela une réponse."* Excellent.
- **"We don't do it for you. We clear the way."** → *"Nous déblayons le
  terrain."* — the French idiom works.
- **All quotation marks, all three languages.** Correct as they stand.
- **British spelling throughout the English.** Zero US spellings found.

---

## 11. Recommended order of work

| Order | Items | Why first |
|---|---|---|
| 1 | **C1** greeting, **C2** straw-man, **C3** fixed fee | Production defects a buyer meets on the first screen |
| 2 | **H4** dead German aliases, **H5** French `comment` stopword, **H3** curated overlap | One-line fixes with disproportionate effect |
| 3 | **§5** French U+202F sweep | Mechanical, 52 instances, breaches the stated standard |
| 4 | **H1/H2** basic-question coverage, curated parity for DE/FR | The largest quality gap, but needs writing, not just fixing |
| 5 | **§6** the twelve wording corrections | Real but not urgent |
| 6 | **§7** the cross-language decisions | Need your call, not my judgement |

---

## 12. What I could not do, and what needs you

- **I could not rebuild the localised pages.** `build.sh` needs
  `beautifulsoup4`; this machine has neither it nor the `/tmp/qvenv`
  interpreter `STATUS.md` names. Pass 2 needs either permission to install it,
  or someone with the working build to regenerate.
- **The nine principle names (§7) are a brand decision, not a language one.**
  They map to the nine circles of the mark. I have not assumed an answer.
- **`reviewed_by_native_speaker` stays `false`** — now a recorded
  deferral rather than an open question. See 0c: held until after launch,
  from 9 September 2026.
- **The build now runs here.** `beautifulsoup4` is installed and
  `PY=python ./build.sh` works; the gate is 16 of 17.
- **Superseded:** I am not a native German or
  French speaker, and this audit does not change that flag. It finds defects a
  native reviewer would find; it is not a substitute for one on the remaining
  prose. `STATUS.md` §6 already records this as an open item, and it should
  stay open.

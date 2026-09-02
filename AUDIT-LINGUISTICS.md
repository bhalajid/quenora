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
var kq = LANG==='en' ? q.toLowerCase() : ' ';
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
- **`reviewed_by_native_speaker` stays `false`.** I am not a native German or
  French speaker, and this audit does not change that flag. It finds defects a
  native reviewer would find; it is not a substitute for one on the remaining
  prose. `STATUS.md` §6 already records this as an open item, and it should
  stay open.

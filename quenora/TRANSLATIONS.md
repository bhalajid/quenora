# Quenora — multilingual site

Five languages: **English** (base), **Deutsch**, **Français**, **Español**, **Italiano**.
396 strings each, 3,524 words per language, ~14,100 words total.

```
/                 English (base, x-default)
/de/              Deutsch
/fr/              Français
/es/              Español
/it/              Italiano
```

## How it works

The English HTML is the single source. `build_i18n.py` parses it, substitutes
translations **at the text-node and attribute level** — never by blind string
replacement, which would corrupt markup — and writes a complete localised copy
of all six pages per language.

```bash
python3 build_i18n.py        # regenerate de/ fr/ es/ it/
python3 test/i18n_qa.py      # translation quality gate
cd test && ./release.sh ..   # full 6-stage gate, translations included
```

Per language the generator also rewrites: `<html lang>`, `<title>`, meta
description, all `og:*` and `twitter:*`, `og:locale`, canonical, a full set of
`hreflang` alternates including `x-default`, asset paths (one level deeper),
and inserts a localised language switcher into the header.

## Editing copy

**Never edit the files in `de/`, `fr/`, `es/`, `it/`.** They are generated and
will be overwritten. Edit:

- **English copy** → the source `.html` files, then rerun `build_i18n.py`
- **A translation** → `i18n/<lang>.json`, then rerun `build_i18n.py`

If you add new English copy, `build_i18n.py` reports it as untranslated and
lists it in `_untranslated.json`. Coverage below 100% fails the gate.

## The quality gate

`test/i18n_qa.py` — ten mechanical checks, run against the built pages:

| # | Check | Catches |
|---|---|---|
| 1 | Coverage | Any string still in English |
| 2 | English residue | Translation identical to the source |
| 3 | Placeholders | Brand, domain, email, product names lost |
| 4 | Symbols | Arrows and em dashes dropped |
| 5 | Capitalisation | English Title Case carried into FR/ES/IT |
| 6 | Punctuation | FR narrow no-break space before `; : ! ?`; ES missing `¿` `¡` |
| 7 | Orthography | German `ss` where Germany requires `ß`; double spaces |
| 8 | HTML integrity | Tag counts diverging from the English source |
| 9 | Metadata | `lang`, canonical, hreflang, `og:locale` |
| 10 | Length | Short labels that grew enough to wrap and break layout |

**Errors this gate actually caught during the build**, all now fixed:

- `ai:boosters` still hardcoded in the assistant panel on all six pages
- Swiss `ss` used where German German needs `ß` (*anschließend*, *Maßstab*,
  *schließen*, *heißt*, *fließen*, *Großteil*)
- Empty `canonical` and `hreflang` hrefs — a BeautifulSoup `new_tag` quirk
- The language switcher's `aria-label` hardcoded in German for every language
- A **stray space before the full stop** in four split headlines, in all four
  languages — `"… noch läuft ."` instead of `"… noch läuft."`
- The QR code still encoding the old domain inside its base64 payload
- Homepage capability marquee disagreeing with `services.html`

## Conventions per language

**German** — `Sie` throughout. Nouns capitalised. **`ß`, not `ss`** (this site
targets Germany, not Switzerland; the gate enforces it).

**French** — vouvoiement. Narrow no-break space (U+202F) before `; : ! ?`.
Guillemets `« »`. Sentence case in headings, never English Title Case.

**Spanish** — *usted*. Opening `¿` and `¡` are mandatory — the gate fails
without them. Sentence case. Angular quotes `« »`.

**Italian** — formal *lei*. Sentence case. Angular quotes `« »`.

## What is deliberately NOT translated

Brand name, `quenora.ai`, the email address, `EU AI Act`, `GDPR`, `MLOps`,
`RAG`, `ERP`, `CRM`, `IaC`, `Platform Engineering`, numerals, phase numbers,
and the language names in the switcher.

## Before this goes in front of a client

> **These translations have not been reviewed by a native speaker.**
> `"reviewed_by_native_speaker": false` in every `i18n/<lang>.json`.

The gate verifies mechanics — coverage, punctuation, orthography, markup,
metadata. It cannot judge idiom, register or whether a sentence sounds like a
consultancy or like a translation. For an enterprise site selling into these
markets, budget a native-speaker pass per language. Flip the `_meta` flag to
`true` once each is done.

Also open: **50 length warnings** where a translated label is 85%+ longer than
the English. Body copy reflows fine; check the short ones in a browser at
375px, 768px and 1440px. Run `python3 test/i18n_qa.py` to list them.

## SEO

`sitemap.xml` lists all 30 URLs with reciprocal `xhtml:link` alternates.
Every page carries a self-referencing canonical plus five `hreflang` alternates
and `x-default` pointing at English. Vercel serves `/de/` etc. as static paths
with no configuration needed.

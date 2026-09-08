# Launch checklist — quenora.ai

Everything below is a step only you can take. The repo is ready for all of it;
nothing here is code that still needs writing.

Do them in this order. **Step 2 before step 3** — reversing them takes the site
offline for as long as DNS takes to propagate.

---

## 1 · Fill the Impressum and the privacy notice — DONE, 9 September

`Kleiststr. 12` completed the address. No `{{TODO:}}` placeholders remain in
the repo, and `build_seo.py` now carries `streetAddress` in its PostalAddress
as well, so the structured data matches the Impressum.

```bash
cd quenora/test && PY=python bash release.sh ..
```

**RELEASE APPROVED — 24 pass, 0 held, 0 fail.** (The gate has nine stages and
24 assertions now, not the 14 this file used to quote.)

---

## 2 · Point quenora.ai at Vercel — DONE, but pointed the wrong way round

DNS resolves and the site is live. **But the apex redirects to www, and this
repo is built apex-first.**

```
https://quenora.ai/       308 -> https://www.quenora.ai/
https://www.quenora.ai/   200, serving the current build
```

Every canonical, hreflang, og:url and sitemap entry declares
`https://quenora.ai/...`, and all three printed QR codes encode the apex. So
the page served at `www` declares a canonical pointing at a URL that redirects
back to it, and every QR scan takes an extra hop.

**Fix it in the Vercel dashboard, not in code:** set `quenora.ai` as the
project's primary domain and `www.quenora.ai` to redirect to it. That is the
arrangement step 3 below already assumes. Nothing in the repo needs
regenerating either way — it is one dashboard setting.

`test/launch_check.sh` stops on its first assertion until this is swapped: it
requires the apex to answer 200, and today it answers 308.

---

## 3 · Send the deployment host to the real one

Only after step 2 answers 200. Add this to `quenora/vercel.json` at the top
level, beside `"headers"`:

```json
  "redirects": [
    {
      "source": "/:path*",
      "has": [{ "type": "host", "value": "(?<h>.*\\.vercel\\.app)" }],
      "destination": "https://quenora.ai/:path*",
      "permanent": true
    },
  ],
```

Only the one rule. Add `www.quenora.ai` as a domain in the Vercel dashboard and
set it to redirect to the apex there — the dashboard handles www natively, and
a second vercel.json rule doing the same job is a redirect loop waiting to
happen.

**This is now in `quenora/vercel.json`, added 9 September once the domain
answered.** It sits first in the `redirects` array so a `.vercel.app` request
leaves for the real domain before any of the path redirects below it can
rewrite it on the wrong host. It fires only on `.vercel.app`, so it cannot
loop with the dashboard's www rule.

Until then the deployment host carries `X-Robots-Tag: noindex, nofollow`, so it
stays out of search without being broken. Once the redirect is in, that header
becomes redundant but is harmless — a redirected host is never indexed anyway.

---

## 4 · Release the hidden section, if you want it at launch

`index.html` has `<section hidden id="build">` — the products and ongoing work
chapter. Releasing it means renumbering the chapters after it: `#honest`,
`#who`, `#commercial` and `#principles` go from 06/07/08/09 to 07/08/09/10.
Ask and it is a ten-minute change.

---

## 5 · After the first deploy on the real domain

One command, twenty checks:

```bash
cd /Users/balajidurai/Quenora/quenora && bash test/launch_check.sh
```

It answers only the questions the repo cannot: whether DNS resolves, whether
the certificate is issued, whether every clean URL serves without a hop,
whether the deployment host redirects away and keeps the path, whether the
sitemap and canonicals name quenora.ai, and whether the security headers
survived the domain change.

Today it stops at the first check, because the domain does not answer. Run
against the deployment host it already reports **17 passed, 2 failed** — the
two failures being the redirect from step 3, which is not in place yet by
design.

Then submit `https://quenora.ai/sitemap.xml` in Google Search Console.

---

## Still open, and worth knowing

- **`story.html` has no German or French version.** It is not in `PAGES`, so it
  is never localised. Nothing links to it, but it is deployed and indexable.
  Either localise it or retire it.
- **es/ and it/ sit at ~45% translated.** Both are deliberately unlisted —
  absent from the switcher, the hreflang set and the sitemap, and served
  noindex — so no visitor reaches them. They drift further with every English
  change.
- **The DE and FR translations have not had a native-speaker review.**
  `i18n/*.json` still carries `reviewed_by_native_speaker: false`. The
  mechanical gate is clean; idiom and register are not the same thing.

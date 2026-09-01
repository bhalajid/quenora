# Launch checklist — quenora.ai

Everything below is a step only you can take. The repo is ready for all of it;
nothing here is code that still needs writing.

Do them in this order. **Step 2 before step 3** — reversing them takes the site
offline for as long as DNS takes to propagate.

---

## 1 · Fill the Impressum and the privacy notice

The release gate has one failing stage, 4b, and this is it. German law (§5 DDG)
requires a postal address and a contact route on the Impressum, so the build
refuses to pass while placeholders remain.

```bash
grep -rn "{{TODO:" /Users/balajidurai/Quenora/quenora/*.html
```

Five placeholders across two files: `{{TODO:STREET_AND_NUMBER}}`,
`{{TODO:POSTCODE}}`, `{{TODO:TELEPHONE}}`. Replace them, then:

```bash
cd /Users/balajidurai/Quenora/quenora/test && bash release.sh ..
```

That should be 14 of 14 green.

---

## 2 · Point quenora.ai at Vercel

Today the domain resolves but nothing answers:

```
quenora.ai          -> 192.64.119.248   (registrar parking)   HTTPS times out
quenora.vercel.app  -> 64.29.17.3, 216.198.79.3               200 OK
```

In the Vercel dashboard, add `quenora.ai` and `www.quenora.ai` as domains on
the project, then set the DNS records Vercel gives you at the registrar. Wait
until `curl -sS -o /dev/null -w "%{http_code}\n" https://quenora.ai` returns
`200` before going on.

Every canonical, hreflang, og:url and sitemap entry in the repo already
declares `https://quenora.ai/...`, so nothing needs regenerating afterwards.

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
    {
      "source": "/:path*",
      "has": [{ "type": "host", "value": "www.quenora.ai" }],
      "destination": "https://quenora.ai/:path*",
      "permanent": true
    }
  ],
```

This is deliberately **not** in the repo yet. While quenora.ai does not answer,
quenora.vercel.app is the only working address, and redirecting it to a host
that times out would take the site down on the next deploy.

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

```bash
curl -sI https://quenora.ai/de/work | head -3      # 200, no redirect
curl -sI https://quenora.vercel.app/ | head -3     # 308 to quenora.ai
curl -s  https://quenora.ai/sitemap.xml | head     # every loc on quenora.ai
```

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

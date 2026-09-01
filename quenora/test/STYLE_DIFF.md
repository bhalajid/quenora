# style_diff.js — the check that does not depend on me guessing

Every drift so far was found by a person, and each fix added a rule for the
one thing they found: the wordmark, then the footer map, then the emphasis
colour, then the eyebrow colour. That is reactive by construction — the rule
always arrives after the defect.

This does the opposite. It renders every page, samples **the whole computed
property set** for twelve roles, and diffs each page against `index.html`.
Nothing in it is a list of things I decided were worth checking.

## Running it

Serve the site, open it in the browser pane, then in the page console:

```js
await eval('(async()=>{' + (await (await fetch('/test/style_diff.js')).text()) + '})()')
```

It returns one entry per page with a count and the differing properties.

## Reading the output

Three kinds come back and they are not equal:

- **drift** — the same role rendering differently for no reason. The eyebrow
  colour was here: `rgb(201,122,60)` on eight pages, `rgb(233,160,99)` on two.
  Fix these.
- **intended difference** — a home-page hero h1 at 98px against a sub-page
  title h1 at 55px. Leave these.
- **artefact** — a role whose selector matched a different kind of element on
  the two pages. Fix the selector, not the site.

Judgement is still needed on which is which. What this removes is the need to
guess *where to look*.

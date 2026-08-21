# Test suite

Run before every push:

    cd test && npm install && ./release.sh

Five gates — nothing ships unless all pass:

1. **Syntax + structure** — every inline script parses; div/section/main tags balanced
2. **Sphere hit-testing** — real Three.js math, 9 spheres x 4 viewports x 5 rotations
3. **Smoke test** — jsdom executes the real page JS: assistant opens/closes, chips
   post messages, Escape closes, demo tabs switch, timer accumulates, automate
   button gates correctly, nine principles render, links resolve
4. **Accessibility + SEO** — landmarks, skip link, focus styles, reduced-motion,
   alt text, canvas hidden from screen readers, favicon, OG tags, no broken links
5. **Contrast** — every text colour against the ground, WCAG AA (4.5:1)

Exit code is non-zero if anything fails, so it can gate CI.

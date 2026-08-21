/* Appearance test — the hero's FALLBACK layout.
 *
 * Two paths exist in fit():
 *
 *   snapped   the desktop composition, built on the page's six-column grid
 *             against measured headline metrics. Covered by hero_geometry.js,
 *             which can model those metrics; this file cannot, because the
 *             fallback deliberately does not depend on them.
 *
 *   fallback  narrow screens, and the first frames before the headline is
 *             measurable. Centred under the type, halo budgeted inside the
 *             fit. That is what this file checks — plus the final safety
 *             clamps, which have to hold on BOTH paths.
 *
 * The fallback matters more than its name suggests: it is what renders on
 * every phone, and it is what renders for a frame or two on desktop before
 * webfonts settle. It has to be correct on its own, not merely survivable.
 *
 *   node test/hero_fit.js [dir]
 */
'use strict';

const fs = require('fs');
const path = require('path');

const DIR = process.argv[2] || path.join(__dirname, '..');
const src = fs.readFileSync(path.join(DIR, 'index.html'), 'utf8');

const num = (re, label) => {
  const m = src.match(re);
  if (!m) { console.error('   could not read ' + label + ' from index.html'); process.exit(2); }
  return parseFloat(m[1]);
};

const HALO = num(/var HALO = ([\d.]+)/, 'halo multiplier');
const PAD  = 27 * HALO;

/* the fallback box, read from the page */
const fb = (() => {
  const m = src.match(/if\(!snapped\)\{[\s\S]*?fx0 = W\*([\d.]+); fx1 = W\*([\d.]+); fy0 = H\*([\d.]+); fy1 = H\*([\d.]+);/);
  if (!m) { console.error('   could not read the fallback box'); process.exit(2); }
  return { x0: +m[1], x1: +m[2], y0: +m[3], y1: +m[4] };
})();

const ARC = [...src.matchAll(/<circle cx="([\d.]+)" cy="([\d.]+)" r="([\d.]+)"/g)]
  .slice(0, 9).map(m => ({ x: +m[1], y: +m[2], r: +m[3] }));
if (ARC.length !== 9) { console.error('   expected 9 circles, found ' + ARC.length); process.exit(2); }

const B = [Math.min(...ARC.map(c => c.x - c.r)), Math.max(...ARC.map(c => c.x + c.r)),
           Math.min(...ARC.map(c => c.y - c.r)), Math.max(...ARC.map(c => c.y + c.r))];
const BW = B[1] - B[0], BH = B[3] - B[2];
const CXA = (B[0] + B[1]) / 2, CYA = (B[2] + B[3]) / 2;

function fallback(W, H) {
  const fx0 = W * fb.x0, fx1 = W * fb.x1, fy0 = H * fb.y0, fy1 = H * fb.y1;
  const SC = Math.min((fx1 - fx0) / (BW + PAD * 2), (fy1 - fy0) / (BH + PAD * 2));
  let OX = (fx0 + fx1) / 2 - CXA * SC;
  let OY = (fy0 + fy1) / 2 - CYA * SC;
  /* the same final clamps the page applies on both paths */
  if (OX + B[1] * SC > W - 2) OX = W - 2 - B[1] * SC;
  if (OY + B[3] * SC > H - 2) OY = H - 2 - B[3] * SC;
  if (OY + B[2] * SC < 2)     OY = 2 - B[2] * SC;
  return { SC, OX, OY };
}

/* phones and small tablets, where this path actually ships */
const VIEWPORTS = [
  ['iPhone SE',          375, 667],
  ['iPhone 15 Pro',      393, 852],
  ['Android mid-range',  412, 915],
  ['Pixel Fold cover',   344, 882],
  ['iPad mini portrait', 744, 1133],
  ['iPad portrait',      768, 1024],
  ['small landscape',    740, 420],
  ['desktop first frame', 1920, 1080],
];

let bad = 0;
console.log('\n   viewport              r9px    left   right     top  bottom   verdict');
console.log('   ' + '─'.repeat(72));

for (const [name, W, H] of VIEWPORTS) {
  const { SC, OX, OY } = fallback(W, H);
  const halo = 27 * SC * HALO;

  const left   = OX + B[0] * SC - halo;
  const right  = OX + B[1] * SC + halo;
  const top    = OY + B[2] * SC - halo;
  const bottom = OY + B[3] * SC + halo;

  /* the fallback budgets the halo inside the fit, so here the GLOW must fit
     too — not just the mark */
  const contained = left >= -1 && right <= W + 1 && top >= -1 && bottom <= H + 1;
  const r9 = 27 * SC;
  const bigEnough = r9 >= 12;

  if (!contained || !bigEnough) bad++;

  console.log('   %s %s %s %s %s %s  %s',
    name.padEnd(20),
    r9.toFixed(0).padStart(5),
    Math.round(left).toString().padStart(6),
    Math.round(right).toString().padStart(7),
    Math.round(top).toString().padStart(7),
    Math.round(bottom).toString().padStart(7),
    !contained ? 'CLIPS the viewport'
    : !bigEnough ? 'too small to read'
    : 'ok');
}

console.log('   ' + '─'.repeat(72));
if (bad) {
  console.log('   %d of %d viewports fail\n', bad, VIEWPORTS.length);
  process.exit(1);
}
console.log('   fallback contained and legible at all %d viewports\n', VIEWPORTS.length);

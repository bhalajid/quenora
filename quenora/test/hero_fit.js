/* Appearance test — does the hero constellation stay on screen?
 *
 * The hero cannot be rendered headlessly here (no browser binary), so this
 * ports the fit maths straight out of index.html and replays it across the
 * viewport sizes real visitors arrive on. The scale, offset and clamp
 * constants are READ FROM THE PAGE, so if someone edits the hero the test
 * follows them rather than drifting out of date.
 *
 *   node test/hero_fit.js [dir]
 */
'use strict';

const fs = require('fs');
const path = require('path');

const DIR = process.argv[2] || path.join(__dirname, '..');
const src = fs.readFileSync(path.join(DIR, 'index.html'), 'utf8');

/* ── constants lifted from the page ───────────────────────────── */
const num = (re, label) => {
  const m = src.match(re);
  if (!m) { console.error('   could not read ' + label + ' from index.html'); process.exit(2); }
  return parseFloat(m[1]);
};
const PAD    = num(/var pad = ([\d.]+)/, 'pad');
const SM     = num(/W<900 \? ([\d.]+) : [\d.]+\)/, 'small-screen scale');
const LG     = num(/W<900 \? [\d.]+ : ([\d.]+)\)/, 'large-screen scale');
const HALO   = num(/var big = 27\*SC\*([\d.]+)/, 'halo multiplier');
const OXS    = num(/OX = W\*\(W<900 \? ([\d.]+)/, 'small OX fraction');
const OXL    = num(/OX = W\*\(W<900 \? [\d.]+ : ([\d.]+)/, 'large OX fraction');
const OYS    = num(/OY = H\*\(W<900 \? ([\d.]+)/, 'small OY fraction');
const OYL    = num(/OY = H\*\(W<900 \? [\d.]+ : ([\d.]+)/, 'large OY fraction');

/* the nine-circle mark, read from the #mark9 symbol */
const ARC = [...src.matchAll(/<circle cx="([\d.]+)" cy="([\d.]+)" r="([\d.]+)"/g)]
  .slice(0, 9).map(m => ({ x: +m[1], y: +m[2], r: +m[3] }));
if (ARC.length !== 9) { console.error('   expected 9 circles, found ' + ARC.length); process.exit(2); }

const b = [Math.min(...ARC.map(c => c.x - c.r)), Math.max(...ARC.map(c => c.x + c.r)),
           Math.min(...ARC.map(c => c.y - c.r)), Math.max(...ARC.map(c => c.y + c.r))];
const bw = b[1] - b[0], bh = b[3] - b[2];

/* ── the page's own fit routine ───────────────────────────────── */
function layout(W, H) {
  const availW = W * (1 - PAD * 2), availH = H * (1 - PAD * 2);
  const SC = Math.min(availW / bw, availH / bh) * (W < 900 ? SM : LG);
  let OX = W * (W < 900 ? OXS : OXL) - ((b[0] + b[1]) / 2) * SC;
  const OY = H * (W < 900 ? OYS : OYL) - ((b[2] + b[3]) / 2) * SC;
  const big = 27 * SC * HALO;
  if (OX + b[1] * SC + big > W) OX = W - b[1] * SC - big;
  if (OX + b[0] * SC - big < 0) OX = big - b[0] * SC;
  return { SC, OX, OY, big };
}

/* Real-world viewports: the small phones, the common laptops, the
   boardroom display someone will inevitably mirror this onto. */
const VIEWPORTS = [
  ['iPhone SE',            375,  667],
  ['iPhone 15 Pro',        393,  852],
  ['Android mid-range',    412,  915],
  ['iPad portrait',        768, 1024],
  ['iPad landscape',      1024,  768],
  ['laptop',              1280,  800],
  ['MacBook Pro 14"',     1512,  982],
  ['desktop 1080p',       1920, 1080],
  ['ultrawide',           2560, 1080],
  ['5K display',          3440, 1440],
  ['short window',        1440,  560],
];

let bad = 0;
console.log('\n   viewport              scale    left    right      top   bottom');
console.log('   ' + '─'.repeat(63));

for (const [name, W, H] of VIEWPORTS) {
  const { SC, OX, OY, big } = layout(W, H);
  /* the visible extent includes the glow halo around the outermost sphere */
  const left   = OX + b[0] * SC - big;
  const right  = OX + b[1] * SC + big;
  const top    = OY + b[2] * SC - big;
  const bottom = OY + b[3] * SC + big;

  /* Horizontal is hard-clamped, so it must be inside. Vertical is allowed a
     modest bleed — the hero is a full-bleed field, and a halo grazing the top
     or bottom edge reads as intentional. More than a quarter-viewport of the
     mark itself off screen does not. */
  const coreTop    = OY + b[2] * SC;
  const coreBottom = OY + b[3] * SC;
  const coreH      = coreBottom - coreTop;
  const cut = Math.max(0, -coreTop) + Math.max(0, coreBottom - H);

  const hOk = left >= -1 && right <= W + 1;
  const vOk = cut <= coreH * 0.25;
  if (!hOk || !vOk) bad++;

  console.log('   %s %s %s %s %s %s  %s',
    name.padEnd(20),
    SC.toFixed(3).padStart(6),
    Math.round(left).toString().padStart(6),
    Math.round(right).toString().padStart(7),
    Math.round(top).toString().padStart(8),
    Math.round(bottom).toString().padStart(7),
    (hOk && vOk) ? 'ok' : (!hOk ? 'OFF SCREEN horizontally' : 'clipped vertically'));
}

console.log('   ' + '─'.repeat(63));
if (bad) {
  console.log('   %d of %d viewports clip the mark\n', bad, VIEWPORTS.length);
  process.exit(1);
}
console.log('   mark contained at all %d viewports\n', VIEWPORTS.length);

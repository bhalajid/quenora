/* Appearance test — does the hero constellation stay on screen, and does it
 * stay out of the headline?
 *
 * The hero cannot be rendered headlessly here (no browser binary), so this
 * ports the fit maths straight out of index.html and replays it across the
 * viewport sizes real visitors arrive on. The field box and halo budget are
 * READ FROM THE PAGE, so if someone edits the hero the test follows them
 * rather than drifting out of date.
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

/* the field box, per breakpoint, read from fit() */
const box = (which) => {
  const block = src.match(/if\(narrow\)\{([\s\S]*?)\}\s*else\s*\{([\s\S]*?)\}/);
  if (!block) { console.error('   could not read the field box'); process.exit(2); }
  const b = which === 'narrow' ? block[1] : block[2];
  const f = (k) => {
    const m = b.match(new RegExp(k + '\\s*=\\s*[WH]\\*([\\d.]+)'));
    if (!m) { console.error('   could not read ' + k); process.exit(2); }
    return parseFloat(m[1]);
  };
  return { x0: f('fx0'), x1: f('fx1'), y0: f('fy0'), y1: f('fy1') };
};
const NARROW = box('narrow'), WIDE = box('wide');

/* the nine-circle mark, read from the #mark9 symbol */
const ARC = [...src.matchAll(/<circle cx="([\d.]+)" cy="([\d.]+)" r="([\d.]+)"/g)]
  .slice(0, 9).map(m => ({ x: +m[1], y: +m[2], r: +m[3] }));
if (ARC.length !== 9) { console.error('   expected 9 circles, found ' + ARC.length); process.exit(2); }

const B = [Math.min(...ARC.map(c => c.x - c.r)), Math.max(...ARC.map(c => c.x + c.r)),
           Math.min(...ARC.map(c => c.y - c.r)), Math.max(...ARC.map(c => c.y + c.r))];
const BW = B[1] - B[0], BH = B[3] - B[2];
const CXA = (B[0] + B[1]) / 2, CYA = (B[2] + B[3]) / 2;

/* ── the page's own fit routine ─────────────────────────────── */
function layout(W, H) {
  const f = W < 900 ? NARROW : WIDE;
  const fx0 = W * f.x0, fx1 = W * f.x1, fy0 = H * f.y0, fy1 = H * f.y1;
  const SC = Math.min((fx1 - fx0) / (BW + PAD * 2), (fy1 - fy0) / (BH + PAD * 2));
  return {
    SC,
    OX: (fx0 + fx1) / 2 - CXA * SC,
    OY: (fy0 + fy1) / 2 - CYA * SC,
    fx0,
  };
}

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
console.log('\n   viewport             r9px    left   right     top  bottom   verdict');
console.log('   ' + '─'.repeat(70));

for (const [name, W, H] of VIEWPORTS) {
  const { SC, OX, OY, fx0 } = layout(W, H);
  const halo = 27 * SC * HALO;               /* full extent of a lit sphere */

  const left   = OX + B[0] * SC - halo;
  const right  = OX + B[1] * SC + halo;
  const top    = OY + B[2] * SC - halo;
  const bottom = OY + B[3] * SC + halo;

  const onScreen = left >= -1 && right <= W + 1 && top >= -1 && bottom <= H + 1;
  /* on desktop the field must also stay out of the headline column */
  const clearsType = W < 900 ? true : left >= fx0 - 1;
  /* and it has to be worth looking at — a 12px sphere is not a hero */
  const r9 = 27 * SC;
  const bigEnough = W < 900 ? r9 >= 14 : r9 >= 30;

  if (!onScreen || !clearsType || !bigEnough) bad++;

  console.log('   %s %s %s %s %s %s  %s',
    name.padEnd(20),
    r9.toFixed(0).padStart(5),
    Math.round(left).toString().padStart(6),
    Math.round(right).toString().padStart(7),
    Math.round(top).toString().padStart(7),
    Math.round(bottom).toString().padStart(7),
    !onScreen   ? 'CLIPS the viewport'
    : !clearsType ? 'OVERLAPS the headline'
    : !bigEnough  ? 'too small to read as a hero'
    : 'ok');
}

console.log('   ' + '─'.repeat(70));
if (bad) {
  console.log('   %d of %d viewports fail\n', bad, VIEWPORTS.length);
  process.exit(1);
}
console.log('   contained, clear of the type, and legible at all %d viewports\n',
            VIEWPORTS.length);

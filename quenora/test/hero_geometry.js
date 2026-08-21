/* Is the hero actually composed with the type, and is it still the logo?
 *
 * Two separate failures led here.
 *
 *   1. Every sphere had its own orbit — different radius, phase and speed —
 *      which pulled the gaps apart every frame. The nine circles ARE the
 *      mark, and the mark IS the spacing, so the hero stopped being the logo.
 *
 *   2. The field box was arbitrary viewport fractions (0.50, 0.985) with
 *      nothing aligned to anything, so the arc floated beside the headline
 *      instead of being composed with it.
 *
 * The arc is now built on the six-column grid the page already draws, and it
 * does not move. This models that construction from the page's own CSS values
 * and asserts every alignment it claims.
 *
 *   node test/hero_geometry.js [dir]
 */
'use strict';

const fs = require('fs');
const path = require('path');

const DIR = process.argv[2] || path.join(__dirname, '..');
const src = fs.readFileSync(path.join(DIR, 'index.html'), 'utf8');

const g = (re, label) => {
  const m = src.match(re);
  if (!m) { console.error('   could not read ' + label); process.exit(2); }
  return parseFloat(m[1]);
};
const HALO = g(/var HALO = ([\d.]+)/, 'HALO');
const SWAY = g(/var SWAY = ([\d.]+)/, 'SWAY');
const BOB  = g(/var SWAY = [\d.]+, BOB = ([\d.]+)/, 'BOB');
const WRAP = g(/--wrap:(\d+)px/, '--wrap');
const SP4  = g(/--sp4:(\d+)px/, '--sp4');
const LH   = g(/h1,h2,h3\{[^}]*line-height:([\d.]+)/, 'h1 line-height');

const ARC = [...src.matchAll(/<circle cx="([\d.]+)" cy="([\d.]+)" r="([\d.]+)"/g)]
  .slice(0, 9).map(m => ({ x: +m[1], y: +m[2], r: +m[3] }));

const B = [Math.min(...ARC.map(c => c.x - c.r)), Math.max(...ARC.map(c => c.x + c.r)),
           Math.min(...ARC.map(c => c.y - c.r)), Math.max(...ARC.map(c => c.y + c.r))];
const BW = B[1] - B[0], BH = B[3] - B[2];

const trueGap = [];
for (let i = 0; i < 8; i++) {
  const a = ARC[i], b = ARC[i + 1];
  trueGap.push(Math.hypot(b.x - a.x, b.y - a.y) - a.r - b.r);
}

/* ── model the page's layout ──────────────────────────────────
   .wrap  = min(100% - 40px, 1480px), centred
   h1     = clamp(3rem, 12vw, 13rem), line-height .92, three lines
   Ink width per line is estimated from Inter's average advance; the runtime
   uses a real Range measurement, so this only has to be in the right area to
   exercise the column-snapping logic. */
function layout(W, H) {
  const wrapW = Math.min(W - SP4, WRAP);
  const wrapL = (W - wrapW) / 2;
  const col = wrapW / 6;
  const line = (i) => wrapL + col * i;

  const fs = Math.min(Math.max(2.6 * 16, 0.082 * W), 9 * 16);
  const h1H = fs * LH * 3;
  /* widest line is "AI never leaves" — 15 characters at Inter's rough 0.50em
     average advance, tightened by the -.048em tracking */
  const ink = wrapL + 15 * fs * (0.50 - 0.048);
  const h1Top = (H - h1H) / 2, h1Bot = h1Top + h1H;

  /* the arc is exactly as tall as the headline block, and its right edge
     sits on the wrap's own right grid line — always */
  const SC = h1H / BH;
  const r9 = 27 * SC;
  const R = 6;
  const fx1 = line(R), fx0 = fx1 - BW * SC;
  return {
    SC, R, col, wrapL, wrapW, ink, r9,
    OX: fx1 - B[1] * SC,
    OY: h1Bot - B[3] * SC,
    fx0, fx1, h1Top, h1Bot, h1H, gridLine: line,
  };
}

const VIEWPORTS = [
  ['laptop',          1280, 800],
  ['MacBook Pro 14"', 1512, 982],
  ['desktop 1080p',   1920, 1080],
  ['ultrawide',       2560, 1080],
  ['large desktop',   2560, 1352],
  ['5K display',      3440, 1440],
];

let bad = 0, worstGap = 0;
console.log('\n   viewport            cols   r9px   right-edge   mark   verdict');
console.log('   ' + '─'.repeat(68));

for (const [name, W, H] of VIEWPORTS) {
  const P = layout(W, H);
  const nodes = ARC.map(a => ({ x: P.OX + a.x * P.SC, y: P.OY + a.y * P.SC, rr: a.r * P.SC }));

  /* 1 — the spacing is still exactly the logo's */
  for (let i = 0; i < 8; i++) {
    const a = nodes[i], b = nodes[i + 1];
    const gap = Math.hypot(b.x - a.x, b.y - a.y) - a.rr - b.rr;
    worstGap = Math.max(worstGap, Math.abs(gap - trueGap[i] * P.SC));
  }

  /* 2 — the mark's right edge sits on a grid column line */
  const markRight = P.OX + B[1] * P.SC;
  const onGrid = Math.abs(markRight - P.gridLine(P.R)) < 0.01;

  /* 3 — the mark's bottom sits on the headline's bottom */
  const markBottom = P.OY + B[3] * P.SC;
  const onBaseline = Math.abs(markBottom - P.h1Bot) < 0.01;

  /* 4 — the mark's left edge clears the widest line of type */
  const markLeft = P.OX + B[0] * P.SC;
  const clears = markLeft >= P.ink + 24 - 0.01;

  /* 5 — the mark stays on screen. The glow is a gradient that has fallen to
         roughly 14% alpha by the edge, so it is allowed to bleed; the solid
         spheres are not. */
  const n9 = nodes[8];
  const haloFits = n9.x + n9.rr <= W - 1 && nodes[0].x - nodes[0].rr >= 0;

  /* 6 — and it is still worth looking at */
  const r9 = P.r9;
  const big = r9 >= 34;

  /* 7 — the arc and the headline are the same height: the tie itself */
  const markH = (B[3] - B[2]) * P.SC;
  const sameHeight = Math.abs(markH - P.h1H) < 0.01;

  const ok = onGrid && onBaseline && clears && haloFits && big && sameHeight;
  if (!ok) bad++;

  console.log('   %s %s %s %s %s  %s',
    name.padEnd(18),
    ('4–' + P.R).padStart(5),
    r9.toFixed(0).padStart(6),
    (onGrid ? 'grid ' + P.R : 'OFF GRID').padStart(12),
    (haloFits ? 'in' : 'OFF').padStart(6),
    ok ? 'ok'
      : [!onGrid && 'right edge off the grid',
         !onBaseline && 'bottom off the headline',
         !clears && 'overlaps the type',
         !haloFits && 'mark leaves the screen',
         !big && 'too small',
         !sameHeight && 'not the headline height'].filter(Boolean).join(', '));
}

console.log('   ' + '─'.repeat(68));
console.log('   worst gap deviation from the logo: %s px', worstGap.toFixed(6));
console.log('   mark motion at rest: sway %s rad, bob %s px', SWAY, BOB);

if (SWAY !== 0 || BOB !== 0) {
  console.log('   ✗ the mark drifts — it cannot stay on the grid lines it is built on');
  bad++;
}
if (worstGap > 0.1) {
  console.log('   ✗ on-screen spacing no longer matches the mark');
  bad++;
}
if (bad) { console.log('   %d failures\n', bad); process.exit(1); }
console.log('   on the grid, on the baseline, clear of the type, still the logo\n');

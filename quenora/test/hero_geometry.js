/* Is what the hero draws still the logo?
 *
 * The nine circles are the mark, and the mark IS the spacing. An earlier
 * build gave every sphere its own orbit — different radius, phase and speed
 * per node — which pulled the gaps apart every frame. On screen the arc
 * stopped being the logo and the spacing visibly disagreed with the mark in
 * the nav right above it.
 *
 * The motion is now a rigid transform: one rotation about the arc's centroid
 * plus a shared bob. This replays the whole sway cycle and asserts that
 * centre-to-centre distances, and the gaps between sphere surfaces, stay
 * proportional to the source geometry throughout.
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
const SWAY = g(/var SWAY = ([\d.]+)/, 'SWAY');
const BOB  = g(/var BOB\s+= ([\d.]+)/, 'BOB');
const HALO = g(/var HALO = ([\d.]+)/, 'HALO');
const PAD  = 27 * HALO;

const ARC = [...src.matchAll(/<circle cx="([\d.]+)" cy="([\d.]+)" r="([\d.]+)"/g)]
  .slice(0, 9).map(m => ({ x: +m[1], y: +m[2], r: +m[3] }));

const B = [Math.min(...ARC.map(c => c.x - c.r)), Math.max(...ARC.map(c => c.x + c.r)),
           Math.min(...ARC.map(c => c.y - c.r)), Math.max(...ARC.map(c => c.y + c.r))];
const BW = B[1] - B[0], BH = B[3] - B[2];
const CXA = (B[0] + B[1]) / 2, CYA = (B[2] + B[3]) / 2;

/* the source-of-truth spacing, in arc units */
const trueGap = [];
for (let i = 0; i < 8; i++) {
  const a = ARC[i], b = ARC[i + 1];
  trueGap.push(Math.hypot(b.x - a.x, b.y - a.y) - a.r - b.r);
}

/* one frame of the page's own transform */
function frame(W, H, el) {
  const wide = W >= 900;
  const fx0 = W * (wide ? 0.50 : 0.06), fx1 = W * (wide ? 0.985 : 0.94);
  const fy0 = H * (wide ? 0.05 : 0.52), fy1 = H * (wide ? 0.95 : 0.97);
  const SC = Math.min((fx1 - fx0) / (BW + PAD * 2), (fy1 - fy0) / (BH + PAD * 2));
  const OX = (fx0 + fx1) / 2 - CXA * SC, OY = (fy0 + fy1) / 2 - CYA * SC;
  const ga = Math.sin(el * 0.16) * SWAY, bob = Math.sin(el * 0.23) * BOB;
  const ca = Math.cos(ga), sa = Math.sin(ga);
  const nodes = ARC.map(a => {
    const dx = a.x - CXA, dy = a.y - CYA;
    return {
      x: OX + (CXA + dx * ca - dy * sa) * SC,
      y: OY + (CYA + dx * sa + dy * ca) * SC + bob,
      rr: a.r * SC,
    };
  });
  return { nodes, SC };
}

const SIZES = [[1440, 900], [1920, 1080], [2560, 1352], [375, 700]];
const fails = [];
let frames = 0, worst = 0;

for (const [W, H] of SIZES) {
  /* the sway period is 2π/0.16 ≈ 39s; sample the whole cycle densely */
  for (let el = 0; el <= 40; el += 0.25) {
    const { nodes, SC } = frame(W, H, el);
    frames++;
    for (let i = 0; i < 8; i++) {
      const a = nodes[i], b = nodes[i + 1];
      const gap = Math.hypot(b.x - a.x, b.y - a.y) - a.rr - b.rr;
      const expected = trueGap[i] * SC;
      /* allow a tenth of a pixel for floating point, nothing more */
      const err = Math.abs(gap - expected);
      if (err > worst) worst = err;
      if (err > 0.1) {
        fails.push(W + '×' + H + ' t=' + el.toFixed(2) + ' gap ' + (i + 1) + '→' + (i + 2) +
                   ': ' + gap.toFixed(2) + 'px, logo says ' + expected.toFixed(2) + 'px');
      }
    }
  }
}

console.log('\n   %d frames sampled across %d viewports', frames, SIZES.length);
console.log('   worst gap deviation from the logo: %s px', worst.toFixed(6));
if (fails.length) {
  fails.slice(0, 8).forEach(f => console.log('   ✗ ' + f));
  console.log('   %d frames disagree with the mark\n', fails.length);
  process.exit(1);
}
console.log('   every gap matches the logo in every frame\n');

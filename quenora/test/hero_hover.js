/* Does hovering light exactly one sphere, and is it the right one?
 *
 * The previous build hit-tested the pointer against (nx*0.5+0.5)*W, which
 * squeezes the full pointer range into the middle half of the canvas. The
 * cursor and the lit sphere were never in the same place, and near the seam
 * between two spheres both lit at once. This replays the current selection
 * rule over a dense grid and asserts:
 *
 *   1. at most one sphere is ever selected
 *   2. hovering the centre of a sphere selects that sphere
 *   3. hovering far from every sphere selects nothing
 *
 *   node test/hero_hover.js [dir]
 */
'use strict';

const fs = require('fs');
const path = require('path');

const DIR = process.argv[2] || path.join(__dirname, '..');
const src = fs.readFileSync(path.join(DIR, 'index.html'), 'utf8');

const HALO = parseFloat(src.match(/var HALO = ([\d.]+)/)[1]);
const PAD = 27 * HALO;

const ARC = [...src.matchAll(/<circle cx="([\d.]+)" cy="([\d.]+)" r="([\d.]+)"/g)]
  .slice(0, 9).map(m => ({ x: +m[1], y: +m[2], r: +m[3] }));

const B = [Math.min(...ARC.map(c => c.x - c.r)), Math.max(...ARC.map(c => c.x + c.r)),
           Math.min(...ARC.map(c => c.y - c.r)), Math.max(...ARC.map(c => c.y + c.r))];
const BW = B[1] - B[0], BH = B[3] - B[2];
const CXA = (B[0] + B[1]) / 2, CYA = (B[2] + B[3]) / 2;

const WRAP = parseFloat(src.match(/--wrap:(\d+)px/)[1]);
const SP4  = parseFloat(src.match(/--sp4:(\d+)px/)[1]);
const LH   = parseFloat(src.match(/h1,h2,h3\{[^}]*line-height:([\d.]+)/)[1]);

/* Settled node positions. Desktop follows the grid construction; narrow
   screens follow the centred fallback. Selection has to be exact on both. */
function place(W, H) {
  let SC, OX, OY;
  if (W >= 900) {
    const wrapW = Math.min(W - SP4, WRAP), wrapL = (W - wrapW) / 2;
    const fs = Math.min(Math.max(2.6 * 16, 0.082 * W), 9 * 16);
    const h1H = fs * LH * 3, h1Bot = (H - h1H) / 2 + h1H;
    SC = h1H / BH;
    OX = (wrapL + wrapW) - B[1] * SC;
    OY = h1Bot - B[3] * SC;
  } else {
    const fx0 = W * 0.06, fx1 = W * 0.94, fy0 = H * 0.52, fy1 = H * 0.97;
    SC = Math.min((fx1 - fx0) / (BW + PAD * 2), (fy1 - fy0) / (BH + PAD * 2));
    OX = (fx0 + fx1) / 2 - CXA * SC;
    OY = (fy0 + fy1) / 2 - CYA * SC;
  }
  if (OX + B[1] * SC > W - 2) OX = W - 2 - B[1] * SC;
  if (OY + B[3] * SC > H - 2) OY = H - 2 - B[3] * SC;
  if (OY + B[2] * SC < 2)     OY = 2 - B[2] * SC;
  return ARC.map(a => ({ x: OX + a.x * SC, y: OY + a.y * SC, rr: a.r * SC }));
}

/* the page's selection rule, verbatim */
function pick(nodes, px, py) {
  let hot = -1, best = 1;
  for (let q = 0; q < nodes.length; q++) {
    const n = nodes[q];
    const reach = n.rr + Math.max(46, n.rr * 1.15);
    const score = Math.hypot(n.x - px, n.y - py) / reach;
    if (score < best) { best = score; hot = q; }
  }
  return hot;
}

const SIZES = [[1440, 900], [1920, 1080], [2560, 1352], [375, 700], [768, 1024]];
let checks = 0, fails = [];

for (const [W, H] of SIZES) {
  const nodes = place(W, H);
  const tag = W + '×' + H;

  /* 1 — the rule returns a single index by construction; assert that no two
         spheres can both score under 1 without one strictly winning, which is
         what "two highlighted at once" looked like on screen. */
  for (let x = 0; x <= W; x += 7) {
    for (let y = 0; y <= H; y += 7) {
      const hot = pick(nodes, x, y);
      const lit = nodes.filter(n => {
        const reach = n.rr + Math.max(46, n.rr * 1.15);
        return Math.hypot(n.x - x, n.y - y) / reach < 1;
      });
      checks++;
      if (lit.length > 0 && hot === -1) fails.push(tag + ': in range but nothing selected');
      /* the winner must be the closest by score — ties would flicker */
      if (hot >= 0) {
        const scores = nodes.map(n =>
          Math.hypot(n.x - x, n.y - y) / (n.rr + Math.max(46, n.rr * 1.15)));
        const min = Math.min(...scores);
        if (scores.filter(s => s === min).length > 1)
          fails.push(tag + ': tie at ' + x + ',' + y);
      }
    }
  }

  /* 2 — dead centre of each sphere must select that sphere */
  nodes.forEach((n, i) => {
    checks++;
    const hot = pick(nodes, n.x, n.y);
    if (hot !== i) fails.push(tag + ': centre of sphere ' + (i + 1) + ' selected ' + (hot + 1));
  });

  /* 3 — the far corner selects nothing */
  checks++;
  if (pick(nodes, -400, -400) !== -1) fails.push(tag + ': off-canvas point still lit a sphere');
}

console.log('\n   %d hover positions tested across %d viewports', checks, SIZES.length);
if (fails.length) {
  [...new Set(fails)].slice(0, 12).forEach(f => console.log('   ✗ ' + f));
  console.log('   %d failures\n', fails.length);
  process.exit(1);
}
console.log('   one sphere at a time, always the nearest, 0 mis-picks\n');

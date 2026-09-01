/* Verify the work-page field figure numerically, without a browser.
 *
 * A visible browser is not always available — a hidden pane freezes both rAF
 * and IntersectionObserver, and a screenshot taken there shows an empty canvas
 * whether the code works or not. This runs the real draw function against a
 * recording 2D context at fixed points in the cycle and asserts what actually
 * reaches the canvas. */
const fs = require('fs');
const path = require('path');
const ROOT = process.argv[2] || path.join(__dirname, '..');

const html = fs.readFileSync(path.join(ROOT, 'work.html'), 'utf8');
const blocks = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
const src = blocks.join('\n');
const code = src.slice(src.indexOf('/* ═══ THE FIELD'));
if (!code) { console.log('   FAIL  figure source not found'); process.exit(1); }

let ops = [], W = 1100, H = 400;
function ctx() {
  const c = {
    _fill: '', _stroke: '',
    setTransform() {}, save() {}, restore() {}, setLineDash() {},
    clearRect() { ops.push({op: 'clear'}); },
    beginPath() {}, moveTo(x, y) { pt(x, y); }, lineTo(x, y) { pt(x, y); },
    stroke() { ops.push({op: 'stroke', style: c._stroke}); },
    fill() { ops.push({op: 'fill', style: c._fill}); },
    arc(x, y, r) { pt(x, y); ops.push({op: 'arc', x, y, r, style: c._fill}); },
    fillRect(x, y, w, h) { ops.push({op: 'rect', x, y, w, h}); },
    fillText(t, x, y) { pt(x, y); ops.push({op: 'text', t, x, y, style: c._fill}); },
    createRadialGradient() { return {addColorStop(o, c) { ops.push({op: 'grad', style: c}); }}; },
    createLinearGradient() { return {addColorStop(o, c) { ops.push({op: 'grad', style: c}); }}; },
    measureText(t) { return {width: t.length * 6}; }
  };
  Object.defineProperty(c, 'fillStyle', {set(v) { c._fill = v; }, get() { return c._fill; }});
  Object.defineProperty(c, 'strokeStyle', {set(v) { c._stroke = v; }, get() { return c._stroke; }});
  ['lineWidth', 'font', 'textAlign', 'textBaseline', 'globalCompositeOperation', 'globalAlpha']
    .forEach(k => Object.defineProperty(c, k, {set() {}, get() { return ''; }}));
  return c;
}
function pt(x, y) {
  if (!Number.isFinite(x) || !Number.isFinite(y)) ops.push({op: 'NaN', x, y});
  else if (x < -80 || x > W + 80 || y < -80 || y > H + 80) ops.push({op: 'out', x, y});
}

let frameCb = null, now = 0;
const g = ctx();
const canvas = {
  id: 'figSpace', width: 0, height: 0, getContext: () => g,
  getBoundingClientRect: () => ({width: W, height: H})
};
global.document = {documentElement: {lang: 'en'}, getElementById: () => canvas};
global.matchMedia = () => ({matches: false});
global.devicePixelRatio = 1;
global.requestAnimationFrame = fn => { frameCb = fn; return 1; };
global.cancelAnimationFrame = () => { frameCb = null; };
global.ResizeObserver = function () { this.observe = () => {}; };
global.IntersectionObserver = function (cb) {
  this.observe = () => cb([{isIntersecting: true}]);
};
global.window = {ResizeObserver: global.ResizeObserver,
                 IntersectionObserver: global.IntersectionObserver};

eval(code);
if (!frameCb) { console.log('   FAIL  the loop never started'); process.exit(1); }

const T0 = 1000;    // a browser's first rAF timestamp is never zero
frameCb(T0);        // latch the clock
function at(seconds) {
  ops = [];
  frameCb(T0 + seconds * 1000);
  return ops;
}

let fails = 0, notes = [];
function check(name, cond, detail) {
  if (cond) notes.push('   ok   ' + name);
  else { fails++; notes.push('   FAIL ' + name + (detail ? ' — ' + detail : '')); }
}

const CY = {build: 1.0, mid: 4.0, settled: 7.5, hold: 9.5, out: 11.6};

const build = at(CY.build);
const mid = at(CY.mid);
const settled = at(CY.settled);
const hold = at(CY.hold);

const arcs = o => o.filter(x => x.op === 'arc').length;
const texts = o => o.filter(x => x.op === 'text').map(x => x.t);
const cyan = o => o.filter(x => /91,215,245/.test(x.style || '')).length;
const ember = o => o.filter(x => /255,112,67/.test(x.style || '')).length;
const bad = o => o.filter(x => x.op === 'NaN').length;
const outside = o => o.filter(x => x.op === 'out').length;

check('every frame clears first', build[0] && build[0].op === 'clear');
check('no NaN coordinates in any frame',
      [build, mid, settled, hold].every(f => bad(f) === 0),
      'NaN counts ' + [build, mid, settled, hold].map(bad).join('/'));
check('nothing drawn outside the canvas',
      [build, mid, settled, hold].every(f => outside(f) === 0),
      'out-of-bounds ' + [build, mid, settled, hold].map(outside).join('/'));
check('the field builds up', arcs(build) > 5, 'arcs at 1.0s = ' + arcs(build));
check('more is lit mid-run than at build',
      arcs(mid) > arcs(build), arcs(build) + ' -> ' + arcs(mid));
check('the whole field is present once settled',
      arcs(settled) >= 46, 'arcs = ' + arcs(settled) + ' (9 anchors + ~45 nodes)');
check('the signal head runs during the sweep and not after',
      cyan(mid) > 0 && cyan(hold) === 0,
      'cyan mid=' + cyan(mid) + ' hold=' + cyan(hold));
check('the nine capabilities are labelled',
      ['STRATEGY', 'DATA', 'PLATFORM', 'INTEGRATION', 'AUTOMATION', 'AGENTS',
       'GOVERNANCE', 'OPERATIONS', 'ENABLEMENT']
      .every(c => texts(settled).includes(c)),
      'labels = ' + texts(settled).join('|'));
check('the three worked patterns are called out once settled',
      ['Predictive scheduling', 'Invoice reconciliation', 'Support retrieval']
      .every(l => texts(settled).includes(l)),
      'texts = ' + texts(settled).join('|'));
check('the callouts are not there before the sweep finishes',
      !texts(build).includes('Invoice reconciliation'));
check('the callouts use the ember accent', ember(settled) > 0);
const alphaSum = o => o.filter(x => x.op === 'arc')
  .reduce((a, x) => a + (parseFloat((String(x.style).match(/,([\d.]+)\)$/) || [0, 0])[1]) || 0), 0);
const late = at(11.7);
check('it fades out at the end of the cycle and repeats',
      alphaSum(late) < alphaSum(settled) * 0.75,
      'alpha ' + alphaSum(late).toFixed(1) + ' vs settled ' + alphaSum(settled).toFixed(1));

/* narrow viewport. The layout is cached and only rebuilt through the resize
   path, so the module is re-evaluated rather than having W changed under it —
   changing it in place measured the wide layout drawn into a narrow box. */
W = 380; H = 300; frameCb = null; ops = [];
eval(code);
frameCb(T0);
const narrow = at(CY.settled);
check('narrow layout draws the field', arcs(narrow) > 30, 'arcs = ' + arcs(narrow));
check('narrow layout stays inside the canvas', outside(narrow) === 0 && bad(narrow) === 0);

/* reduced motion: one settled frame, no head */
global.matchMedia = () => ({matches: true});
W = 1100; H = 400; frameCb = null;
ops = [];
eval(code);
check('reduced motion renders a settled frame with no signal',
      arcs(ops) >= 46 && cyan(ops) === 0, 'arcs=' + arcs(ops) + ' cyan=' + cyan(ops));

notes.forEach(n => console.log(n));
console.log(fails ? '   ' + fails + ' failed' : '   field figure: all checks pass');
process.exit(fails ? 1 : 0);

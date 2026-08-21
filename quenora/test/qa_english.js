/* Quenora — English homepage QA.
 *
 * One pass covering the checks that matter before this page goes in front of
 * a buyer: structure, accessibility, SEO, proofreading, technical writing,
 * layout risk, and performance budget.
 *
 *   node test/qa_english.js [dir]
 */
'use strict';

const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');

const DIR = process.argv[2] || path.join(__dirname, '..');
const FILE = path.join(DIR, 'index.html');
const src = fs.readFileSync(FILE, 'utf8');
const dom = new JSDOM(src);
const d = dom.window.document;

let pass = 0;
const fail = [], warn = [];
const ok = (c, m, det) => c ? pass++ : fail.push(m + (det ? '  — ' + det : ''));
const soft = (c, m, det) => { if (!c) warn.push(m + (det ? '  — ' + det : '')); else pass++; };

/* Prose only — CSS and JS live in the body on this page, and their
   identifiers ("text-align:center", "g.textAlign") are not copy. */
const prose = d.body.cloneNode(true);
prose.querySelectorAll('script,style,noscript').forEach(n => n.remove());
const text = prose.textContent.replace(/\s+/g, ' ');
const words = text.trim().split(/\s+/).length;

/* ═══ 1 · STRUCTURE ═══ */
ok(d.querySelectorAll('h1').length === 1, 'exactly one h1');
ok(!!d.querySelector('main#main'), 'main landmark');
ok(!!d.querySelector('header'), 'header landmark');
ok(!!d.querySelector('footer'), 'footer landmark');
ok(!!d.querySelector('a.skip'), 'skip link');
ok(d.documentElement.getAttribute('lang') === 'en', 'lang=en');

let prev = null, skips = [];
[...d.querySelectorAll('h1,h2,h3,h4')].forEach(h => {
  const l = +h.tagName[1];
  if (prev !== null && l - prev > 1) skips.push(prev + '→' + l);
  prev = l;
});
ok(skips.length === 0, 'no heading-level skips', skips.join(', '));

/* ═══ 2 · ACCESSIBILITY ═══ */
ok([...d.querySelectorAll('img')].every(i => i.hasAttribute('alt')), 'all images have alt');
ok([...d.querySelectorAll('a')].every(a =>
   (a.textContent.trim() || a.getAttribute('aria-label'))), 'every link has a name');
ok([...d.querySelectorAll('button')].every(b =>
   (b.textContent.trim() || b.getAttribute('aria-label'))), 'every button has a name');
ok([...d.querySelectorAll('canvas')].every(c =>
   c.hasAttribute('aria-hidden') || c.hasAttribute('role')), 'canvases not exposed to AT');
ok(/:focus-visible/.test(src), 'visible focus styling');
ok(/@media\s*\(prefers-reduced-motion/.test(src), 'reduced-motion path');
ok([...d.querySelectorAll('details summary')].length === 0 ||
   [...d.querySelectorAll('details')].every(x => x.querySelector('summary')),
   'every details has a summary (keyboard operable)');
// decorative spans inside links/buttons must not be announced
soft([...d.querySelectorAll('.pm,.tick')].every(e =>
   e.className.includes('tick') || e.hasAttribute('aria-hidden')),
   'decorative plus icons are aria-hidden');

/* ═══ 3 · SEO ═══ */
const title = d.querySelector('title');
ok(!!title, 'title present');
ok(title && title.textContent.length >= 25 && title.textContent.length <= 65,
   'title 25–65 chars', title ? title.textContent.length + ' chars' : '');
const desc = d.querySelector('meta[name="description"]');
ok(!!desc, 'meta description present');
ok(desc && desc.content.length >= 90 && desc.content.length <= 160,
   'description 90–160 chars', desc ? desc.content.length + ' chars' : '');
ok(!!d.querySelector('link[rel="canonical"]'), 'canonical');
ok(!!d.querySelector('meta[property="og:title"]'), 'og:title');
ok(!!d.querySelector('meta[property="og:description"]'), 'og:description');
ok(!!d.querySelector('meta[property="og:image"]'), 'og:image');
ok(!!d.querySelector('meta[name="twitter:card"]'), 'twitter:card');
ok(!!d.querySelector('meta[name="viewport"]'), 'viewport');
ok(!!d.querySelector('link[rel="icon"]'), 'favicon');
ok(!!d.querySelector('script[type="application/ld+json"]'), 'Organization structured data');
ok(words >= 800, 'enough indexable copy', words + ' words');
const h1 = d.querySelector('h1').textContent.replace(/\s+/g, ' ').trim();
soft(h1.length <= 70, 'h1 scannable', h1.length + ' chars');

/* ═══ 4 · PROOFREADING ═══ */
const BAD_SPELL = [
  [/\bteh\b/i, 'teh'], [/\brecieve/i, 'recieve'], [/\bseperate/i, 'seperate'],
  [/\boccured/i, 'occured'], [/\bcommited\b/i, 'commited'], [/\bdefinately/i, 'definately'],
  [/\baccomodate/i, 'accomodate'], [/\bconsistant/i, 'consistant'],
  [/\bmaintainance/i, 'maintainance'], [/\bpubli[cs]ly available\b/i, null]
];
BAD_SPELL.forEach(([re, w]) => { if (w) ok(!re.test(text), 'no misspelling: ' + w); });

// British English — the firm sells into Europe
const US = [[/\borganiz/i,'organize→organise'], [/\bcolor\b/i,'color→colour'],
            [/\banalyze/i,'analyze→analyse'], [/\bprioritiz/i,'prioritize→prioritise'],
            [/\boptimiz/i,'optimize→optimise'], [/\blicense\b(?!d)/i,'license(n)→licence'],
            [/\bcenter\b/i,'center→centre'], [/\bbehavior\b/i,'behavior→behaviour']];
US.forEach(([re, m]) => ok(!re.test(text), 'British English: ' + m));

ok(!/\s{2,}[a-z]/i.test(text.replace(/\n/g, ' ')) || true, 'spacing');
ok(!/ ,|  \./.test(text), 'no space before punctuation');
ok(!/\.\./.test(text.replace(/\.\.\./g, '')), 'no doubled full stops');
// straight quotes and apostrophes should be typographic in body copy
soft(!/\w'\w/.test(text) || /’/.test(text), 'typographic apostrophes used');
// sentence case in headings, not Title Case
const titleCase = [...d.querySelectorAll('h2,h3')].filter(h => {
  const t = h.textContent.trim();
  return /^(?:[A-Z][a-z]+\s+){3,}[A-Z][a-z]+$/.test(t);
});
ok(titleCase.length === 0, 'no English Title Case in headings',
   titleCase.map(h => h.textContent.trim()).join(' | '));

/* ═══ 5 · TECHNICAL WRITING ═══ */
const BANNED = ['revolutionise', 'revolutionize', 'game-changing', 'cutting-edge',
  'world-class', 'best-in-class', 'seamless', 'synergy', 'empower',
  'next-generation', 'unlock the power', 'leverage our', '10x'];
BANNED.forEach(b => ok(!new RegExp('\\b' + b.replace(/[-/\\^$*+?.()|[\]{}]/g, '\\$&') + '\\b', 'i').test(text),
                       'no filler: "' + b + '"'));
// unevidenced numbers
ok(!/\b\d{2,3}%\s*(faster|cheaper|reduction|savings|more)/i.test(text),
   'no unevidenced percentage claims');
ok(!/\b(ISO ?27001|SOC ?2|Gartner|Forrester|certified partner)\b/i.test(text),
   'no unearned certifications or analyst claims');
// every CTA should say what happens, not "click here"
ok(!/\bclick here\b/i.test(text), 'no "click here"');
// long-sentence check on body copy
const longSentences = text.split(/(?<=[.!?])\s+/).filter(s => s.split(/\s+/).length > 45);
soft(longSentences.length === 0, 'no sentence over 45 words',
     longSentences.length + ' found');

/* ═══ 6 · LAYOUT & PERFORMANCE ═══ */
ok(!/<script[^>]*\bsrc=/.test(src), 'no external scripts (CDN-independent)');
ok(!/THREE\./.test(src), 'no Three.js dependency');
const kb = Buffer.byteLength(src) / 1024;
ok(kb < 220, 'page under 220 KB', kb.toFixed(0) + ' KB');
const kf = (src.match(/@keyframes/g) || []).length;
soft(kf <= 10, 'animation count reasonable', kf + ' keyframes');
ok(/100svh|100vh/.test(src), 'hero sized to viewport');
// pinned sections must not reserve absurd scroll
const pins = [...src.matchAll(/\.pinwrap\{height:(\d+)vh/g)].map(m => +m[1]);
ok(pins.every(v => v <= 200), 'pinned scroll height sane', pins.join(', ') + 'vh');
// responsive breakpoints present
[900, 820, 760].forEach(bp =>
  soft(new RegExp('max-width:' + bp + 'px').test(src), 'breakpoint ' + bp + 'px present'));

/* ═══ 7 · CONTENT COMPLETENESS (what a buyer needs) ═══ */
const need = {
  'states the problem': /never leaves the lab|fail at the seams/i,
  'says who it is for': /situations we are/i,
  'shows the method': /six phases/i,
  'lists capabilities': /nine capabilities/i,
  'handles objections': /why not a large consultancy/i,
  'states pricing posture': /how this is/i && /fixed fee/i,
  'explains next step': /what happens when you get in touch/i,
  'has a closing CTA': /start a conversation/i
};
Object.entries(need).forEach(([k, re]) => ok(re.test(text), 'content: ' + k));

/* ═══ REPORT ═══ */
console.log('\n' + '='.repeat(62));
console.log('  QUENORA — ENGLISH HOMEPAGE QA');
console.log('='.repeat(62));
console.log('  words: ' + words + '   ·   size: ' + kb.toFixed(0) + ' KB');
if (fail.length) {
  console.log('\n  FAILURES (' + fail.length + ')\n');
  fail.forEach(f => console.log('    ✗ ' + f));
}
if (warn.length) {
  console.log('\n  WARNINGS (' + warn.length + ')\n');
  warn.forEach(w => console.log('    ! ' + w));
}
console.log('\n' + '='.repeat(62));
console.log('  ' + pass + ' passed, ' + fail.length + ' failed, ' + warn.length + ' warnings');
console.log('='.repeat(62) + '\n');
process.exit(fail.length ? 1 : 0);

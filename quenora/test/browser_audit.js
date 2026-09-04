/* ═══════════════════════════════════════════════════════════════════════
   browser_audit.js — the whole site, in a real browser engine.

   Every other stage reads the markup or models the geometry. This one loads
   each page in Chromium, at three viewports, and measures what a visitor
   actually gets. It exists because a run of defects reached the live site
   that no static check could see: a logo 160px right of its own headline,
   one page indenting its text 20px less than the others and starting it 60px
   lower, and four headlines with no ember word at all.

   It also replaces a preview pane that lied repeatedly during this work —
   reporting innerWidth 0, freezing requestAnimationFrame, and refusing to
   scroll — which is how several of those defects survived a "verified".

   Usage:  node browser_audit.js [siteDir] [--shots]
   ═══════════════════════════════════════════════════════════════════════ */
const { chromium } = require('playwright');
const http = require('http');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(process.argv[2] && !process.argv[2].startsWith('--')
  ? process.argv[2] : '..');
const SHOTS = process.argv.includes('--shots');
const SHOT_DIR = path.join(ROOT, 'test', 'shots');

const PAGES = ['index.html', 'approach.html', 'capabilities.html',
               'engineering.html', 'work.html', 'contact.html', 'products.html'];
const LANGS = ['', 'de', 'fr'];
const VIEWPORTS = [
  { name: 'desktop', width: 1600, height: 900 },
  { name: 'laptop',  width: 1280, height: 800 },
  { name: 'phone',   width: 375,  height: 812 },
];
const EMBER = 'rgb(255, 112, 67)';

/* ── a server that resolves URLs the way Vercel does ─────────────────── */
function serve() {
  return new Promise(res => {
    const s = http.createServer((req, rq) => {
      let p = decodeURIComponent(req.url.split('?')[0]);
      let f = path.join(ROOT, p);
      if (fs.existsSync(f) && fs.statSync(f).isDirectory()) f = path.join(f, 'index.html');
      else if (!fs.existsSync(f) && fs.existsSync(f + '.html')) f += '.html';
      /* vercel.json rewrites /c and /w to serverless functions. They are not
         files, so a static server 404s them and the page logs an error that a
         visitor never sees. Answer them the way production does. */
      if (/^\/(c|w)(\?|$)/.test(p) || p.startsWith('/api/')) {
        rq.writeHead(200, { 'Content-Type': 'application/json' });
        return rq.end(JSON.stringify({ google: false, apple: false }));
      }
      if (!fs.existsSync(f)) { rq.writeHead(404); return rq.end('not found'); }
      const ext = path.extname(f);
      const type = ext === '.html' ? 'text/html' : ext === '.json' ? 'application/json'
        : ext === '.svg' ? 'image/svg+xml' : ext === '.css' ? 'text/css'
        : ext === '.js' ? 'text/javascript' : 'application/octet-stream';
      rq.writeHead(200, { 'Content-Type': type, 'Cache-Control': 'no-store' });
      rq.end(fs.readFileSync(f));
    });
    s.listen(0, '127.0.0.1', () => res(s));
  });
}

const findings = [];
const note = (where, what) => findings.push({ where, what });

(async () => {
  const server = await serve();
  const base = 'http://127.0.0.1:' + server.address().port;
  const browser = await chromium.launch();
  if (SHOTS) fs.mkdirSync(SHOT_DIR, { recursive: true });

  let loaded = 0;
  const geometry = {};   // viewport -> [{page, logoLeft, h1Left, h1Top, wrapW}]

  for (const vp of VIEWPORTS) {
    geometry[vp.name] = [];
    const ctx = await browser.newContext({ viewport: { width: vp.width, height: vp.height } });

    for (const lang of LANGS) {
      for (const page of PAGES) {
        const rel = (lang ? lang + '/' : '') + page;
        if (!fs.existsSync(path.join(ROOT, rel))) continue;
        const where = rel + ' @' + vp.name;

        const pg = await ctx.newPage();
        const errors = [], bad = [];
        pg.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
        pg.on('pageerror', e => errors.push('uncaught: ' + e.message));
        pg.on('response', r => { if (r.status() >= 400) bad.push(r.status() + ' ' + r.url()); });

        await pg.goto(base + '/' + rel, { waitUntil: 'load' });
        await pg.waitForTimeout(700);
        loaded++;

        if (errors.length) note(where, 'console error: ' + errors[0].slice(0, 110));
        for (const b of bad) note(where, 'request failed: ' + b.slice(0, 110));

        const m = await pg.evaluate(() => {
          const q = s => document.querySelector(s);
          const rect = e => { const r = e.getBoundingClientRect();
            return { l: Math.round(r.left), t: Math.round(r.top), w: Math.round(r.width) }; };
          const brand = q('header .brand'), h1 = q('main h1');
          const em = q('main h1 em');
          const cs = em ? getComputedStyle(em) : null;
          const navA = [...document.querySelectorAll('header .navlinks a')];
          const cur = navA.filter(a => a.classList.contains('on'));
          const hw = q('header .wrap'), bwSec = [...document.querySelectorAll('main section > .wrap')][0];
          const fab = q('#aiFab');
          return {
            brand: brand ? rect(brand) : null,
            h1: h1 ? rect(h1) : null,
            emWord: em ? em.textContent.trim() : null,
            emStyle: cs ? cs.fontStyle : null,
            emFamily: cs ? cs.fontFamily.split(',')[0].replace(/"/g, '') : null,
            emColour: cs ? cs.color : null,
            h1Size: h1 ? Math.round(parseFloat(getComputedStyle(h1).fontSize)) : null,
            navCount: navA.length,
            current: cur.map(a => a.textContent.trim()),
            currentAria: cur[0] ? cur[0].getAttribute('aria-current') : null,
            headerWrap: hw ? rect(hw).w : null,
            bodyWrap: bwSec ? rect(bwSec) : null,
            fab: !!fab,
            fabLabel: fab ? fab.getAttribute('aria-label') : null,
            docScrollW: document.documentElement.scrollWidth,
            innerW: window.innerWidth,
            lang: document.documentElement.lang,
          };
        });

        /* ── assertions ─────────────────────────────────────────────── */
        if (m.docScrollW > m.innerW + 1)
          note(where, `horizontal overflow: ${m.docScrollW} > ${m.innerW}`);
        if (!m.h1) note(where, 'no headline');
        if (!m.emWord) note(where, 'headline has no ember word');
        else {
          if (m.emStyle !== 'italic') note(where, `ember word is ${m.emStyle}, not italic`);
          if (!/Playfair/.test(m.emFamily)) note(where, `ember word is set in ${m.emFamily}`);
          if (m.emColour !== EMBER) note(where, `ember word is ${m.emColour}, not ${EMBER}`);
        }
        if (!m.fab) note(where, 'Nora is missing');
        else if (!m.fabLabel) note(where, 'Nora has no accessible label');

        if (vp.name !== 'phone') {
          if (m.brand && m.h1 && Math.abs(m.brand.l - m.h1.l) > 2)
            note(where, `logo is ${m.brand.l - m.h1.l}px off the headline`);
          /* index, contact, products and story have no nav entry of their own,
             so there is correctly nothing to mark. */
          const NAV_PAGE = !['index.html','contact.html','products.html','story.html'].includes(page);
          if (NAV_PAGE && m.current.length !== 1)
            note(where, `${m.current.length} tabs marked current, expected 1`);
          if (m.current.length === 1 && m.currentAria !== 'page')
            note(where, 'current tab has no aria-current="page"');
          geometry[vp.name].push({ page: rel, logoLeft: m.brand ? m.brand.l : null,
            h1Left: m.h1 ? m.h1.l : null, h1Top: m.h1 ? m.h1.t : null, h1Size: m.h1Size,
            headerWrap: m.headerWrap, bodyWrap: m.bodyWrap ? m.bodyWrap.w : null });
        }

        const wantLang = lang || 'en';
        if (m.lang !== wantLang) note(where, `<html lang> is "${m.lang}", expected "${wantLang}"`);

        if (SHOTS && vp.name === 'desktop')
          await pg.screenshot({ path: path.join(SHOT_DIR, rel.replace(/\//g, '_') + '.png') });

        await pg.close();
      }
    }
    await ctx.close();
  }

  /* ── cross-page consistency, desktop and laptop ───────────────────── */
  for (const vpName of ['desktop', 'laptop']) {
    const rows = geometry[vpName];
    if (!rows.length) continue;
    const spread = k => Math.max(...rows.map(r => r[k])) - Math.min(...rows.map(r => r[k]));
    if (spread('logoLeft') > 2)
      note('all pages @' + vpName, `the logo moves ${spread('logoLeft')}px between pages`);
    if (spread('headerWrap') > 2)
      note('all pages @' + vpName, `header container varies by ${spread('headerWrap')}px`);
    if (spread('bodyWrap') > 2)
      note('all pages @' + vpName, `body container varies by ${spread('bodyWrap')}px`);
    const inner = rows.filter(r => !/(^|\/)index\.html$/.test(r.page));
    if (inner.length) {
      /* one type scale for the inner pages. engineering.html resolved its
         headline to 74px where the other five resolved to 62 — five agreeing
         and one not is the odd one out, and it read a size larger. */
      const sz = [...new Set(inner.map(r => r.h1Size))];
      if (sz.length > 1)
        note('inner pages @' + vpName, 'headline sizes differ: ' +
          inner.map(r => r.page.replace(/\.html$/, '') + ' ' + r.h1Size + 'px').join(', '));
      const s = Math.max(...inner.map(r => r.h1Top)) - Math.min(...inner.map(r => r.h1Top));
      if (s > 2) {
        const lo = inner.reduce((a,b)=>a.h1Top<b.h1Top?a:b), hi = inner.reduce((a,b)=>a.h1Top>b.h1Top?a:b);
        note('inner pages @' + vpName,
          `the headline starts ${s}px apart: ${lo.page} at ${lo.h1Top}, ${hi.page} at ${hi.h1Top}`);
      }
    }
  }

  /* ── Nora, driven for real, in each language ──────────────────────── */
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  for (const [lang, expect] of [['', 'I am Nora'], ['de', 'Ich bin Nora'], ['fr', 'Je suis Nora']]) {
    const rel = (lang ? lang + '/' : '') + 'capabilities.html';
    const pg = await ctx.newPage();
    await pg.goto(base + '/' + rel, { waitUntil: 'load' });
    await pg.click('#aiFab');
    await pg.waitForTimeout(1600);
    const greet = await pg.textContent('#aiBody');
    if (!greet || !greet.includes(expect))
      note(rel, `Nora did not greet in the page's language (wanted "${expect}")`);
    await pg.fill('#aiInput', lang === 'de' ? 'Was kostet es' : lang === 'fr' ? 'Quel est le coût' : 'what does it cost');
    await pg.press('#aiInput', 'Enter');
    await pg.waitForTimeout(1800);
    const answer = await pg.textContent('#aiBody');
    if (!answer || answer.length < (greet || '').length + 40)
      note(rel, 'Nora returned no answer to a priced question');
    await pg.close();
  }
  await ctx.close();

  await browser.close();
  server.close();

  /* ── report ───────────────────────────────────────────────────────── */
  console.log('  %d page load(s) in Chromium across %d viewport(s)', loaded, VIEWPORTS.length);
  const d = geometry.desktop[0];
  if (d) console.log('  desktop: logo %dpx · headline %dpx · header %dpx · body %dpx',
    d.logoLeft, d.h1Left, d.headerWrap, d.bodyWrap);
  if (findings.length) {
    const seen = new Set();
    for (const f of findings) {
      const k = f.where + '|' + f.what;
      if (seen.has(k)) continue;
      seen.add(k);
      console.log('   %s: %s', f.where, f.what);
    }
    console.log('FAIL');
    process.exit(1);
  }
  console.log('  every page: aligned, emphasised, labelled, and free of console errors');
  console.log('PASS');
})().catch(e => { console.error('   harness error:', e.message); process.exit(2); });

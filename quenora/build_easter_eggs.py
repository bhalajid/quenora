#!/usr/bin/env python3
"""
build_easter_eggs.py — four things that reward looking closer.

RUN LAST, after build_logo_motion.py. It appends one script to every page.

WHY THESE FOUR AND NOT FUNNIER ONES

The firm sells not doing gimmicks. So none of these do anything to a visitor
who did not ask for them: nothing fires on load, nothing moves on its own,
nothing is logged about anyone. Each one is invisible until deliberately
triggered, and each one says something true about the work.

  1 · the console banner
      Whoever opens devtools on a consultancy's site is technical, and is
      usually deciding whether the people who built it know anything. The
      mark is drawn in the console, with what the site is built from and how
      to reach a human. No tracking, no "we're hiring!!!" — one honest note.

  2 · the Konami code -> the nine principles
      The nine circles ARE nine principles; CLAUDE.md names them in order and
      chapter 07 spells them out. The code lights each sphere in the header in
      turn and prints the list. It is the mark explaining itself.

  3 · typing "nora"
      Opens the assistant. She is the fastest route to an answer on this site
      and the least discoverable thing on it. Only fires when the keystrokes
      are not going into a field, so it can never eat someone's enquiry.

  4 · ?grid
      Not a joke — the layout grid the whole site is built on, drawn over the
      page. Every alignment defect this project has shipped was a thing sitting
      half a column off, and this is the tool that shows it. It is behind a
      query parameter, so it costs a visitor nothing.

ALL OF THEM are inert under prefers-reduced-motion where they animate, and
none of them touch storage, the network, or the DOM a screen reader walks.
"""
import os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
PAGES = ["index.html", "engineering.html", "capabilities.html", "products.html",
         "approach.html", "work.html", "contact.html", "about.html",
         "impressum.html", "privacy.html", "pricing.html"]

PRINCIPLES = ["Trustworthy", "Human", "Confident", "Elegant", "Timeless",
              "Enterprise", "Premium", "Innovative", "Intelligent"]

JS = """<!--EGGS:JS--><script>
/* Four things that reward looking closer. See build_easter_eggs.py for why
   these four and not funnier ones. Nothing here fires on its own. */
(function(){
  var d = document, w = window;
  /* The work page's field figure is verified by a headless harness that runs
     this page's scripts against a minimal DOM stub — no matchMedia, no
     addEventListener, and a getElementById that returns something truthy for
     every id. Check for the things this code actually calls, the way the
     assistant does, or the figure's own test dies on our keydown handler. */
  if (typeof d.addEventListener !== 'function' ||
      typeof w.matchMedia !== 'function' ||
      typeof location === 'undefined') return;
  var reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var NINE = %PRINCIPLES%;

  /* 1 ─ the console banner ------------------------------------------------ */
  /* Newlines are built, not escaped. An earlier version wrote them as a
     backslash-n inside this template and the generator turned it into a real
     line break in the middle of a JS string literal, which took the work
     page's figure test down with a syntax error. */
  var NL = String.fromCharCode(10);
  try {
    var mono = 'ui-monospace,SFMono-Regular,Menlo,monospace';
    console.log('%c' + [
      '                                   ●',
      '                              ●',
      '                         ●',
      '                    ●',
      '               ●',
      '          ●',
      '      ●',
      '   ●',
      ' ·'
    ].join(NL), 'color:#FF7043;font-size:11px;line-height:1.15;font-family:' + mono);
    console.log('%cQuenora%c  ·  enterprise AI, engineered to operate',
      'color:#FF7043;font:600 15px system-ui', 'color:#A8AEBB;font:400 13px system-ui');
    console.log('%cNo framework, no bundler, no third-party script. Every page is one '
      + 'self-contained file — the hero is 2D canvas, the assistant is BM25 over a '
      + 'prebuilt index, and neither needs a network you do not control.',
      'color:#7C8290;font:400 12px/1.55 ' + mono);
    console.log('%cTry: the Konami code  ·  type  nora   ·  add ?grid to the URL',
      'color:#5BD7F5;font:400 12px ' + mono);
    console.log('%cinfo@quenora.ai', 'color:#C97A3C;font:400 12px ' + mono);
  } catch (e) {}

  /* 2 ─ the Konami code, which lights the nine and names them ------------- */
  var SEQ = ['ArrowUp','ArrowUp','ArrowDown','ArrowDown',
             'ArrowLeft','ArrowRight','ArrowLeft','ArrowRight','b','a'];
  var at = 0;
  function principles(){
    var sph = d.querySelectorAll('header .qsph');
    console.log('%cThe nine circles are nine principles, smallest first:',
      'color:#FF7043;font:600 13px system-ui');
    NINE.forEach(function(name, i){
      setTimeout(function(){
        console.log('%c' + String(i + 1).padStart(2, '0') + '  %c' + name,
          'color:#7C8290;font:400 12px ui-monospace,monospace',
          'color:#F2EFE8;font:400 13px system-ui');
        var s = sph[i];
        if (s && !reduced) {
          s.style.transition = 'transform .45s cubic-bezier(.16,1,.3,1)';
          s.style.transform = 'scale(1.45)';
          setTimeout(function(){ s.style.transform = ''; }, 520);
        }
      }, reduced ? 0 : i * 160);
    });
  }

  /* 3 ─ typing "nora" ------------------------------------------------------ */
  var typed = '';

  d.addEventListener('keydown', function(e){
    var t = e.target;
    /* never while someone is filling in the enquiry form */
    if (t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.isContentEditable)) return;

    at = (e.key === SEQ[at]) ? at + 1 : (e.key === SEQ[0] ? 1 : 0);
    if (at === SEQ.length) { at = 0; principles(); }

    if (e.key && e.key.length === 1) {
      typed = (typed + e.key.toLowerCase()).slice(-4);
      if (typed === 'nora') {
        typed = '';
        var fab = d.getElementById('aiFab'), panel = d.getElementById('aiPanel');
        if (fab && panel && !panel.classList.contains('open')) fab.click();
      }
    }
  });

  /* 4 ─ ?grid — the six columns everything is measured against ------------- */
  if (/[?&]grid\\b/.test(location.search)) {
    var wrap = d.querySelector('main .wrap') || d.querySelector('.wrap');
    if (wrap) {
      var box = wrap.getBoundingClientRect();
      var g = d.createElement('div');
      g.setAttribute('aria-hidden', 'true');
      g.style.cssText = 'position:fixed;top:0;bottom:0;z-index:9999;' +
        'pointer-events:none;display:grid;grid-template-columns:repeat(6,1fr);' +
        'gap:24px;left:' + Math.round(box.left) + 'px;width:' + Math.round(box.width) + 'px';
      for (var i = 0; i < 6; i++) {
        var col = d.createElement('div');
        col.style.cssText = 'background:rgba(255,112,67,.07);' +
          'border-left:1px solid rgba(255,112,67,.22);' +
          'border-right:1px solid rgba(255,112,67,.22)';
        g.appendChild(col);
      }
      d.body.appendChild(g);
      console.log('%c?grid  ' + Math.round(box.width) + 'px across six columns, left edge ' +
        Math.round(box.left) + 'px',
        'color:#5BD7F5;font:400 12px ui-monospace,monospace');
    }
  }
})();
</script><!--/EGGS:JS-->"""


def main():
    js = JS.replace('%PRINCIPLES%',
                    '[' + ','.join("'%s'" % p for p in PRINCIPLES) + ']')
    """Served rather than inlined: 5.3KB on every page, against a 220KB
    budget on index.html that it helped push over."""
    body = re.sub(r'^.*?<script>', '', js, flags=re.S)
    body = re.sub(r'</script>.*$', '', body, flags=re.S)
    open(os.path.join(ROOT, 'assets', 'eggs.js'), 'w', encoding='utf-8').write(body.strip())
    n = 0
    for page in PAGES:
        p = os.path.join(ROOT, page)
        if not os.path.exists(p):
            continue
        s = open(p, encoding='utf-8').read()
        before = s
        s = re.sub(r'<!--EGGS:JS-->.*?<!--/EGGS:JS-->\s*', '', s, flags=re.S)
        # matched with or without the ?v= build_asset_versions adds later,
        # or every build appends another copy of the tag
        s = re.sub(r'<script[^>]*src="/assets/eggs\.js(?:\?v=[0-9a-f]+)?"[^>]*>\s*</script>\s*', '', s)
        s = s.replace('</body>',
                      '<script defer src="/assets/eggs.js"></script>\n</body>', 1)
        if s != before:
            open(p, 'w', encoding='utf-8').write(s)
            n += 1
    print('  four easter eggs on %d page(s): console, Konami, "nora", ?grid' % n)


if __name__ == '__main__':
    main()

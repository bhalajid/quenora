#!/usr/bin/env python3
"""
build_backto.py — one way back to the spot on the home page you left from.

THE RULE, WHICH I HAD WRONG

Back means "return me to the home page, to the place I clicked from". It does
not mean "the previous page in history", and it has no meaning at all on the
home page itself — you cannot go back to where you already are.

The first version got all three wrong. It offered the control anywhere a
previous page had been recorded, including on the home page, and it called
history.back(), which returns to whatever happened to precede this page rather
than to the home page. Chain two inner pages and it walked backwards through
them one at a time.

So: the position is recorded only when leaving the home page, the control is
shown only on pages that are not the home page, and it always goes to the home
page. history.back() is still used when the browser is one step from home,
because then it is both correct and pixel-exact; otherwise the recorded anchor
is restored.

AND IT SITS IN THE FLOW

It was position:sticky at top:88px, which put it on top of the heading of every
page it appeared on. It is a block above the eyebrow now, so it cannot overlap
anything.
"""
import os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))

MARK = ('<!--BACKTO:JS-->', '<!--/BACKTO:JS-->')

JS = """<script>
/* Remember where the reader was when they left for another page, so the page
   they land on can offer a way back to that exact spot rather than to the top
   of a very long document. sessionStorage: one tab, one visit, never sent. */
(function(){
  /* The headless harness that verifies the work page's field figure runs every
     script against a minimal DOM stub, where document exists but
     addEventListener does not. Guard on the capability, not on the object —
     this is the third time that stub has caught a script assuming a browser. */
  if (typeof sessionStorage === 'undefined') return;
  if (typeof document === 'undefined' ||
      typeof document.addEventListener !== 'function') return;
  var KEY = 'qn:from';
  /* '/', '/index.html', '/de', '/de/index.html' and so on */
  var HOME = /^\/(?:(?:de|fr|es|it)\/?)?(?:index\.html)?$/;

  /* leaving: record the offset against the link's destination */
  document.addEventListener('click', function(e){
    var a = e.target.closest && e.target.closest('a[href]');
    if (!a) return;
    var href = a.getAttribute('href') || '';
    if (!/\\.html(#|$)|^\\/(de|fr)\\//.test(href)) return;
    if (a.target === '_blank' || href.charAt(0) === '#') return;
    /* Only the home page is worth returning to. Recording every page turned
       Back into a history walk: from capabilities it pointed at approach,
       the page before it, instead of at the home page it was meant to. */
    if (!HOME.test(location.pathname)) return;
    try {
      /* Record an ANCHOR, not a pixel — and anchor to the section the
         reader was actually IN, not whichever one happened to be at the top
         of the viewport. This page pins and grows sections as they reveal, so
         a raw offset landed 758px out and a top-of-viewport anchor still
         landed 432px out. The section under the click is stable, and its
         distance from the viewport top is the thing to reproduce. */
      var host = a.closest('section[id]') || a.closest('[id]');
      var top = host ? Math.round(host.getBoundingClientRect().top) : null;
      sessionStorage.setItem(KEY, JSON.stringify({
        url: location.pathname + location.search,
        anchor: host ? host.id : '',
        top: top,
        y: Math.round(window.scrollY || 0)
      }));
    } catch (err) {}
  }, true);

  /* arriving: if we were sent here from somewhere, offer the way back */
  var raw = null;
  try { raw = sessionStorage.getItem(KEY); } catch (err) {}
  if (!raw) return;
  var from;
  try { from = JSON.parse(raw); } catch (err) { return; }
  if (!from || !from.url || from.url === location.pathname) return;
  /* Never on the home page: there is nowhere to go back to from the thing
     you go back to. */
  if (HOME.test(location.pathname)) return;

  var host = document.querySelector('main .wrap');
  if (!host) return;
  var a = document.createElement('a');
  a.className = 'backto';
  a.href = from.url + '#qn-back';
  a.innerHTML = '<span class="arw" aria-hidden="true">&#8592;</span>' +
                (document.documentElement.lang === 'de' ? 'Zur\\u00fcck' :
                 document.documentElement.lang === 'fr' ? 'Retour' : 'Back');
  a.addEventListener('click', function(e){
    /* A real history step, when there is one. The browser restores the exact
       offset itself — my own attempt at reproducing it landed 371 to 500px
       out, because this page keeps growing as its sections reveal and no
       script can chase that reliably. Falling back to the recorded anchor
       only when there is no history entry to step back to. */
    /* history.back() only when the step behind us really is the home page —
       then it is exact and free. Otherwise navigate and restore. */
    var ref = document.referrer || '';
    var cameStraightFromHome = ref.indexOf(location.origin) === 0 &&
                  ref.replace(location.origin, '').split('#')[0] === from.url;
    if (cameStraightFromHome && history.length > 1) {
      e.preventDefault();
      history.back();
      return;
    }
    try { sessionStorage.setItem('qn:restore', JSON.stringify(from)); } catch (err) {}
  });
  host.insertBefore(a, host.firstChild);
})();

/* landing back: put the reader on the pixel they left from, before paint */
(function(){
  if (typeof sessionStorage === 'undefined') return;
  if (typeof window === 'undefined' ||
      typeof window.addEventListener !== 'function') return;
  var raw = null;
  try { raw = sessionStorage.getItem('qn:restore'); } catch (err) {}
  if (!raw) return;
  try { sessionStorage.removeItem('qn:restore'); } catch (err) {}
  var want;
  try { want = JSON.parse(raw); } catch (err) { return; }
  if (!want) return;

  /* Resolve the anchor every time rather than once: the section moves as the
     page reveals, so the target is only correct at the moment it is read. */
  function target(){
    if (want.anchor && want.top !== null && want.top !== undefined) {
      var el = document.getElementById(want.anchor);
      /* put the section back exactly as far down the viewport as it was */
      if (el) return Math.max(0, el.getBoundingClientRect().top + window.scrollY - want.top);
    }
    return want.y > 0 ? want.y : null;
  }
  function put(){ var t = target(); if (t !== null) window.scrollTo(0, t); }
  put();

  /* Keep correcting until the target stops moving, rather than for a fixed
     number of ticks. This page reveals sections as it goes, so its layout is
     still settling for a second or two after load — a fixed window gave up
     early and left the reader 371px adrift. Stop once the computed target has
     agreed with itself several times, and give up after three seconds so this
     can never spin. */
  var last = null, stable = 0, ticks = 0;
  var iv = setInterval(function(){
    var t = target();
    if (t === null) { clearInterval(iv); return; }
    if (last !== null && Math.abs(t - last) <= 1) { stable++; } else { stable = 0; }
    last = t;
    if (Math.abs(window.scrollY - t) > 1) { window.scrollTo(0, t); stable = 0; }
    if (stable >= 6 || ++ticks > 60) clearInterval(iv);
  }, 50);
  addEventListener('load', put);
})();
</script>"""

PAGES = ['index.html', 'approach.html', 'capabilities.html', 'engineering.html',
         'work.html', 'contact.html', 'products.html', 'about.html']


def main():
    a, b = MARK
    done = 0
    for page in PAGES:
        p = os.path.join(ROOT, page)
        if not os.path.exists(p):
            continue
        s = open(p, encoding='utf-8').read()
        if a in s and b in s:
            i, j = s.index(a), s.index(b) + len(b)
            s = s[:i] + a + '\n' + JS + '\n' + b + s[j:]
        elif '</body>' in s:
            s = s.replace('</body>', a + '\n' + JS + '\n' + b + '\n</body>', 1)
        else:
            continue
        open(p, 'w', encoding='utf-8').write(s)
        done += 1
    print('  back-to-where-you-were on %d page(s)' % done)
    return 0


if __name__ == '__main__':
    sys.exit(main())

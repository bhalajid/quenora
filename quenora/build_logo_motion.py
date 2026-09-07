#!/usr/bin/env python3
"""
build_logo_motion.py — the lockup stops being a picture and starts moving.

RUN AFTER build_brand.py. It replaces the header <img> that build_brand
writes; running them the other way round puts the flat image back.

WHAT THIS DOES, AND WHY EACH PART EXISTS

1 · THE HEADER LOCKUP IS INLINED, THE FOOTER ONE IS NOT

   build_brand deliberately used <img> for both: one cached file beats 12KB
   inlined into every page. That reasoning still holds for the footer, which
   nobody hovers. But CSS cannot reach inside an <img>, so a sheen on the Q
   and a hover on the spheres are impossible while the header is one too.

   So the header lockup is inlined and the footer is left exactly as it was.
   The stripped primary is 6KB, and only the header carries it.

   Two inline copies on one page would collide on the gradient ids — both
   would define #q79d4b — so this is also the reason not to inline both.

2 · THE SPHERES ARE GROUPED

   The supplied file draws each sphere as three elements in sequence: a base
   circle, a rim circle over it, and a highlight ellipse. Nothing groups them,
   so there is no single thing to transform. This wraps each triple in a <g>
   carrying its index, which is what lets them animate in sequence and scale
   from their own centres rather than from the canvas origin.

3 · THE SHEEN IS CLIPPED TO THE Q, NOT DRAWN OVER IT

   A highlight that merely passes over the logo lights the gaps between the
   letters too, which reads as a rectangle sliding past rather than as light
   on a surface. The Q's own path becomes a clipPath, and the moving gradient
   is drawn inside it. It can only ever appear on ink.

4 · THE CURSOR

   The homepage drew a copper ring that stretched into a comet, plus a lead
   dot. It is replaced by the mark's own nine spheres, translucent, each
   lagging further behind the pointer than the last, so the cursor is the
   logo in motion. Same lerp chain the ring used; nine of them.

REDUCED MOTION

   Every part of this is switched off under prefers-reduced-motion: the sheen
   does not sweep, the spheres do not breathe, and the trail is not built at
   all. The lockup still renders in full — it is a logo, not an animation.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PAGES = ["index.html", "engineering.html", "capabilities.html", "products.html",
         "approach.html", "work.html", "contact.html", "about.html",
         "impressum.html", "privacy.html", "pricing.html"]

CSS = """/*LOGOMOTION:CSS*/
/* ── the lockup, moving ────────────────────────────────────────────────
   Sizes match what build_brand set on the image it replaces, so swapping one
   for the other never reflows the header. (Written without the literal tag
   name: stage 4 regexes image tags straight out of the raw HTML, comments
   included, and reported every page as having one with no alt text.) */
.brandsvg{display:block;height:58px;width:auto;flex:none;overflow:visible}
.brand.lg .brandsvg{height:96px}
@media(max-width:900px){.brandsvg{height:42px}.brand.lg .brandsvg{height:56px}}
@media(max-width:560px){.brandsvg{height:37px}.brand.lg .brandsvg{height:49px}}

/* The sheen. A soft band of white at low alpha, clipped to the Q, crossing
   once and then waiting — a reflection catching the edge, not a shimmer.

   The travel is the Q's OWN width, not the canvas width. The first version
   swept the full 1166-unit viewBox while the clip is a Q occupying x 18..191,
   so the reflection was on screen for about a third of a second in every six
   and a half, at an unpredictable moment. It now enters at the Q's left edge
   and leaves at its right, and the pause is the pause. */
.qsheen{animation:qsweep 7s cubic-bezier(.36,0,.2,1) infinite}
@keyframes qsweep{
  0%,4%{transform:translateX(-110px) skewX(-16deg)}
  26%{transform:translateX(215px) skewX(-16deg)}
  100%{transform:translateX(215px) skewX(-16deg)}
}
/* Each sphere breathes on its own beat, smallest first, so the arc reads as
   rising rather than pulsing as one block. */
.qsph{transform-box:fill-box;transform-origin:center;
  animation:qbreathe 4.2s ease-in-out infinite;
  animation-delay:calc(var(--i) * -0.42s)}
@keyframes qbreathe{0%,100%{transform:scale(1)}50%{transform:scale(1.075)}}

/* Hover: the arc lifts in sequence, largest last, and the ember warms.
   Pointer-driven only — it must never fire from a tap that was a scroll. */
@media(hover:hover) and (pointer:fine){
  .brand:hover .qsph{animation:none;
    transform:translateY(calc(var(--i) * -0.9px)) scale(calc(1 + var(--i) * 0.02));
    transition:transform .5s cubic-bezier(.16,1,.3,1);
    transition-delay:calc(var(--i) * 22ms)}
  .brand:hover .qsheen{animation-duration:2.2s}
}

/* The cursor: nine translucent spheres, each further behind than the last.
   A speed-driven version of this was tried and taken out again: brightening
   the head as the pointer moved turned it into a bright blob leading the
   cursor rather than a trail behind it. Fixed and faint is the brief. */
#qtrail{position:fixed;inset:0;z-index:9998;pointer-events:none;opacity:0;
  transition:opacity .5s ease}
body.con #qtrail{opacity:1}
#qtrail i{position:absolute;top:0;left:0;display:block;border-radius:50%;
  will-change:transform;filter:blur(.3px);
  background:radial-gradient(circle at 32% 29%,
    rgba(245,210,176,.95) 0%, rgba(233,160,99,.8) 16%,
    rgba(201,122,60,.62) 46%, rgba(158,92,42,.4) 82%, rgba(90,50,20,.24) 100%)}
/* Over something clickable the trail brightens, which is the affordance the
   old ring carried and the only reason it earned its place. */
body.clg #qtrail i{filter:brightness(1.35)}
@media(hover:none),(pointer:coarse){#qtrail{display:none}}

@media(prefers-reduced-motion:reduce){
  .qsheen{display:none}
  .qsph{animation:none}
  .brand:hover .qsph{transform:none}
  #qtrail{display:none}
}
/*/LOGOMOTION:CSS*/"""

JS = """<!--LOGOMOTION:JS--><script>
/* The nine spheres, following the pointer. Replaces the ring-and-dot cursor:
   same lerp chain, nine of them, each with a slower follow than the one in
   front so the arc trails out behind a fast movement and collapses back into
   a single mark when the pointer stops. */
(function(){
  var w = window, d = document, body = d.body;
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  if (!matchMedia('(hover:hover) and (pointer:fine)').matches) return;
  var wrap = d.getElementById('qtrail');
  if (!wrap) return;

  /* Sizes are the logo's own ratio, 9^(1/8) per step, smallest at the tail. */
  var N = 9, dots = [], i, el;
  for (i = 0; i < N; i++) {
    el = d.createElement('i');
    var r = 2.8 * Math.pow(1.3161, i);          /* 2.8px -> 24px */
    el.style.width = el.style.height = r.toFixed(2) + 'px';
    el.style.marginLeft = el.style.marginTop = (-r / 2).toFixed(2) + 'px';
    /* Deliberately far below what looks right for ONE sphere. At rest all
       nine sit on the same point and their alpha compounds; a brighter tuning
       turned the pointer into a lamp that washed out whatever it hovered. */
    el.style.opacity = (0.045 + 0.011 * i).toFixed(3);
    wrap.appendChild(el);
    dots.push({ el: el, x: 0, y: 0, k: 0.30 - i * 0.026 });
  }

  var mx = 0, my = 0, seen = false;
  w.addEventListener('mousemove', function (e) {
    mx = e.clientX; my = e.clientY;
    if (!seen) {
      seen = true;
      for (var j = 0; j < N; j++) { dots[j].x = mx; dots[j].y = my; }
      body.classList.add('con');
    }
  }, { passive: true });

  (function frame() {
    for (var j = 0; j < N; j++) {
      var t = dots[j];
      t.x += (mx - t.x) * t.k;
      t.y += (my - t.y) * t.k;
      t.el.style.transform = 'translate3d(' + t.x.toFixed(1) + 'px,'
                                            + t.y.toFixed(1) + 'px,0)';
    }
    requestAnimationFrame(frame);
  })();

  d.addEventListener('mouseover', function (e) {
    if (e.target.closest && e.target.closest('a,button,.nrow')) body.classList.add('clg');
  });
  d.addEventListener('mouseout', function (e) {
    if (e.target.closest && e.target.closest('a,button,.nrow')) body.classList.remove('clg');
  });
})();
</script><!--/LOGOMOTION:JS-->"""


def animated_svg():
    """The stripped primary, regrouped so its parts can be addressed."""
    src = open(os.path.join(ROOT, "assets/brand/quenora-primary.svg")).read()

    # The ember path is the Q; the white one is the wordmark.
    paths = list(re.finditer(r'<path\b[^>]*?d="([^"]+)"[^>]*/>', src))
    if len(paths) < 2:
        sys.exit("  primary.svg does not have the two paths this expects")
    qd = paths[0].group(1)

    # Each sphere is three consecutive elements; wrap every triple.
    g = re.search(r'(<g class="quenora-rise">)(.*?)(</g>)', src, re.S)
    if not g:
        sys.exit("  primary.svg has no .quenora-rise group")
    els = re.findall(r'<(?:circle|ellipse)\b[^>]*/>', g.group(2))
    if len(els) % 3:
        sys.exit("  expected circle/circle/ellipse triples, got %d elements" % len(els))
    grouped = "".join(
        '<g class="qsph" style="--i:%d">%s</g>' % (n, "".join(els[n * 3:n * 3 + 3]))
        for n in range(len(els) // 3))
    src = src[:g.start(2)] + grouped + src[g.end(2):]

    # The sheen, clipped to the Q so it can only ever land on ink.
    sheen = (
        '<clipPath id="qclip"><path d="%s"/></clipPath>'
        '<linearGradient id="qshine" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        '<stop offset="0.42" stop-color="#fff" stop-opacity="0.34"/>'
        '<stop offset="0.5" stop-color="#fff" stop-opacity="0.62"/>'
        '<stop offset="0.58" stop-color="#fff" stop-opacity="0.34"/>'
        '<stop offset="1" stop-color="#fff" stop-opacity="0"/>'
        '</linearGradient>') % qd
    src = src.replace('</defs>', sheen + '</defs>', 1)
    src = src.replace('</svg>',
                      '<g clip-path="url(#qclip)">'
                      '<rect class="qsheen" x="0" y="404" width="86" height="232" '
                      'fill="url(#qshine)" transform="translate(-620,0)"/>'
                      '</g></svg>', 1)

    src = src.replace('<svg ', '<svg class="brandsvg" focusable="false" ', 1)
    return re.sub(r'\s*\n\s*', '', src).strip()


def swap(page, svg):
    p = os.path.join(ROOT, page)
    s = open(p, encoding="utf-8").read()
    before = s

    # 1 · the HEADER lockup only. The footer copy stays an <img>: nobody
    #     hovers it, and two inline copies would collide on the gradient ids.
    m = re.search(r'<header\b.*?</header>', s, re.S)
    if m:
        head = m.group(0)
        new = re.sub(r'<img[^>]*\bclass="brandimg"[^>]*/?>',
                     '<!--LOGOMOTION:MARK-->' + svg + '<!--/LOGOMOTION:MARK-->',
                     head, count=1)
        # a re-run replaces the previous inline mark rather than nesting one
        new = re.sub(r'<!--LOGOMOTION:MARK-->.*?<!--/LOGOMOTION:MARK-->',
                     '<!--LOGOMOTION:MARK-->' + svg + '<!--/LOGOMOTION:MARK-->',
                     new, count=1, flags=re.S)
        s = s[:m.start()] + new + s[m.end():]

    """The footer keeps an image tag, but it is now a DIFFERENT file and a
    different shape: the full lockup, with the long rise and the tagline, in a
    1166x1007 box. build_brand only writes a lockup where none exists, so a
    page that already had one kept the old file name and the old intrinsic
    size — which meant the browser reserved a 2.10:1 box for a 1.16:1 file and
    the footer jumped when the SVG landed. Restate both here."""
    s = re.sub(r'(<img[^>]*\bclass="brandimg"[^>]*?)src="/assets/brand/quenora-primary\.svg"',
               r'\1src="/assets/brand/quenora-full.svg"', s)
    s = re.sub(r'(<img[^>]*\bclass="brandimg"[^>]*?)height="\d+"', r'\1height="1007"', s)
    s = re.sub(r'(<img[^>]*\bclass="brandimg"[^>]*?)width="\d+"', r'\1width="1166"', s)

    # 2 · CSS, between markers so this is idempotent
    if '/*LOGOMOTION:CSS*/' in s:
        s = re.sub(r'/\*LOGOMOTION:CSS\*/.*?/\*/LOGOMOTION:CSS\*/', CSS, s, flags=re.S)
    else:
        s = s.replace('</style>', CSS + '\n</style>', 1)

    # 3 · the cursor, homepage only — it is the only page that has one
    if page == 'index.html':
        s = re.sub(r'<div aria-hidden="true" class="cur" id="cur"></div>\s*'
                   r'<div aria-hidden="true" class="cdot" id="cdot"></div>',
                   '<div aria-hidden="true" id="qtrail"></div>', s)
        # neutralise the ring, which would throw now that #cur is gone
        s = re.sub(
            r'/\* ─+ 2 · CURSOR \(ring lags, dot leads\) ─+ \*/\s*'
            r'if \(!reduced && w\.matchMedia\(\'\(hover:hover\) and \(pointer:fine\)\'\)\.matches\) \{.*?\n  \}\n',
            '/* ─────────── 2 · CURSOR ───────────\n'
            '     The ring and its lead dot are gone; the mark\'s own nine\n'
            '     spheres trail the pointer instead. See build_logo_motion.py,\n'
            '     which owns that code and the elements it drives. */\n',
            s, count=1, flags=re.S)
        if '<!--LOGOMOTION:JS-->' in s:
            s = re.sub(r'<!--LOGOMOTION:JS-->.*?<!--/LOGOMOTION:JS-->', JS, s, flags=re.S)
        else:
            s = s.replace('</body>', JS + '\n</body>', 1)

    if s != before:
        open(p, "w", encoding="utf-8").write(s)
        return True
    return False


def main():
    svg = animated_svg()
    n = 0
    for page in PAGES:
        if not os.path.exists(os.path.join(ROOT, page)):
            continue
        if swap(page, svg):
            n += 1
    print("  the lockup moves, and the cursor is the mark, on %d page(s)" % n)
    print("  inline header SVG: %d bytes" % len(svg))


if __name__ == "__main__":
    main()

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
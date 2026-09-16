/* A language offer. Not a redirect, and not a cookie banner.
 *
 * Signal: navigator.language — the visitor's own browser setting. Nothing is
 * read from or written to the device to decide whether to show this, so
 * showing it stores nothing and needs no consent.
 *
 * Storage: one cookie, q_lang, written ONLY when the visitor clicks. That is
 * user-interface customisation resulting from an explicit user action, which
 * is the clean exemption under §25 TDDDG / the ePrivacy directive. It holds a
 * language code and nothing else — no identifier, no tracking, no profiling.
 *
 * Timing out is not a choice. If the bar hides itself the visitor never
 * answered, so nothing is persisted; it simply stays quiet for the rest of
 * the session. Recording a permanent "no" from silence would take the offer
 * away from someone who merely looked out of the window. */
(function (w, d) {
  if (typeof d.addEventListener !== 'function' || typeof d.cookie !== 'string') return;
  if (!w.navigator || typeof w.navigator.language !== 'string') return;

  var HIDE_AFTER = 12000;          /* long enough to read twice, unhurried */

  var COPY = {
    de: { t: 'Diese Seite gibt es auf Deutsch.',
          go: 'Zur deutschen Seite', no: 'Auf Englisch bleiben',
          why: 'Ihre Auswahl wird in einem Cookie gespeichert, damit wir nicht erneut fragen. Sonst nichts.' },
    fr: { t: 'Ce site existe en français.',
          go: 'Voir en français', no: 'Rester en anglais',
          why: 'Votre choix est conservé dans un cookie pour ne plus vous le redemander. Rien d’autre.' }
  };

  function cookie(n) {
    var m = d.cookie.match(new RegExp('(?:^|; )' + n + '=([^;]*)'));
    return m ? decodeURIComponent(m[1]) : '';
  }
  function remember(v) {
    d.cookie = 'q_lang=' + v + '; Path=/; Max-Age=31536000; SameSite=Lax';
  }
  function quietForNow() {
    try { w.sessionStorage.setItem('q_lang_seen', '1'); } catch (e) {}
  }
  function alreadyQuiet() {
    try { return w.sessionStorage.getItem('q_lang_seen') === '1'; } catch (e) { return false; }
  }

  var previewing = false;
  try {
    previewing = new w.URLSearchParams(w.location.search).has('lang-offer');
  } catch (e) {}
  if (!previewing && (cookie('q_lang') || alreadyQuiet())) return;

  /* ?lang-offer=de forces the bar for one page load, whatever the browser is
     set to. There is no other way to see this on an English-language machine,
     which is every machine the people who build the site are using. It only
     forces the DISPLAY — the cookie is still written on a click and nothing
     else, so previewing it changes nothing permanent. */
  var forced = '';
  try {
    forced = (new w.URLSearchParams(w.location.search).get('lang-offer') || '')
               .toLowerCase();
  } catch (e) {}

  /* "de-AT" -> "de". Only the primary subtag decides. */
  var want = forced || String(w.navigator.language).toLowerCase().split('-')[0];
  if (!COPY[want]) return;

  /* Already reading that language, or this page has no such translation. */
  if (new RegExp('^/(' + want + ')(?:/|$)').test(w.location.pathname)) return;
  var alt = d.querySelector('link[rel="alternate"][hreflang="' + want + '"]');
  if (!alt) return;

  /* The hreflang alternates are absolute (https://quenora.ai/de), so following
     one verbatim would take a visitor on a preview or staging host across to
     production — and drop the cookie on the wrong origin on the way. Keep the
     path, keep the visitor where they are. */
  var href = alt.getAttribute('href');
  try { href = new w.URL(href, w.location.href).pathname; } catch (e) {}

  var c = COPY[want];
  var bar = d.createElement('div');
  bar.className = 'q-langoffer';
  bar.setAttribute('role', 'region');
  bar.setAttribute('aria-label', c.t);
  bar.innerHTML =
    '<div class="q-lo-text"><p>' + c.t + '</p><p class="q-lo-why">' + c.why + '</p></div>' +
    '<div class="q-lo-acts">' +
      '<a class="q-lo-go" href="' + href + '">' + c.go + '</a>' +
      '<button class="q-lo-no" type="button">' + c.no + '</button>' +
    '</div>';

  var timer = null;
  function dismiss(persist) {
    if (timer) { w.clearTimeout(timer); timer = null; }
    if (persist) remember(persist);   /* already marked seen on display */
    bar.classList.remove('in');
    w.setTimeout(function () { if (bar.parentNode) bar.parentNode.removeChild(bar); }, 280);
  }
  function arm()   { if (!timer) timer = w.setTimeout(function () { dismiss(null); }, HIDE_AFTER); }
  function hold()  { if (timer) { w.clearTimeout(timer); timer = null; } }

  /* Write on pointerdown as well as click. A plain click handler on an
     anchor races the navigation it triggers, and the document can unload
     before the cookie is committed — which it did, reproducibly. pointerdown
     lands milliseconds earlier and still leaves the anchor a real link, so
     middle-click and open-in-new-tab keep working. remember() is idempotent. */
  var go = bar.querySelector('.q-lo-go');
  go.addEventListener('pointerdown', function () { remember(want); });
  go.addEventListener('click', function () { remember(want); });
  bar.querySelector('.q-lo-no').addEventListener('click', function () { dismiss('en'); });

  /* Reading it, or tabbing through it, stops the clock — a countdown the
     visitor cannot pause is WCAG 2.2.1's whole complaint. */
  bar.addEventListener('mouseenter', hold);
  bar.addEventListener('mouseleave', arm);
  bar.addEventListener('focusin', hold);
  bar.addEventListener('focusout', arm);

  /* Say so, loudly, when this is a preview. The override ignores the
     once-per-session rule by design — otherwise it could preview the bar
     exactly once, which is no use for checking it. Without this line the two
     facts look like a contradiction: "it shows once per session" and "it
     shows every time I load my test URL". */
  if (previewing && w.console && typeof w.console.info === 'function') {
    w.console.info(
      '%cQuenora%c lang-offer=' + want + ' — PREVIEW. The once-per-session ' +
      'limit is bypassed while this parameter is in the URL. Drop it to see ' +
      'what a real visitor gets.',
      'color:#C97A3C;font-weight:700', 'color:inherit');
  }

  d.body.appendChild(bar);
  /* Mark it seen the moment it is SHOWN, not when it hides. Marking on hide
     meant a reader moving faster than the 12s timer outran it and met the bar
     again on every page — the exact nuisance this was built to avoid. Once
     per tab, whatever speed they read at. */
  quietForNow();
  w.requestAnimationFrame(function () {
    w.requestAnimationFrame(function () { bar.classList.add('in'); arm(); });
  });
})(window, document);

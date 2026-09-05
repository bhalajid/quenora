#!/usr/bin/env bash
# Empirical launch verification. Run it against the real domain the moment DNS
# has propagated — it answers the questions that cannot be answered from the
# repo, because they are about DNS, TLS and how Vercel actually behaves.
#
#   bash test/launch_check.sh                     # defaults to quenora.ai
#   bash test/launch_check.sh quenora.ai quenora.vercel.app
#
# Exit code is non-zero if anything fails, so it can gate a deploy.
set -uo pipefail
LIVE="${1:-quenora.ai}"
DEPLOY="${2:-quenora.vercel.app}"
# The host the markup is supposed to declare. It stays quenora.ai even when the
# fetch host is the deployment one, because a canonical names where the page
# lives, not where it was fetched from.
DECLARES="${3:-quenora.ai}"
pass=0; fail=0
ok(){   printf '   \033[32mok\033[0m   %s\n' "$1"; pass=$((pass+1)); }
no(){   printf '   \033[31mFAIL\033[0m %s\n' "$1"; fail=$((fail+1)); }
sect(){ printf '\n\033[1m── %s\033[0m\n' "$1"; }

code(){ curl -sS -o /dev/null -w '%{http_code}' --max-time 8 "$1" 2>/dev/null; }
loc(){  curl -sS -o /dev/null -w '%{redirect_url}' --max-time 8 "$1" 2>/dev/null; }
hdr(){  curl -sSI --max-time 8 "$1" 2>/dev/null | tr -d '\r'; }

check_qr(){
  # The printed codes encode https://quenora.ai/c and nothing else. Until the
  # domain answers, every card and every stand code is a dead link, and a scan
  # gives a browser error rather than a contact. This cannot be caught from the
  # repo — the URL is correct there — so it is checked here, against the world.
  sect "the contact QR resolves"
  for u in "https://$LIVE/c" "https://$LIVE/c?k=card" "https://$LIVE/c?k=event"; do
    c=$(code "$u")
    if [ "$c" = "200" ]; then
      ct=$(hdr "$u" | grep -i '^content-type:' | head -1)
      case "$ct" in
        *vcard*) ok "$u -> 200, text/vcard" ;;
        *)       no "$u -> 200 but $ct — a scanner will not offer to save it" ;;
      esac
    else
      no "$u -> $c — every printed code points here"
    fi
  done
  c=$(code "https://$LIVE/w?probe=1")
  [ "$c" = "200" ] && ok "https://$LIVE/w?probe=1 -> 200" \
    || no "https://$LIVE/w?probe=1 -> $c — the wallet probe logs an error on every home page load"
}

sect "the domain answers"
c=$(code "https://$LIVE/")
[ "$c" = "200" ] && ok "https://$LIVE/ -> 200" || no "https://$LIVE/ -> $c (DNS not pointed, or TLS not issued yet)"

if [ "$c" != "200" ]; then
  printf '\n   \033[33mThe domain is not answering, so the rest of the checks would\n'
  printf '   each wait for a timeout. Point %s at Vercel first —\n' "$LIVE"
  printf '   LAUNCH.md step 2 — then run this again.\033[0m\n\n'
  printf '\033[1m%d passed, %d failed\033[0m\n' "$pass" "$fail"
  exit 1
fi

sect "TLS is valid for the apex"
if curl -sS -o /dev/null --max-time 8 "https://$LIVE/" 2>/dev/null; then
  ok "certificate accepted without --insecure"
else
  no "TLS handshake failed — Vercel may still be issuing the certificate"
fi

sect "clean URLs serve directly, without a redirect hop"
for p in "" "engineering" "services" "work" "approach" "de" "de/work" "fr/services"; do
  c=$(code "https://$LIVE/$p")
  [ "$c" = "200" ] && ok "/$p -> 200" || no "/$p -> $c"
done

sect "the .html form still redirects to the clean one"
l=$(loc "https://$LIVE/engineering.html")
case "$l" in
  *"/engineering") ok "/engineering.html -> $l" ;;
  *)               no "/engineering.html -> '${l:-no redirect}'" ;;
esac

sect "the deployment host does not stay in the address bar"
c=$(code "https://$DEPLOY/")
l=$(loc "https://$DEPLOY/")
case "$l" in
  "https://$LIVE/"*) ok "https://$DEPLOY/ -> $l" ;;
  *) if hdr "https://$DEPLOY/" | grep -qi 'x-robots-tag:.*noindex'; then
       no "no redirect yet ($c) — noindex is holding it out of search, add the redirect block from LAUNCH.md step 3"
     else
       no "https://$DEPLOY/ neither redirects nor carries noindex — it will be indexed"
     fi ;;
esac

sect "path is preserved across the redirect"
l=$(loc "https://$DEPLOY/de/work")
case "$l" in
  "https://$LIVE/de/work") ok "deep path survives: $l" ;;
  "") no "no redirect from the deployment host yet" ;;
  *)  no "path lost or rewritten: $l" ;;
esac

sect "the site declares only the live host"
sm=$(curl -sS --max-time 8 "https://$LIVE/sitemap.xml" 2>/dev/null)
n=$(printf '%s' "$sm" | grep -c "<loc>https://$DECLARES/" || true)
bad=$(printf '%s' "$sm" | grep -c 'vercel\.app\|\.html</loc>' || true)
[ "$n" -gt 0 ] && ok "sitemap reachable, $n url(s) on $DECLARES" || no "sitemap missing or empty"
[ "$bad" = "0" ] && ok "no deployment host and no .html in the sitemap" || no "$bad bad sitemap entry(ies)"

can=$(curl -sS --max-time 8 "https://$LIVE/services" 2>/dev/null \
        | grep -o '<link[^>]*rel="canonical"[^>]*>' | head -1)
case "$can" in
  *"https://$DECLARES/services\""*) ok "canonical on /services is the live clean URL" ;;
  *) no "canonical on /services is: ${can:-not found}" ;;
esac

sect "security headers survived the domain change"
h=$(hdr "https://$LIVE/")
for k in "strict-transport-security" "content-security-policy" "x-content-type-options"; do
  printf '%s' "$h" | grep -qi "^$k:" && ok "$k present" || no "$k missing"
done

check_qr

printf '\n\033[1m%d passed, %d failed\033[0m\n' "$pass" "$fail"
[ "$fail" -eq 0 ] || exit 1

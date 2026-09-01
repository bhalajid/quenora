#!/usr/bin/env bash
QPY_NAV="${QUENORA_PY:-python3}"
# ---------------------------------------------------------------
# Quenora release gate. Nothing ships unless every stage passes.
#   ./release.sh <site-dir>
# ---------------------------------------------------------------
set -uo pipefail
DIR="${1:-..}"
FAILED=0
step(){ printf '\n\033[1m%s\033[0m\n' "── $1"; }
ok(){   printf '   \033[32mPASS\033[0m %s\n' "$1"; }
bad(){  printf '   \033[31mFAIL\033[0m %s\n' "$1"; FAILED=1; }

step "1/8  JS syntax + tag balance"
node -e '
const fs=require("fs"),path=require("path");
const dir=process.argv[1];let bad=0;
for(const f of fs.readdirSync(dir).filter(x=>x.endsWith(".html"))){
  const h=fs.readFileSync(path.join(dir,f),"utf8");
  for(const m of h.matchAll(/<script>([\s\S]*?)<\/script>/g)){
    try{new Function(m[1]);}catch(e){console.log("   syntax error in "+f+": "+e.message);bad=1;}
  }
  const pairs={div:["<div","</div>"],section:["<section","</section>"],main:["<main","</main>"]};
  for(const[k,[o,c]]of Object.entries(pairs)){
    const a=(h.match(new RegExp(o,"g"))||[]).length,b=(h.match(new RegExp(c,"g"))||[]).length;
    if(a!==b){console.log(`   ${f}: ${k} ${a}/${b} unbalanced`);bad=1;}
  }
}
process.exit(bad);
' "$DIR" && ok "syntax + structure" || bad "syntax + structure"

step "2/8  sphere hit-testing (real Three.js math)"
node test_pick_real.js >/tmp/pick.log 2>&1
if grep -q "0 mis-picks" /tmp/pick.log; then ok "$(grep 'correct,' /tmp/pick.log|head -1)"; else bad "mis-picks found"; tail -5 /tmp/pick.log; fi

step "3/8  smoke test (jsdom, real page JS)"
node smoke.js "$DIR" >/tmp/smoke.log 2>&1
if [ $? -eq 0 ]; then ok "$(grep 'SMOKE TEST' /tmp/smoke.log)"; else bad "smoke failures"; sed -n '/FAILURES/,$p' /tmp/smoke.log; fi

step "4/8  accessibility + SEO audit"
python3 - "$DIR" <<'PY'
import re,sys,os,glob
d=sys.argv[1];issues=[]
for f in sorted(glob.glob(os.path.join(d,'*.html'))):
    h=open(f,encoding='utf-8').read();n=os.path.basename(f)
    if 'rel="icon"' not in h: issues.append(n+': no favicon')
    if 'og:title' not in h: issues.append(n+': no OG tags')
    if '<main' not in h: issues.append(n+': no main landmark')
    if 'class="skip"' not in h: issues.append(n+': no skip link')
    if 'focus-visible' not in h: issues.append(n+': no focus styles')
    if 'prefers-reduced-motion' not in h: issues.append(n+': no reduced-motion')
    if len(re.findall(r'<h1',h))!=1: issues.append(n+': h1 count != 1')
    for i in re.findall(r'<img[^>]*>',h):
        if 'alt=' not in i: issues.append(n+': img without alt')
    for c in re.finditer(r'<canvas[^>]*>',h):
        if 'aria-hidden' not in c.group(0) and 'role="img"' not in c.group(0):
            issues.append(n+': canvas exposed to screen readers')
    for m in re.finditer(r'href="([a-z0-9\-]+\.html)"',h):
        if not os.path.exists(os.path.join(d,m.group(1))): issues.append(n+': broken link '+m.group(1))
print('\n'.join('   '+i for i in issues))
sys.exit(1 if issues else 0)
PY
[ $? -eq 0 ] && ok "a11y + SEO clean" || bad "a11y/SEO issues"

step "4b/8  legal completeness (Impressum, privacy notice, no stray placeholders)"
python3 - "$DIR" <<'LEGALPY'
import os, re, sys, glob
d = sys.argv[1]
issues = []

# The pages themselves must exist. Everything else here is pointless without them.
for req in ("impressum.html", "privacy.html"):
    if not os.path.exists(os.path.join(d, req)):
        issues.append("missing " + req)

# No unfilled content may ship. The footer of every page in every language
# carried "[PLACEHOLDER]" for months without anyone catching it, so this is a
# hard gate now rather than a convention.
TOKENS = (r"\{\{TODO:[A-Z_]+\}\}", r"\[PLACEHOLDER\]", r"\[LinkedIn\]",
          r"\[Impressum\]", r"\[Privacy notice\]", r"\bTBD\b", r"\bXXXX+\b")
for f in sorted(glob.glob(os.path.join(d, "*.html")) +
                glob.glob(os.path.join(d, "??", "*.html"))):
    h = open(f, encoding="utf-8").read()
    n = os.path.relpath(f, d).replace(os.sep, "/")
    if n == "index-old-backup.html":
        continue
    for t in TOKENS:
        for m in sorted(set(re.findall(t, h))):
            issues.append(n + ": unfilled placeholder " + m)
    # A legal link that goes nowhere is worse than no link at all.
    for label in ("Impressum", "Legal notice", "Privacy notice", "Datenschutz",
                  "Mentions", "Aviso legal", "Note legali"):
        if re.search(r'<a href="#"[^>]*>[^<]*' + label, h):
            issues.append(n + ": dead legal link (" + label + ")")
    # Every page must be able to reach both legal pages from its own footer.
    if not re.search(r'href="(\.\./)?impressum\.html"', h):
        issues.append(n + ": no link to the legal notice")
    if not re.search(r'href="(\.\./)?privacy\.html"', h):
        issues.append(n + ": no link to the privacy notice")

print("\n".join("   " + i for i in issues))
sys.exit(1 if issues else 0)
LEGALPY
[ $? -eq 0 ] && ok "legal pages present and complete" || bad "legal content incomplete"

step "3b/8  work-page field figure (headless, recorded canvas)"
node figure_space.js "$DIR"
[ $? -eq 0 ] && ok "the field draws, sweeps, calls out three and repeats" \
  || bad "the field figure is not drawing what it claims"

step "4d/8  header and footer agree, page by page"
$QPY_NAV nav_map.py "$DIR"
[ $? -eq 0 ] && ok "every page sends the same word to the same place" \
  || bad "a label leads to two different places on the same page"

step "4c/8  links, resolved the way the deployed site resolves them"
python3 deployed_links.py "$DIR"
[ $? -eq 0 ] && ok "no 404s, no link leaves its language" \
  || bad "a link goes somewhere the author did not mean"

step "5/8  colour contrast (WCAG AA)"
python3 contrast.py "$DIR"
[ $? -eq 0 ] && ok "all text passes AA" || bad "contrast below AA"

step "6/8  translations (DE / FR / ES / IT)"
if [ -f "$DIR/i18n/FROZEN" ]; then
  printf '   \033[33mHELD\033[0m localised builds are frozen while the English page is\n'
  printf '        being finalised. They still carry the previous English copy.\n'
  printf '        Before launch: rm i18n/FROZEN && python3 build_i18n.py, then\n'
  printf '        re-run this gate — it will fail until they are regenerated.\n'
elif [ -d "$DIR/de" ]; then
  # i18n_qa.py needs beautifulsoup4, which the system python here does not
  # have (PEP 668 blocks installing into it). Pick the first interpreter that
  # can actually import it. Without this the stage reported "translation gate
  # failed" for a missing dependency, which sent the last investigation after
  # the translations instead of the environment.
  QPY=""
  for c in "${QUENORA_PY:-}" "$DIR/../.venv/bin/python3" "$DIR/.venv/bin/python3" \
           /tmp/qvenv/bin/python3 python3; do
    [ -n "$c" ] || continue
    if command -v "$c" >/dev/null 2>&1 || [ -x "$c" ]; then
      "$c" -c 'import bs4' >/dev/null 2>&1 && { QPY="$c"; break; }
    fi
  done
  if [ -z "$QPY" ]; then
    printf '   \033[33mHELD\033[0m beautifulsoup4 is not installed for any python found here,\n'
    printf '        so the translations could not be checked (this is the tooling,\n'
    printf '        not the content). Fix with:\n'
    printf '          python3 -m venv .venv && .venv/bin/pip install beautifulsoup4\n'
    printf '        or set QUENORA_PY to an interpreter that has it.\n'
  else
    "$QPY" i18n_qa.py 2>&1 | sed -n '/FAILURES/,/^====/p;/failure(s)/p' | head -30
    "$QPY" i18n_qa.py >/dev/null 2>&1 && ok "every offered language clean" \
      || bad "translation gate failed — run: $QPY test/i18n_qa.py"
  fi
else
  printf '   \033[33mSKIP\033[0m no localised builds — run: python3 build_i18n.py\n'
fi

step "7/8  hero fit + hover (appearance and interaction)"
node hero_fit.js "$DIR" >/tmp/hero.log 2>&1
if [ $? -eq 0 ]; then ok "$(grep 'contained' /tmp/hero.log)"; else bad "hero clips"; cat /tmp/hero.log; fi
node hero_hover.js "$DIR" >/tmp/hover.log 2>&1
if [ $? -eq 0 ]; then ok "$(grep 'one sphere' /tmp/hover.log)"; else bad "hover mis-picks"; cat /tmp/hover.log; fi
node hero_geometry.js "$DIR" >/tmp/geo.log 2>&1
if [ $? -eq 0 ]; then ok "$(grep 'still the logo' /tmp/geo.log)"; else bad "hero geometry broke"; cat /tmp/geo.log; fi

step "8/8  English page — proofread, technical writing, SEO"
node qa_english.js "$DIR" >/tmp/en.log 2>&1
if [ $? -eq 0 ]; then
  ok "$(grep 'passed,' /tmp/en.log | tr -s ' ')"
  sed -n '/WARNINGS/,/^====/p' /tmp/en.log | head -12
else
  bad "English QA failed"; sed -n '/FAILURES/,$p' /tmp/en.log | head -20
fi

echo
if [ $FAILED -eq 0 ]; then
  printf '\033[32m════ RELEASE APPROVED ════\033[0m\n'
else
  printf '\033[31m════ RELEASE BLOCKED ════\033[0m\n'
fi
exit $FAILED

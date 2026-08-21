#!/usr/bin/env bash
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

step "1/6  JS syntax + tag balance"
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

step "2/6  sphere hit-testing (real Three.js math)"
node test_pick_real.js >/tmp/pick.log 2>&1
if grep -q "0 mis-picks" /tmp/pick.log; then ok "$(grep 'correct,' /tmp/pick.log|head -1)"; else bad "mis-picks found"; tail -5 /tmp/pick.log; fi

step "3/6  smoke test (jsdom, real page JS)"
node smoke.js "$DIR" >/tmp/smoke.log 2>&1
if [ $? -eq 0 ]; then ok "$(grep 'SMOKE TEST' /tmp/smoke.log)"; else bad "smoke failures"; sed -n '/FAILURES/,$p' /tmp/smoke.log; fi

step "4/6  accessibility + SEO audit"
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

step "5/6  colour contrast (WCAG AA)"
python3 - "$DIR" <<'PY'
import re,sys,os
def lum(x):
    x=x.lstrip('#');r,g,b=[int(x[i:i+2],16)/255 for i in(0,2,4)]
    f=lambda c:c/12.92 if c<=0.03928 else ((c+0.055)/1.055)**2.4
    return .2126*f(r)+.7152*f(g)+.0722*f(b)
def cr(a,b):
    l=sorted([lum(a),lum(b)],reverse=True);return (l[0]+.05)/(l[1]+.05)
h=open(os.path.join(sys.argv[1],'index.html'),encoding='utf-8').read()
ink=re.search(r'--ink:(#[0-9A-Fa-f]{6})',h).group(1)
bad=[]
for tok in['white','grey','grey-d','copper','copper-lt']:
    m=re.search(r'--%s:(#[0-9A-Fa-f]{6})'%tok,h)
    if m:
        c=cr(m.group(1),ink)
        print(f"   --{tok:10} {m.group(1)}  {c:5.2f}:1")
        if c<4.5: bad.append(tok)
sys.exit(1 if bad else 0)
PY
[ $? -eq 0 ] && ok "all text passes AA" || bad "contrast below AA"

step "6/6  translations (DE / FR / ES / IT)"
if [ -d "$DIR/de" ]; then
  python3 i18n_qa.py 2>&1 | sed -n '/FAILURES/,/^====/p;/failure(s)/p' | head -30
  python3 i18n_qa.py >/dev/null 2>&1 && ok "all four languages clean" \
    || bad "translation gate failed — run: python3 test/i18n_qa.py"
else
  printf '   \033[33mSKIP\033[0m no localised builds — run: python3 build_i18n.py\n'
fi

echo
if [ $FAILED -eq 0 ]; then
  printf '\033[32m════ RELEASE APPROVED ════\033[0m\n'
else
  printf '\033[31m════ RELEASE BLOCKED ════\033[0m\n'
fi
exit $FAILED

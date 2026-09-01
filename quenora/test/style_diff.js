/* Render every page and diff its computed styles against index.html, role by
   role, property by property. Nothing here is a list of things I decided to
   check — it compares the whole property set and reports whatever differs. */
const REF = '/index.html';
const PAGES = ['/engineering.html','/services.html','/work.html','/approach.html',
               '/contact.html','/products.html','/story.html','/impressum.html','/privacy.html',
               '/de/index.html','/de/engineering.html','/de/services.html','/de/work.html',
               '/de/approach.html','/de/contact.html','/de/products.html',
               '/fr/index.html','/fr/engineering.html','/fr/services.html','/fr/work.html',
               '/fr/approach.html','/fr/contact.html','/fr/products.html'];
const ROLES = {
  'body':        'body',
  'h1':          'h1',
  'h2':          'h2',
  'h3':          'h3',
  'body copy':   'main p:not(.mono):not(.ch):not(.kicker):not(.eyebrow):not(.lede)',
  'heading em':  'h1 em, h2 em, h3 em',
  'wordmark':    '.brand b, .brand',
  'nav link':    '.navlinks a',
  'CTA':         '.navcta',
  'footer':      'footer',
  'footer link': 'footer a',
  'mono label':  '.mono, .kicker, .ch, .figlab, .tag, h5',
};
const PROPS = ['color','backgroundColor','fontFamily','fontSize','fontWeight',
               'fontStyle','letterSpacing','lineHeight','textTransform',
               'borderTopColor','borderRadius','textDecorationColor'];

function sample(doc){
  const out = {};
  for(const [role, sel] of Object.entries(ROLES)){
    const el = doc.querySelector(sel);
    if(!el){ out[role] = null; continue; }
    const cs = doc.defaultView.getComputedStyle(el);
    const v = {};
    for(const p of PROPS) v[p] = cs[p];
    out[role] = v;
  }
  out['__selection'] = (()=>{ // ::selection is not on an element
    const rules = [...doc.styleSheets].flatMap(s=>{try{return [...s.cssRules]}catch(e){return[]}});
    const r = rules.find(r=>r.selectorText && r.selectorText.includes('selection'));
    return r ? r.style.cssText : null;
  })();
  return out;
}

async function load(f, url){
  f.src = url + '?d=' + Date.now();
  await new Promise(r=>{ f.onload = r; setTimeout(r, 1400); });
  await new Promise(r=>setTimeout(r, 120));
  return f.contentDocument;
}

const f = document.createElement('iframe');
f.style.cssText = 'position:fixed;left:-9999px;top:0;border:0;width:1200px;height:900px';
document.body.appendChild(f);

const ref = sample(await load(f, REF));
const report = [];
for(const p of PAGES){
  const got = sample(await load(f, p));
  const diffs = [];
  if(got.__selection !== ref.__selection)
    diffs.push('::selection  ' + (got.__selection||'none') + '   vs   ' + (ref.__selection||'none'));
  for(const role of Object.keys(ROLES)){
    const a = ref[role], b = got[role];
    if(a && !b){ diffs.push(role + ': absent on this page'); continue; }
    if(!a || !b) continue;
    for(const prop of PROPS){
      if(a[prop] !== b[prop]) diffs.push(role + '.' + prop + ': ' + b[prop] + '   vs   ' + a[prop]);
    }
  }
  report.push({page:p, n:diffs.length, diffs});
}
f.remove();
return report;

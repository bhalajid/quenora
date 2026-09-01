// ---------------------------------------------------------------
// Quenora — automated smoke test
// Loads each page in jsdom, executes its inline JS, and asserts that
// the interactive features actually work. No browser required.
// ---------------------------------------------------------------
const fs=require('fs'), path=require('path');
const {JSDOM,VirtualConsole}=require('jsdom');

const DIR=process.argv[2]||'..';
const PAGES=['index.html','capabilities.html','products.html','approach.html','work.html','contact.html'];
let pass=0, fail=0;
const failures=[];

function check(page,name,cond,detail=''){
  if(cond){pass++;}
  else{fail++;failures.push(`${page} :: ${name}${detail?'  ('+detail+')':''}`);}
}

async function load(file,reduceMotion=false){
  const html=fs.readFileSync(path.join(DIR,file),'utf8');
  const vc=new VirtualConsole();
  const errors=[];
  vc.on('jsdomError',e=>errors.push(e.message));
  vc.on('error',(...a)=>errors.push(a.join(' ')));
  const dom=new JSDOM(html,{
    runScripts:'dangerously', pretendToBeVisual:true, virtualConsole:vc,
    resources:undefined, url:'https://quenora.ai/'+file,
    beforeParse(w){
      // stubs jsdom lacks — must exist BEFORE page scripts run
      w.matchMedia=q=>({matches:reduceMotion&&/reduced-motion/.test(q),media:q,
        addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});
      w.IntersectionObserver=class{
        constructor(cb){this.cb=cb;}
        observe(el){setTimeout(()=>this.cb([{isIntersecting:true,target:el}],this),0);}
        unobserve(){} disconnect(){}
      };
      w.requestAnimationFrame=cb=>setTimeout(()=>cb(Date.now()),16);
      w.cancelAnimationFrame=id=>clearTimeout(id);
      w.scrollTo=()=>{};
      Object.defineProperty(w,'devicePixelRatio',{value:1});
      // Realistic corporate browser: 2D canvas works, WebGL is blocked.
      // (Returning null for BOTH was hiding real behaviour in the tests.)
      const noop=()=>{};
      const ctx2d={setTransform:noop,clearRect:noop,beginPath:noop,moveTo:noop,lineTo:noop,
        stroke:noop,fill:noop,arc:noop,fillText:noop,save:noop,restore:noop,closePath:noop,
        createLinearGradient:()=>({addColorStop:noop}),
        createRadialGradient:()=>({addColorStop:noop}),
        measureText:()=>({width:10}),
        set fillStyle(v){},get fillStyle(){return '';},
        set strokeStyle(v){},get strokeStyle(){return '';},
        set lineWidth(v){},get lineWidth(){return 1;},
        set font(v){},get font(){return '';},
        set globalAlpha(v){},get globalAlpha(){return 1;},
        set textAlign(v){},get textAlign(){return 'left';}};
      w.HTMLCanvasElement.prototype.getContext=function(type){
        return type==='2d' ? ctx2d : null;   // no WebGL, like managed Edge
      };
    }
  });
  const w=dom.window;
  await new Promise(r=>setTimeout(r,200));
  return {w,d:w.document,errors};
}

(async()=>{
for(const page of PAGES){
  const {w,d,errors}=await load(page);
  const src=fs.readFileSync(path.join(DIR,page),'utf8');

  // ---- no runtime errors ----
  check(page,'no JS runtime errors',errors.length===0,errors[0]);

  // ---- structure ----
  check(page,'has <main>',!!d.querySelector('main'));
  check(page,'exactly one <h1>',d.querySelectorAll('h1').length===1,
        d.querySelectorAll('h1').length+' found');
  check(page,'skip link present',!!d.querySelector('a.skip'));
  check(page,'favicon present',!!d.querySelector('link[rel="icon"]'));
  check(page,'og:title present',!!d.querySelector('meta[property="og:title"]'));
  check(page,'canonical present',!!d.querySelector('link[rel="canonical"]'));

  // ---- nav links resolve to real files ----
  const links=[...d.querySelectorAll('a[href$=".html"]')].map(a=>a.getAttribute('href'));
  const bad=[...new Set(links)].filter(h=>!fs.existsSync(path.join(DIR,h)));
  check(page,'all internal links resolve',bad.length===0,bad.join(','));

  // ---- images have alt ----
  const noalt=[...d.querySelectorAll('img')].filter(i=>!i.hasAttribute('alt'));
  check(page,'all images have alt',noalt.length===0);

  // ---- assistant panel ----
  const fab=d.getElementById('aiFab'), panel=d.getElementById('aiPanel');
  if(fab&&panel){
    check(page,'assistant closed by default',!panel.classList.contains('open'));
    fab.dispatchEvent(new w.MouseEvent('click',{bubbles:true}));
    check(page,'assistant opens on click',panel.classList.contains('open'));
    check(page,'aria-expanded syncs',fab.getAttribute('aria-expanded')==='true');
    /* The requirement is that a chip can be reached and fired from the
       keyboard. The inner pages do that with div + role=button + tabindex;
       the homepage uses a real <button>, which is keyboard-accessible by
       definition and needs neither. Assert the requirement, not one spelling
       of it. */
    const chip=d.querySelector('.chip, .ai-chip');
    const nativeBtn = chip && chip.tagName==='BUTTON'
                   && (chip.getAttribute('type')||'submit')!=='submit';
    const ariaBtn   = chip && chip.getAttribute('role')==='button'
                   && chip.hasAttribute('tabindex');
    check(page,'chips keyboard-accessible', !!(nativeBtn || ariaBtn));
    if(chip){
      chip.dispatchEvent(new w.MouseEvent('click',{bubbles:true}));
      await new Promise(r=>setTimeout(r,50));
      check(page,'chip posts a user message',!!d.querySelector('.ai-msg.user'));
    }
    w.dispatchEvent(new w.KeyboardEvent('keydown',{key:'Escape'}));
    check(page,'Escape closes assistant',!panel.classList.contains('open'));
  }

  // ---- homepage-only: automation demo ----
  // The homepage is the editorial scroll narrative. Features that only
  // exist on the legacy layout are asserted only when present, so the
  // suite covers whichever homepage is deployed.
  if(page==='index.html' && d.querySelector('.demo-tab')){
    const tabs=[...d.querySelectorAll('.demo-tab')];
    check(page,'demo has 5 scenarios',tabs.length===5,tabs.length+' tabs');
    check(page,'tabs have role=tab',tabs.every(t=>t.getAttribute('role')==='tab'));
    check(page,'tabs focusable',tabs.every(t=>t.hasAttribute('tabindex')));
    const btn=d.getElementById('demoBtn');
    check(page,'automate button disabled before steps load',btn&&btn.disabled===true);
    await new Promise(r=>setTimeout(r,4200));   // let all 5 steps reveal
    check(page,'automate button enabled after reveal',btn&&btn.disabled===false);
    const timer=d.getElementById('demoTimer');
    check(page,'timer accumulated real time',timer&&/h|m|s/.test(timer.textContent)&&timer.textContent!=='0s',
          timer&&timer.textContent);
    if(btn&&!btn.disabled){
      btn.dispatchEvent(new w.MouseEvent('click',{bubbles:true}));
      await new Promise(r=>setTimeout(r,1800));
      const badge=d.getElementById('resultBadge');
      check(page,'result badge shows after automating',badge&&badge.classList.contains('show'));
      check(page,'result shows a reduction',badge&&/%/.test(badge.textContent),badge&&badge.textContent.slice(0,40));
    }
    // switching tabs resets
    if(tabs[2]){
      tabs[2].dispatchEvent(new w.MouseEvent('click',{bubbles:true}));
      await new Promise(r=>setTimeout(r,60));
      check(page,'tab switch sets aria-selected',tabs[2].getAttribute('aria-selected')==='true');
      check(page,'tab switch resets button',d.getElementById('demoBtn').textContent.includes('Automate'));
    }
  }

  if(page==='index.html' && d.querySelector('.nine-row')){
    // ── legacy layout only: the sphere/SVG homepage ──
    check(page,'nine principles rendered',d.querySelectorAll('.nine-row').length===9,
          d.querySelectorAll('.nine-row').length+' rows');
    const svg=d.getElementById('svgMark');
    check(page,'SVG hero present in HTML (no JS required)',!!svg);
    check(page,'SVG hero has all nine circles',
          svg?svg.querySelectorAll('.sm').length===9:false);
    check(page,'SVG circles labelled for screen readers',
          svg?[...svg.querySelectorAll('.sm')].every(c=>c.hasAttribute('aria-label')):false);
  }

  if(page==='index.html'){
    // ── applies to whichever homepage is deployed ──
    const h1=d.querySelector('h1').textContent.replace(/\s+/g,' ').trim();
    check(page,'headline does not open on a negative',
          !/^(we (don'?t|do not|never))/i.test(h1),h1.slice(0,50));
    check(page,'headline is short enough to scan',h1.split(/\s+/).length<=9,h1);
    check(page,'hero canvas present',!!d.getElementById('heroCanvas'));
    check(page,'hero is 2D canvas, not WebGL',
          !/getContext\(\s*['"]webgl/.test(src));
    check(page,'no Three.js dependency',!/THREE\./.test(src));
    check(page,'no external script tags',!/<script[^>]*\bsrc=/.test(src),
          'the hero must not depend on a CDN');
    check(page,'reduced-motion honoured',/prefers-reduced-motion/.test(src));
  }

  // ---- contact form ----
  if(page==='contact.html'){
    const f=d.getElementById('briefForm');
    check(page,'form present',!!f);
    check(page,'name has autocomplete',d.getElementById('f-name')?.hasAttribute('autocomplete'));
    check(page,'email has autocomplete',d.getElementById('f-email')?.hasAttribute('autocomplete'));
  }

  w.close();
}

// ---- corporate/VDI case: OS animation effects disabled ----
// The editorial homepage has no manual motion toggle — it obeys the OS
// setting outright. The legacy layout shipped a toggle. Assert whichever
// contract the deployed homepage actually offers.
{
  const page='index.html (reduced-motion)';
  const {w,d,errors}=await load('index.html',true);
  check(page,'no JS runtime errors',errors.length===0,errors[0]);

  const t=d.getElementById('flowToggle');
  if(t){
    check(page,'defaults to paused, honouring the OS setting',
          t.textContent==='Play animation'&&t.getAttribute('aria-pressed')==='false',
          t.textContent+'/'+t.getAttribute('aria-pressed'));
    t.dispatchEvent(new w.MouseEvent('click',{bubbles:true}));
    check(page,'user can opt in to animation',
          t.textContent==='Pause animation'&&t.getAttribute('aria-pressed')==='true');
    t.dispatchEvent(new w.MouseEvent('click',{bubbles:true}));
    check(page,'user can pause again',t.getAttribute('aria-pressed')==='false');
  }else{
    // no toggle: the page must simply not animate, and must stay readable
    check(page,'reduced-motion rules present in CSS',
          /@media \(prefers-reduced-motion:\s*reduce\)/.test(
            fs.readFileSync(path.join(DIR,'index.html'),'utf8')));
    check(page,'loader does not trap the page',!d.getElementById('ld'));
  }

  // content must be readable whether or not motion runs
  const rv=[...d.querySelectorAll('.rv')];
  check(page,'scroll-reveal content exists',rv.length>0);
  check(page,'scroll-reveal content not stuck hidden',
        rv.every(el=>el.classList.contains('in')||el.style.opacity==='1'),
        rv.filter(el=>!el.classList.contains('in')&&el.style.opacity!=='1').length+' hidden');
  w.close();
}

// ---- default case: motion allowed ----
{
  const page='index.html (motion allowed)';
  const {w,d}=await load('index.html',false);
  const t=d.getElementById('flowToggle');
  if(t){
    check(page,'defaults to playing',t.getAttribute('aria-pressed')==='true');
  }else{
    check(page,'hero canvas is present and drivable',!!d.getElementById('heroCanvas'));
  }
  w.close();
}

// ---- terminology consistency across the whole site ----
{
  const fsx=require('fs'), px=require('path');
  const BANNED=[
    [/\bthree disciplines\b/i,'"three disciplines" (undefined term)'],
    [/\bservice lines?\b/i,'"service line(s)" — use "capabilities"'],
    [/\ball nine services\b/i,'"all nine services" — use "capabilities"'],
    [/\bour offerings\b/i,'"offerings" — use "capabilities"'],
    [/\bpillars?\b/i,'"pillar(s)" — use "core capabilities"']
  ];
  for(const f of PAGES){
    const raw=fsx.readFileSync(px.join(DIR,f),'utf8');
    const body=raw.replace(/<(script|style)[^>]*>[\s\S]*?<\/\1>/g,'');
    const txt=body.replace(/<[^>]+>/g,' ').replace(/\s+/g,' ');
    for(const [re,label] of BANNED){
      check(f,'terminology: no '+label,!re.test(txt),
            re.test(txt)?(txt.match(re)||[''])[0]:'');
    }
    // British English throughout — the firm sells into Europe
    const am=(txt.match(/\b[A-Za-z]+(?:ization|ized|izing)\b/g)||[])
             .filter(w=>!/^(size|sized|sizing|resize|resized|resizing)$/i.test(w));
    check(f,'British spelling in prose',am.length===0,am.join(','));

    // nav label must match the page it points at
    if(/href="services\.html"/.test(body)){
      check(f,'nav calls it Capabilities, not Services',
            !/>\s*Services\s*</.test(body));
    }
  }
}

console.log('='.repeat(64));
console.log(`SMOKE TEST:  ${pass} passed, ${fail} failed`);
console.log('='.repeat(64));
if(failures.length){console.log('\nFAILURES:');failures.forEach(f=>console.log('  ✗ '+f));}
process.exit(fail?1:0);
})();

(function(){
  var fab=document.getElementById('aiFab'), panel=document.getElementById('aiPanel'),
      body=document.getElementById('aiBody'), form=document.getElementById('aiForm'),
      input=document.getElementById('aiInput'), sug=document.getElementById('aiSuggest');
  if(!fab||!panel||!body) return;
  /* The widget needs a browser, and it is now on every page — including the
     work page, whose field figure is verified by a headless harness running a
     minimal DOM stub with no location. Checking the elements is not enough:
     that stub returns something truthy for every id. Check for the thing the
     code actually uses. */
  if(typeof location==='undefined'||typeof fab.addEventListener!=='function') return;
  var opened=false;
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  function close(){
    panel.classList.remove('open');
    fab.classList.remove('open');
    fab.setAttribute('aria-expanded','false');
  }

  function add(t,who,html){
    var m=document.createElement('div');
    m.className='ai-msg '+who;
    /* Anything a visitor typed goes in as text, always — that is the XSS
       guard and it does not move. Only the panel's own markup, built here
       from esc()'d passages, is allowed in as HTML. */
    if(html && who==='bot') m.innerHTML=t; else m.textContent=t;
    body.appendChild(m); body.scrollTop=body.scrollHeight;
  }
  function bot(t){
    if(reduce){ add(t,'bot',true); return; }
    var w=document.createElement('div');
    w.className='ai-msg bot';
    w.innerHTML='<span class="ai-typing"><i></i><i></i><i></i></span>';
    body.appendChild(w); body.scrollTop=body.scrollHeight;
    setTimeout(function(){ w.remove(); add(t,'bot',true); }, 420+Math.random()*260);
  }

  var A=[
    [['automation','automate','workflow','process','unattended','rpa'],
     "Automation is capability 02 and one of the three core ones. We automate the processes a business repeats — approvals, handoffs, reconciliations, the reporting someone does on a Tuesday. The part that matters is the exceptions: an automation is only trustworthy if it knows which cases it should not decide, and drawing that line is most of the work."],
    [['what do you','services','offer','do you do','capabilit'],
     "Nine capabilities. Three are core — platform and deployment engineering, process and workflow automation, and AI integration — because everything runs through them. The other six step in only when the work needs them. Nothing is handed to a subcontractor you’ve never met."],
    [['who are you','about','founder','balaji','team','how big','size'],
     "Quenora is founder-led, founded in 2025 by Balaji Durai. Before Quenora he ran transformation work for multinational manufacturers, retail banking and life sciences groups; those systems went on to be used by more than 100,000 people. We work from Heilbronn, internationally, in German, French and English."],
    [['different','why you','compare','competitor','large consult','big four'],
     "Use a large consultancy for a multi-year, multi-country programme with a thousand stakeholders — they’re built for that and we’re not. For a single system that needs to reach production this year, the person who scopes your engagement is the person who does the work and the person you call when it breaks."],
    [['long','time','timeline','how fast','duration','weeks'],
     "Six phases, from framing to handover, and each carries an exit condition written into the statement of work. Most engagements run twelve to fourteen weeks end to end, with a working pilot well before that. The engagement is designed to end."],
    [['cost','price','pricing','budget','how much','rate'],
     "Scoped to outcomes rather than day rates. Chapter 08 on the homepage states how it’s priced rather than making you sit through three meetings to find out. A briefing gives you a real number, not a range designed to get a second meeting."],
    [['work','case','client','example','project','reference'],
     "Three patterns come up most: invoice processing across unintegrated ERP instances, support triage with knowledge retrieval, and legacy modernisation with predictive scheduling. They are described by shape rather than by client name, and the figures on the Work page are illustrative of the pattern rather than audited results."],
    [['product','framework','accelerator','toolkit','blueprint'],
     "Five: the Automation Accelerator, the Enterprise Agent Framework, the AI Readiness Assessment, the Governance Toolkit and the Platform Blueprint. They are frameworks you own rather than licences you rent. The Products page has the detail."],
    [['platform','infrastructure','data','deploy'],
     "Platform and deployment engineering is capability 01 and core: data architecture, infrastructure and the internal platforms that make AI repeatable rather than a one-off — then deployment onto them, with monitoring and handover documentation that survives contact with reality."],
    [['govern','security','compliance','risk','gdpr','eu ai act','audit'],
     "Model risk, data privacy and audit trails are built in from the start rather than added as a separate workstream. For European clients that includes GDPR and EU AI Act alignment."],
    [['agent','copilot','chatbot','llm','model'],
     "Purpose-built agents wired into the systems that actually hold the work — ERP, CRM, service desk — rather than a chatbot bolted onto a homepage. The hard part is almost never the model."],
    [['contact','talk','call','briefing','email','reach'],
     "Start a conversation from the button in the header, or email info@quenora.ai. A first call is a briefing, not a pitch."],
    [['language','german','french','english','deutsch'],
     "German, French and English."],
    [['where','located','based','heilbronn','germany','office'],
     "Based in Heilbronn, Germany, working internationally."]
  ];

  /* ═══ RETRIEVAL ═══════════════════════════════════════════════════════
     Answers are passages from this site, ranked against the question with
     BM25. No model, so it cannot invent a capability the firm does not have
     — which is the failure the whole page argues against — and no third
     party ever sees what a visitor typed, so the privacy notice stays true.

     The index is fetched the first time the panel opens, not on page load:
     it costs a visitor who never asks anything nothing at all. */
  var IDX = null, IDXSTATE = 'cold';

  /* Everything inside a <script> is invisible to the localisation build, so
     without this the German page refused in English and matched on English
     synonyms — "wer seid ihr" and "wo sitzt ihr" both came back empty. Same
     mechanism as the engineering page's figure labels. */
  var LANG = document.documentElement.lang || 'en';
  var UI = {
    en:{ none:'Nothing on this site matches that, and I would rather say so than find words in common and call it an answer. Email <a href="mailto:info@quenora.ai">info@quenora.ai</a>, or press Start a conversation below.',
         many:function(n){ return n+' passages from this site.'; },
         one:'One passage from this site.',
         notit:'Not what you asked?', email:'Email us',
         team:'Written by the team.', more:'Ask something else' },
    de:{ none:'Dazu steht nichts auf dieser Website, und das sage ich Ihnen lieber, als gemeinsame Wörter zu finden und es eine Antwort zu nennen. Schreiben Sie an <a href="mailto:info@quenora.ai">info@quenora.ai</a> oder starten Sie unten ein Gespräch.',
         many:function(n){ return n+' Passagen von dieser Website.'; },
         one:'Eine Passage von dieser Website.',
         notit:'Nicht das, was Sie gefragt haben?', email:'Schreiben Sie uns',
         team:'Vom Team geschrieben.', more:'Fragen Sie etwas anderes' },
    fr:{ none:'Rien sur ce site ne correspond, et je préfère vous le dire plutôt que de trouver des mots en commun et d’appeler cela une réponse. Écrivez à <a href="mailto:info@quenora.ai">info@quenora.ai</a>, ou engagez la conversation ci-dessous.',
         many:function(n){ return n+' passages de ce site.'; },
         one:'Un passage de ce site.',
         notit:'Ce n’est pas votre question ?', email:'Écrivez-nous',
         team:'Écrit par l’équipe.', more:'Posez une autre question' }
  }[LANG] || null;
  if(!UI) UI = { none:'Nothing on this site matches that.', many:function(n){return n+' passages.';},
                 one:'One passage.', notit:'', email:'Email', team:'', more:'' };

  function fold(s){
    return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'');
  }
  var STOP = ('a an and are as at be but by for from has have if in into is it its of on or '
    +'that the their then there these this to was were what when which will with you your '
    +'our we us how why can does do not no der die das den dem des ein eine einer eines und '
    +'oder aber ist sind war waren sein ihre ihr wir uns sie ihnen mit von zu im am auf fur '
    +'als auch nicht kein wie wer wo wenn dann dass le la les un une des du de et ou mais '
    +'est sont etait etaient etre leur nos nous vous avec pour dans sur comme aussi ne pas '
    +'que quoi quand si').split(' ');
  var STOPSET = {}; STOP.forEach(function(w){ STOPSET[w]=1; });

  function terms(s){
    var out=[], parts=fold(s).split(/[^a-z0-9]+/);
    for(var i=0;i<parts.length;i++){
      var t=parts[i];
      if(t.length>2 && !STOPSET[t]){
        out.push(t);
        /* one suffix strip, not a stemmer: "certifications" has to reach
           "certification", and "weeks" has to reach "week". Anything more
           aggressive starts matching words that only look alike. */
        if(t.length>4 && /(s|es)$/.test(t)) out.push(t.replace(/(es|s)$/,''));
      }
    }
    return out;
  }

  /* BM25 is lexical: it cannot know that "how long" is asking about the
     fourteen weeks, or that "who owns the code" is answered by "you keep
     everything". This is the bridge — the words buyers use, mapped to the
     words the site uses. Query side only, so it never distorts a passage.
     Hand-written and short on purpose: a wrong synonym here surfaces the
     wrong passage, which is the one failure this design exists to avoid. */
  var ALIAS = {
    long:['weeks','phases','fourteen'],
    duration:['weeks','phases','fourteen'], timeline:['weeks','phases'],
    take:['weeks','phases'], time:['weeks','phases'],
    own:['keep','yours','handover','owner'], owns:['keep','yours','owner'],
    owner:['keep','yours','handover'], ownership:['keep','yours','handover'],
    keep:['yours','own','handover'], afterwards:['handover','leave','ends'],
    cost:['priced','costs'],
    price:['priced','cost'], pricing:['priced','cost'],
    fee:['priced','cost'], budget:['priced','cost'],
    charge:['priced','cost'], expensive:['priced','cost'],
    change:['governance','control','approvals'],
    security:['governance','permission','audit','access'],
    gdpr:['privacy','data','governance'], privacy:['data','governance'],
    team:['who','firm','founder','size'], size:['firm','team','who'],
    hire:['firm','team','who'], support:['operations','monitoring','runbook'],
    start:['frame','first','begin'], contract:['statement','work','exit'],
    guarantee:['exit','condition','number','measure'],
    proof:['harness','measure','number','evidence'],
    references:['reference','case','studies','call'],
    certification:['iso','soc','attestations'],
    certifications:['iso','soc','attestations'],
    certified:['iso','soc','attestations'], compliance:['governance','iso','soc'],
    big:['firm','small','size','depth'], many:['firm','small','size'],
    people:['firm','team','size','depth'], headcount:['firm','size','depth'],
    staff:['firm','team','size'],
    who:['hiring','founder','firm','balaji','founded'],
    where:['heilbronn','germany','based'],
    you:['quenora','firm','hiring'], about:['hiring','founder','firm','founded'],
    behind:['founder','hiring','balaji'], founder:['balaji','hiring','founded'],
    based:['heilbronn','germany','where'], where:['heilbronn','germany','based'],
    located:['heilbronn','germany','based'], office:['heilbronn','germany','based'],
    country:['heilbronn','germany'], languages:['german','french','english'],
    language:['german','french','english']
  };
  /* the same bridge in the two other published languages */
  var ALIAS_DE = {
    wer:['balaji','inhabergefuhrt','firma','gegrundet'],
    wo:['heilbronn','deutschland','sitz'],
    seid:['quenora','firma'], sitzt:['heilbronn','deutschland','sitz'],
    sitz:['heilbronn','deutschland'], standort:['heilbronn','deutschland','sitz'],
    kostet:['kosten','gekostet','zusammensetzt'], kosten:['kostet','gekostet'],
    lange:['wochen','phasen','vierzehn','dauert'],
    dauer:['wochen','phasen','dauert'], dauert:['wochen','phasen'],
    team:['firma','inhabergefuhrt'], gehort:['ubergabe','ihnen'],
    sicherheit:['governance','zugriff','audit'],
    zertifizierung:['iso','soc'], zertifiziert:['iso','soc'],
    sprachen:['deutsch','franzosisch','englisch'],
    sprache:['deutsch','franzosisch','englisch']
  };
  var ALIAS_FR = {
    qui:['balaji','fondateur','cabinet','dirige'],
    etes:['quenora','cabinet','dirige'],
    situes:['heilbronn','allemagne','siege'], situe:['heilbronn','allemagne','siege'],
    base:['heilbronn','allemagne','siege'], siege:['heilbronn','allemagne'],
    coute:['tarife','cout'], cout:['tarife'], couts:['tarife','cout'],
    tarif:['tarife','cout'], budget:['tarife','cout'],
    duree:['semaines','phases'], temps:['semaines','phases'],
    longtemps:['semaines','phases'],
    equipe:['cabinet','fondateur'], appartient:['transmission','appartiennent'],
    certification:['iso','soc'], securite:['gouvernance','acces'],
    langues:['allemand','francais','anglais'],
    langue:['allemand','francais','anglais']
  };
  if(LANG==='de') for(var dk in ALIAS_DE) ALIAS[dk]=ALIAS_DE[dk];
  if(LANG==='fr') for(var fk in ALIAS_FR) ALIAS[fk]=ALIAS_FR[fk];
  function expand(qs){
    var seen={}, out=[];
    qs.forEach(function(t){
      if(!seen[t]){ seen[t]=1; out.push(t); }
      (ALIAS[t]||[]).forEach(function(a){ if(!seen[a]){ seen[a]=1; out.push(a); } });
    });
    return out;
  }

  function indexDocs(docs){
    var df={}, total=0;
    docs.forEach(function(d){
      d.f={}; d.hf={};
      terms(d.h).forEach(function(t){ d.hf[t]=1; });
      var ts=terms(d.h+' '+d.t);
      ts.forEach(function(t){ d.f[t]=(d.f[t]||0)+1; });
      d.l=ts.length; total+=d.l;
      for(var t in d.f) df[t]=(df[t]||0)+1;
    });
    var N=docs.length, idf={};
    for(var t in df) idf[t]=Math.log(1+(N-df[t]+0.5)/(df[t]+0.5));
    return {docs:docs, idf:idf, avg:total/Math.max(1,N)};
  }

  /* BM25, the standard parameters. k1 damps a term repeated many times in one
     passage; b normalises for passage length so a long chapter does not win
     on volume alone. */
  function rank(q){
    if(!IDX) return [];
    var raw=terms(q);
    /* "who are you" is three stopwords, so the query came out empty and the
       panel refused to answer the most basic question a visitor asks. When
       stripping leaves nothing, keep the words. */
    if(!raw.length){
      raw = fold(q).split(/[^a-z0-9]+/).filter(function(t){ return t.length>2; });
    }
    var qs=expand(raw), k1=1.5, b=0.75, out=[];
    if(!raw.length) return [];
    IDX.docs.forEach(function(d){
      var sc=0, hit=0;
      qs.forEach(function(t){
        var f=d.f[t]; if(!f) return;
        hit++;
        var idf=IDX.idf[t]||0;
        sc += idf * (f*(k1+1)) / (f + k1*(1-b+b*d.l/IDX.avg));
        /* A question that names the heading is asking for that section. The
           body alone ranked "what does it cost" onto a paragraph about the
           cost of a bad design, over the chapter actually headed pricing. */
        if(d.hf[t]) sc += idf * 1.8;
      });
      if(hit) out.push({d:d, s:sc, hit:hit/raw.length});
    });
    out.sort(function(a,b2){ return b2.s-a.s; });
    return out;
  }

  function esc(t){ return t.replace(/&/g,'&amp;').replace(/</g,'&lt;'); }

  function answer(q){
    var hits = rank(q);
    if(!hits.length){
      bot(UI.none);
      return;
    }
    /* Measuring this made the design decision. "can you build me a chatbot for
       my shop" scored 7.62 — higher than "what does it cost" at 3.40 — because
       score is dominated by rare terms, not by whether the question was
       answered. No threshold separates the two. So this stops asserting an
       answer and shows what it found, which is what it actually has: a search
       over the site's own sentences, with the reader judging relevance. */
    var top = hits.slice(0, 3).filter(function(h, i){
      return i === 0 || h.s > hits[0].s * 0.42;
    });
    var html = '';
    var lastHead = null;
    top.forEach(function(h, i){
      html += (i ? '<span class="ai-more">' : '<span class="ai-first">') + esc(h.d.t);
      /* three passages from one chapter repeated its name three times */
      if(h.d.h !== lastHead){
        html += '<a class="ai-src" href="' + h.d.u + '">' + esc(h.d.h) + '</a>';
        lastHead = h.d.h;
      }
      html += '</span>';
    });
    html += '<span class="ai-foot">'
         +  (top.length > 1 ? UI.many(top.length) : UI.one)
         +  ' ' + UI.notit + ' <a href="mailto:info@quenora.ai">' + UI.email + '</a>.</span>';
    bot(html);
  }

  function ask(q){
    q=(q||'').trim(); if(!q) return;
    add(q,'user');
    /* The curated answers were written for the questions buyers actually ask
       and are better than any passage retrieval can surface for them. The
       rewrite left them unused; they belong in front of it, with retrieval
       carrying everything they do not cover. */
    /* the curated answers are English prose and were never translated,
       so a German visitor got English text. Retrieval covers those pages,
       and its passages are already in their language. */
    var kq = LANG==='en' ? q.toLowerCase() : '\u0000';
    for(var ci=0; ci<A.length; ci++){
      for(var cj=0; cj<A[ci][0].length; cj++){
        if(kq.indexOf(A[ci][0][cj]) > -1){
          bot(esc(A[ci][1]) + '<span class="ai-foot">' + UI.team
            + ' <a href="mailto:info@quenora.ai">' + UI.more + '</a>.</span>');
          return;
        }
      }
    }
    if(IDX){ answer(q); return; }
    if(IDXSTATE==='failed'){ answer(q); return; }
    /* No placeholder bubble: bot() already shows a typing indicator, and the
       earlier version removed body.lastChild, which during that animation is
       the indicator rather than the placeholder — so the '…' stayed. */
    loadIndex().then(function(){ answer(q); });
  }

  function loadIndex(){
    if(IDXSTATE==='loading' || IDXSTATE==='ready') return IDXSTATE_P;
    IDXSTATE='loading';
    IDXSTATE_P = fetch(ASSET_BASE+'assistant.json')
      .then(function(r){ if(!r.ok) throw 0; return r.json(); })
      .then(function(j){ IDX=indexDocs(j.docs); IDXSTATE='ready'; })
      .catch(function(){ IDXSTATE='failed'; });
    return IDXSTATE_P;
  }
  var IDXSTATE_P = null;
  /* /de/ and /fr/ each ship their own index; the page knows which it is */
  var ASSET_BASE = (location.pathname.match(/^\/(de|fr)(?:\/|$)/) || [null,''])[1];
  ASSET_BASE = ASSET_BASE ? '/'+ASSET_BASE+'/' : '/';

  function toggle(){
    var open=panel.classList.toggle('open');
    fab.classList.toggle('open', open);
    fab.setAttribute('aria-expanded', open?'true':'false');
    if(open && !opened){
      opened=true;
      setTimeout(function(){
        var g=document.getElementById('aiGreet');
        bot(g ? g.textContent.trim() : 'Ask anything about Quenora.');
      }, 260);
    }
    if(open) setTimeout(function(){ input && input.focus(); }, 320);
  }

  fab.addEventListener('click', toggle);
  if(form) form.addEventListener('submit', function(e){
    e.preventDefault(); ask(input.value); input.value='';
  });
  if(sug) sug.addEventListener('click', function(e){
    var c=e.target.closest('.ai-chip'); if(!c) return;
    /* the assistant's job is to hand over, not to hold on to people */
    if(c.getAttribute('data-act')==='contact'){
      close();
      /* The form is on the home page. On the other ten pages there is nothing
         to scroll to, and the button used to do nothing at all — silently,
         which is the worst way for a hand-off to fail. Elsewhere it goes to
         the contact page, in the visitor's own language. */
      var cl=document.getElementById('climax');
      if(cl){
        cl.scrollIntoView({behavior: reduce?'auto':'smooth', block:'start'});
        setTimeout(function(){
          var f=document.getElementById('cfName'); if(f) f.focus();
        }, reduce?0:700);
      } else {
        location.href = ASSET_BASE + 'contact';
      }
      return;
    }
    ask(c.getAttribute('data-q'));
  });
  addEventListener('keydown', function(e){
    if(e.key==='Escape' && panel.classList.contains('open')){
      close();
      fab.focus();
    }
  });
})();

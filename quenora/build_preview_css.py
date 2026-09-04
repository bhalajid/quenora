#!/usr/bin/env python3
"""
build_preview_css.py — the preview stylesheet, injected between markers.

PREVIEW ONLY, on the `infographics` branch.

Written after losing every style block twice. The generators rewrite the
markup, so re-running them means checking index.html out from main first — and
that silently took the hand-added CSS with it. The rail rendered as
display:block, six stops 1255px tall each, an 8000px chapter of nothing. The
markup was right and the page was wrong, which is the hardest kind to spot.

So the CSS lives here, delimited, idempotent, and re-applied by build.sh on
every run. Same discipline as the widget and the nav: nothing hand-placed that
a regeneration can drop.
"""
import os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
M = ('/*PREVIEW:CSS*/', '/*/PREVIEW:CSS*/')

RAIL = '''
/* ── the six phases, summarised ────────────────────────────────────────
   The home page used to retell the whole method: 432 words whose titles and
   exit conditions are word for word the same as approach.html. This is a
   summary — six stops, a mark, a name, the weeks, the title on hover — and
   each stop links into its gate on approach.html. That link is also how the
   tooltip works on a phone, where there is no hover to give. */
.ph{list-style:none;margin:var(--sp5) 0 0;padding:0;display:grid;
  grid-template-columns:repeat(6,minmax(0,1fr));position:relative}
.ph::before{content:'';position:absolute;left:7px;right:7px;top:7px;height:1px;
  background:linear-gradient(90deg,var(--copper) 0%,rgba(201,122,60,.5) 62%,
    rgba(201,122,60,.10) 100%)}
.ph-stop{position:relative}
.ph-link{position:relative;display:flex;flex-direction:column;gap:5px;
  padding:26px 16px 14px 0;text-decoration:none;border-radius:3px}
.ph-dot{position:absolute;left:0;top:0;width:15px;height:15px;border-radius:50%;
  background:var(--copper);box-shadow:0 0 0 5px var(--void);
  transition:transform .2s var(--e)}
.ph-stop.last .ph-dot{background:transparent;border:1.5px solid var(--copper)}
.ph-mark{width:22px;height:22px;color:var(--t3);margin-bottom:2px;
  transition:color .2s var(--e),transform .2s var(--e)}
.ph-name{color:var(--t1);font-size:.66rem;letter-spacing:.14em;
  text-transform:uppercase;margin:0}
.ph-dur{color:var(--t3);font-size:.6rem;letter-spacing:.12em;
  text-transform:uppercase;margin:0}
.ph-link:hover .ph-dot,.ph-link:focus-visible .ph-dot{transform:scale(1.25)}
.ph-link:hover .ph-mark,.ph-link:focus-visible .ph-mark{color:var(--copper-lt)}
.ph-link:hover .ph-name,.ph-link:focus-visible .ph-name{color:var(--copper-lt)}
.ph-link:hover .ph-dur,.ph-link:focus-visible .ph-dur{color:var(--t2)}
.ph-link:focus-visible{outline:2px solid var(--signal);outline-offset:3px}
.ph-tip{position:absolute;left:0;bottom:calc(100% - 18px);z-index:5;
  min-width:190px;max-width:250px;background:rgba(20,22,30,.97);
  border:1px solid var(--line2);border-radius:3px;padding:9px 12px;
  font-size:.86rem;line-height:1.35;color:var(--t1);opacity:0;
  transform:translateY(5px);pointer-events:none;
  transition:opacity .18s var(--e),transform .18s var(--e)}
.ph-tip em{font-family:'Playfair Display',Georgia,serif;font-style:italic;color:var(--ember)}
.ph-link:hover .ph-tip,.ph-link:focus-visible .ph-tip{opacity:1;transform:none}
.ph-stop:nth-child(n+5) .ph-tip{left:auto;right:16px}
@media(max-width:760px){
  .ph{grid-template-columns:minmax(0,1fr);row-gap:0}
  .ph::before{left:7px;right:auto;top:7px;bottom:22px;height:auto;width:1px;
    background:linear-gradient(180deg,var(--copper) 0%,rgba(201,122,60,.5) 62%,
      rgba(201,122,60,.10) 100%)}
  .ph-link{padding:0 0 20px 30px;display:grid;
    grid-template-columns:auto 1fr auto;align-items:center;gap:4px 12px}
  .ph-mark{grid-row:1 / span 2;width:20px;height:20px;margin:0}
  .ph-name{grid-column:2}
  .ph-dur{grid-column:3;grid-row:1}
  .ph-tip{position:static;opacity:1;transform:none;grid-column:2 / -1;
    background:none;border:0;padding:0;min-width:0;max-width:none;
    font-size:.92rem;color:var(--t2)}
  .ph-stop:last-child .ph-link{padding-bottom:0}
}

/* ── chapters 02, 04, 05 ───────────────────────────────────────────────
   Marks in the wordmark's vocabulary — circles and one stroke — so they read
   as a family rather than icons bought by the set. */
.ch3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:var(--sp3);
  margin-top:var(--sp5)}
@media(max-width:820px){.ch3{grid-template-columns:minmax(0,1fr);gap:var(--sp2)}}
.ch-card{border-top:1px solid var(--line2);padding:20px 0 0;display:block;
  text-decoration:none}
/* every card responds to the pointer, whether or not it leads anywhere. The
   three situations in chapter 02 are a diagnosis, not a destination, so they
   light up without pretending to be links. */
.ch-card{transition:border-color .2s var(--e)}
.ch-card:hover{border-top-color:var(--copper)}
.ch-card:hover .ch-mark{color:var(--copper-lt);transform:translateY(-2px)}
.ch-card:hover .ch-title{color:var(--copper-lt)}
.ch-card:hover .ch-eyebrow{color:var(--copper)}
a.ch-card:focus-visible{outline:2px solid var(--signal);outline-offset:4px}
.ch-mark{width:24px;height:24px;color:var(--copper);margin-bottom:14px;display:block;
  transition:color .2s var(--e),transform .2s var(--e)}
a.ch-card:hover .ch-mark{color:var(--copper-lt)}
.ch-eyebrow{color:var(--t3);font-size:.6rem;letter-spacing:.2em;
  text-transform:uppercase;margin:0 0 8px}
.ch-title{font-size:1.06rem;font-weight:600;color:var(--t1);margin:0;
  letter-spacing:-.01em;line-height:1.3}
a.ch-card:hover .ch-title{color:var(--copper-lt)}
.ch-body{color:var(--t2);font-size:.93rem;margin:10px 0 0;max-width:44ch}


/* ── nine capabilities, as a hub ───────────────────────────────────────
   A grid said the same thing as the rail and the card rows — everything on
   this page had become a line or a list. The shape has to carry the claim:
   three the work runs through, six that come in when the work needs them.

   The first attempt put the six on a true ring, by angle. It collided:
   "Change Management & Enablement" ran straight through "Data Engineering &
   Analytics", because a 212px label cannot sit on a 106px radius. Real names
   are the constraint, so the six are split three and three either side of the
   core instead — still a hub, no longer a heap.

   On a phone it becomes two columns, filled then hollow: the same nine, the
   same grouping, rearranged. That is the test the Gantt failed. */
.orb{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;
  gap:0 var(--sp4);margin:var(--sp5) auto 0;max-width:1000px;position:relative}
.orb-ring,.orb-core{list-style:none;margin:0;padding:0}
.orb-item{display:flex;align-items:center;gap:9px}
.orb-dot{width:9px;height:9px;border-radius:50%;flex:none;
  border:1.5px solid var(--copper);background:transparent;
  transition:transform .2s var(--e),background .2s var(--e)}
.orb-item.core .orb-dot{background:var(--copper);width:11px;height:11px}
.orb-n{color:var(--t3);font-size:.58rem;letter-spacing:.1em;margin:0;flex:none}
.orb-name{color:var(--t2);font-size:.9rem;line-height:1.25}
.orb-item.core .orb-name{color:var(--t1);font-weight:500;font-size:1rem}

/* the six: three down the left, three down the right */
.orb-ring{display:contents}
.orb-ring li{padding:11px 0}
.orb-ring li:nth-child(-n+3){grid-column:1;justify-content:flex-end;
  text-align:right;flex-direction:row-reverse}
.orb-ring li:nth-child(-n+3) .orb-name{text-align:right}
.orb-ring li:nth-child(n+4){grid-column:3}
.orb-ring li:nth-child(1){grid-row:1}
.orb-ring li:nth-child(2){grid-row:2}
.orb-ring li:nth-child(3){grid-row:3}
.orb-ring li:nth-child(4){grid-row:1}
.orb-ring li:nth-child(5){grid-row:2}
.orb-ring li:nth-child(6){grid-row:3}

/* the three, together, ringed */
.orb-core{grid-column:2;grid-row:1 / span 3;display:flex;flex-direction:column;
  gap:12px;padding:26px 30px;border:1px dashed rgba(201,122,60,.28);
  border-radius:200px;
  background:radial-gradient(ellipse at 50% 50%,rgba(201,122,60,.10),transparent 72%)}

.orb-item:hover .orb-dot{transform:scale(1.4);background:var(--copper)}
.orb-item:hover .orb-name{color:var(--copper-lt)}
.orb-item:hover .orb-n{color:var(--copper)}

@media(max-width:900px){
  .orb{grid-template-columns:minmax(0,1fr);gap:0}
  .orb-core{grid-column:1;grid-row:auto;border-radius:14px;padding:20px 22px;
    margin-bottom:16px}
  .orb-ring{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:4px 20px}
  .orb-ring li,.orb-ring li:nth-child(-n+3),.orb-ring li:nth-child(n+4){
    grid-column:auto;grid-row:auto;justify-content:flex-start;text-align:left;
    flex-direction:row}
  .orb-ring li:nth-child(-n+3) .orb-name{text-align:left}
}
@media(max-width:520px){.orb-ring{grid-template-columns:minmax(0,1fr)}}

/* (superseded) nine capabilities as a grid — The three core are
   filled and the six are hollow, which is what the "Core" badge said in
   words. */
.caps{list-style:none;margin:var(--sp5) 0 0;padding:0;display:grid;
  grid-template-columns:repeat(3,minmax(0,1fr));gap:2px 0}
@media(max-width:820px){.caps{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:520px){.caps{grid-template-columns:minmax(0,1fr)}}
.cap{display:grid;grid-template-columns:auto auto 1fr;align-items:center;
  gap:10px;padding:13px 18px 13px 0}
.cap-dot{width:9px;height:9px;border-radius:50%;border:1.5px solid var(--copper);
  background:transparent}
.cap.core .cap-dot{background:var(--copper)}
.cap-n{color:var(--t3);font-size:.6rem;letter-spacing:.1em;margin:0}
.cap-name{color:var(--t2);font-size:.92rem;line-height:1.3}
.cap.core .cap-name{color:var(--t1);font-weight:500}
'''

SPINE = '''
/* ── six exits ─────────────────────────────────────────────────────────
   The method is this page's job, so the detail lives here rather than being
   told twice. Each gate carries an id so the home page rail links into it. */
.ex{list-style:none;margin:var(--sp4,40px) 0 0;padding:0;position:relative}
.ex::before{content:'';position:absolute;left:7px;top:10px;bottom:30px;width:1px;
  background:linear-gradient(180deg,var(--copper) 0%,rgba(201,122,60,.55) 55%,
    rgba(201,122,60,.12) 100%)}
.ex-step{position:relative;padding-left:38px;padding-bottom:26px;scroll-margin-top:110px}
.ex-step:last-child{padding-bottom:0}
.ex-step:target .ex-title{color:var(--copper-lt)}
.ex-node{position:absolute;left:0;top:8px;width:15px;height:15px;border-radius:50%;
  background:var(--copper);box-shadow:0 0 0 5px var(--ink)}
.ex-step.last .ex-node{background:transparent;border:1.5px solid var(--copper)}
.ex-row{border-bottom:1px solid var(--line)}
.ex-step:last-child .ex-row{border-bottom:0}
.ex-sum{cursor:pointer;list-style:none;padding:2px 0 16px;display:block}
.ex-sum::-webkit-details-marker{display:none}
.ex-sum:focus-visible{outline:2px solid var(--signal);outline-offset:4px}
.ex-title{display:block;font-size:1.24rem;font-weight:600;color:var(--white);
  letter-spacing:-.015em;margin-bottom:8px}
.ex-row[open] .ex-title{color:var(--copper-lt)}
.ex-title em{font-family:var(--serif);font-style:italic;color:var(--ember)}
.ex-cond{color:var(--grey);font-size:.95rem;max-width:66ch;margin:0}
.ex-cond b{display:block;font-family:var(--mono);font-size:.6rem;letter-spacing:.2em;
  text-transform:uppercase;color:var(--grey-d);font-weight:400;margin-bottom:5px}
.ex-detail{padding:0 0 16px}
.ex-detail > p{color:var(--grey);margin:0 0 12px;max-width:66ch;font-size:.95rem}
@media(max-width:560px){
  .ex-step{padding-left:30px}
  .ex-node{width:13px;height:13px}
  .ex::before{left:6px}
  .ex-title{font-size:1.1rem}
}
'''

ABOUT = '''
/* the About page's fact list */
.ab-facts{display:grid;grid-template-columns:auto 1fr;gap:10px 22px;
  margin:var(--sp4,40px) 0 0;max-width:52ch}
.ab-facts dt{color:var(--grey-d);font-size:.6rem;letter-spacing:.2em;
  text-transform:uppercase;align-self:center}
.ab-facts dd{margin:0;color:var(--white);font-size:.98rem}
'''


def splice(path, body):
    a, b = M
    s = open(path, encoding='utf-8').read()
    block = a + '\n' + body.strip() + '\n' + b
    if a in s and b in s:
        i, j = s.index(a), s.index(b) + len(b)
        s = s[:i] + block + s[j:]
    else:
        if '</style>' not in s:
            print('  %s: no </style>' % path); return False
        i = s.rindex('</style>')
        s = s[:i] + block + '\n' + s[i:]
    open(path, 'w', encoding='utf-8').write(s)
    return True


def main():
    ok = True
    ok &= splice(os.path.join(ROOT, 'index.html'), RAIL)
    ok &= splice(os.path.join(ROOT, 'approach.html'), SPINE)
    if os.path.exists(os.path.join(ROOT, 'about.html')):
        ok &= splice(os.path.join(ROOT, 'about.html'), ABOUT)
    print('  preview stylesheet applied')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())

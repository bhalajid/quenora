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

RAIL_ANIM = '''
/* ── the rail draws itself ─────────────────────────────────────────────
   The six stops arrive in order when the chapter comes into view: the line
   draws left to right and each stop lands as the line reaches it. It is the
   one chapter where motion means something — the content is a sequence, and
   the animation is that sequence.

   The line stops at the sixth stop and the last dot stays hollow. Nothing
   loops: an engagement designed to finish should not animate forever.

   Everything is opt-in through .go, added by an IntersectionObserver, so a
   reader who never scrolls here pays nothing — and prefers-reduced-motion
   gets the finished state immediately rather than a degraded one. */
.ph::before{transform-origin:left center;transform:scaleX(0);
  transition:transform 1.15s cubic-bezier(.22,1,.36,1)}
.ph.go::before{transform:scaleX(1)}
.ph-stop{opacity:0;transform:translateY(6px);
  transition:opacity .5s var(--e),transform .5s var(--e)}
.ph.go .ph-stop{opacity:1;transform:none}
.ph.go .ph-stop:nth-child(1){transition-delay:.10s}
.ph.go .ph-stop:nth-child(2){transition-delay:.28s}
.ph.go .ph-stop:nth-child(3){transition-delay:.46s}
.ph.go .ph-stop:nth-child(4){transition-delay:.64s}
.ph.go .ph-stop:nth-child(5){transition-delay:.82s}
.ph.go .ph-stop:nth-child(6){transition-delay:1.00s}
/* the handover lands, then breathes once and stops */
.ph.go .ph-stop.last .ph-dot{animation:phlast 1.6s var(--e) 1.15s 1}
@keyframes phlast{
  0%{box-shadow:0 0 0 5px var(--void),0 0 0 5px rgba(201,122,60,.55)}
  70%{box-shadow:0 0 0 5px var(--void),0 0 0 16px rgba(201,122,60,0)}
  100%{box-shadow:0 0 0 5px var(--void),0 0 0 16px rgba(201,122,60,0)}
}
@media(max-width:760px){
  .ph::before{transform-origin:center top;transform:scaleY(0)}
  .ph.go::before{transform:scaleY(1)}
}
@media(prefers-reduced-motion:reduce){
  .ph::before,.ph.go::before{transform:none;transition:none}
  .ph-stop,.ph.go .ph-stop{opacity:1;transform:none;transition:none;
    transition-delay:0s}
  .ph.go .ph-stop.last .ph-dot{animation:none}
}
'''

FIXES = '''
/* ── three faults found by measuring, not by eye ───────────────────────

   1  THE FOOTER DECLARED THREE COLUMNS AND HAS FOUR CHILDREN

      .fgrid was 2fr 1fr 1fr with brand, Site, Contact and Follow inside it.
      The fourth wrapped onto a second row at 636px wide, which is why the
      footer read as collapsed: one wide orphan under three columns, and a
      large hole beside it. Four children, four columns.

   2  THE PHASE TOOLTIP WAS PAINTED OVER

      It had opacity 1 on hover and sat inside the viewport — but
      elementFromPoint at its centre returned the section, not the tooltip.
      z-index:5 was competing at the root because nothing in the rail created
      a stacking context, so later content in the chapter simply painted on
      top. That is why it only seemed to appear after a click: the click moved
      focus and scrolled, changing what overlapped it.

      The rail now owns a stacking context and the hovered stop is lifted
      above it. The tooltip also opens downward: the rail sits under the lede,
      so upward it had to fight the text, and below it there is room.

   3  THE CHAPTERS HAD NO SHARED RHYTHM

      Every main > section carried padding 0 and relied on whatever margins
      its own contents happened to have, so the gap between chapters changed
      from one to the next. One rule gives them all the same top and bottom,
      and the hero and the closing chapter keep their own deliberate values.
*/
footer .fgrid{grid-template-columns:1.6fr 1fr 1fr 1fr}
@media(max-width:900px){footer .fgrid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:560px){footer .fgrid{grid-template-columns:minmax(0,1fr)}}

/* The tooltip opens downward, which puts it over the NEXT chapter — and a
   later sibling paints on top of an earlier one no matter what the tooltip's
   own z-index says. The chapter itself has to win first. */
main > section#journey{position:relative;z-index:3}
.ph{position:relative;z-index:2}
.ph-stop{position:relative;z-index:1}
.ph-link:hover,.ph-link:focus-within,.ph-link:focus-visible{z-index:40}
.ph-tip{top:calc(100% - 8px);bottom:auto;transform:translateY(-5px)}
.ph-link:hover .ph-tip,.ph-link:focus-visible .ph-tip{transform:none}

main > section{padding-block:var(--sp7)}
main > section.hook{padding-block:168px 64px}
main > section#climax{padding-block:104px 250px}
main > section[hidden]{padding-block:0}
@media(max-width:760px){main > section{padding-block:var(--sp6)}}
'''

RHYTHM = '''
/* ── one gap between a chapter's head and its content ──────────────────
   The chapters themselves were already even — 168px top and bottom, heading
   169px in. The unevenness was inside them: measured across the home page,
   the gap between the heading block and the first block of content came out
   at 64px on five chapters, 63px on two, and 40px on #honest and
   #commercial. Two chapters opening 24px tighter than the rest is exactly
   the "not uniform" that was reported, and it is invisible until you measure
   because no two of them sit next to each other.

   One value, set on the head and cancelled on whatever follows so the two
   cannot add up. */
main > section .chead{margin-bottom:64px}
main > section .chead + *{margin-top:0}
main > section .chead + .obj,
main > section .chead + .money,
main > section .chead + .nine,
main > section .chead + .whogrid,
main > section .chead + .ch3{margin-top:0}
@media(max-width:760px){
  main > section .chead{margin-bottom:44px}
}
'''

CNT = '''
/* The counters kept a 168px top margin from where they used to sit, under the
   hub in #solution. As the only thing in chapter 01's panel that margin was
   pure gap: .pin measured 624px around 326px of content, and 168 of the 298
   left over was this one rule. */
#problem .counters{margin-top:0}
/* ── the counts lead somewhere ─────────────────────────────────────────
   Nine capabilities and six phases both name a page. Making the numeral a
   link is the shortest route to it, and it is where a reader's eye already
   is. Underlined only on hover so the row still reads as three figures
   rather than three links. */
.cnt-link{display:inline-block;text-decoration:none;
  transition:transform .2s var(--e)}
.cnt-link b{transition:color .2s var(--e)}
.cnt-link:hover b,.cnt-link:focus-visible b{color:var(--copper-lt)}
.cnt-link:hover{transform:translateY(-2px)}
.cnt-link:focus-visible{outline:2px solid var(--signal);outline-offset:4px;
  border-radius:2px}
'''

POLISH = '''
/* ── 1 · the gutter between chapters ───────────────────────────────────
   Uniform at 168px top and bottom, which meant 336px of dead space between
   any two chapters — even and far too generous. 104 each side gives 208,
   which still separates them without a screen of nothing in between. */
main > section{padding-block:var(--sp6)}
main > section.hook{padding-block:168px 64px}
main > section#climax{padding-block:104px 250px}
main > section[hidden]{padding-block:0}
@media(max-width:760px){main > section{padding-block:var(--sp5)}}

/* ── 2 · the hub's dots have to line up ────────────────────────────────
   The left column was flex with row-reverse, so each dot sat wherever its
   own label ended: measured at x=404, 447 and 446 for the three rows while
   the right column held a straight 948. A grid puts the dot in a column of
   its own, so the label length stops moving it. */
.orb-ring li{display:grid;align-items:center;column-gap:9px}
.orb-ring li:nth-child(-n+3){grid-template-columns:1fr auto auto;
  justify-items:end;text-align:right}
.orb-ring li:nth-child(-n+3) .orb-name{grid-column:1}
.orb-ring li:nth-child(-n+3) .orb-n{grid-column:2}
.orb-ring li:nth-child(-n+3) .orb-dot{grid-column:3}
.orb-ring li:nth-child(n+4){grid-template-columns:auto auto 1fr;
  justify-items:start;text-align:left}
.orb-ring li:nth-child(n+4) .orb-dot{grid-column:1}
.orb-ring li:nth-child(n+4) .orb-n{grid-column:2}
.orb-ring li:nth-child(n+4) .orb-name{grid-column:3}
@media(max-width:900px){
  .orb-ring li,.orb-ring li:nth-child(-n+3),.orb-ring li:nth-child(n+4){
    grid-template-columns:auto auto 1fr;justify-items:start;text-align:left}
  .orb-ring li:nth-child(-n+3) .orb-dot{grid-column:1}
  .orb-ring li:nth-child(-n+3) .orb-n{grid-column:2}
  .orb-ring li:nth-child(-n+3) .orb-name{grid-column:3}
}

/* ── 3 · the cursor ring goes ──────────────────────────────────────────
   A 76px dashed circle trailing the pointer, with a 5px ember dot inside it.
   It reads as a loading spinner or a rendering artefact rather than as a
   cursor — it turns up in every screenshot as a stray unfinished circle, and
   it is the first thing anyone asks about. It also costs a pointer listener
   and a transform on every frame for no function at all. */
.cur,.cdot{display:none!important}
'''

WHO = '''
/* ── chapter 07, once the detail moved to about.html ───────────────────
   The body paragraphs left with the page. What remained was a two-column
   grid holding one child — the facts sat in the first column and the second
   was simply a hole, which is what the blank in the screenshot was.

   The lede lives in the chapter header like every other chapter, so the grid
   has one job left: the five facts. They run as a strip across the full
   width, which fills the measure instead of leaving it. */
#who .whogrid{grid-template-columns:minmax(0,1fr)}
#who .whofacts{border-left:0;padding-left:0;
  border-top:1px solid var(--line);padding-top:var(--sp4);
  display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:var(--sp3)}
#who .wfact{display:flex;flex-direction:column;gap:6px;
  border-right:1px solid var(--line);padding-right:var(--sp3)}
#who .wfact:last-child{border-right:0;padding-right:0}
#who .wfact span{color:var(--t3);font-size:.6rem;letter-spacing:.2em;
  text-transform:uppercase}
#who .wfact b{color:var(--t1);font-weight:500;font-size:1rem;line-height:1.3}
@media(max-width:900px){
  #who .whofacts{grid-template-columns:repeat(2,minmax(0,1fr));gap:var(--sp3)}
  #who .wfact{border-right:0;padding-right:0;
    border-bottom:1px solid var(--line);padding-bottom:14px}
  #who .wfact:nth-last-child(-n+1){border-bottom:0;padding-bottom:0}
}
@media(max-width:480px){#who .whofacts{grid-template-columns:minmax(0,1fr)}}
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
.ex-head{display:flex;align-items:baseline;gap:14px;margin-bottom:6px;
  flex-wrap:wrap}
.ex-eyebrow{color:var(--copper-lt);font-size:.62rem;letter-spacing:.2em;
  text-transform:uppercase;margin:0}
.ex-wk{color:var(--grey-d);font-size:.6rem;letter-spacing:.12em;
  text-transform:uppercase;margin:0}
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

BACKTO = '''
/* ── back to where you came from ───────────────────────────────────────
   A reader who clicked a phase on the home page landed here and had no way
   back except the browser button, which on a page this long returns them to
   the top rather than to the rail they were reading. The control only exists
   when there is somewhere to go back TO, and it names it. */
.backto{display:inline-flex;align-items:center;
  gap:9px;margin:0 0 var(--sp3);padding:9px 14px;border-radius:2px;
  font-family:var(--mono);font-size:.66rem;letter-spacing:.14em;
  text-transform:uppercase;color:var(--white);text-decoration:none;
  background:rgba(20,22,30,.94);border:1px solid var(--line);
  transition:border-color .2s,color .2s}
.backto:hover{border-color:var(--copper);color:var(--copper-lt)}
.backto:focus-visible{outline:2px solid var(--signal);outline-offset:3px}
.backto .arw{font-size:.9rem;line-height:1}
@media(max-width:560px){.backto{font-size:.6rem;padding:8px 11px}}
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
    ok &= splice(os.path.join(ROOT, 'index.html'), RAIL + RAIL_ANIM + WHO + FIXES + RHYTHM + CNT + POLISH)
    ok &= splice(os.path.join(ROOT, 'approach.html'), SPINE + BACKTO)
    if os.path.exists(os.path.join(ROOT, 'about.html')):
        ok &= splice(os.path.join(ROOT, 'about.html'), ABOUT)
    print('  preview stylesheet applied')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""
build_ticker.py — the capability band, slowed down and stopped from jumping.

PREVIEW ONLY, on the `infographics` branch.

WHAT IT WAS DOING

The band's speed was tied to scroll velocity:

    boost = clamp(1 + v / 26, 1, 6);
    tt.style.animationDuration = (38 / boost) + 's';

Measured on this page: the track is 3704px, so a cycle travels 1852px. At the
resting 38s that is 49px/s and a label takes about 30 seconds to cross the
band — calm, and readable. But v/26 reaches the cap of 6 almost immediately:
during an ordinary wheel flick the page was setting durations of 6.7s to 8.1s,
which is roughly 250-280px/s, five to six times resting. A label crossed in
five seconds. That is the band becoming unreadable exactly when a reader is
moving past it.

TWO CHANGES

  1  A nudge, not a whip. The cap drops from 6x to 1.35x and the response is
     divided by 220 rather than 26, so it takes a deliberately fast scroll to
     reach even that. Worst case is now 66px/s — a label still takes 22
     seconds to cross, and stays legible the whole way.

  2  No more jumping. A CSS animation's position is elapsed/duration, so
     rewriting animation-duration mid-flight moves the band instantly — the
     faster it got, the more it stuttered. updatePlaybackRate changes the
     speed without moving anything, which is what that API is for. The old
     path is kept as a fallback for anything that lacks it.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))

OLD_BOOST = "boost = clamp(1 + v / 26, 1, 6);"
NEW_BOOST = ("boost = clamp(1 + v / 220, 1, 1.35);   /* a nudge, not a whip:"
             " v/26 capped at 6 reached ~280px/s on an ordinary flick */")

OLD_TK = """    function tk() {
      boost = lerp(boost, 1, 0.06);
      tt.style.animationDuration = (38 / boost) + 's';
      if (Math.abs(boost - 1) > 0.002) { tkRaf = requestAnimationFrame(tk); }
      else { tt.style.animationDuration = '38s'; tkRaf = null; }
    }"""

NEW_TK = """    /* Rewriting animation-duration re-computes the animation's position as
       elapsed/duration, so every change jumped the band sideways — the faster
       it went, the more it stuttered. updatePlaybackRate changes speed without
       moving anything. Kept the old write as a fallback. */
    var tkAnim = (tt.getAnimations && tt.getAnimations()[0]) || null;
    function tkRate(r) {
      if (tkAnim && tkAnim.updatePlaybackRate) { tkAnim.updatePlaybackRate(r); }
      else { tt.style.animationDuration = (38 / r) + 's'; }
    }
    function tk() {
      boost = lerp(boost, 1, 0.06);
      tkRate(boost);
      if (Math.abs(boost - 1) > 0.002) { tkRaf = requestAnimationFrame(tk); }
      else { tkRate(1); tkRaf = null; }
    }"""


def main():
    p = os.path.join(ROOT, 'index.html')
    s = open(p, encoding='utf-8').read()
    done = 0
    if OLD_BOOST in s:
        s = s.replace(OLD_BOOST, NEW_BOOST, 1); done += 1
    if OLD_TK in s:
        s = s.replace(OLD_TK, NEW_TK, 1); done += 1
    if done == 0:
        print('  ticker: already patched, or the source moved')
        return 0
    open(p, 'w', encoding='utf-8').write(s)
    print('  ticker: %d/2 patches applied — 1.35x cap, no position jump' % done)
    return 0


if __name__ == '__main__':
    sys.exit(main())

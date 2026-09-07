#!/usr/bin/env python3
"""
build_asset_versions.py — make the year-long cache safe to use.

RUN LAST, after every generator that writes an /assets/ reference.

THE BUG THIS FIXES

vercel.json serves everything under /assets/ with

    Cache-Control: public, max-age=31536000, immutable

and the asset URLs never change. `immutable` is a promise to the browser that
the bytes at this URL will never differ, so it is entitled to keep them for a
year and never revalidate — and it does. The favicon was replaced, deployed
correctly, verified byte-identical on the live host, and still did not reach
anyone who had opened the site before. Neither would nora.js, nora.css or the
logo, all of which changed on the same day.

That header is right; unversioned filenames underneath it are the mistake.
So every /assets/ reference gets ?v=<first 8 of the file's sha256>. Change
the file and the URL changes with it, which is the condition `immutable` is
supposed to be paired with.

  /assets/brand/favicon.ico            -> /assets/brand/favicon.ico?v=3f9c1a72
  /assets/nora.js                      -> /assets/nora.js?v=c81e4d05

Query strings are enough: Vercel matches the header rule on the path, so the
long cache still applies, and browsers key their cache on the full URL.

It is idempotent — an existing ?v= is stripped before the current one is
added — so it can run on every build without stacking.

ALSO: /favicon.ico AT THE ROOT

Browsers ask for /favicon.ico whether or not a page declares one, and the
site answered 404. The declared links are what modern browsers use, but the
root request is what a bookmark, a feed reader or an older browser falls back
to, and answering it costs one copied file.
"""
import hashlib, os, re, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
PAGES = ["index.html", "engineering.html", "capabilities.html", "products.html",
         "approach.html", "work.html", "contact.html", "about.html",
         "impressum.html", "privacy.html", "pricing.html"]

REF = re.compile(r'(?P<q>["\'])(?P<path>/assets/[A-Za-z0-9_./-]+?\.[A-Za-z0-9]+)'
                 r'(?:\?v=[0-9a-f]+)?(?P=q)')


def version(path):
    f = os.path.join(ROOT, path.lstrip("/"))
    if not os.path.exists(f):
        return None
    with open(f, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()[:8]


def main():
    src = os.path.join(ROOT, "assets", "brand", "favicon.ico")
    dst = os.path.join(ROOT, "favicon.ico")
    if os.path.exists(src):
        shutil.copyfile(src, dst)
        print("  /favicon.ico answered at the root (%d bytes)" % os.path.getsize(dst))

    seen, missing, changed = {}, set(), 0
    for page in PAGES:
        p = os.path.join(ROOT, page)
        if not os.path.exists(p):
            continue
        s = open(p, encoding="utf-8").read()

        def sub(m):
            path = m.group("path")
            v = version(path)
            if v is None:
                missing.add(path)
                return m.group(0)
            seen[path] = v
            return '%s%s?v=%s%s' % (m.group("q"), path, v, m.group("q"))

        out = REF.sub(sub, s)
        if out != s:
            open(p, "w", encoding="utf-8").write(out)
            changed += 1

    for path in sorted(seen):
        print("  %-42s v=%s" % (path, seen[path]))
    for path in sorted(missing):
        print("  ! %s is referenced but not on disk" % path)
    print("  %d asset URL(s) versioned across %d page(s)" % (len(seen), changed))


if __name__ == "__main__":
    main()

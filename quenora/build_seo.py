#!/usr/bin/env python3
"""
build_seo.py — what a machine reads when it reads this site.

RUN THIS AFTER build_i18n.py. Always. build_i18n regenerates de/ and fr/ from
the English source, so anything written into a localised page before it runs
is overwritten. build.sh enforces the order; if you are running steps by hand,
that is the one rule.

────────────────────────────────────────────────────────────────────────
WHY THIS FILE EXISTS

Within a few years the first thing to read this site will not be a CTO. It
will be their agent, cutting a shortlist to three before a person looks at
anything. That reader does not scroll, cannot see the typography, and gives
the site a few thousand tokens at most. It wants four answers: what does this
firm do, who for, are they credible, how do I reach them.

For a firm that sells "make your systems legible to machines", a site that is
not itself legible to machines is an argument against the firm.

WHAT WAS ACTUALLY WRONG

  1  Structured data existed on exactly one of eleven pages — the homepage.
     capabilities and work, the two pages that answer "what do they do",
     carried none at all.

  2  Worse: build_i18n copied the homepage's block verbatim into every
     language, so /de and /fr each declared inLanguage "en-GB" and the
     English canonical. Both German pages were telling machines they were
     the English page.

  3  There was no llms.txt.

WHAT IT WRITES

  · a JSON-LD @graph on every page, in that page's own language, at that
    page's own served URL, with the correct breadcrumb
  · Service entries for the nine capabilities, so nine descriptions become
    nine machine-readable offerings
  · FAQPage from the objections chapter, which is already written as Q&A
  · /llms.txt — a briefing, not a sitemap: what this is, where the substance
    lives, in a few hundred tokens
  · /llms-full.txt — the whole site as plain text, built from the assistant
    index that already exists, so an agent needs no scraping at all

Everything is generated. Nothing here is maintained by hand, so nothing here
can drift away from the pages it describes.
────────────────────────────────────────────────────────────────────────
"""
import json, os, re, sys
from bs4 import BeautifulSoup as BS

ROOT   = os.path.dirname(os.path.abspath(__file__))
DOMAIN = "https://quenora.ai"

PAGES = ["index.html", "engineering.html", "capabilities.html", "products.html",
         "approach.html", "work.html", "contact.html"]
EN_ONLY   = ["impressum.html", "privacy.html"]
UNLISTED  = {"products.html"}
LANGS     = ["en", "de", "fr"]

LOCALE = {"en": "en-GB", "de": "de-DE", "fr": "fr-FR"}

TEL = ["+49 152 3392 7436", "+49 152 5643 3329"]

# The word each language puts at the root of a breadcrumb.
HOME = {"en": "Home", "de": "Start", "fr": "Accueil"}


def served(lang, page):
    """The URL Vercel actually serves — cleanUrls, so no .html and no
    trailing slash. A canonical that is not the final URL is a canonical
    that disagrees with the site."""
    path = "" if lang == "en" else "/" + lang
    if page == "index.html":
        return DOMAIN + (path or "/")
    return DOMAIN + path + "/" + page[: -len(".html")]


def pagedir(lang, page):
    return os.path.join(ROOT, "" if lang == "en" else lang, page)


def tidy(t):
    """A heading is split into text nodes by its <em>, and joining them with
    a space leaves "five layers ." — invisible on the page, and the first
    thing a machine reads. French keeps its space before ; : ! ?; nothing
    keeps one before a full stop or a comma."""
    t = " ".join(t.split())
    return re.sub(r"\s+([.,])", r"\1", t)


def clip(t, limit):
    """Cut at a sentence, never mid-word. "designed around the except." is
    worse than a shorter description that ends where the writer did."""
    if len(t) <= limit:
        return t
    cut = t[:limit]
    stop = max(cut.rfind(". "), cut.rfind("? "), cut.rfind("! "))
    if stop > limit * 0.5:
        return cut[:stop + 1]
    return cut[:cut.rfind(" ")].rstrip(" ,;:") + "…"


def text(el, limit=None):
    if el is None:
        return ""
    t = tidy(el.get_text(" ", strip=True))
    return clip(t, limit) if limit else t


# ── extraction ────────────────────────────────────────────────────────
# Read what the page says, rather than keeping a second copy of it here.

def page_meta(soup):
    t = soup.find("title")
    d = soup.find("meta", attrs={"name": "description"})
    h = soup.find("h1")
    return (text(t), (d.get("content", "").strip() if d else ""), text(h))


def capabilities(soup, limit=320):
    """The nine cards. Each h3 with a following block of prose is one
    offering; a heading with no description is a section label, not a
    service, and is skipped."""
    out = []
    for h in soup.find_all("h3"):
        nxt = h.find_next_sibling()
        if not nxt:
            continue
        body = text(nxt, limit)
        if len(body) < 40:
            continue
        out.append((text(h), body))
    return out


def faq(soup):
    """The objections chapter is already written as question and answer,
    in <details><summary>. Nothing needs authoring; it only needs
    declaring."""
    out = []
    for d in soup.find_all("details"):
        s = d.find("summary")
        if not s:
            continue
        # The answer is whatever the <details> holds once the question is
        # taken out of it — a div here, not a <p>, which is why matching on
        # tag names found nothing.
        clone = BS(str(d), "html.parser")
        cs = clone.find("summary")
        if cs:
            cs.decompose()
        body = text(clone)
        if s and body:
            out.append((text(s), body[:900]))
    return out


# ── the graph ─────────────────────────────────────────────────────────

def organisation(lang):
    """One organisation, described once, referenced by @id everywhere else.
    Duplicating it per page is how sites end up claiming two founders."""
    return {
        "@type": "Organization",
        "@id": DOMAIN + "/#org",
        "name": "Quenora Consulting",
        "url": DOMAIN + "/",
        "email": "info@quenora.ai",
        "telephone": TEL,
        "sameAs": ["https://www.linkedin.com/company/quenora",
                   "https://x.com/quenora_ai",
                   "https://www.instagram.com/quenora.ai/"],
        "logo":  DOMAIN + "/assets/og-quenora.jpg",
        "image": DOMAIN + "/assets/og-quenora.jpg",
        "description": ("Quenora engineers enterprise AI into the systems a "
                        "business already runs, then hands the client's own "
                        "team the keys."),
        "foundingDate": "2025",
        "founder": {"@type": "Person", "name": "Balaji Durai",
                    "jobTitle": "Founder and Principal Consultant"},
        "address": {"@type": "PostalAddress",
                    "addressLocality": "Heilbronn", "addressCountry": "DE"},
        "areaServed": [{"@type": "Place", "name": "Europe"}],
        "availableLanguage": ["en", "de", "fr"],
        "knowsAbout": ["Enterprise AI integration", "Platform engineering",
                       "MLOps", "AI governance", "Data foundations",
                       "Process automation", "Retrieval-augmented generation"],
    }


def graph_for(lang, page, soup):
    url = served(lang, page)
    title, desc, h1 = page_meta(soup)
    loc = LOCALE[lang]

    g = [organisation(lang),
         {"@type": "WebSite", "@id": DOMAIN + "/#site", "url": DOMAIN + "/",
          "name": "Quenora", "publisher": {"@id": DOMAIN + "/#org"},
          "inLanguage": loc}]

    webpage = {"@type": "WebPage", "@id": url + "#page", "url": url,
               "name": h1 or title,
               "isPartOf": {"@id": DOMAIN + "/#site"},
               "about": {"@id": DOMAIN + "/#org"},
               "inLanguage": loc}
    if desc:
        webpage["description"] = desc

    # Breadcrumb: two levels, because the site is two levels deep. A
    # breadcrumb that invents a hierarchy is worse than none.
    crumbs = [{"@type": "ListItem", "position": 1, "name": HOME[lang],
               "item": served(lang, "index.html")}]
    if page != "index.html":
        crumbs.append({"@type": "ListItem", "position": 2,
                       "name": h1 or title, "item": url})
        webpage["breadcrumb"] = {"@id": url + "#crumb"}
        g.append({"@type": "BreadcrumbList", "@id": url + "#crumb",
                  "itemListElement": crumbs})

    if page == "capabilities.html":
        caps = capabilities(soup)
        if caps:
            g.append({
                "@type": "ItemList", "@id": url + "#services",
                "name": h1 or title, "numberOfItems": len(caps),
                "itemListElement": [
                    {"@type": "ListItem", "position": i + 1,
                     "item": {"@type": "Service",
                              "@id": url + "#service-%d" % (i + 1),
                              "name": n, "description": b,
                              "serviceType": n,
                              "provider": {"@id": DOMAIN + "/#org"},
                              "areaServed": {"@type": "Place", "name": "Europe"},
                              "availableLanguage": ["en", "de", "fr"]}}
                    for i, (n, b) in enumerate(caps)]})

    if page == "index.html":
        qs = faq(soup)
        if qs:
            g.append({"@type": "FAQPage", "@id": url + "#faq",
                      "mainEntity": [
                          {"@type": "Question", "name": q,
                           "acceptedAnswer": {"@type": "Answer", "text": a}}
                          for q, a in qs]})

    g.insert(2, webpage)
    return {"@context": "https://schema.org", "@graph": g}


# ── writing it back ───────────────────────────────────────────────────

def inject(lang, page):
    path = pagedir(lang, page)
    if not os.path.exists(path):
        return None
    html = open(path, encoding="utf-8").read()
    soup = BS(html, "html.parser")

    data = graph_for(lang, page, soup)

    # Remove whatever was there — the generated block from a previous run,
    # and the hand-written homepage block whose content this now supersedes.
    for sc in soup.find_all("script", attrs={"type": "application/ld+json"}):
        sc.decompose()

    tag = soup.new_tag("script", type="application/ld+json")
    tag["data-generated"] = "ld"
    tag.string = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    head = soup.find("head")
    if head is None:
        return None
    head.append(tag)

    open(path, "w", encoding="utf-8").write(str(soup))
    return data


def llms_txt():
    """A briefing, not a sitemap. A sitemap lists everything for a crawler
    that will read everything. This is for a reader with a token budget,
    and it answers the four questions in the first ten lines."""
    en = BS(open(pagedir("en", "index.html"), encoding="utf-8").read(), "html.parser")
    caps = capabilities(BS(open(pagedir("en", "capabilities.html"),
                                encoding="utf-8").read(), "html.parser"),
                        limit=None)

    L = []
    A = L.append
    A("# Quenora Consulting")
    A("")
    A("> Enterprise AI and automation consultancy in Heilbronn, Germany.")
    A("> Founder-led. Works in English, German and French across Europe.")
    A("> Engineers AI into the systems a business already runs, then hands")
    A("> the client's own team the keys.")
    A("")
    A("Founded 2025. Contact: info@quenora.ai · " + " · ".join(TEL))
    A("")
    A("## What the firm does")
    A("")
    for n, b in caps:
        A("- **%s** — %s" % (n, b))
    A("")
    A("## Pages")
    A("")
    for p in PAGES:
        if p in UNLISTED:
            continue
        s = BS(open(pagedir("en", p), encoding="utf-8").read(), "html.parser")
        t, d, h = page_meta(s)
        A("- [%s](%s): %s" % (h or t, served("en", p), d or t))
    A("")
    A("## Other languages")
    A("")
    for lang in ("de", "fr"):
        A("- %s: %s" % (LOCALE[lang], served(lang, "index.html")))
    A("")
    A("## Machine-readable")
    A("")
    A("- [Full site text](%s/llms-full.txt): every paragraph, plain text." % DOMAIN)
    A("- [Site index, JSON](%s/assistant.json): the same corpus, one object" % DOMAIN)
    A("  per passage, with its heading. `/de/assistant.json`, `/fr/assistant.json`.")
    A("- Structured data: JSON-LD on every page (Organization, WebPage,")
    A("  BreadcrumbList, Service ×%d, FAQPage)." % len(caps))
    A("")
    A("## Notes")
    A("")
    A("This site sets no cookies and runs no third-party JavaScript. Nothing")
    A("here is generated by a language model; every sentence was written by")
    A("the firm and is a claim it stands behind. There are no case studies")
    A("because the firm is new and will not invent a client list.")
    A("")
    return "\n".join(L)


def llms_full_txt():
    """The whole site as plain text, built from the index that already
    exists for the on-page assistant. Nothing new is extracted; an agent
    simply gets what a scraper would have had to work for."""
    idx = json.load(open(os.path.join(ROOT, "assistant.json"), encoding="utf-8"))
    L = ["# Quenora Consulting — full site text",
         "# Generated from the site's own paragraphs. Source: https://quenora.ai",
         ""]
    last = None
    for d in idx["docs"]:
        h = d.get("h") or ""
        if h and h != last:
            L += ["", "## " + h, ""]
            last = h
        body = d.get("t") or d.get("text") or ""
        # "Covers: …" passages are keyword lists the assistant index builds
        # for retrieval. They are scaffolding, not something the site says.
        if body and not re.match(r"^(Covers|Umfasst|Couvre):", body):
            L.append(body)
    return "\n".join(L) + "\n"


def main():
    print("structured data")
    n = 0
    for lang in LANGS:
        for page in PAGES + (EN_ONLY if lang == "en" else []):
            if inject(lang, page):
                n += 1
        print("  %-3s pages written" % lang, end="  ")
        print()
    print("  %d page(s) carry a generated @graph" % n)

    for name, body in (("llms.txt", llms_txt()),
                       ("llms-full.txt", llms_full_txt())):
        p = os.path.join(ROOT, name)
        open(p, "w", encoding="utf-8").write(body)
        print("  %-14s %5.1f KB" % (name, len(body.encode()) / 1024))


if __name__ == "__main__":
    main()

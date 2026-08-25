#!/usr/bin/env python3
"""Quenora — multilingual site generator.

Reads the English HTML, substitutes translated strings at the text-node and
attribute level (never by blind string replacement, which corrupts markup),
and writes a complete localised copy of the site into de/ fr/ es/ it/.

Also rewrites, per language:
  * <html lang>
  * <title>, meta description, og:*, twitter:*
  * canonical + a full set of hreflang alternates (incl. x-default)
  * internal links, so /de/ stays inside /de/
  * asset and stylesheet paths (one level deeper)
  * the language switcher in the header

Run:  python3 build_i18n.py
"""
import json
import os
import re
import shutil
import sys

from bs4 import BeautifulSoup, Comment, NavigableString

ROOT = os.path.dirname(os.path.abspath(__file__))
PAGES = ["index.html", "services.html", "products.html",
         "approach.html", "work.html", "contact.html"]
# Pages that exist in English only. Links to these must climb out of the
# language directory instead of resolving to a /de/... file that is not there.
EN_ONLY_PAGES = {"impressum.html", "privacy.html"}
LANGS = ["de", "fr", "es", "it"]
LANG_NAMES = {"en": "English", "de": "Deutsch", "fr": "Français",
              "es": "Español", "it": "Italiano"}
DOMAIN = "https://quenora.ai"
SKIP_TAGS = {"script", "style"}

# strings that must never be translated
DNT = re.compile(
    r"^(quenora|quenora\.ai|hello@quenora\.ai|Quenora Technology Consulting|"
    r"GDPR|EU AI Act|IaC|MLOps|ERP|CRM|API|BI & reporting|RAG systems|"
    r"\[[^\]]+\]|Main|Footer|Contact|Legal|Site|Quenora home|Reg / VAT|AI|Core|Continuous|Choose language|Sprache w\u00e4hlen|Choisir la langue|Elegir idioma|Scegli la lingua|Deutsch|English|Français|Español|Italiano|EN|DE|FR|ES|IT|AB/\d+|Phase \d+|\d+[\d\s:.,%–—/-]*|00:00|html|uenora|"
    r"[©·→←↓↑✓–—]+)$", re.I)


def load(lang):
    p = os.path.join(ROOT, "i18n", lang + ".json")
    if not os.path.exists(p):
        return {}
    d = json.load(open(p, encoding="utf-8"))
    d.pop("_meta", None)
    return d


def translate_soup(soup, tr, stats):
    """Substitute text nodes and visible attributes in place."""
    for node in soup.find_all(string=True):
        if isinstance(node, Comment):
            continue
        if node.parent.name in SKIP_TAGS:
            continue
        raw = str(node)
        key = raw.strip()
        if len(key) < 2:
            continue
        if DNT.match(key):
            continue
        stats["total"] += 1
        if key in tr:
            lead = raw[:len(raw) - len(raw.lstrip())]
            trail = raw[len(raw.rstrip()):]
            node.replace_with(NavigableString(lead + tr[key] + trail))
            stats["hit"] += 1
        else:
            stats["miss"].add(key)

    for attr in ("alt", "aria-label", "placeholder", "title"):
        for el in soup.find_all(attrs={attr: True}):
            v = el[attr].strip()
            if not v or DNT.match(v):
                continue
            stats["total"] += 1
            if v in tr:
                el[attr] = tr[v]
                stats["hit"] += 1
            else:
                stats["miss"].add(v)

    for m in soup.find_all("meta", attrs={"content": True}):
        n = (m.get("name", "") or "") + (m.get("property", "") or "")
        if n in ("description", "og:title", "og:description", "og:site_name",
                 "twitter:title", "twitter:description"):
            v = m["content"].strip()
            if DNT.match(v):
                continue
            stats["total"] += 1
            if v in tr:
                m["content"] = tr[v]
                stats["hit"] += 1
            else:
                stats["miss"].add(v)

    # <title> is already covered by the text-node pass above; re-checking it
    # here would count the translated string as a miss.


SWITCH_LABEL = {"en": "Choose language", "de": "Sprache wählen",
                "fr": "Choisir la langue", "es": "Elegir idioma",
                "it": "Scegli la lingua"}


def switcher(lang, page):
    """Header language menu. Current language first, marked."""
    items = []
    for code in ["en"] + LANGS:
        if code == "en":
            href = page if lang == "en" else "../" + page
        else:
            href = (code + "/" + page) if lang == "en" else "../" + code + "/" + page
        cur = ' aria-current="true"' if code == lang else ""
        items.append(
            '<li><a hreflang="%s" lang="%s" href="%s"%s>%s</a></li>'
            % (code, code, href, cur, LANG_NAMES[code]))
    return (
        '<div class="langsel">'
        '<button type="button" id="langBtn" aria-expanded="false" '
        'aria-controls="langMenu" aria-label="%s">'
        '<svg width="15" height="15" viewBox="0 0 16 16" fill="none" aria-hidden="true">'
        '<circle cx="8" cy="8" r="6.4" stroke="currentColor" stroke-width="1.3"/>'
        '<path d="M1.6 8h12.8M8 1.6a11 11 0 0 1 0 12.8A11 11 0 0 1 8 1.6" '
        'stroke="currentColor" stroke-width="1.3"/></svg>'
        '<span>%s</span></button>'
        '<ul class="langmenu" id="langMenu" role="menu">%s</ul></div>'
        % (SWITCH_LABEL[lang], lang.upper(), "".join(items)))


LANG_CSS = """
.langsel{position:relative;margin-left:14px}
.langsel>button{display:inline-flex;align-items:center;gap:7px;min-height:38px;
  padding:0 12px;background:transparent;border:1px solid var(--line);
  border-radius:3px;color:var(--grey);font:inherit;font-size:12px;
  letter-spacing:.06em;cursor:pointer;transition:border-color .25s,color .25s}
.langsel>button:hover{border-color:var(--copper);color:var(--white)}
.langmenu{position:absolute;right:0;top:calc(100% + 8px);min-width:160px;
  margin:0;padding:6px;list-style:none;background:var(--ink-2);
  border:1px solid var(--line);border-radius:4px;display:none;z-index:120;
  box-shadow:0 18px 44px rgba(0,0,0,.5)}
.langmenu.open{display:block}
.langmenu a{display:block;padding:9px 12px;border-radius:2px;font-size:13.5px;
  color:var(--grey);transition:background .2s,color .2s}
.langmenu a:hover{background:rgba(201,122,60,.12);color:var(--white)}
.langmenu a[aria-current=true]{color:var(--copper-lt)}
@media(max-width:900px){.langsel{margin-left:auto;margin-right:8px}
  .langsel>button span{display:none}}
"""

LANG_JS = """
<script>
(function(){
  var b=document.getElementById('langBtn'),m=document.getElementById('langMenu');
  if(!b||!m)return;
  b.addEventListener('click',function(e){
    e.stopPropagation();
    var o=m.classList.toggle('open');
    b.setAttribute('aria-expanded',o?'true':'false');
  });
  document.addEventListener('click',function(){
    m.classList.remove('open');b.setAttribute('aria-expanded','false');
  });
  document.addEventListener('keydown',function(e){
    if(e.key==='Escape'){m.classList.remove('open');
      b.setAttribute('aria-expanded','false');}
  });
})();
</script>
"""


def localise_paths(soup, lang):
    """Rewrite asset paths one level deeper; keep internal links in-language."""
    for el in soup.find_all(["img", "source"]):
        for a in ("src", "srcset"):
            if el.has_attr(a) and el[a].startswith("assets/"):
                el[a] = "../" + el[a]
    for el in soup.find_all("link", href=True):
        if el["href"].startswith("assets/") or el["href"] == "manifest.json":
            el["href"] = "../" + el["href"]
    for a in soup.find_all("a", href=True):
        h = a["href"]
        if h in EN_ONLY_PAGES:
            a["href"] = "../" + h          # legal pages are English-only
            continue
        if h.endswith(".html") and "/" not in h:
            continue                       # already relative, stays in-language
        if h.startswith("assets/"):
            a["href"] = "../" + h


def head_links(soup, lang, page):
    """canonical + hreflang alternates + og:url + lang attribute."""
    soup.html["lang"] = lang
    slug = "" if page == "index.html" else page
    base = DOMAIN + ("/" if lang == "en" else "/" + lang + "/")
    canon = base + slug

    for l in soup.find_all("link", rel=lambda v: v and "canonical" in v):
        l.decompose()
    for l in soup.find_all("link", rel=lambda v: v and "alternate" in v):
        l.decompose()

    head = soup.head
    c = soup.new_tag("link")
    c["rel"] = "canonical"
    c["href"] = canon
    head.append(c)
    for code in ["en"] + LANGS:
        b = DOMAIN + ("/" if code == "en" else "/" + code + "/")
        alt = soup.new_tag("link")
        alt["rel"] = "alternate"
        alt["href"] = b + slug
        alt["hreflang"] = code
        head.append(alt)
    xd = soup.new_tag("link")
    xd["rel"] = "alternate"
    xd["href"] = DOMAIN + "/" + slug
    xd["hreflang"] = "x-default"
    head.append(xd)

    for m in soup.find_all("meta", attrs={"property": "og:url"}):
        m["content"] = canon
    ol = soup.find("meta", attrs={"property": "og:locale"})
    loc = {"en": "en_GB", "de": "de_DE", "fr": "fr_FR",
           "es": "es_ES", "it": "it_IT"}[lang]
    if ol:
        ol["content"] = loc
    else:
        m = soup.new_tag("meta")
        m["property"] = "og:locale"
        m["content"] = loc
        head.append(m)


def build_lang(lang):
    tr = load(lang)
    outdir = os.path.join(ROOT, lang)
    os.makedirs(outdir, exist_ok=True)
    stats = {"total": 0, "hit": 0, "miss": set()}

    for page in PAGES:
        html = open(os.path.join(ROOT, page), encoding="utf-8").read()
        soup = BeautifulSoup(html, "html.parser")

        translate_soup(soup, tr, stats)
        localise_paths(soup, lang)
        head_links(soup, lang, page)

        # language switcher into the header, before the nav links
        st = soup.find("style")
        if st and "langsel" not in st.text:
            st.string = st.text + LANG_CSS
        nav = soup.find(class_="navlinks")
        if nav and not soup.find(class_="langsel"):
            frag = BeautifulSoup(switcher(lang, page), "html.parser")
            nav.insert_after(frag)
        if "id=\"langBtn\"" in str(soup) and "langBtn'" not in str(soup):
            body = soup.body
            body.append(BeautifulSoup(LANG_JS, "html.parser"))

        open(os.path.join(outdir, page), "w", encoding="utf-8").write(str(soup))

    cov = 100.0 * stats["hit"] / stats["total"] if stats["total"] else 0
    return lang, cov, stats


def build_en_switcher():
    """Add the same switcher to the English pages."""
    for page in PAGES:
        p = os.path.join(ROOT, page)
        soup = BeautifulSoup(open(p, encoding="utf-8").read(), "html.parser")
        old = soup.find(class_="langsel")
        if old:
            old.decompose()          # always rebuild: hrefs may have changed
        st = soup.find("style")
        if st and "langsel" not in st.text:
            st.string = st.text + LANG_CSS
        # drop any previously appended switcher script before re-adding it,
        # otherwise every rebuild leaves another copy behind
        for sc in soup.find_all("script"):
            if sc.string and "getElementById('langBtn')" in sc.string:
                sc.decompose()
        nav = soup.find(class_="navlinks")
        if nav:
            nav.insert_after(BeautifulSoup(switcher("en", page), "html.parser"))
            soup.body.append(BeautifulSoup(LANG_JS, "html.parser"))
        head_links(soup, "en", page)
        open(p, "w", encoding="utf-8").write(str(soup))


def sitemap():
    urls = []
    for lang in ["en"] + LANGS:
        base = DOMAIN + ("/" if lang == "en" else "/" + lang + "/")
        for page in PAGES:
            slug = "" if page == "index.html" else page
            alts = "".join(
                '\n    <xhtml:link rel="alternate" hreflang="%s" href="%s"/>'
                % (c, DOMAIN + ("/" if c == "en" else "/" + c + "/") + slug)
                for c in ["en"] + LANGS)
            urls.append(
                '  <url>\n    <loc>%s%s</loc>%s\n    <priority>%s</priority>\n  </url>'
                % (base, slug, alts, "1.0" if page == "index.html" else "0.8"))
    # English-only pages: no hreflang alternates, low priority, but they must be
    # indexable — an Impressum that search engines cannot find is not published.
    for page in sorted(EN_ONLY_PAGES):
        urls.append(
            '  <url>\n    <loc>%s/%s</loc>\n    <priority>0.3</priority>\n  </url>'
            % (DOMAIN, page))
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
        '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "\n".join(urls) + "\n</urlset>\n")


if __name__ == "__main__":
    build_en_switcher()
    print("%-6s %-9s %s" % ("lang", "coverage", "untranslated"))
    print("-" * 46)
    report = {}
    for lang in LANGS:
        l, cov, st = build_lang(lang)
        report[l] = sorted(st["miss"])
        print("%-6s %6.1f%%   %d string(s)" % (l, cov, len(st["miss"])))
    sitemap()
    json.dump(report, open(os.path.join(ROOT, "_untranslated.json"), "w"),
              indent=1, ensure_ascii=False)
    print("\nsitemap.xml rewritten with hreflang alternates")
    print("gaps listed in _untranslated.json")

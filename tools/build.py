"""Build the fishcut site from src/.

Usage (from anywhere; paths resolve from this file):
    python3 -I tools/build.py           write every page
    python3 -I tools/build.py --check   write nothing, exit 1 when a committed page differs from src/

Korean is the site root (/) and English lives under /en/ (the "path" of each language in
src/strings.json). Each language gets four pages: home, privacy, terms and how-it-works.
A page is src/shell.html around src/layout-home.html or src/layout-doc.html around the
content in src/<lang>/<page>.html. A language marked "draft": true is not built.

Placeholders:
    {{root}}      path from the page to the site root, for assets
    {{home}}      path from the page to its language home, for links between pages
    {{s.<key>}}   a string of the page's language from src/strings.json (HTML-escaped)
    and the shell keys set in page() below. Any {{...}} left after the build is an error.

Also writes 404.html (Korean shell, links from the site root), sitemap.xml and robots.txt.
GitHub Pages serves the repository root as is, so the written files are committed.
"""

import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
DOCS = ("privacy", "terms", "how-it-works")
PAGES = ("home", *DOCS)


def read(rel: str) -> str:
    return (SRC / rel).read_text(encoding="utf-8")


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def text_of(fragment: str) -> str:
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", fragment)).split())


def url_of(lang: dict, page: str) -> str:
    """Path below the site root, always ending in "/"."""
    return lang["path"] + ("" if page == "home" else f"{page}/")


def fill(template: str, values: dict[str, str]) -> str:
    return re.sub(r"\{\{([a-z_.]+)\}\}", lambda m: values.get(m.group(1), m.group(0)), template)


def assemble(cfg: dict, code: str, main: str, values: dict[str, str], top_band: bool, switch: str, where: str) -> str:
    shell = read("shell.html")
    shell = shell.replace("{{top_band}}\n", '  <p class="top-band">{{s.top_band}}</p>\n' if top_band else "")
    shell = shell.replace("{{switch}}\n", switch + "\n" if switch else "")
    lang = cfg["langs"][code]
    values = {
        "lang": code,
        "github": esc(cfg["github"]),
        "youtube": esc(cfg["youtube"]),
        "email": esc(cfg["email"]),
        "updated": esc(cfg["updated"]),
        **{f"s.{k}": esc(v) for k, v in lang.items() if isinstance(v, str)},
        **values,
    }
    out = fill(shell.replace("{{main}}", main.rstrip("\n")), values)
    left = sorted(set(re.findall(r"\{\{[^}]*\}\}", out)))
    if left:
        raise SystemExit(f"{where}: unfilled {', '.join(left)}")
    return out


def page(cfg: dict, code: str, name: str, live: list[str]) -> str:
    lang = cfg["langs"][code]
    rel = url_of(lang, name)
    root = "../" * rel.count("/")
    where = f"src/{code}/{name}.html"
    content = read(f"{code}/{name}.html").rstrip("\n")
    if name == "home":
        main = read("layout-home.html").replace("{{content}}", content)
        title, description = lang["home_title"], lang["home_description"]
    else:
        main = read("layout-doc.html").replace("{{content}}", content)
        h1 = re.search(r"<h1[^>]*>(.*?)</h1>", content, re.S)
        if not h1:
            raise SystemExit(f"{where}: no <h1>")
        lede = re.search(r'<p class="lede">(.*?)</p>', content, re.S)
        title = f"{text_of(h1.group(1))} | fishcut"
        description = text_of(lede.group(1)) if lede else lang["home_description"]

    site = cfg["site"]
    canonical = f"{site}/{rel}"
    meta = [f'  <link rel="canonical" href="{canonical}">']
    if len(live) > 1:
        meta += [f'  <link rel="alternate" hreflang="{o}" href="{site}/{url_of(cfg["langs"][o], name)}">' for o in live]
        default = "en" if "en" in live else live[0]
        meta.append(f'  <link rel="alternate" hreflang="x-default" href="{site}/{url_of(cfg["langs"][default], name)}">')
    meta += [
        '  <meta property="og:type" content="website">',
        '  <meta property="og:site_name" content="fishcut">',
        f'  <meta property="og:title" content="{esc(title)}">',
        f'  <meta property="og:description" content="{esc(description)}">',
        f'  <meta property="og:url" content="{canonical}">',
        f'  <meta property="og:locale" content="{esc(lang["og_locale"])}">',
    ]
    switch = "\n".join(
        f'          <li class="nav-lang"><a href="{root}{url_of(cfg["langs"][o], name)}" hreflang="{o}" lang="{o}">{esc(cfg["langs"][o]["name"])}</a></li>'
        for o in live
        if o != code
    )
    values = {
        "title": esc(title),
        "description": esc(description),
        "head_meta": "\n".join(meta),
        "root": root,
        "home": "" if name == "home" else "../",
        "home_link": "#top" if name == "home" else "../",
        "page": name,
    }
    return assemble(cfg, code, main, values, name == "home", switch, where)


def not_found(cfg: dict) -> str:
    lang = cfg["langs"]["ko"]
    values = {
        "title": esc(f"{lang['not_found']} | fishcut"),
        "description": esc(lang["home_description"]),
        "head_meta": '  <meta name="robots" content="noindex">',
        "root": "/",
        "home": "/",
        "home_link": "/",
        "page": "404",
    }
    return assemble(cfg, "ko", read("404.html"), values, False, "", "src/404.html")


def sitemap(cfg: dict, live: list[str]) -> str:
    site = cfg["site"]
    rows = []
    for code in live:
        for name in PAGES:
            alts = "".join(
                f'\n    <xhtml:link rel="alternate" hreflang="{o}" href="{site}/{url_of(cfg["langs"][o], name)}"/>' for o in live
            ) if len(live) > 1 else ""
            rows.append(f"  <url>\n    <loc>{site}/{url_of(cfg['langs'][code], name)}</loc>{alts}\n    <lastmod>{cfg['updated']}</lastmod>\n  </url>")
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "\n".join(rows)
        + "\n</urlset>\n"
    )


def outputs() -> tuple[dict[str, str], list[str]]:
    cfg = json.loads(read("strings.json"))
    live = [code for code, lang in cfg["langs"].items() if not lang.get("draft")]
    files = {}
    for code in live:
        for name in PAGES:
            files[url_of(cfg["langs"][code], name) + "index.html"] = page(cfg, code, name, live)
    files["404.html"] = not_found(cfg)
    files["sitemap.xml"] = sitemap(cfg, live)
    files["robots.txt"] = f"User-agent: *\nAllow: /\nSitemap: {cfg['site']}/sitemap.xml\n"
    return files, [code for code in cfg["langs"] if code not in live]


def main() -> int:
    files, drafts = outputs()
    if "--check" in sys.argv[1:]:
        stale = [rel for rel, body in files.items() if not (ROOT / rel).is_file() or (ROOT / rel).read_text(encoding="utf-8") != body]
        if stale:
            print("out of date, run python3 -I tools/build.py:", *stale, sep="\n    ")
            return 1
        print(f"{len(files)} files match src/")
        return 0
    for rel, body in files.items():
        out = ROOT / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(body, encoding="utf-8")
    print(f"wrote {len(files)} files" + (f" (draft, not built: {', '.join(drafts)})" if drafts else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())

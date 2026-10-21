"""Check the built site for what Google OAuth verification and the YouTube API policies need.

Usage (from anywhere):
    python3 -I tools/check.py             check every built language
    python3 -I tools/check.py --publish   also fail on what must not go live: a draft language,
                                          a draft note (aside.note.draft) left in a page

It reads the built pages only and does not judge design. The policy items come from the
fishcut landing research (Google OAuth brand verification, YouTube API Services Terms and
Developer Policies); each label names its rule. Phrases differ per language, so every
language needs an entry in PHRASES before it can leave draft.
"""

import html.parser
import json
import pathlib
import re
import sys
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONT_HOSTS = ("fonts.googleapis.com", "fonts.gstatic.com", "cdn.jsdelivr.net")
# arrows, em dash, middle dots, section sign, circled numbers, emoji and dingbats
FORBIDDEN = re.compile("[←-⇿—·・§①-⓿\U0001f300-\U0001faff☀-➿]")
DOCS = ("privacy", "terms", "how-it-works")
PAGES = ("home", *DOCS)
REVOKE = r"security\.google\.com/settings/security/permissions|myaccount\.google\.com/connections"

# Text each page must carry, per language. Rule names in the labels.
PHRASES = {
    "ko": {
        "trademark": "Google LLC의 상표",
        "no_affiliation": "제휴하거나",
        "limited_use": "제한적 사용",
        "human_upload": "사람이 누릅니다",
        "cookies": "쿠키",
        "no_ads": "광고를 싣지 않고",
        "retention": ("보관 기간", "7일", "30일"),
        "diagram": "구조도",
        "data_table": "저장하는 데이터",
        "revoke_steps": "권한 취소와 삭제",
    },
    "en": {
        "trademark": "a trademark of Google LLC",
        "no_affiliation": "not affiliated with",
        "limited_use": "including the Limited Use requirements",
        "human_upload": "person presses the final upload button",
        "cookies": "cookies",
        "no_ads": "do not show ads",
        "retention": ("Retention period", "7 days", "30 days"),
        "diagram": "Architecture diagram",
        "data_table": "Data fishcut stores",
        "revoke_steps": "Revoking access and deleting data",
    },
}


class Page(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack: list[str] = []
        self.links: list[tuple[str, tuple[str, ...]]] = []
        self.refs: list[str] = []
        self.ids: set[str] = set()
        self.text: list[str] = []
        self.imgs: list[dict] = []
        self.external: list[str] = []
        self.counts: dict[str, int] = {}
        self.lang = ""
        self.canonical = ""
        self.alternates: dict[str, str] = {}
        self.drafts = 0
        self.iframes = 0
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        a = {k: v or "" for k, v in attrs}
        self.counts[tag] = self.counts.get(tag, 0) + 1
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "html":
            self.lang = a.get("lang", "")
        if tag in ("script", "style"):
            self.skip += 1
        for attr in ("src", "href", "srcset", "poster"):
            value = a.get(attr, "")
            if not value:
                continue
            if value.startswith(("http:", "https:", "//")):
                if tag in ("script", "link", "img", "source", "video") and a.get("rel") not in ("canonical", "alternate"):
                    self.external.append(value)
            elif tag != "a":
                self.refs.append(value.split()[0])
        if tag == "link" and a.get("rel") == "canonical":
            self.canonical = a.get("href", "")
        if tag == "link" and a.get("rel") == "alternate" and a.get("hreflang"):
            self.alternates[a["hreflang"]] = a.get("href", "")
        if tag == "a" and "href" in a:
            self.links.append((a["href"], tuple(self.stack)))
        if tag == "img":
            self.imgs.append(a)
        if tag in ("iframe", "embed", "object"):
            self.iframes += 1
        if tag == "aside" and "draft" in a.get("class", "").split():
            self.drafts += 1
        if tag not in ("img", "br", "hr", "meta", "link", "input", "source", "wbr", "path", "rect", "circle", "line", "use"):
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip = max(0, self.skip - 1)
        if tag in self.stack:
            while self.stack and self.stack.pop() != tag:
                pass

    def handle_data(self, data):
        if not self.skip:
            self.text.append(data)


def parse(path: pathlib.Path) -> tuple[Page, str]:
    page = Page()
    page.feed(path.read_text(encoding="utf-8"))
    return page, " ".join(" ".join(page.text).split())


def has_link(page: Page, pattern: str, inside: str | None = None) -> bool:
    return any(re.search(pattern, href) and (inside is None or inside in stack) for href, stack in page.links)


def target_of(page_file: pathlib.Path, ref: str) -> tuple[pathlib.Path, str]:
    """The file a relative or root-absolute reference points at, and its #fragment."""
    url = urllib.parse.urlsplit(ref)
    if url.path.startswith("/"):
        path = ROOT / url.path.lstrip("/")
    else:
        path = (page_file.parent / url.path) if url.path else page_file
    if url.path.endswith("/") or path.is_dir():
        path = path / "index.html"
    return path.resolve(), url.fragment


def check_site(publish: bool) -> list[tuple[str, str, bool]]:
    results: list[tuple[str, str, bool]] = []
    cfg = json.loads((ROOT / "src/strings.json").read_text(encoding="utf-8"))
    live = [code for code, lang in cfg["langs"].items() if not lang.get("draft")]
    parsed: dict[pathlib.Path, Page] = {}

    def get(path: pathlib.Path) -> Page | None:
        if path not in parsed and path.is_file() and path.suffix == ".html":
            parsed[path] = parse(path)[0]
        return parsed.get(path)

    if publish:
        drafts = [code for code in cfg["langs"] if code not in live]
        results.append(("site", f"no draft language ({', '.join(drafts) or 'none'})", not drafts))

    # The privacy policy promises the privacy-enhanced player and nothing else.
    script = (ROOT / "assets/main.js").read_text(encoding="utf-8")
    players = re.findall(r"https://[^/\"'`]+/embed/", script)
    results.append(("site", "script embeds only youtube-nocookie.com", players == ["https://www.youtube-nocookie.com/embed/"]))

    built: dict[str, dict[str, tuple[Page, str]]] = {}
    for code in live:
        lang = cfg["langs"][code]
        words = PHRASES.get(code)
        results.append((code, "phrases defined for the language", words is not None))
        words = words or {}
        built[code] = {}
        for name in PAGES:
            where = f"{code}/{name}"
            rel = lang["path"] + ("" if name == "home" else f"{name}/")
            f = ROOT / rel / "index.html"
            ok = f.is_file()
            results.append((where, "file exists", ok))
            if not ok:
                continue
            page, text = parse(f)
            parsed[f.resolve()] = page
            built[code][name] = (page, text)
            add = lambda label, value: results.append((where, label, bool(value)))
            add("html lang matches the language", page.lang == code)
            add("canonical is the page's own address", page.canonical == f"{cfg['site']}/{rel}")
            if len(live) > 1:
                add("hreflang for every language and x-default", all(o in page.alternates for o in live) and "x-default" in page.alternates)
            add("app name fishcut, no other casing", "fishcut" in text and not re.search(r"Fishcut|FishCut|FISHCUT", text))
            add("privacy link in header (III.A.2.a)", has_link(page, r"(^|/)privacy/$", "header"))
            add("privacy, terms, how-it-works links in footer", all(has_link(page, rf"(^|/){d}/$", "footer") for d in DOCS))
            add("contact mailto in footer (III.A.2.i)", has_link(page, r"^mailto:", "footer"))
            add("trademark line (brand guidance)", words.get("trademark", "\0") in text)
            add("only font hosts outside (no tracking)", all(any(h in u for h in FONT_HOSTS) for u in page.external))
            add("no iframe or embed in the HTML (players load on click)", page.iframes == 0)
            add("img alt and size", all("alt" in i and "width" in i and "height" in i for i in page.imgs))
            add("no forbidden symbols in visible text", not FORBIDDEN.search(text))
            broken = []
            for ref in page.refs + [h for h, _ in page.links]:
                if re.match(r"^(https?:|mailto:|tel:|//)", ref):
                    continue
                target, frag = target_of(f, ref)
                tp = get(target) if target.suffix == ".html" else None
                if not target.is_file() or (frag and tp is not None and frag not in tp.ids):
                    broken.append(ref)
            add(f"local links and assets resolve{': ' + ', '.join(sorted(set(broken))[:4]) if broken else ''}", not broken)
            if publish:
                add("no draft note left", page.drafts == 0)

        pages = built[code]
        if "home" in pages:
            page, text = pages["home"]
            add = lambda label, value: results.append((f"{code}/home", label, bool(value)))
            add("says it uses YouTube API Services (III.A.2.b)", "YouTube API Services" in text)
            add("both scopes named with purpose", "youtube.upload" in text and "youtube.readonly" in text)
            add("Limited Use statement", "Limited Use" in text and words.get("limited_use", "Limited Use") in text)
            add("no affiliation statement (ToS 13)", words.get("no_affiliation", "\0") in text)
            add("revoke link (III.A.2.h)", has_link(page, REVOKE))
            add("a person presses the final upload", words.get("human_upload", "\0") in text)
            add("GitHub link", has_link(page, r"github\.com/NomaDamas"))
            add("published shorts linked", sum(1 for h, _ in page.links if "youtube.com/shorts/" in h) >= 3)
        if "privacy" in pages:
            page, text = pages["privacy"]
            add = lambda label, value: results.append((f"{code}/privacy", label, bool(value)))
            add("Google privacy policy link (III.A.2.c)", has_link(page, r"google\.com/policies/privacy|policies\.google\.com/privacy"))
            add("revoke link (III.A.2.h)", has_link(page, REVOKE))
            add("cookies and device storage (III.A.2.g)", words.get("cookies", "\0") in text)
            add("click-to-load YouTube player disclosed (III.A.2.g)", "youtube-nocookie.com" in text)
            add("ads statement (III.A.2.f)", words.get("no_ads", "\0") in text)
            add("retention and deletion", all(w in text for w in words.get("retention", ("\0",))))
            add("Limited Use statement", "Limited Use" in text)
        if "terms" in pages:
            page, text = pages["terms"]
            add = lambda label, value: results.append((f"{code}/terms", label, bool(value)))
            add("YouTube ToS link and binding sentence (III.A.1)", has_link(page, r"youtube\.com/t/terms") and "agree to be bound by the YouTube Terms of Service" in text)
            add("upload notice text (ToS 9.1.i)", "By clicking 'upload,' you certify" in text)
            add("links back to privacy", has_link(page, r"(^|/)privacy/$"))
        if "how-it-works" in pages:
            page, text = pages["how-it-works"]
            add = lambda label, value: results.append((f"{code}/how-it-works", label, bool(value)))
            raw = (ROOT / cfg["langs"][code]["path"] / "how-it-works/index.html").read_text(encoding="utf-8")
            add("architecture diagram", words.get("diagram", "\0") in raw)
            add("data table and revoke steps", words.get("data_table", "\0") in text and words.get("revoke_steps", "\0") in text)

    # The languages are translations of one page, so their structure must match.
    for code in live[1:]:
        base = live[0]
        for name in PAGES:
            a, b = built.get(base, {}).get(name), built.get(code, {}).get(name)
            if not a or not b:
                continue
            pa, pb = a[0], b[0]
            ids_ok = pa.ids == pb.ids
            tags = ("section", "h2", "h3", "img", "video", "table", "tr", "li", "a", "code")
            diff = [t for t in tags if pa.counts.get(t, 0) != pb.counts.get(t, 0)]
            ext = lambda p: sorted(h for h, _ in p.links if h.startswith("http") and "google.com" not in h)
            results.append((f"{code}/{name}", f"same ids as {base}{'' if ids_ok else ': ' + ', '.join(sorted(pa.ids ^ pb.ids)[:6])}", ids_ok))
            results.append((f"{code}/{name}", f"same element counts as {base}{'' if not diff else ': ' + ', '.join(diff)}", not diff))
            results.append((f"{code}/{name}", f"same outside links as {base}", ext(pa) == ext(pb)))
    return results


def main() -> int:
    publish = "--publish" in sys.argv[1:]
    results = check_site(publish)
    bad = [r for r in results if not r[2]]
    print(f"{len(results) - len(bad)}/{len(results)} passed" + (" (publish)" if publish else ""))
    for where, label, _ in bad:
        print(f"    FAIL {where}: {label}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

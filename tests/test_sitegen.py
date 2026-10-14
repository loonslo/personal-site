from __future__ import annotations

import hashlib
import json
import re
import shutil
import socket
from html import escape as html_escape
from html.parser import HTMLParser
from pathlib import Path

import pytest

import build
from sitegen import checks, content, icons, render

ROOT = Path(__file__).resolve().parents[1]


class _MetadataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.description = ""
        self.json_ld: list[str] = []
        self.script_types: list[str | None] = []
        self._in_json_ld = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "meta" and attributes.get("name") == "description":
            self.description = attributes.get("content") or ""
        if tag == "script":
            self.script_types.append(attributes.get("type"))
            self._in_json_ld = attributes.get("type") == "application/ld+json"
            if self._in_json_ld:
                self.json_ld.append("")

    def handle_data(self, data: str) -> None:
        if self._in_json_ld:
            self.json_ld[-1] += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self._in_json_ld = False


def test_real_content_is_valid() -> None:
    site = content.load_site(ROOT / "content" / "site.json")
    projects = content.load_projects(ROOT / "content" / "projects.json", ROOT / "content" / "projects")
    assert site["name"] == "半開"
    assert {p.status for p in projects} <= set(content.STATUSES)
    assert len({p.slug for p in projects}) == len(projects)


def _write_site_config(path: Path, *, base_url: str = "https://example.com", account_href: str = "") -> None:
    path.write_text(
        json.dumps(
            {
                "name": "Site",
                "tagline": "Tagline",
                "poem": ["line"],
                "identity": "identity",
                "intro": "intro",
                "headline": "headline",
                "description": "description",
                "base_url": base_url,
                "sponsored_links": [{"label": "project", "href": "https://project.example.com"}],
                "email": "",
                "accounts": [{"label": "account", "handle": "user", "href": account_href}],
            }
        ),
        encoding="utf-8",
    )


@pytest.mark.parametrize(
    "href",
    [
        "javascript:alert(1)",
        "data:text/html,alert(1)",
        "http://example.com/",
        "https://user:password@example.com/",
        "https://bad host.example/",
        "https://127.0.0.1/",
    ],
)
def test_site_rejects_unsafe_account_links(tmp_path: Path, href: str) -> None:
    path = tmp_path / "site.json"
    _write_site_config(path, account_href=href)
    with pytest.raises(content.ContentError, match="HTTPS"):
        content.load_site(path)


def test_site_base_url_must_be_an_https_origin(tmp_path: Path) -> None:
    path = tmp_path / "site.json"
    _write_site_config(path, base_url="https://example.com/private")
    with pytest.raises(content.ContentError, match="base_url"):
        content.load_site(path)


@pytest.mark.parametrize("href", ["javascript:alert(1)", "http://project.example.com", "https://127.0.0.1/"])
def test_site_rejects_unsafe_sponsored_links(tmp_path: Path, href: str) -> None:
    path = tmp_path / "site.json"
    _write_site_config(path)
    site = json.loads(path.read_text(encoding="utf-8"))
    site["sponsored_links"][0]["href"] = href
    path.write_text(json.dumps(site), encoding="utf-8")
    with pytest.raises(content.ContentError, match="sponsored_links.*HTTPS"):
        content.load_site(path)


@pytest.mark.parametrize("skills", ["Python", [""], ["   "], [None], [42]])
def test_site_rejects_invalid_skills(tmp_path: Path, skills: object) -> None:
    path = tmp_path / "site.json"
    _write_site_config(path)
    site = json.loads(path.read_text(encoding="utf-8"))
    site["skills"] = skills
    path.write_text(json.dumps(site), encoding="utf-8")
    with pytest.raises(content.ContentError, match="skills"):
        content.load_site(path)


def test_external_checker_rejects_private_dns_without_connecting(monkeypatch: pytest.MonkeyPatch) -> None:
    def resolve_private(*args, **kwargs):
        return [(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", ("127.0.0.1", 443))]

    def fail_connect(*args, **kwargs):
        pytest.fail("private addresses must be rejected before a socket is opened")

    monkeypatch.setattr(checks.socket, "getaddrinfo", resolve_private)
    monkeypatch.setattr(checks.socket, "socket", fail_connect)
    errors = checks.check_external({"https://attacker.example/"})
    assert len(errors) == 1
    assert "非公网地址" in errors[0]


def test_external_checker_rejects_non_web_ports_before_resolving(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_resolve(*args, **kwargs):
        pytest.fail("non-web ports must be rejected before DNS resolution")

    monkeypatch.setattr(checks.socket, "getaddrinfo", fail_resolve)
    errors = checks.check_external({"https://example.com:22/"})
    assert len(errors) == 1
    assert "仅允许 HTTP 80 和 HTTPS 443 端口" in errors[0]


@pytest.mark.parametrize(
    ("item", "message"),
    [
        ({"slug": "Bad_Slug", "status": "open", "link": {"type": "external", "href": "https://x.y"}}, "slug"),
        ({"slug": "a", "status": "done", "link": {"type": "none"}}, "status"),
        ({"slug": "a", "status": "open", "link": {"type": "external", "href": "http://x.y"}}, "https://"),
        ({"slug": "a", "status": "intro", "link": {"type": "page"}}, "缺少介绍页"),
        ({"slug": "a", "status": "open", "link": {"type": "none"}}, "建设中"),
        ({"slug": "a", "status": "building", "link": {"type": "none"},
          "app": {"href": "https://x.y", "label": "试用", "short_label": 3}}, "short_label"),
    ],
)
def test_project_validation_rejects_bad_items(tmp_path: Path, item: dict, message: str) -> None:
    data = [{"name": "名称", "summary": "一句话", **item}]
    path = tmp_path / "projects.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(content.ContentError, match=message):
        content.load_projects(path, tmp_path)


def test_duplicate_slug_is_rejected(tmp_path: Path) -> None:
    item = {"slug": "a", "name": "名称", "summary": "一句话", "status": "building", "link": {"type": "none"}}
    path = tmp_path / "projects.json"
    path.write_text(json.dumps([item, item], ensure_ascii=False), encoding="utf-8")
    with pytest.raises(content.ContentError, match="重复"):
        content.load_projects(path, tmp_path)


def test_frontmatter_keeps_colons_in_values() -> None:
    meta, body = content.parse_frontmatter("---\ntitle: A: B\ndraft: true\n---\n正文\n")
    assert meta == {"title": "A: B", "draft": "true"}
    assert body == "正文\n"


def test_frontmatter_without_end_marker_fails() -> None:
    with pytest.raises(content.ContentError):
        content.parse_frontmatter("---\ntitle: A\n正文")


def test_markdown_escapes_raw_html_and_wraps_tables() -> None:
    html = content.render_markdown("<script>x</script>\n\n| a | b |\n| - | - |\n| 1 | 2 |\n")
    assert "<script>" not in html
    assert '<div class="table-wrap"><table>' in html


def test_each_status_has_a_distinct_moon() -> None:
    shapes = {icons.moon(s) for s in content.STATUSES}
    assert len(shapes) == len(content.STATUSES)


def test_build_outputs_pages_and_skips_drafts(tmp_path: Path) -> None:
    out = build.build(ROOT, tmp_path / "dist")
    for rel in ["index.html", "about/index.html", "projects/knowledge/index.html",
                "projects/alpha-research/index.html", "projects/finunity/index.html",
                "404.html", "sitemap.xml", "robots.txt",
                "favicon.svg", "_headers"]:
        assert (out / rel).exists(), rel
    assert (out / "writing/index.html").exists()
    for locale in ("", "en/"):
        for slug in ("rag-hybrid-search", "testing-to-ai-development"):
            assert (out / f"{locale}writing/{slug}/index.html").exists()
        assert not (out / f"{locale}writing/ui-testing-ten-years/index.html").exists()
        feed = (out / f"{locale}feed.xml").read_text(encoding="utf-8")
        assert feed.count("<entry>") == 2
        assert "ui-testing-ten-years" not in feed
    index = (out / "index.html").read_text(encoding="utf-8")
    assert "文章" in index.split("<main")[0]
    assert re.search(r'<script src="/site\.js\?v=[0-9a-f]{10}" defer></script>', index)
    assert "<script>" not in index
    assert "<title>半開｜个人产品与开发札记</title>" in index
    assert '<h1 class="hero__lead">' in index
    assert "我是半開" in index
    assert "软件测试出身" in index
    assert "写开发过程" in index
    assert 'class="hero__job"' not in index
    hero = index.split('<section class="hero">')[1].split('</section>')[0]
    assert 'href="/writing/rag-hybrid-search/"' in hero
    assert "RAG 混合检索怎么做" in hero
    assert 'class="scroll"' not in index
    assert 'class="hero__actions"' not in hero
    names = ["衡仓", "投资看板", "角色设定卡"]
    listing = index.split('<ol class="index">')[1].split("</ol>")[0]
    assert listing.count('class="index__item"') == 3
    assert 'class="index__no"' not in listing
    assert [listing.index(name) for name in names] == sorted(listing.index(name) for name in names)
    assert "WorldQuant Alpha 研究工具" not in listing
    catalog = (out / "projects/index.html").read_text(encoding="utf-8")
    assert "WorldQuant Alpha 研究工具" in catalog
    assert "AI 应用开发学习仓库" in catalog
    assert "其他个人项目" not in index
    about = (out / "about" / "index.html").read_text(encoding="utf-8")
    assert "关于我 · 半開" in about
    assert "职业经历与角色" in about
    assert 'id="contact"' in about
    assert (out / "site.js").exists()
    assert "Content-Security-Policy" in (out / "_headers").read_text(encoding="utf-8")

    preview = build.build(ROOT, tmp_path / "preview", drafts=True)
    assert (preview / "writing" / "index.html").exists()
    assert (preview / "feed.xml").exists()


def test_navigation_and_sponsored_links_are_separated(tmp_path: Path) -> None:
    site = content.load_site(ROOT / "content" / "site.json")
    out = build.build(ROOT, tmp_path / "dist")
    index = (out / "index.html").read_text(encoding="utf-8")
    nav = index.split('<nav class="nav"')[1].split('</nav>')[0]
    assert 'href="/projects/"' in nav
    assert 'href="/writing/"' in nav
    assert 'href="/about/"' in nav
    assert 'https://' not in nav
    footer = index.split('<footer')[1]
    for link in site["sponsored_links"]:
        assert f'href="{link["href"]}" target="_blank" rel="sponsored noopener"' in footer
        assert link["href"] not in index.split('<footer')[0]
    assert "推广" in footer


def test_about_page_puts_contact_in_side_column(tmp_path: Path) -> None:
    site = content.load_site(ROOT / "content" / "site.json")
    out = build.build(ROOT, tmp_path / "dist")
    about = (out / "about" / "index.html").read_text(encoding="utf-8")
    assert '<article class="wrap page about">' in about
    _, aside_open, rest = about.partition('<aside class="about__aside"')
    assert aside_open, "联系应放在侧栏里"
    aside, _, tail = rest.partition("</aside>")
    assert "正在找工作" not in about
    assert "求职方向" not in about
    assert 'id="contact"' in aside
    assert site["email"] in aside
    # 侧栏在正文之后：窄屏单列时仍是 标题 → 正文 → 联系
    assert about.index('class="prose"') < about.index('<aside class="about__aside"')
    assert tail.lstrip().startswith("</article>")


def test_built_person_schema_and_page_descriptions(tmp_path: Path) -> None:
    site = content.load_site(ROOT / "content" / "site.json")
    about = content.load_doc(ROOT / "content" / "about.md")
    out = build.build(ROOT, tmp_path / "dist", drafts=True)
    descriptions = {}
    schemas = []
    for path in out.rglob("*.html"):
        parser = _MetadataParser()
        parser.feed(path.read_text(encoding="utf-8"))
        # boot.js 与 site.js 两个外置脚本，加上唯一的 JSON-LD；页面里没有任何内联脚本
        assert parser.script_types == [None, None, "application/ld+json"]
        assert len(parser.json_ld) == 1
        person = json.loads(parser.json_ld[0])
        assert person["@context"] == "https://schema.org"
        assert person["@type"] == "Person"
        assert person["@id"] == site["base_url"] + "/#person"
        assert person["url"] == site["base_url"] + "/"
        assert person["name"] == site["name"]
        assert person["description"] == site["identity"]
        assert person["knowsAbout"] == site["skills"]
        assert person["email"] == site["email"]
        assert person["sameAs"] == [a["href"] for a in site["accounts"] if a["href"]]
        assert all(person["sameAs"])
        schemas.append(person)
        descriptions[path.relative_to(out).as_posix()] = parser.description
    assert all(person == schemas[0] for person in schemas)
    assert descriptions["index.html"] == site["description"]
    assert descriptions["about/index.html"] == about.meta["summary"]
    assert descriptions["index.html"] != descriptions["about/index.html"]
    assert "AI 应用项目经历" in descriptions["about/index.html"]
    assert "19/20" not in descriptions["about/index.html"]
    assert "19 个" in (out / "about/index.html").read_text(encoding="utf-8")


def test_person_schema_omits_unfilled_public_fields() -> None:
    site = content.load_site(ROOT / "content" / "site.json")
    site = {**site, "email": "", "skills": [], "accounts": [{"href": ""}]}
    ctx = render.Context(site, False, "/styles.css", 2026)
    parser = _MetadataParser()
    parser.feed(render.not_found(ctx))
    person = json.loads(parser.json_ld[0])
    assert "email" not in person
    assert "sameAs" not in person
    assert "knowsAbout" not in person


def test_not_found_page_is_not_indexed_or_canonicalized() -> None:
    site = content.load_site(ROOT / "content" / "site.json")
    ctx = render.Context(site, False, "/styles.css", 2026)
    page = render.not_found(ctx)
    assert '<meta name="robots" content="noindex">' in page
    assert 'rel="canonical"' not in page
    assert 'hreflang=' not in page.split("</head>", 1)[0]


def test_public_seo_manifest_matches_default_build(tmp_path: Path) -> None:
    out = build.build(ROOT, tmp_path / "dist")
    pages = json.loads((ROOT / "docs/seo-pages.json").read_text(encoding="utf-8"))["pages"]
    sitemap = (out / "sitemap.xml").read_text(encoding="utf-8")
    for page in pages:
        html = (out / page["source"]).read_text(encoding="utf-8")
        assert page["canonical"] in sitemap
        assert f'<link rel="canonical" href="{page["canonical"]}">' in html
        parser = _MetadataParser()
        parser.feed(html)
        assert parser.description
        assert '<meta name="robots" content="noindex">' not in html
    assert "404.html" not in sitemap


def test_person_schema_cannot_close_script_element() -> None:
    site = content.load_site(ROOT / "content" / "site.json")
    hostile = '</ScRiPt><script>alert("x")</script>&<!--'
    site = {**site, "name": hostile, "identity": hostile, "skills": [hostile]}
    ctx = render.Context(site, False, "/styles.css", 2026)
    parser = _MetadataParser()
    parser.feed(render.not_found(ctx))
    # boot.js 与 site.js 两个外置脚本，加上唯一的 JSON-LD；页面里没有任何内联脚本
    assert parser.script_types == [None, None, "application/ld+json"]
    assert len(parser.json_ld) == 1
    assert "<" not in parser.json_ld[0]
    person = json.loads(parser.json_ld[0])
    assert person["name"] == hostile
    assert person["description"] == hostile
    assert person["knowsAbout"] == [hostile]


def test_build_refuses_to_delete_foreign_directory(tmp_path: Path) -> None:
    foreign = tmp_path / "dist"
    foreign.mkdir()
    (foreign / "keep.txt").write_text("不是构建产物", encoding="utf-8")
    with pytest.raises(build.BuildError):
        build.build(ROOT, foreign)
    assert (foreign / "keep.txt").exists()


def test_built_site_has_no_broken_internal_links(tmp_path: Path) -> None:
    out = build.build(ROOT, tmp_path / "dist", drafts=True)
    assert checks.check_internal(out, checks.scan_pages(out)) == []


def test_internal_check_reports_missing_file_and_anchor(tmp_path: Path) -> None:
    (tmp_path / "index.html").write_text(
        '<a href="/missing/">x</a><a href="/#nowhere">y</a><a href="#top">z</a><p id="top"></p>',
        encoding="utf-8",
    )
    errors = checks.check_internal(tmp_path, checks.scan_pages(tmp_path))
    assert any("/missing/" in e for e in errors)
    assert any("#nowhere" in e for e in errors)
    assert not any("#top" in e for e in errors)


def test_blocklist_scan_is_case_insensitive(tmp_path: Path) -> None:
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("<p>Hello ACME team</p>", encoding="utf-8")
    words = tmp_path / "words.txt"
    words.write_text("# 注释\nacme\n不存在的词\n", encoding="utf-8")
    hits = checks.scan_blocklist(dist, checks.load_blocklist(words))
    assert hits == ["index.html: 出现禁用词「acme」"]


def test_placeholders_are_reported() -> None:
    site = {"email": "", "base_url": "https://example.pages.dev", "accounts": [{"label": "小红书", "href": ""}]}
    notes = checks.placeholders(site)
    assert len(notes) == 3


def _vercel_header_rules() -> dict[str, dict]:
    config = json.loads((ROOT / "vercel.json").read_text(encoding="utf-8"))
    return {rule["source"]: rule for rule in config["headers"]}


def test_scripts_are_versioned_by_content_and_ordered_for_first_paint(tmp_path: Path) -> None:
    out = build.build(ROOT, tmp_path / "dist")
    for name in ("boot.js", "site.js"):
        digest = hashlib.sha256((out / name).read_bytes()).hexdigest()[:10]
        for page in ("index.html", "about/index.html", "en/index.html", "projects/finunity/index.html", "404.html"):
            html = (out / page).read_text(encoding="utf-8")
            assert f'src="/{name}?v={digest}"' in html, (name, page)
            assert f'src="/{name}"' not in html, (name, page)
    index = (out / "index.html").read_text(encoding="utf-8")
    # boot.js 同步执行、在样式表之前；site.js 延迟执行，不挡首屏
    boot, css, site = (index.index(s) for s in ('<script src="/boot.js?v=', '<link rel="stylesheet"', '<script src="/site.js?v='))
    assert boot < css < site
    assert re.search(r'<script src="/boot\.js\?v=[0-9a-f]{10}"></script>', index)
    assert re.search(r'<script src="/site\.js\?v=[0-9a-f]{10}" defer></script>', index)


def test_script_version_changes_when_the_file_changes(tmp_path: Path) -> None:
    root = tmp_path / "site"
    shutil.copytree(ROOT / "static", root / "static")
    shutil.copytree(ROOT / "content", root / "content")

    def version(out: Path) -> str:
        return re.search(r"/site\.js\?v=([0-9a-f]{10})", (out / "index.html").read_text(encoding="utf-8"))[1]

    first = version(build.build(root, tmp_path / "one"))
    (root / "static" / "site.js").write_text('"use strict";\nconsole.log("changed");\n', encoding="utf-8")
    assert version(build.build(root, tmp_path / "two")) != first


def test_entrance_motion_plays_once_and_page_changes_use_view_transitions() -> None:
    css = (ROOT / "static" / "styles.css").read_text(encoding="utf-8")
    motion = css[css.index("/* ---------- 动效 ---------- */"):]
    motion = motion[:motion.index("@media (prefers-reduced-motion: reduce)")]
    # 每条 animation 声明都必须挂在 html:not(.seen) 下，否则站内每翻一页都会重播
    for line in motion.splitlines():
        stripped = line.strip()
        if stripped.startswith("@keyframes") or stripped.startswith("from") or stripped.startswith("to"):
            continue
        if "animation:" in stripped or "animation-delay:" in stripped:
            assert stripped.startswith("html:not(.seen) "), stripped
    assert "@view-transition { navigation: auto; }" in motion
    assert "@media (prefers-reduced-motion: no-preference)" in motion
    # 滚动显现不再依赖 .js 类（它在脚本到达后才出现，会让首屏内的块先闪一下）
    assert ".js [data-reveal]" not in css
    assert "[data-reveal].is-pending" in css


def test_boot_and_site_scripts_are_small_and_safe() -> None:
    boot = (ROOT / "static" / "boot.js").read_text(encoding="utf-8")
    site = (ROOT / "static" / "site.js").read_text(encoding="utf-8")
    assert 'classList.add("seen")' in boot and "try {" in boot and "catch" in boot
    for text in (boot, site):
        assert "eval(" not in text and "innerHTML" not in text and "document.write" not in text
    # 预取只针对同源页面，跨域链接只预连接，不能把用户页面地址发给第三方
    assert 'hint("prefetch"' in site and 'hint("preconnect", url.origin)' in site
    assert "saveData" in site


def test_hosting_marks_only_versioned_scripts_and_styles_immutable() -> None:
    rules = _vercel_header_rules()
    immutable = [{"key": "Cache-Control", "value": "public, max-age=31536000, immutable"}]
    assert rules["/styles.css"]["headers"] == immutable
    for source in ("/site.js", "/boot.js"):
        assert rules[source]["headers"] == immutable
        # 没有 ?v= 的请求（例如旧版本页面）不能被缓存一年
        assert rules[source]["has"] == [{"type": "query", "key": "v"}]
    # 页面本身仍然每次校验
    assert not any("html" in source or source == "/" for source in rules if "Cache-Control" in json.dumps(rules[source]))


# ---- 主站到三个子站的交接：卡片承诺、深链、名称、截图 ----------------------------------------------

SAMPLE_ENTRANCES = {
    "zh": {
        "finunity": "https://finunity.halfopen.dev/app?from=portfolio&lang=zh",
        "character": "https://character.halfopen.dev/workspace/?start=guide&from=portfolio&lang=zh",
        "knowledge": "https://knowledge.halfopen.dev/chat?from=portfolio&lang=zh",
    },
    "en": {
        "finunity": "https://finunity.halfopen.dev/app?from=portfolio&lang=en",
        "character": "https://character.halfopen.dev/workspace/?start=guide&from=portfolio&lang=en",
        "knowledge": "https://knowledge.halfopen.dev/chat?from=portfolio&lang=en",
    },
}
FEATURED = ("finunity", "character")  # the home page lists three featured products; Knowledge is in the catalogue


def _projects(locale: str) -> dict[str, content.Project]:
    base = ROOT / "content" / ("en" if locale == "en" else "")
    return {p.slug: p for p in content.load_projects(base / "projects.json", base / "projects")}


@pytest.mark.parametrize("locale", ["zh", "en"])
def test_sample_sites_are_entered_through_a_marked_deep_link(locale: str) -> None:
    projects = _projects(locale)
    for slug, href in SAMPLE_ENTRANCES[locale].items():
        app = projects[slug].app
        assert app is not None and app.href == href
        # 按钮写点了会发生什么，不带登录门槛的措辞；短标签只用在首页的紧凑行
        assert "登录" not in app.label and "sign in" not in app.label.lower()
        assert app.short_label and len(app.short_label) <= len(app.label)
    # 没有示例的看板仍是普通入口，不带来源标记，也没有短标签
    dashboards = projects["dashboards"].app
    assert dashboards is not None and "from=portfolio" not in dashboards.href and not dashboards.short_label


@pytest.mark.parametrize(("locale", "prefix", "generic"), [("zh", "", "打开 ↗"), ("en", "en/", "Open ↗")])
def test_cards_and_project_pages_promise_what_the_sample_pages_deliver(
    tmp_path: Path, locale: str, prefix: str, generic: str
) -> None:
    out = build.build(ROOT, tmp_path / "dist")
    projects = _projects(locale)
    home = (out / prefix / "index.html").read_text(encoding="utf-8")
    listing = home.split('<ol class="index">')[1].split("</ol>")[0]
    catalog = (out / prefix / "projects" / "index.html").read_text(encoding="utf-8")
    for slug in SAMPLE_ENTRANCES[locale]:
        app = projects[slug].app
        assert app is not None
        href = f'href="{html_escape(app.href)}"'
        if slug in FEATURED:
            assert href in listing and f"{app.short_label} ↗" in listing, "首页卡片：短标签加深链"
        assert href in catalog and f"{app.label} ↗" in catalog, "产品列表：完整标签加深链"
        page = (out / prefix / "projects" / slug / "index.html").read_text(encoding="utf-8")
        assert f'class="button" {href}' in page and f"{app.label} ↗" in page, "项目页按钮：完整标签加深链"
    assert generic in listing, "没有短标签的入口保持通用文字"


def test_every_link_to_the_knowledge_demo_goes_through_the_marked_entrance(tmp_path: Path) -> None:
    """演示开放后，主站所有指向 knowledge 演示站的链接都走带来源和语言参数的 /chat 入口，不直接落到子站根目录。"""
    out = build.build(ROOT, tmp_path / "dist")
    seen = 0
    for page in out.rglob("*.html"):
        language = "en" if page.relative_to(out).parts[0] == "en" else "zh"
        for href in re.findall(r'href="(https://knowledge\.halfopen\.dev[^"]*)"', page.read_text(encoding="utf-8")):
            seen += 1
            assert href == f"https://knowledge.halfopen.dev/chat?from=portfolio&amp;lang={language}", (page.relative_to(out), href)
    assert seen >= 4, "卡片、项目页按钮、产品列表和文章里应该都有入口"
    for locale in ("zh", "en"):
        knowledge = _projects(locale)["knowledge"]
        assert knowledge.status == "intro", "产品本身仍只是介绍；在线的只是只读示例"


@pytest.mark.parametrize(
    ("locale", "prefix", "names"),
    [
        ("zh", "", {"knowledge": "Knowledge 本地知识库", "finunity": "衡仓", "character": "角色设定卡"}),
        ("en", "en/", {"knowledge": "Knowledge", "finunity": "Hengcang", "character": "Character Atelier"}),
    ],
)
def test_each_project_keeps_one_name_across_card_page_title_and_about(
    tmp_path: Path, locale: str, prefix: str, names: dict[str, str]
) -> None:
    out = build.build(ROOT, tmp_path / "dist")
    projects = _projects(locale)
    about = (out / prefix / "about" / "index.html").read_text(encoding="utf-8")
    for slug, name in names.items():
        assert projects[slug].name == name
        page = (out / prefix / "projects" / slug / "index.html").read_text(encoding="utf-8")
        assert f"<title>{name} · 半開</title>" in page
        assert f'<h1 class="page-title">{name}</h1>' in page
        assert f'<a href="/{prefix}projects/{slug}/">{name}</a>' in about


def test_project_screenshots_carry_their_size_and_exist(tmp_path: Path) -> None:
    out = build.build(ROOT, tmp_path / "dist")
    for rel in ("projects/finunity", "en/projects/finunity", "projects/character", "en/projects/character",
                "projects/knowledge", "en/projects/knowledge"):
        page = (out / rel / "index.html").read_text(encoding="utf-8")
        shots = [tag for tag in re.findall(r"<img [^>]*>", page) if 'src="/shots/' in tag]
        assert shots, rel
        for tag in shots:
            src = re.search(r'src="(/shots/[^"]+)"', tag).group(1)
            width = int(re.search(r'width="(\d+)"', tag).group(1))
            height = int(re.search(r'height="(\d+)"', tag).group(1))
            assert (width, height) == content._png_size(out / src.lstrip("/")), src
            assert 'loading="lazy"' in tag and re.search(r'alt="[^"]{20,}"', tag), "要有懒加载和说明性的替代文字"
        # 说明文字写在图片后面，同属一个段落，样式把它排成图下小字
        assert re.search(r"<p><img [^>]*/>\s*<em>[^<]+</em></p>", page), rel


def test_markdown_images_only_get_a_size_for_real_local_screenshots() -> None:
    sized = content.render_markdown("![图](/shots/finunity-overview.zh.png)")
    assert 'width="1280" height="980"' in sized and 'loading="lazy"' in sized
    for src in ("/shots/missing.png", "https://example.com/a.png", "/styles.css", "/shots/../styles.css",
                "/shots/../../README.md"):
        assert "width=" not in content.render_markdown(f"![x]({src})"), src
    # 不是 PNG 或不存在的文件读不出尺寸
    assert content._png_size(ROOT / "static" / "favicon.svg") is None
    assert content._png_size(ROOT / "static" / "shots" / "nope.png") is None

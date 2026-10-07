from __future__ import annotations

import hashlib
import json
import re
import shutil
import socket
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
                "job": "job",
                "description": "description",
                "base_url": base_url,
                "project_links": [{"label": "project", "href": "https://project.example.com"}],
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
def test_site_rejects_unsafe_project_links(tmp_path: Path, href: str) -> None:
    path = tmp_path / "site.json"
    _write_site_config(path)
    site = json.loads(path.read_text(encoding="utf-8"))
    site["project_links"][0]["href"] = href
    path.write_text(json.dumps(site), encoding="utf-8")
    with pytest.raises(content.ContentError, match="project_links.*HTTPS"):
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
    assert "<title>半開｜AI 应用与全栈开发作品集</title>" in index
    assert '<h1 class="hero__lead">' in index
    assert "十年互联网经验" in index
    assert "从软件工程走向 AI 应用开发" in index
    assert "做过软件测试、Python 开发和产品工作。" in index
    assert "关注 AI Agent、自动化工作流" in index
    # 首页不再有底部“经历与联系”区块；进入经历页靠导航和首屏链接
    assert 'id="about-title"' not in index
    assert "先说边界，再看结果" not in index
    assert '<a class="text-link" href="/about/">经历与联系</a>' in index
    names = ["个人知识服务", "WorldQuant Alpha 研究工具", "AI 应用开发学习仓库", "衡仓", "投资看板", "角色设定卡"]
    # 只在项目列表内比较顺序：站点 description 里也会出现项目名
    listing = index.split('<ol class="index">')[1].split("</ol>")[0]
    assert [listing.index(name) for name in names] == sorted(listing.index(name) for name in names)
    assert "其他个人项目" not in index
    about = (out / "about" / "index.html").read_text(encoding="utf-8")
    assert "经历与求职方向 · 半開" in about
    assert "职业经历与角色" in about
    assert 'id="contact"' in about
    assert (out / "site.js").exists()
    assert "Content-Security-Policy" in (out / "_headers").read_text(encoding="utf-8")

    preview = build.build(ROOT, tmp_path / "preview", drafts=True)
    assert (preview / "writing" / "index.html").exists()
    assert (preview / "feed.xml").exists()


def test_project_navigation_links_open_in_new_tabs(tmp_path: Path) -> None:
    site = content.load_site(ROOT / "content" / "site.json")
    out = build.build(ROOT, tmp_path / "dist")
    index = (out / "index.html").read_text(encoding="utf-8")
    for link in site["project_links"]:
        assert (
            f'<a href="{link["href"]}" target="_blank" rel="noopener">'
            f'{link["label"]}<span class="sr-only">（在新窗口打开）</span>'
        ) in index


def test_about_page_puts_job_and_contact_in_side_column(tmp_path: Path) -> None:
    site = content.load_site(ROOT / "content" / "site.json")
    out = build.build(ROOT, tmp_path / "dist")
    about = (out / "about" / "index.html").read_text(encoding="utf-8")
    assert '<article class="wrap page about">' in about
    _, aside_open, rest = about.partition('<aside class="about__aside"')
    assert aside_open, "求职与联系应放在侧栏里"
    aside, _, tail = rest.partition("</aside>")
    assert "正在找工作" in aside
    assert site["job"] in aside
    assert 'id="contact"' in aside
    assert site["email"] in aside
    # 侧栏在正文之后：窄屏单列时仍是 标题 → 正文 → 求职与联系
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

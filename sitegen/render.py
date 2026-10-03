"""页面模板。来自 JSON 的文字全部转义；Markdown 由 mistune 渲染，其中的原始 HTML 也会被转义。"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date
from html import escape
from typing import Any
from xml.sax.saxutils import escape as xml_escape

from .content import Doc, Project
from .icons import SVG_DEFS, moon, seal

@dataclass(frozen=True)
class Context:
    site: dict[str, Any]
    show_writing: bool
    css_href: str
    year: int
    locale: str = "zh"
    other_paths: frozenset[str] = frozenset()
    person_site: dict[str, Any] | None = None

    @property
    def base(self) -> str:
        return self.site["base_url"].rstrip("/")

    @property
    def copy(self) -> dict[str, Any]:
        return _COPY[self.locale]

    def page_href(self, path: str, *, locale: str | None = None) -> str:
        target_locale = locale or self.locale
        prefix = "/en" if target_locale == "en" else ""
        return f"{prefix}{path}" if prefix else path

    def language_href(self, path: str) -> str:
        target_locale = "en" if self.locale == "zh" else "zh"
        target_path = path if path in self.other_paths else "/"
        return self.page_href(target_path, locale=target_locale)


_COPY: dict[str, dict[str, Any]] = {
    "zh": {
        "html_lang": "zh-CN", "nav_label": "主导航", "nav_work": "作品",
        "nav_writing": "文章", "nav_about": "经历", "language": "EN",
        "switch_language": "切换到英文", "skip": "跳到正文", "home_aria": "，回到首页",
        "new_window": "（在新窗口打开）", "footer_rss": "RSS", "home_eyebrow": "个人作品集",
        "cta_work": "看代表作品", "cta_about": "经历与联系", "projects_heading": "个人项目",
        "projects_desc": "从问题、实现到验证，查看我实际做过的事。", "writing_heading": "文章",
        "writing_desc": "做的过程和想明白的事。", "all_writing": "全部文章",
        "project_page": "介绍", "project_go": "前往", "not_open": "尚未开放",
        "flow_label": "方案流程", "crumb_label": "位置", "projects": "项目",
        "back_projects": "回到项目目录", "status": "状态", "technology": "技术",
        "updated": "更新", "about_aside": "求职与联系", "job_heading": "正在找工作",
        "contact_heading": "联系与账号", "email": "邮箱", "missing": "待补",
        "writing_list_desc": "半開的文章列表。", "back_writing": "回到文章列表",
        "not_found_title": "这朵花还没开。", "not_found_desc": "你要找的页面不存在，或者还在路上。",
        "back_home": "回到首页", "rss_title": "RSS",
        "statuses": {"building": "建设中", "intro": "仅介绍", "open": "开源", "live": "在线"},
    },
    "en": {
        "html_lang": "en", "nav_label": "Main navigation", "nav_work": "Work",
        "nav_writing": "Writing", "nav_about": "About", "language": "中文",
        "switch_language": "Switch language to Chinese", "skip": "Skip to content",
        "home_aria": ", back to home", "new_window": " (opens in a new tab)",
        "footer_rss": "RSS", "home_eyebrow": "Selected work & projects",
        "cta_work": "Selected work", "cta_about": "About & contact", "projects_heading": "Projects",
        "projects_desc": "A look at the problems, implementation, and validation behind my work.",
        "writing_heading": "Writing", "writing_desc": "Notes on what I build and learn.",
        "all_writing": "All articles", "project_page": "Case study", "project_go": "Visit",
        "not_open": "Not yet available", "flow_label": "Project workflow", "crumb_label": "Breadcrumb",
        "projects": "Projects", "back_projects": "Back to all projects", "status": "Status",
        "technology": "Technologies", "updated": "Updated", "about_aside": "Career and contact",
        "job_heading": "Open to opportunities", "contact_heading": "Contact & profiles",
        "email": "Email", "missing": "Not provided", "writing_list_desc": "Articles by 半開.",
        "back_writing": "Back to all articles", "not_found_title": "This page is still taking shape.",
        "not_found_desc": "The page may have moved, or it may not exist yet.", "back_home": "Back to home",
        "rss_title": "半開 — Writing", "statuses": {"building": "In progress", "intro": "Overview",
            "open": "Open source", "live": "Live"},
    },
}


def _e(text: str) -> str:
    return escape(text, quote=True)


def _phrases(text: str) -> str:
    """按逗号、冒号、分号切成短语，短语之间才换行，避免“正在转 / AI”这种断法。"""
    parts = re.split(r"(?<=[，：；])", text)
    return "".join(f'<span class="phrase">{_e(p)}</span>' for p in parts if p)


def _localized_phrases(text: str, locale: str) -> str:
    if locale == "zh":
        return _phrases(text)
    parts = re.split(r"(?<=[,;:])", text)
    return "".join(f'<span class="phrase">{_e(p)}</span>' for p in parts if p)


def _fmt(d: date | None) -> str:
    return d.strftime("%Y.%m.%d") if d else ""


def _person_json_ld(ctx: Context) -> str:
    """复用公开信息；转义 HTML 特殊字符，防止数据提前关闭 script 标签。"""
    site = ctx.person_site or ctx.site
    person: dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "Person",
        "@id": ctx.base + "/#person",
        "name": site["name"],
        "url": ctx.base + "/",
        "description": site["identity"],
    }
    if site.get("skills"):
        person["knowsAbout"] = site["skills"]
    if site.get("email"):
        person["email"] = site["email"]
    same_as = [a["href"] for a in site["accounts"] if a.get("href")]
    if same_as:
        person["sameAs"] = same_as
    data = json.dumps(person, ensure_ascii=False, separators=(",", ":"))
    data = data.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return f'<script type="application/ld+json">{data}</script>'


def layout(ctx: Context, *, title: str, description: str, path: str, body: str, active: str = "") -> str:
    site = ctx.site
    copy = ctx.copy
    name = site["name"]
    full_title = (
        site.get("home_title", f"{name} · {site['tagline'].rstrip('。.')}")
        if path == "/" else f"{title} · {name}"
    )
    url, og_image = ctx.base + ctx.page_href(path), ctx.base + "/og-image.png"
    nav_items = [
        (copy["nav_work"], ctx.page_href("/#projects"), "projects", False),
        (copy["nav_writing"], ctx.page_href("/writing/"), "writing", False),
        (copy["nav_about"], ctx.page_href("/about/"), "about", False),
        (("特价AI会员" if ctx.locale == "zh" else "AI Membership Deal"), "https://prodclub.xyz/r/2QFJWC", "", True),
        *[(link["label"], link["href"], "", True) for link in site["project_links"]],
    ]
    new_window_text = f'<span class="sr-only">{_e(copy["new_window"])}</span>'
    nav = "".join(
        f'<a href="{_e(href)}"{" aria-current=\"page\"" if key == active else ""}'
        f'{" target=\"_blank\" rel=\"noopener\"" if external else ""}>{_e(label)}'
        f'{new_window_text if external else ""}</a>'
        for label, href, key, external in nav_items
        if key != "writing" or ctx.show_writing
    )
    target_locale = "en" if ctx.locale == "zh" else "zh"
    target_lang = "en" if target_locale == "en" else "zh-CN"
    language_link = (
        f'<a class="language-switch" href="{_e(ctx.language_href(path))}" '
        f'lang="{target_lang}" hreflang="{target_lang}" aria-label="{_e(copy["switch_language"])}">'
        f'{_e(copy["language"])}</a>'
    )
    feed_link = (
        f'\n<link rel="alternate" type="application/atom+xml" title="{_e(copy["rss_title"])}" '
        f'href="{ctx.page_href("/feed.xml")}">'
        if ctx.show_writing else ""
    )
    accounts = "".join(
        f'<a href="{_e(a["href"])}" rel="me">{_e(a["label"])}</a>' for a in site["accounts"] if a.get("href")
    )
    rss = f'<a href="{ctx.page_href("/feed.xml")}">{_e(copy["footer_rss"])}</a>' if ctx.show_writing else ""
    alternates = ""
    if path != "/404.html" and path in ctx.other_paths:
        zh_url = ctx.base + ctx.page_href(path, locale="zh")
        en_url = ctx.base + ctx.page_href(path, locale="en")
        alternates = (
            f'\n<link rel="alternate" hreflang="zh-CN" href="{_e(zh_url)}">'
            f'\n<link rel="alternate" hreflang="en" href="{_e(en_url)}">'
            f'\n<link rel="alternate" hreflang="x-default" href="{_e(zh_url)}">'
        )
    return f"""<!doctype html>
<html lang="{copy["html_lang"]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_e(full_title)}</title>
<meta name="description" content="{_e(description)}">
{('<meta name="robots" content="noindex">' if path == '/404.html' else f'<link rel="canonical" href="{_e(url)}">')}
{alternates}
<meta property="og:type" content="website">
<meta property="og:site_name" content="{_e(name)}">
<meta property="og:title" content="{_e(full_title)}">
<meta property="og:description" content="{_e(description)}">
<meta property="og:url" content="{_e(url)}">
<meta property="og:image" content="{_e(og_image)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#f4efe6" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#161513" media="(prefers-color-scheme: dark)">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="stylesheet" href="{_e(ctx.css_href)}">
<script src="/site.js" defer></script>{feed_link}
{_person_json_ld(ctx)}
</head>
<body>
{SVG_DEFS}
<a class="skip" href="#main">{_e(copy["skip"])}</a>
<header class="site-header">
  <div class="wrap site-header__inner">
    <a class="brand" href="{ctx.page_href("/")}" aria-label="{_e(name + copy["home_aria"])}">{seal("seal--sm")}<span>{_e(name)}</span></a>
    <nav class="nav" aria-label="{_e(copy["nav_label"])}">{nav}{language_link}</nav>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="site-footer">
  <div class="wrap site-footer__inner">
    <p class="site-footer__brand">{seal("seal--xs")}<span>{_e(name)}</span><span class="site-footer__tagline">{_e(site["tagline"])}</span></p>
    <p class="site-footer__links">{accounts}{rss}<span>© {ctx.year}</span></p>
  </div>
</footer>
</body>
</html>
"""


def _project_row(index: int, p: Project, ctx: Context) -> str:
    copy = ctx.copy
    no = f'<span class="index__no">{index:02d}</span>'
    tags = f'<span class="index__tags">{_e(" · ".join(p.tags))}</span>' if p.tags else ""
    main = (
        f'<span class="index__main"><span class="index__name">{_e(p.name)}</span>'
        f'<span class="index__summary">{_e(p.summary)}</span>{tags}</span>'
    )
    status = f'<span class="index__status">{moon(p.status)}<span>{copy["statuses"][p.status]}</span></span>'
    if p.link.type == "page":
        go = f'<span class="index__go">{copy["project_page"]}<span class="index__arrow" aria-hidden="true">→</span></span>'
        inner = f'{no}{main}<span class="index__aside">{status}{go}</span>'
        href = ctx.page_href(f"/projects/{p.slug}/")
        return f'<li class="index__item" data-reveal><a class="index__row" href="{href}">{inner}</a></li>'
    if p.link.type == "external":
        label = _e(p.link.label or copy["project_go"])
        go = (
            f'<span class="index__go">{label}<span class="index__arrow" aria-hidden="true">↗</span>'
            f'<span class="sr-only">{_e(copy["new_window"])}</span></span>'
        )
        inner = f'{no}{main}<span class="index__aside">{status}{go}</span>'
        return (
            f'<li class="index__item" data-reveal><a class="index__row" href="{_e(p.link.href)}" '
            f'target="_blank" rel="noopener">{inner}</a></li>'
        )
    go = f'<span class="index__go">{copy["not_open"]}</span>'
    inner = f'{no}{main}<span class="index__aside">{status}{go}</span>'
    return f'<li class="index__item" data-reveal><div class="index__row is-static">{inner}</div></li>'


def _post_rows(posts: list[Doc], ctx: Context) -> str:
    rows = "".join(
        f'<li data-reveal><a class="post-row" href="{ctx.page_href(f"/writing/{d.slug}/")}">'
        f'<time datetime="{d.date.isoformat() if d.date else ""}">{_fmt(d.date)}</time>'
        f'<span class="post-row__title">{_e(d.title)}</span>'
        f'<span class="post-row__summary">{_e(d.meta.get("summary", ""))}</span></a></li>'
        for d in posts
    )
    return f'<ul class="posts">{rows}</ul>'


def home(ctx: Context, projects: list[Project], posts: list[Doc]) -> str:
    site = ctx.site
    copy = ctx.copy
    name = _e(site["name"])
    intro = "<br>".join(_localized_phrases(line, ctx.locale) for line in site["intro"].splitlines())
    tagline_separator = ";" if ctx.locale == "en" else "，"
    couplet = "".join(
        f'<p class="scroll__line">{_e(part)}</p>'
        for part in (s.strip("，。;,. ") for s in site["tagline"].split(tagline_separator))
        if part
    )
    rows = "".join(_project_row(i, p, ctx) for i, p in enumerate(projects, 1))
    writing = ""
    if posts:
        writing = f"""
<section class="section" id="writing" aria-labelledby="writing-title">
  <div class="wrap">
    <div class="section__head">
      <h2 class="section__title" id="writing-title">{_e(copy["writing_heading"])}</h2>
      <p class="section__desc">{_e(copy["writing_desc"])}</p>
    </div>
    {_post_rows(posts[:5], ctx)}
    <p class="section__more"><a class="text-link" href="{ctx.page_href("/writing/")}">{_e(copy["all_writing"])}</a></p>
  </div>
</section>"""
    body = f"""
<section class="hero">
  <div class="wrap hero__grid">
    <div class="hero__text">
      <p class="hero__eyebrow">{name} · {_e(copy["home_eyebrow"])}</p>
      <h1 class="hero__lead">{_localized_phrases(site["identity"], ctx.locale)}</h1>
      <p class="hero__intro">{intro}</p>
      <p class="hero__job">{_e(site["job"])}</p>
      <p class="hero__actions"><a class="button" href="#projects">{_e(copy["cta_work"])}</a><a class="text-link" href="{ctx.page_href("/about/")}">{_e(copy["cta_about"])}</a></p>
    </div>
    <div class="scroll">
      <p class="scroll__name">{name}{seal("scroll__seal")}</p>
      {couplet}
    </div>
  </div>
</section>

<section class="section" id="projects" aria-labelledby="projects-title">
  <div class="wrap">
    <div class="section__head">
      <h2 class="section__title" id="projects-title">{_e(copy["projects_heading"])}</h2>
      <p class="section__desc">{_e(copy["projects_desc"])}</p>
    </div>
    <ol class="index">{rows}</ol>
  </div>
</section>
{writing}"""
    return layout(ctx, title=site["name"], description=site["description"], path="/", body=body, active="projects")


def project_page(ctx: Context, p: Project, doc: Doc) -> str:
    copy = ctx.copy
    steps = [s.strip() for s in doc.meta.get("flow", "").split("|") if s.strip()]
    flow = (
        f'<ol class="flow" aria-label="{_e(copy["flow_label"])}">'
        + "".join(f"<li><span>{_e(s)}</span></li>" for s in steps)
        + "</ol>"
        if steps else ""
    )
    note = f"<span>· {_e(doc.meta['status_note'])}</span>" if doc.meta.get("status_note") else ""
    tags = f'<div><dt>{_e(copy["technology"])}</dt><dd>{_e(" · ".join(p.tags))}</dd></div>' if p.tags else ""
    updated = f'<div><dt>{_e(copy["updated"])}</dt><dd>{_fmt(doc.date)}</dd></div>' if doc.date else ""
    home_projects = ctx.page_href("/#projects")
    body = f"""
<article class="wrap page">
  <nav class="crumbs" aria-label="{_e(copy["crumb_label"])}"><a href="{home_projects}">{_e(copy["projects"])}</a><span aria-hidden="true">/</span><span>{_e(p.name)}</span></nav>
  <header class="page-head">
    <h1 class="page-title">{_e(p.name)}</h1>
    <p class="page-lead">{_e(p.summary)}</p>
    <dl class="meta">
      <div><dt>{_e(copy["status"])}</dt><dd>{moon(p.status)}<span>{copy["statuses"][p.status]}</span>{note}</dd></div>
      {updated}{tags}
    </dl>
  </header>
  {flow}
  <div class="prose">{doc.html}</div>
  <p class="page-back"><a class="text-link" href="{home_projects}">{_e(copy["back_projects"])}</a></p>
</article>"""
    return layout(ctx, title=p.name, description=p.summary, path=f"/projects/{p.slug}/", body=body, active="projects")


def about_page(ctx: Context, doc: Doc) -> str:
    site = ctx.site
    copy = ctx.copy
    email = site.get("email", "")
    contacts = [(copy["email"], f'<a href="mailto:{_e(email)}">{_e(email)}</a>' if email else f'<span class="muted">{_e(copy["missing"])}</span>')]
    for a in site["accounts"]:
        handle = _e(a["handle"])
        value = f'<a href="{_e(a["href"])}" rel="me">{handle}</a>' if a.get("href") else f"<span>{handle}</span>"
        contacts.append((_e(a["label"]), value))
    contact_html = "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in contacts)
    # 右侧竖排诗句挂轴（呼应首页 hero 的品牌记忆点）按需求移除展示，只注释、不删除。
    # 右栏现在放求职与联系：宽屏时在正文右侧并随滚动吸附，窄屏落到正文之后（见 styles.css“关于页”）。
    # 恢复挂轴时，把下面这段放进 .about__aside 顶部（.poem 样式仍保留在 styles.css）：
    #   <p class="poem">{poem}{seal("poem__seal")}</p>
    # 其中 poem = "".join(f'<span class="poem__line">{_e(line)}</span>' for line in site["poem"])
    body = f"""
<article class="wrap page about">
  <header class="page-head"><h1 class="page-title">{_e(doc.title)}</h1></header>
  <div class="prose">{doc.html}</div>
  <aside class="about__aside" aria-label="{_e(copy["about_aside"])}">
    <h2 class="about__heading">{_e(copy["job_heading"])}</h2>
    <p class="job"><span class="job__dot" aria-hidden="true"></span>{_e(site["job"])}</p>
    <h2 class="about__heading" id="contact">{_e(copy["contact_heading"])}</h2>
    <dl class="contact">{contact_html}</dl>
  </aside>
</article>"""
    return layout(ctx, title=doc.title, description=doc.meta.get("summary", site["description"]), path="/about/", body=body, active="about")


def writing_index(ctx: Context, posts: list[Doc]) -> str:
    copy = ctx.copy
    body = f"""
<section class="wrap page">
  <header class="page-head"><h1 class="page-title">{_e(copy["writing_heading"])}</h1><p class="page-lead">{_e(copy["writing_desc"])}</p></header>
  {_post_rows(posts, ctx)}
</section>"""
    return layout(ctx, title=copy["writing_heading"], description=copy["writing_list_desc"], path="/writing/", body=body, active="writing")


def post_page(ctx: Context, doc: Doc) -> str:
    copy = ctx.copy
    writing_href = ctx.page_href("/writing/")
    body = f"""
<article class="wrap page post">
  <nav class="crumbs" aria-label="{_e(copy["crumb_label"])}"><a href="{writing_href}">{_e(copy["writing_heading"])}</a></nav>
  <header class="page-head">
    <h1 class="page-title">{_e(doc.title)}</h1>
    <p class="post__date"><time datetime="{doc.date.isoformat() if doc.date else ""}">{_fmt(doc.date)}</time></p>
  </header>
  <div class="prose">{doc.html}</div>
  <p class="page-back"><a class="text-link" href="{writing_href}">{_e(copy["back_writing"])}</a></p>
</article>"""
    return layout(
        ctx, title=doc.title, description=doc.meta.get("summary", doc.title),
        path=f"/writing/{doc.slug}/", body=body, active="writing",
    )


def not_found(ctx: Context) -> str:
    copy = ctx.copy
    body = f"""
<section class="wrap notfound">
  {moon("building", "notfound__moon")}
  <h1 class="page-title">{_e(copy["not_found_title"])}</h1>
  <p class="page-lead">{_e(copy["not_found_desc"])}</p>
  <p><a class="button" href="{ctx.page_href("/")}">{_e(copy["back_home"])}</a></p>
</section>"""
    return layout(ctx, title="页面不存在", description=ctx.site["description"], path="/404.html", body=body)


def sitemap(ctx: Context, paths: list[str]) -> str:
    urls = "".join(f"<url><loc>{xml_escape(ctx.base + p)}</loc></url>" for p in paths)
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n'
    )


def robots(ctx: Context) -> str:
    return f"User-agent: *\nAllow: /\nSitemap: {ctx.base}/sitemap.xml\n"


def atom(ctx: Context, posts: list[Doc]) -> str:
    base, name = ctx.base, xml_escape(ctx.site["name"])
    writing_path = ctx.page_href("/writing/")
    feed_path = ctx.page_href("/feed.xml")
    stamp = lambda d: f"{d.isoformat()}T00:00:00+08:00"  # noqa: E731
    entries = "".join(
        f"<entry><title>{xml_escape(d.title)}</title><link href=\"{base}{writing_path}{d.slug}/\"/>"
        f"<id>{base}{writing_path}{d.slug}/</id><updated>{stamp(d.date)}</updated>"
        f"<summary>{xml_escape(d.meta.get('summary', ''))}</summary></entry>"
        for d in posts
        if d.date
    )
    updated = stamp(max(d.date for d in posts if d.date))
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        f'<feed xmlns="http://www.w3.org/2005/Atom"><title>{name}</title>'
        f"<subtitle>{xml_escape(ctx.site['tagline'])}</subtitle>"
        f'<link href="{base}{ctx.page_href("/")}"/><link rel="self" href="{base}{feed_path}"/>'
        f'<id>{base}{ctx.page_href("/")}</id>'
        f"<updated>{updated}</updated><author><name>{name}</name></author>{entries}</feed>\n"
    )

"""页面模板。来自 JSON 的文字全部转义；Markdown 由 mistune 渲染，其中的原始 HTML 也会被转义。"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date
from html import escape, unescape
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
    # 脚本地址带内容哈希（?v=），vercel.json 才能对它们放心设置 immutable；单测里直接构造 Context 时用默认值
    boot_href: str = "/boot.js"
    site_js_href: str = "/site.js"

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
        target_path = path if path in self.other_paths else (
            "/writing/" if path.startswith("/writing/") and "/writing/" in self.other_paths else
            "/projects/" if path.startswith("/projects/") and "/projects/" in self.other_paths else "/"
        )
        return self.page_href(target_path, locale=target_locale)


_COPY: dict[str, dict[str, Any]] = {
    "zh": {
        "html_lang": "zh-CN", "nav_label": "主导航", "nav_work": "产品",
        "nav_writing": "文章", "nav_about": "关于", "language": "EN",
        "switch_language": "切换到英文", "skip": "跳到正文", "home_aria": "，回到首页",
        "new_window": "（在新窗口打开）", "footer_rss": "订阅 RSS", "home_eyebrow": "产品与开发札记",
        "cta_work": "看产品", "cta_about": "关于我", "projects_heading": "精选产品",
        "projects_desc": "一些自己会用的工具。", "writing_heading": "文章",
        "writing_desc": "做的过程和想明白的事。", "all_writing": "全部文章",
        "project_page": "开发记录", "project_go": "前往", "not_open": "尚未开放",
        "flow_label": "方案流程", "crumb_label": "位置", "projects": "产品",
        "back_projects": "回到产品列表", "status": "状态", "technology": "技术",
        "updated": "更新", "about_aside": "联系",
        "contact_heading": "联系与账号", "email": "邮箱", "missing": "待补",
        "writing_list_desc": "半開的文章列表。", "back_writing": "回到文章列表",
        "not_found_title": "这朵花还没开。", "not_found_desc": "你要找的页面不存在，或者还在路上。",
        "back_home": "回到首页", "rss_title": "RSS",
        "statuses": {"building": "建设中", "intro": "仅介绍", "open": "开源", "live": "在线"},
    },
    "en": {
        "html_lang": "en", "nav_label": "Main navigation", "nav_work": "Products",
        "nav_writing": "Writing", "nav_about": "About", "language": "中文",
        "switch_language": "Switch language to Chinese", "skip": "Skip to content",
        "home_aria": ", back to home", "new_window": " (opens in a new tab)",
        "footer_rss": "Subscribe via RSS", "home_eyebrow": "Tools & development notes",
        "cta_work": "Explore tools", "cta_about": "About me", "projects_heading": "Selected tools",
        "projects_desc": "A few tools I use myself.",
        "writing_heading": "Writing", "writing_desc": "Notes on what I build and learn.",
        "all_writing": "All articles", "project_page": "Development notes", "project_go": "Visit",
        "not_open": "Not yet available", "flow_label": "Project workflow", "crumb_label": "Breadcrumb",
        "projects": "Projects", "back_projects": "Back to all projects", "status": "Status",
        "technology": "Technologies", "updated": "Updated", "about_aside": "Contact",
        "contact_heading": "Contact & profiles",
        "email": "Email", "missing": "Not provided", "writing_list_desc": "Articles by 半開.",
        "back_writing": "Back to all articles", "not_found_title": "This page is still taking shape.",
        "not_found_desc": "The page may have moved, or it may not exist yet.", "back_home": "Back to home",
        "rss_title": "半開 — Writing", "statuses": {"building": "In progress", "intro": "Overview",
            "open": "Open source", "live": "Live"},
    },
}

_COPY["zh"].update({
    "all_products": "全部产品与案例", "live_products": "在线产品", "other_projects": "案例与开源",
    "products_lead": "打开工具，或看看它们为什么做、怎么做、怎么验证。",
    "latest_writing": "文章", "read_writing": "读文章", "recent_article": "最近写的", "open_product": "打开", "toc": "本文目录",
    "related_product": "相关产品", "continue_reading": "继续阅读", "process_notes": "过程记录",
    "sponsored": "推广", "types": {"tutorial": "教程", "practice": "实践", "essay": "随笔"},
})
_COPY["en"].update({
    "all_products": "All tools & case studies", "live_products": "Online tools", "other_projects": "Case studies & open source",
    "products_lead": "Open a tool, or explore why it exists, how it works, and how it was checked.",
    "latest_writing": "Writing", "read_writing": "Read articles", "recent_article": "Latest article", "open_product": "Open", "toc": "On this page",
    "related_product": "Related tool", "continue_reading": "Continue reading", "process_notes": "Process notes",
    "sponsored": "Sponsored", "types": {"tutorial": "Tutorial", "practice": "Practice", "essay": "Essay"},
})


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
        (copy["nav_work"], ctx.page_href("/projects/"), "projects", False),
        (copy["nav_writing"], ctx.page_href("/writing/"), "writing", False),
        (copy["nav_about"], ctx.page_href("/about/"), "about", False),
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
    sponsored = "".join(
        f'<a href="{_e(link["href"])}" target="_blank" rel="sponsored noopener">{_e(link["label"])}</a>'
        for link in site["sponsored_links"]
    )
    sponsored = f'<p class="site-footer__sponsored"><span>{_e(copy["sponsored"])}</span>{sponsored}</p>' if sponsored else ""
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
<meta property="og:type" content="{'article' if active == 'writing' and path != '/writing/' else 'website'}">
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
<script src="{_e(ctx.boot_href)}"></script>
<link rel="stylesheet" href="{_e(ctx.css_href)}">
<script src="{_e(ctx.site_js_href)}" defer></script>{feed_link}
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
    {sponsored}
  </div>
</footer>
</body>
</html>
"""


def _project_row(index: int, p: Project, ctx: Context, *, compact: bool = False) -> str:
    copy = ctx.copy
    no = "" if compact else f'<span class="index__no">{index:02d}</span>'
    tags = f'<span class="index__tags">{_e(" · ".join(p.tags))}</span>' if p.tags and not compact else ""
    href = ctx.page_href(f"/projects/{p.slug}/") if p.link.type == "page" else p.link.href
    external = ' target="_blank" rel="noopener"' if p.link.type == "external" else ""
    notice = f'<span class="sr-only">{_e(copy["new_window"])}</span>' if external else ""
    title = f'<a class="index__name index__link" href="{_e(href)}"{external}>{_e(p.name)}{notice}</a>' if href else f'<span class="index__name">{_e(p.name)}</span>'
    summary = p.home_summary if compact and p.home_summary else p.summary
    main = f'<div class="index__main">{title}<span class="index__summary">{_e(summary)}</span>{tags}</div>'
    status = f'<span class="index__status">{moon(p.status)}<span>{copy["statuses"][p.status]}</span></span>'
    label = copy["project_page"] if p.link.type == "page" else p.link.label or copy["project_go"]
    go = f'<span class="index__go" aria-hidden="true">{_e(label)} →</span>' if href else f'<span class="index__go">{copy["not_open"]}</span>'
    if compact:
        status = "" if p.status == "live" else status
        go = ""
    app_label = (p.app.short_label or copy["open_product"]) if p.app and compact else p.app.label if p.app else ""
    app = (f'<a class="index__app" href="{_e(p.app.href)}" target="_blank" rel="noopener">'
           f'{_e(app_label)} ↗<span class="sr-only"> · {_e(p.name)}{_e(copy["new_window"])}</span></a>') if p.app else ""
    return f'<li class="index__item" data-reveal><div class="index__row{" index__row--compact" if compact else ""}{" is-static" if not href else ""}">{no}{main}<div class="index__aside">{status}{go}{app}</div></div></li>'


def _post_rows(posts: list[Doc], ctx: Context) -> str:
    rows = "".join(
        f'<li data-reveal><a class="post-row" href="{ctx.page_href(f"/writing/{d.slug}/")}">'
        f'<span class="post-row__meta"><time datetime="{d.date.isoformat() if d.date else ""}">{_fmt(d.date)}</time>'
        f'<span class="post-type">{_e(ctx.copy["types"][d.meta["type"]])}</span></span>'
        f'<span class="post-row__title">{_e(d.title)}</span>'
        f'<span class="post-row__summary">{_e(d.meta.get("summary", ""))}</span></a></li>'
        for d in posts
    )
    return f'<ul class="posts">{rows}</ul>'


def home(ctx: Context, projects: list[Project], posts: list[Doc]) -> str:
    site = ctx.site
    copy = ctx.copy
    intro = "<br>".join(_e(line) for line in site["intro"].splitlines())
    recent = (f'<p class="hero__recent"><span>{_e(copy["recent_article"])}</span>'
              f'<a href="{ctx.page_href(f"/writing/{posts[0].slug}/")}">{_e(posts[0].title)}</a></p>') if posts else ""
    rows = "".join(_project_row(i, p, ctx, compact=True) for i, p in enumerate((p for p in projects if p.featured), 1))
    writing = ""
    if posts:
        writing = f"""
<section class="section" id="writing" aria-labelledby="writing-title">
  <div class="wrap">
    <div class="section__head">
      <h2 class="section__title" id="writing-title">{_e(copy["latest_writing"])}</h2>
    </div>
    {_post_rows(posts[:5], ctx)}
    <p class="section__more"><a class="text-link" href="{ctx.page_href("/writing/")}">{_e(copy["all_writing"])}</a></p>
  </div>
</section>"""
    body = f"""<div class="home">
<section class="hero">
  <div class="wrap hero__grid">
    <div class="hero__text">
      <h1 class="hero__lead">{_e(site["headline"])}</h1>
      <p class="hero__intro">{intro}</p>
      {recent}
    </div>
  </div>
</section>

<section class="section" id="projects" aria-labelledby="projects-title">
  <div class="wrap">
    <div class="section__head">
      <h2 class="section__title" id="projects-title">{_e(copy["projects_heading"])}</h2>
    </div>
    <ol class="index">{rows}</ol>
    <p class="section__more"><a class="text-link" href="{ctx.page_href('/projects/')}">{_e(copy['all_products'])}</a></p>
  </div>
</section>
{writing}</div>"""
    return layout(ctx, title=site["name"], description=site["description"], path="/", body=body)


def projects_index(ctx: Context, projects: list[Project]) -> str:
    sections = []
    for key, group in (("live_products", [p for p in projects if p.status == "live"]),
                       ("other_projects", [p for p in projects if p.status != "live"])):
        if group:
            rows = "".join(_project_row(i, p, ctx) for i, p in enumerate(group, 1))
            sections.append(f'<section class="products-group"><h2 class="section__title">{_e(ctx.copy[key])}</h2><ol class="index">{rows}</ol></section>')
    body = f'<section class="wrap page"><header class="page-head"><h1 class="page-title">{_e(ctx.copy["projects"])}</h1><p class="page-lead">{_e(ctx.copy["products_lead"])}</p></header>{"".join(sections)}</section>'
    return layout(ctx, title=ctx.copy["projects"], description=ctx.copy["products_lead"], path="/projects/", body=body, active="projects")


def project_page(ctx: Context, p: Project, doc: Doc, posts: list[Doc] | None = None) -> str:
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
    home_projects = ctx.page_href("/projects/")
    app = f'<p class="project-actions"><a class="button" href="{_e(p.app.href)}" target="_blank" rel="noopener">{_e(p.app.label)} ↗<span class="sr-only">{_e(copy["new_window"])}</span></a></p>' if p.app else ""
    related = [d for d in (posts or []) if d.meta.get("project") == p.slug]
    process = f'<section class="reading-next"><h2>{_e(copy["process_notes"])}</h2>{_post_rows(related, ctx)}</section>' if related else ""
    body = f"""
<article class="wrap page project">
  <nav class="crumbs" aria-label="{_e(copy["crumb_label"])}"><a href="{home_projects}">{_e(copy["projects"])}</a><span aria-hidden="true">/</span><span>{_e(p.name)}</span></nav>
  <header class="page-head">
    <h1 class="page-title">{_e(p.name)}</h1>
    <p class="page-lead">{_e(p.summary)}</p>
    <dl class="meta">
      <div><dt>{_e(copy["status"])}</dt><dd>{moon(p.status)}<span>{copy["statuses"][p.status]}</span>{note}</dd></div>
      {updated}{tags}
    </dl>{app}
  </header>
  {flow}
  <div class="prose">{doc.html}</div>
  {process}
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
    body = f"""
<article class="wrap page about">
  <header class="page-head"><h1 class="page-title">{_e(doc.title)}</h1><p class="page-lead">{_e(site['identity'])}</p></header>
  <div class="prose">{doc.html}</div>
  <aside class="about__aside" aria-label="{_e(copy["about_aside"])}">
    <h2 class="about__heading" id="contact">{_e(copy["contact_heading"])}</h2>
    <dl class="contact">{contact_html}</dl>
  </aside>
</article>"""
    return layout(ctx, title=doc.title, description=doc.meta.get("summary", site["description"]), path="/about/", body=body, active="about")


def writing_index(ctx: Context, posts: list[Doc]) -> str:
    copy = ctx.copy
    body = f"""
<section class="wrap page">
  <header class="page-head"><h1 class="page-title">{_e(copy["writing_heading"])}</h1><p class="page-lead">{_e(copy["writing_desc"])}</p><p class="writing-subscribe"><a href="{ctx.page_href('/feed.xml')}">{_e(copy['footer_rss'])} ↗</a></p></header>
  {_post_rows(posts, ctx)}
</section>"""
    return layout(ctx, title=copy["writing_heading"], description=copy["writing_list_desc"], path="/writing/", body=body, active="writing")


def post_page(ctx: Context, doc: Doc, posts: list[Doc] | None = None, projects: list[Project] | None = None) -> str:
    copy = ctx.copy
    writing_href = ctx.page_href("/writing/")
    toc = ""
    if len(doc.headings) >= 3:
        items = "".join(f'<li><a href="#{_e(anchor)}">{_e(unescape(re.sub(r"<[^>]+>", "", title)))}</a></li>' for anchor, title in doc.headings)
        toc = f'<nav class="toc" aria-label="{_e(copy["toc"])}"><details open><summary>{_e(copy["toc"])}</summary><ol>{items}</ol></details></nav>'
    product = next((p for p in (projects or []) if p.slug == doc.meta.get("project")), None)
    related = f'<section class="reading-next"><h2>{_e(copy["related_product"])}</h2><ol class="index">{_project_row(1, product, ctx, compact=True)}</ol></section>' if product else ""
    next_posts = [p for p in (posts or []) if p.slug != doc.slug][:2]
    more = f'<section class="reading-next"><h2>{_e(copy["continue_reading"])}</h2>{_post_rows(next_posts, ctx)}</section>' if next_posts else ""
    updated = doc.meta.get("updated", "")
    update_note = f' · {_e(copy["updated"])} <time datetime="{_e(updated)}">{_fmt(date.fromisoformat(updated))}</time>' if updated and updated != doc.meta.get("date") else ""
    body = f"""
<article class="wrap page post">
  <nav class="crumbs" aria-label="{_e(copy["crumb_label"])}"><a href="{writing_href}">{_e(copy["writing_heading"])}</a></nav>
  <header class="page-head">
    <h1 class="page-title">{_e(doc.title)}</h1>
    <p class="post__date"><time datetime="{doc.date.isoformat() if doc.date else ""}">{_fmt(doc.date)}</time> · {_e(copy['types'][doc.meta['type']])}{update_note}</p>
    <p class="page-lead post__summary">{_e(doc.meta.get('summary', ''))}</p>
  </header>
  <div class="post__layout">{toc}<div class="prose">{doc.html}</div></div>
  {related}{more}
  <section class="author-note"><h2>{_e(ctx.site['name'])}</h2><p>{_e(ctx.site['identity'])}</p><p><a class="text-link" href="{ctx.page_href('/about/#contact')}">{_e(copy['cta_about'])}</a><a href="{ctx.page_href('/feed.xml')}">{_e(copy['footer_rss'])}</a></p></section>
  <p class="page-back"><a class="text-link" href="{writing_href}">{_e(copy["back_writing"])}</a></p>
</article>"""
    return layout(ctx, title=doc.title, description=doc.meta.get("summary", doc.title),
                  path=f"/writing/{doc.slug}/", body=body, active="writing")


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
        f"<id>{base}{writing_path}{d.slug}/</id><published>{stamp(d.date)}</published>"
        f"<updated>{stamp(date.fromisoformat(d.meta['updated']) if d.meta.get('updated') else d.date)}</updated>"
        f"<summary>{xml_escape(d.meta.get('summary', ''))}</summary></entry>"
        for d in posts
        if d.date
    )
    updated = stamp(max(date.fromisoformat(d.meta["updated"]) if d.meta.get("updated") else d.date for d in posts if d.date))
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        f'<feed xmlns="http://www.w3.org/2005/Atom"><title>{name}</title>'
        f"<subtitle>{xml_escape(ctx.site['tagline'])}</subtitle>"
        f'<link href="{base}{ctx.page_href("/")}"/><link rel="self" href="{base}{feed_path}"/>'
        f'<id>{base}{ctx.page_href("/")}</id>'
        f"<updated>{updated}</updated><author><name>{name}</name></author>{entries}</feed>\n"
    )

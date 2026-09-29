"""页面模板。来自 JSON 的文字全部转义；Markdown 由 mistune 渲染，其中的原始 HTML 也会被转义。"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date
from html import escape
from typing import Any
from xml.sax.saxutils import escape as xml_escape

from .content import STATUS_LABELS, Doc, Project
from .icons import SVG_DEFS, moon, seal

@dataclass(frozen=True)
class Context:
    site: dict[str, Any]
    show_writing: bool
    css_href: str
    year: int

    @property
    def base(self) -> str:
        return self.site["base_url"].rstrip("/")


def _e(text: str) -> str:
    return escape(text, quote=True)


def _phrases(text: str) -> str:
    """按逗号、冒号、分号切成短语，短语之间才换行，避免“正在转 / AI”这种断法。"""
    parts = re.split(r"(?<=[，：；])", text)
    return "".join(f'<span class="phrase">{_e(p)}</span>' for p in parts if p)


def _fmt(d: date | None) -> str:
    return d.strftime("%Y.%m.%d") if d else ""


def _person_json_ld(ctx: Context) -> str:
    """复用公开信息；转义 HTML 特殊字符，防止数据提前关闭 script 标签。"""
    site = ctx.site
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
    name = site["name"]
    full_title = (
        site.get("home_title", f"{name} · {site['tagline'].rstrip('。')}")
        if path == "/" else f"{title} · {name}"
    )
    url, og_image = ctx.base + path, ctx.base + "/og-image.png"
    nav_items = [
        ("作品", "/#projects", "projects", False),
        ("文章", "/writing/", "writing", False),
        ("经历", "/about/", "about", False),
        ("特价AI会员", "https://prodclub.xyz/r/2QFJWC", "", True),
    ]
    nav = "".join(
        f'<a href="{_e(href)}"{" aria-current=\"page\"" if key == active else ""}'
        f'{" target=\"_blank\" rel=\"noopener\"" if external else ""}>{_e(label)}'
        f'{"<span class=\"sr-only\">（在新窗口打开）</span>" if external else ""}</a>'
        for label, href, key, external in nav_items
        if key != "writing" or ctx.show_writing
    )
    feed_link = (
        f'\n<link rel="alternate" type="application/atom+xml" title="{_e(name)}" href="/feed.xml">'
        if ctx.show_writing else ""
    )
    accounts = "".join(
        f'<a href="{_e(a["href"])}" rel="me">{_e(a["label"])}</a>' for a in site["accounts"] if a.get("href")
    )
    rss = '<a href="/feed.xml">RSS</a>' if ctx.show_writing else ""
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_e(full_title)}</title>
<meta name="description" content="{_e(description)}">
<link rel="canonical" href="{_e(url)}">
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
<a class="skip" href="#main">跳到正文</a>
<header class="site-header">
  <div class="wrap site-header__inner">
    <a class="brand" href="/" aria-label="{_e(name)}，回到首页">{seal("seal--sm")}<span>{_e(name)}</span></a>
    <nav class="nav" aria-label="主导航">{nav}</nav>
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


def _project_row(index: int, p: Project) -> str:
    no = f'<span class="index__no">{index:02d}</span>'
    tags = f'<span class="index__tags">{_e(" · ".join(p.tags))}</span>' if p.tags else ""
    main = (
        f'<span class="index__main"><span class="index__name">{_e(p.name)}</span>'
        f'<span class="index__summary">{_e(p.summary)}</span>{tags}</span>'
    )
    status = f'<span class="index__status">{moon(p.status)}<span>{STATUS_LABELS[p.status]}</span></span>'
    if p.link.type == "page":
        go = '<span class="index__go">介绍<span class="index__arrow" aria-hidden="true">→</span></span>'
        inner = f'{no}{main}<span class="index__aside">{status}{go}</span>'
        return f'<li class="index__item" data-reveal><a class="index__row" href="/projects/{p.slug}/">{inner}</a></li>'
    if p.link.type == "external":
        label = _e(p.link.label or "前往")
        go = (
            f'<span class="index__go">{label}<span class="index__arrow" aria-hidden="true">↗</span>'
            '<span class="sr-only">（在新窗口打开）</span></span>'
        )
        inner = f'{no}{main}<span class="index__aside">{status}{go}</span>'
        return (
            f'<li class="index__item" data-reveal><a class="index__row" href="{_e(p.link.href)}" '
            f'target="_blank" rel="noopener">{inner}</a></li>'
        )
    go = '<span class="index__go">尚未开放</span>'
    inner = f'{no}{main}<span class="index__aside">{status}{go}</span>'
    return f'<li class="index__item" data-reveal><div class="index__row is-static">{inner}</div></li>'


def _post_rows(posts: list[Doc]) -> str:
    rows = "".join(
        f'<li data-reveal><a class="post-row" href="/writing/{d.slug}/">'
        f'<time datetime="{d.date.isoformat() if d.date else ""}">{_fmt(d.date)}</time>'
        f'<span class="post-row__title">{_e(d.title)}</span>'
        f'<span class="post-row__summary">{_e(d.meta.get("summary", ""))}</span></a></li>'
        for d in posts
    )
    return f'<ul class="posts">{rows}</ul>'


def home(ctx: Context, projects: list[Project], posts: list[Doc]) -> str:
    site = ctx.site
    name = _e(site["name"])
    intro = "<br>".join(_phrases(line) for line in site["intro"].splitlines())
    couplet = "".join(
        f'<p class="scroll__line">{_e(part)}</p>'
        for part in (s.strip("，。 ") for s in site["tagline"].split("，"))
        if part
    )
    rows = "".join(_project_row(i, p) for i, p in enumerate(projects, 1))
    writing = ""
    if posts:
        writing = f"""
<section class="section" id="writing" aria-labelledby="writing-title">
  <div class="wrap">
    <div class="section__head">
      <h2 class="section__title" id="writing-title">文章</h2>
      <p class="section__desc">做的过程和想明白的事。</p>
    </div>
    {_post_rows(posts[:5])}
    <p class="section__more"><a class="text-link" href="/writing/">全部文章</a></p>
  </div>
</section>"""
    body = f"""
<section class="hero">
  <div class="wrap hero__grid">
    <div class="hero__text">
      <p class="hero__eyebrow">{name} · 个人作品集</p>
      <h1 class="hero__lead">{_phrases(site["identity"])}</h1>
      <p class="hero__intro">{intro}</p>
      <p class="hero__job">{_e(site["job"])}</p>
      <p class="hero__actions"><a class="button" href="#projects">看代表作品</a><a class="text-link" href="/about/">经历与联系</a></p>
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
      <h2 class="section__title" id="projects-title">个人项目</h2>
      <p class="section__desc">从问题、实现到验证，查看我实际做过的事。</p>
    </div>
    <ol class="index">{rows}</ol>
  </div>
</section>
{writing}
<section class="section section--about" aria-labelledby="about-title">
  <div class="wrap about-brief">
    <h2 class="section__title" id="about-title">经历与联系</h2>
    <div class="about-brief__body">
      <p>{_e(site["about_brief"])}</p>
      <p class="job"><span class="job__dot" aria-hidden="true"></span>{_e(site["job"])}</p>
      <p><a class="text-link" href="/about/">查看经历与联系方式</a></p>
    </div>
  </div>
</section>"""
    return layout(ctx, title=site["name"], description=site["description"], path="/", body=body, active="projects")


def project_page(ctx: Context, p: Project, doc: Doc) -> str:
    steps = [s.strip() for s in doc.meta.get("flow", "").split("|") if s.strip()]
    flow = (
        '<ol class="flow" aria-label="方案流程">'
        + "".join(f"<li><span>{_e(s)}</span></li>" for s in steps)
        + "</ol>"
        if steps else ""
    )
    note = f"<span>· {_e(doc.meta['status_note'])}</span>" if doc.meta.get("status_note") else ""
    tags = f'<div><dt>技术</dt><dd>{_e(" · ".join(p.tags))}</dd></div>' if p.tags else ""
    updated = f"<div><dt>更新</dt><dd>{_fmt(doc.date)}</dd></div>" if doc.date else ""
    body = f"""
<article class="wrap page">
  <nav class="crumbs" aria-label="位置"><a href="/#projects">项目</a><span aria-hidden="true">／</span><span>{_e(p.name)}</span></nav>
  <header class="page-head">
    <h1 class="page-title">{_e(p.name)}</h1>
    <p class="page-lead">{_e(p.summary)}</p>
    <dl class="meta">
      <div><dt>状态</dt><dd>{moon(p.status)}<span>{STATUS_LABELS[p.status]}</span>{note}</dd></div>
      {updated}{tags}
    </dl>
  </header>
  {flow}
  <div class="prose">{doc.html}</div>
  <p class="page-back"><a class="text-link" href="/#projects">回到项目目录</a></p>
</article>"""
    return layout(ctx, title=p.name, description=p.summary, path=f"/projects/{p.slug}/", body=body, active="projects")


def about_page(ctx: Context, doc: Doc) -> str:
    site = ctx.site
    email = site.get("email", "")
    contacts = [("邮箱", f'<a href="mailto:{_e(email)}">{_e(email)}</a>' if email else '<span class="muted">待补</span>')]
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
  <aside class="about__aside" aria-label="求职与联系">
    <h2 class="about__heading">正在找工作</h2>
    <p class="job"><span class="job__dot" aria-hidden="true"></span>{_e(site["job"])}</p>
    <h2 class="about__heading" id="contact">联系与账号</h2>
    <dl class="contact">{contact_html}</dl>
  </aside>
</article>"""
    return layout(ctx, title=doc.title, description=doc.meta.get("summary", site["description"]), path="/about/", body=body, active="about")


def writing_index(ctx: Context, posts: list[Doc]) -> str:
    body = f"""
<section class="wrap page">
  <header class="page-head"><h1 class="page-title">文章</h1><p class="page-lead">做的过程和想明白的事。</p></header>
  {_post_rows(posts)}
</section>"""
    return layout(ctx, title="文章", description="半開的文章列表。", path="/writing/", body=body, active="writing")


def post_page(ctx: Context, doc: Doc) -> str:
    body = f"""
<article class="wrap page post">
  <nav class="crumbs" aria-label="位置"><a href="/writing/">文章</a></nav>
  <header class="page-head">
    <h1 class="page-title">{_e(doc.title)}</h1>
    <p class="post__date"><time datetime="{doc.date.isoformat() if doc.date else ""}">{_fmt(doc.date)}</time></p>
  </header>
  <div class="prose">{doc.html}</div>
  <p class="page-back"><a class="text-link" href="/writing/">回到文章列表</a></p>
</article>"""
    return layout(
        ctx, title=doc.title, description=doc.meta.get("summary", doc.title),
        path=f"/writing/{doc.slug}/", body=body, active="writing",
    )


def not_found(ctx: Context) -> str:
    body = f"""
<section class="wrap notfound">
  {moon("building", "notfound__moon")}
  <h1 class="page-title">这朵花还没开。</h1>
  <p class="page-lead">你要找的页面不存在，或者还在路上。</p>
  <p><a class="button" href="/">回到首页</a></p>
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
    stamp = lambda d: f"{d.isoformat()}T00:00:00+08:00"  # noqa: E731
    entries = "".join(
        f"<entry><title>{xml_escape(d.title)}</title><link href=\"{base}/writing/{d.slug}/\"/>"
        f"<id>{base}/writing/{d.slug}/</id><updated>{stamp(d.date)}</updated>"
        f"<summary>{xml_escape(d.meta.get('summary', ''))}</summary></entry>"
        for d in posts
        if d.date
    )
    updated = stamp(max(d.date for d in posts if d.date))
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        f'<feed xmlns="http://www.w3.org/2005/Atom"><title>{name}</title>'
        f"<subtitle>{xml_escape(ctx.site['tagline'])}</subtitle>"
        f'<link href="{base}/"/><link rel="self" href="{base}/feed.xml"/><id>{base}/</id>'
        f"<updated>{updated}</updated><author><name>{name}</name></author>{entries}</feed>\n"
    )

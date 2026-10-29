from __future__ import annotations

import json
import re
import shutil
from html.parser import HTMLParser
from pathlib import Path

import pytest

import build
from sitegen import checks, content, render

ROOT = Path(__file__).resolve().parents[1]


def test_home_shows_real_previews_separate_notes_and_bilingual_new_posts(tmp_path):
    out = build.build(ROOT, tmp_path / "dist")
    for prefix, locale in (("", "zh"), ("en/", "en")):
        home = (out / prefix / "index.html").read_text(encoding="utf-8")
        assert home.count('class="index__item product-card"') == 3
        for shot in ("finunity-overview", "character-guide"):
            assert f'/shots/{shot}.{locale}.png' in home
        assert 'class="product-map"' in home
        assert 'href="mailto:' in home
        assert 'id="notes-title"' in home
        for slug in ("finunity-one-ledger", "demo-before-signup", "character-guide-before-chat", "snapshot-needs-a-date"):
            page = out / prefix / "writing" / slug / "index.html"
            assert page.is_file()
            assert f'/{prefix}writing/{slug}/' in home
    assert checks.check_internal(out, checks.scan_pages(out)) == []


class LinkNestingParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_link = False
        self.nested = False

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.nested |= self.in_link
            self.in_link = True

    def handle_endtag(self, tag):
        if tag == "a":
            self.in_link = False


def copy_content(tmp_path: Path) -> Path:
    root = tmp_path / "site"
    shutil.copytree(ROOT / "content", root / "content")
    shutil.copytree(ROOT / "static", root / "static")
    return root


def test_long_article_has_real_toc_targets_and_no_draft_recommendations(tmp_path):
    out = build.build(ROOT, tmp_path / "dist")
    page = (out / "writing/rag-hybrid-search/index.html").read_text(encoding="utf-8")
    toc = page.split('<nav class="toc"')[1].split('</nav>')[0]
    anchors = re.findall(r'href="#([^"]+)"', toc)
    assert len(anchors) == 6
    assert len(set(anchors)) == 6
    assert all(f'id="{anchor}"' in page for anchor in anchors)
    assert "相关产品" in page and 'href="/projects/knowledge/"' in page
    assert "继续阅读" in page and 'href="/writing/testing-to-ai-development/"' in page
    assert "ui-testing-ten-years" not in page
    assert '<meta property="og:type" content="article">' in page
    feed = (out / 'feed.xml').read_text(encoding='utf-8')
    assert '<published>2026-10-03T00:00:00+08:00</published>' in feed
    assert '<updated>2026-10-11T00:00:00+08:00</updated>' in feed
    assert checks.check_internal(out, checks.scan_pages(out)) == []
    for html in out.rglob('*.html'):
        parser = LinkNestingParser()
        parser.feed(html.read_text(encoding='utf-8'))
        assert not parser.nested, html


def test_toc_preserves_duplicate_and_formatted_heading_links(tmp_path):
    path = tmp_path / "post.md"
    path.write_text('## A & B\n\n## A & B\n\n## `code` <script>\n', encoding='utf-8')
    doc = content.load_doc(path)
    assert len({anchor for anchor, _ in doc.headings}) == 3
    site = content.load_site(ROOT / 'content/site.json')
    doc = content.Doc(doc.slug, {"date": "2026-10-11", "type": "essay", "summary": "Example"}, doc.html, doc.headings)
    page = render.post_page(render.Context(site, True, '/styles.css', 2026), doc)
    assert '<script>' not in page
    assert '&lt;script&gt;' in page
    short = content.Doc('short', doc.meta, '<p>Short</p>')
    assert '<nav class="toc"' not in render.post_page(render.Context(site, True, '/styles.css', 2026), short)


def test_untranslated_articles_build_and_language_switch_falls_back(tmp_path):
    root = copy_content(tmp_path)
    # A new standalone post need not have a translation.
    (root / 'content/writing/chinese-only.md').write_text(
        '---\ntitle: Only Chinese\ndate: 2026-10-11\ntype: essay\nsummary: Example\n---\nHello\n', encoding='utf-8')
    out = build.build(root, tmp_path / 'dist')
    page = (out / 'writing/chinese-only/index.html').read_text(encoding='utf-8')
    assert 'hreflang="en"' not in page.split('</head>')[0]
    assert 'class="language-switch" href="/en/writing/"' in page
    assert not (out / 'en/writing/chinese-only/index.html').exists()
    assert checks.check_internal(out, checks.scan_pages(out)) == []
    site = content.load_site(ROOT / 'content/site.json')
    no_en_posts = render.Context(site, True, '/styles.css', 2026, other_paths=frozenset({'/', '/projects/'}))
    assert no_en_posts.language_href('/writing/chinese-only/') == '/en/'
    assert no_en_posts.language_href('/projects/untranslated/') == '/en/projects/'


@pytest.mark.parametrize('field,value', [('type', 'unknown'), ('updated', '2026-01-01'), ('project', 'missing')])
def test_invalid_article_metadata_is_rejected(tmp_path, field, value):
    root = copy_content(tmp_path)
    path = root / 'content/writing/rag-hybrid-search.md'
    text = path.read_text(encoding='utf-8')
    if re.search(rf'^{field}:', text, re.M):
        text = re.sub(rf'^{field}:.*$', f'{field}: {value}', text, flags=re.M)
    else:
        text = text.replace('---\n', f'---\n{field}: {value}\n', 1)
    path.write_text(text, encoding='utf-8')
    with pytest.raises((build.BuildError, content.ContentError), match=field):
        build.build(root, tmp_path / 'dist')


def test_app_links_reject_unsafe_targets(tmp_path):
    path = tmp_path / 'projects.json'
    path.write_text(json.dumps([{'slug': 'test', 'name': 'Test', 'summary': 'Example',
        'status': 'building', 'link': {'type': 'none'},
        'app': {'label': 'Open', 'href': 'javascript:alert(1)'}}]), encoding='utf-8')
    with pytest.raises(content.ContentError, match='app.*HTTPS'):
        content.load_projects(path, tmp_path)


def test_root_404_and_product_routes_keep_language_and_indexing_boundaries(tmp_path):
    out = build.build(ROOT, tmp_path / 'dist')
    page = (out / '404.html').read_text(encoding='utf-8')
    assert '<html lang="zh-CN">' in page
    assert 'content="noindex"' in page
    assert '<link rel="canonical"' not in page
    for locale in ('', 'en/'):
        for suffix in ('projects/index.html', 'projects/dashboards/index.html', 'projects/character/index.html'):
            assert (out / (locale + suffix)).is_file()
    assert (out / 'index.html').stat().st_size < 16 * 1024
    assert (out / 'styles.css').stat().st_size < 30 * 1024

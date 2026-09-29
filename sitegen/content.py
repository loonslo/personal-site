"""读取并校验站点内容：site.json、projects.json 和带 frontmatter 的 Markdown。"""

from __future__ import annotations

import json
import ipaddress
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import mistune

STATUSES = ("building", "intro", "open", "live")
STATUS_LABELS = {"building": "建设中", "intro": "仅介绍", "open": "开源", "live": "在线"}
LINK_TYPES = ("page", "external", "none")
_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_SITE_KEYS = (
    "name", "tagline", "poem", "identity", "intro", "job",
    "description", "base_url", "email", "accounts",
)
_URL_CONTROL_OR_SPACE = re.compile(r"[\x00-\x20\x7f\\]")
_DNS_LABEL = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$", re.IGNORECASE)

_markdown = mistune.create_markdown(escape=True, plugins=["table", "strikethrough", "url"])


def _valid_https_url(value: object, *, origin_only: bool = False) -> bool:
    """Reject unsafe or malformed HTTPS targets before placing them in HTML/XML."""
    if not isinstance(value, str) or not value or _URL_CONTROL_OR_SPACE.search(value):
        return False
    try:
        parts = urlsplit(value)
        hostname = parts.hostname
        port = parts.port
    except ValueError:
        return False
    if not hostname or not _valid_public_host(hostname):
        return False
    if (
        parts.scheme.lower() != "https"
        or parts.username is not None
        or parts.password is not None
        or (port is not None and not 1 <= port <= 65535)
    ):
        return False
    if origin_only and (parts.path not in ("", "/") or parts.query or parts.fragment):
        return False
    return True


def _valid_public_host(hostname: str) -> bool:
    if "%" in hostname:
        return False
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        try:
            ascii_host = hostname.encode("idna").decode("ascii").rstrip(".")
        except UnicodeError:
            return False
        labels = ascii_host.split(".")
        return (
            len(ascii_host) <= 253
            and len(labels) >= 2
            and any(char.isalpha() for char in ascii_host)
            and all(_DNS_LABEL.fullmatch(label) for label in labels)
            and not ascii_host.lower().endswith((".localhost", ".local", ".internal"))
        )
    if isinstance(address, ipaddress.IPv6Address) and address.ipv4_mapped:
        address = address.ipv4_mapped
    return address.is_global


class ContentError(ValueError):
    """内容数据不符合约定时抛出，信息里带文件和位置。"""


@dataclass(frozen=True)
class Link:
    type: str
    href: str = ""
    label: str = ""


@dataclass(frozen=True)
class Project:
    slug: str
    name: str
    summary: str
    status: str
    link: Link
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class Doc:
    slug: str
    meta: dict[str, str] = field(default_factory=dict)
    html: str = ""

    @property
    def title(self) -> str:
        return self.meta.get("title", self.slug)

    @property
    def draft(self) -> bool:
        return self.meta.get("draft", "").lower() == "true"

    @property
    def date(self) -> date | None:
        raw = self.meta.get("date") or self.meta.get("updated")
        return date.fromisoformat(raw) if raw else None


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """解析 `---` 包围的扁平 key: value 头部；没有头部时返回空字典。"""
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ContentError("frontmatter 缺少结束标记 ---")
    meta: dict[str, str] = {}
    for n, line in enumerate(text[4:end].splitlines(), start=2):
        if not line.strip():
            continue
        key, sep, value = line.partition(":")
        if not sep or not key.strip():
            raise ContentError(f"frontmatter 第 {n} 行不是 key: value 格式：{line!r}")
        meta[key.strip()] = value.strip()
    return meta, text[end + 5 :]


def render_markdown(text: str) -> str:
    html = _markdown(text)
    return html.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")


def load_doc(path: Path) -> Doc:
    meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
    return Doc(slug=path.stem, meta=meta, html=render_markdown(body))


def load_docs(folder: Path) -> list[Doc]:
    if not folder.exists():
        return []
    docs = [load_doc(p) for p in sorted(folder.glob("*.md"))]
    for doc in docs:
        if doc.date is None:
            raise ContentError(f"{folder / (doc.slug + '.md')}: 文章缺少 date")
    return sorted(docs, key=lambda d: d.date or date.min, reverse=True)


def load_site(path: Path) -> dict[str, Any]:
    site = json.loads(path.read_text(encoding="utf-8"))
    missing = [k for k in _SITE_KEYS if k not in site]
    if missing:
        raise ContentError(f"{path}: 缺少字段 {', '.join(missing)}")
    if not isinstance(site["poem"], list) or not site["poem"]:
        raise ContentError(f"{path}: poem 必须是非空列表")
    if not _valid_https_url(site["base_url"], origin_only=True):
        raise ContentError(f"{path}: base_url 必须是有效的 HTTPS 站点源地址")
    skills = site.get("skills", [])
    if not isinstance(skills, list) or any(not isinstance(skill, str) or not skill.strip() for skill in skills):
        raise ContentError(f"{path}: skills 必须是非空字符串组成的列表")
    if not isinstance(site["accounts"], list):
        raise ContentError(f"{path}: accounts 必须是列表")
    for i, account in enumerate(site["accounts"], start=1):
        if not isinstance(account, dict):
            raise ContentError(f"{path}: accounts 第 {i} 项必须是对象")
        href = account.get("href", "")
        if not isinstance(href, str):
            raise ContentError(f"{path}: accounts 第 {i} 项的 href 必须是字符串")
        if href and not _valid_https_url(href):
            raise ContentError(f"{path}: accounts 第 {i} 项的 href 必须是有效的 HTTPS 链接")
    return site


def load_projects(path: Path, pages_dir: Path) -> list[Project]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list) or not raw:
        raise ContentError(f"{path}: 顶层必须是非空数组")
    projects: list[Project] = []
    seen: set[str] = set()
    for i, item in enumerate(raw):
        where = f"{path} 第 {i + 1} 项"
        if not isinstance(item, dict):
            raise ContentError(f"{where}: 必须是对象")
        for key in ("slug", "name", "summary", "status", "link"):
            if not item.get(key):
                raise ContentError(f"{where}: 缺少 {key}")
        slug, status, link = item["slug"], item["status"], item["link"]
        if not isinstance(link, dict):
            raise ContentError(f"{where}: link 必须是对象")
        if not _SLUG.match(slug):
            raise ContentError(f"{where}: slug 只能用小写字母、数字和连字符：{slug!r}")
        if slug in seen:
            raise ContentError(f"{where}: slug 重复：{slug}")
        seen.add(slug)
        if status not in STATUSES:
            raise ContentError(f"{where}: status 必须是 {'/'.join(STATUSES)}，实际为 {status!r}")
        kind = link.get("type")
        if kind not in LINK_TYPES:
            raise ContentError(f"{where}: link.type 必须是 {'/'.join(LINK_TYPES)}")
        if kind == "external" and not _valid_https_url(link.get("href")):
            raise ContentError(f"{where}: 外部链接必须是指向有效主机的 https:// URL")
        if kind == "page" and not (pages_dir / f"{slug}.md").exists():
            raise ContentError(f"{where}: 缺少介绍页 {pages_dir / (slug + '.md')}")
        if kind == "none" and status != "building":
            raise ContentError(f"{where}: 只有“建设中”的项目可以没有链接")
        projects.append(
            Project(
                slug=slug,
                name=item["name"],
                summary=item["summary"],
                status=status,
                link=Link(type=kind, href=link.get("href", ""), label=link.get("label", "")),
                tags=tuple(item.get("tags", [])),
            )
        )
    return projects

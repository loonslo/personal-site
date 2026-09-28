"""发布前检查：站内链接与锚点、外部链接、禁用词、待补占位。"""

from __future__ import annotations

import http.client
import ipaddress
import socket
import ssl
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import quote, urljoin, urldefrag, urlparse, urlsplit

TEXT_SUFFIXES = {".html", ".xml", ".txt", ".css", ".svg", ".json"}
_NAT64_WELL_KNOWN = ipaddress.ip_network("64:ff9b::/96")


@dataclass
class PageLinks:
    refs: list[str] = field(default_factory=list)
    ids: set[str] = field(default_factory=set)


class _Collector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.page = PageLinks()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for key, value in attrs:
            if value is None:
                continue
            if key == "id":
                self.page.ids.add(value)
            elif key in ("href", "src") and not (tag == "link" and ("rel", "canonical") in attrs):
                self.page.refs.append(value)


def scan_pages(dist: Path) -> dict[Path, PageLinks]:
    pages: dict[Path, PageLinks] = {}
    for path in sorted(dist.rglob("*.html")):
        collector = _Collector()
        collector.feed(path.read_text(encoding="utf-8"))
        pages[path] = collector.page
    return pages


def _target_file(dist: Path, page: Path, ref: str) -> Path:
    path = urlparse(ref).path
    target = dist / path.lstrip("/") if path.startswith("/") else page.parent / path
    return target / "index.html" if path.endswith("/") or target.is_dir() else target


def check_internal(dist: Path, pages: dict[Path, PageLinks]) -> list[str]:
    """站内链接必须指向存在的文件；带 #锚点 的链接，目标页面必须有对应 id。"""
    errors: list[str] = []
    for page, links in pages.items():
        for ref in links.refs:
            where = page.relative_to(dist).as_posix()
            try:
                parsed = urlparse(ref)
            except ValueError:
                errors.append(f"{where}: 无效链接 {ref}")
                continue
            if parsed.scheme.lower() in ("http", "https", "mailto", "data") or ref.startswith("//"):
                continue
            url, fragment = urldefrag(ref)
            target = page if not url else _target_file(dist, page, url)
            if not target.exists():
                errors.append(f"{where}: 链接指向不存在的文件 {ref}")
            elif fragment and target.suffix == ".html":
                target_ids = pages[target].ids if target in pages else set()
                if fragment not in target_ids:
                    errors.append(f"{where}: 锚点 #{fragment} 在 {target.relative_to(dist).as_posix()} 中不存在")
    return errors


def external_links(pages: dict[Path, PageLinks]) -> set[str]:
    urls: set[str] = set()
    for links in pages.values():
        for ref in links.refs:
            try:
                if urlsplit(ref).scheme.lower() in ("http", "https"):
                    urls.add(ref)
            except ValueError:
                continue
    return urls


class _PinnedHTTPConnection(http.client.HTTPConnection):
    """Connect to the exact public address checked during DNS resolution."""

    def __init__(self, host: str, port: int, timeout: float, address: tuple[Any, ...]) -> None:
        super().__init__(host, port, timeout=timeout)
        self._address = address

    def connect(self) -> None:
        family, socktype, proto, _, sockaddr = self._address
        sock = socket.socket(family, socktype, proto)
        try:
            sock.settimeout(self.timeout)
            sock.connect(sockaddr)
        except OSError:
            sock.close()
            raise
        self.sock = sock


class _PinnedHTTPSConnection(http.client.HTTPSConnection):
    """Use a pinned socket while retaining TLS hostname and certificate checks."""

    def __init__(
        self, host: str, tls_name: str, port: int, timeout: float, address: tuple[Any, ...]
    ) -> None:
        super().__init__(host, port, timeout=timeout, context=ssl.create_default_context())
        self._tls_name = tls_name
        self._address = address

    def connect(self) -> None:
        family, socktype, proto, _, sockaddr = self._address
        sock = socket.socket(family, socktype, proto)
        try:
            sock.settimeout(self.timeout)
            sock.connect(sockaddr)
            self.sock = self._context.wrap_socket(sock, server_hostname=self._tls_name)
        except (OSError, ssl.SSLError):
            sock.close()
            raise


def _public_target(url: str) -> tuple[Any, str, int, tuple[Any, ...]]:
    if any(ord(char) <= 32 or ord(char) == 127 or char == "\\" for char in url):
        raise ValueError("URL 包含空白、控制字符或反斜杠")
    try:
        parts = urlsplit(url)
        raw_host = parts.hostname
        port = parts.port
    except ValueError as exc:
        raise ValueError("URL 格式无效") from exc
    scheme = parts.scheme.lower()
    if (
        scheme not in ("http", "https")
        or not raw_host
        or parts.username is not None
        or parts.password is not None
    ):
        raise ValueError("仅允许带有效主机名的 HTTP(S) 公网链接")
    default_port = 443 if scheme == "https" else 80
    if port is not None and port != default_port:
        raise ValueError("外链检查仅允许 HTTP 80 和 HTTPS 443 端口")
    try:
        host = raw_host.encode("idna").decode("ascii").lower()
        port = default_port
        addresses = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except (UnicodeError, OSError, ValueError) as exc:
        raise ValueError("主机名无法解析") from exc
    if not addresses:
        raise ValueError("主机名没有可用地址")
    for family, _, _, _, sockaddr in addresses:
        try:
            ip = ipaddress.ip_address(sockaddr[0].split("%", 1)[0])
        except ValueError as exc:
            raise ValueError("主机名解析结果无效") from exc
        if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
            ip = ip.ipv4_mapped
        elif isinstance(ip, ipaddress.IPv6Address) and (
            ip.sixtofour is not None or ip.teredo is not None or ip in _NAT64_WELL_KNOWN
        ):
            raise ValueError("不允许使用 IPv6 地址转换机制访问目标")
        if not ip.is_global:
            raise ValueError("主机名解析到非公网地址，已拒绝请求")
    return parts, host, port, addresses[0]


def _request_public_url(url: str, timeout: float, max_redirects: int = 5) -> int:
    current = url
    for redirect_count in range(max_redirects + 1):
        parts, host, port, address = _public_target(current)
        scheme = parts.scheme.lower()
        host_header = f"[{host}]" if ":" in host else host
        path = quote(parts.path or "/", safe="/%:@!$&'()*+,;=-._~")
        query = quote(parts.query, safe="/?%:@!$&'()*+,;=-._~")
        if query:
            path += f"?{query}"
        if scheme == "https":
            connection: http.client.HTTPConnection = _PinnedHTTPSConnection(
                host_header, host, port, timeout, address
            )
        else:
            connection = _PinnedHTTPConnection(host_header, port, timeout, address)
        try:
            connection.request(
                "GET", path,
                headers={"User-Agent": "Mozilla/5.0 (site-link-check)", "Range": "bytes=0-0"},
            )
            response = connection.getresponse()
            status = response.status
            location = response.getheader("Location")
        finally:
            connection.close()
        if 300 <= status < 400 and location:
            if redirect_count == max_redirects:
                raise ValueError("重定向次数过多")
            current = urljoin(current, location)
            continue
        if 300 <= status < 400:
            raise ValueError(f"HTTP {status} 响应没有有效重定向地址")
        return status
    raise ValueError("重定向次数过多")


def check_external(urls: set[str], timeout: float = 10.0) -> list[str]:
    errors: list[str] = []
    for url in sorted(urls):
        try:
            status = _request_public_url(url, timeout)
            if status >= 400:
                errors.append(f"{url}: HTTP {status}")
        except (http.client.HTTPException, OSError, ssl.SSLError, TimeoutError, ValueError) as exc:
            errors.append(f"{url}: 无法访问（{exc}）")
    return errors


def load_blocklist(path: Path) -> list[str]:
    words = []
    for line in path.read_text(encoding="utf-8").splitlines():
        word = line.strip()
        if word and not word.startswith("#"):
            words.append(word)
    return words


def scan_blocklist(dist: Path, words: list[str]) -> list[str]:
    hits: list[str] = []
    lowered = [(w, w.lower()) for w in words]
    for path in sorted(dist.rglob("*")):
        if path.suffix not in TEXT_SUFFIXES or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        for word, low in lowered:
            if low in text:
                hits.append(f"{path.relative_to(dist).as_posix()}: 出现禁用词「{word}」")
    return hits


def placeholders(site: dict[str, Any]) -> list[str]:
    notes = []
    if not site.get("email"):
        notes.append("site.json: email 未填写，关于页显示“待补”")
    if "example" in site.get("base_url", ""):
        notes.append("site.json: base_url 仍是示例地址，canonical、分享图和 sitemap 会指向它")
    for account in site.get("accounts", []):
        if not account.get("href"):
            notes.append(f"site.json: {account.get('label')} 链接未填写，目前只显示账号名")
    return notes

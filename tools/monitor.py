"""Uptime, health and certificate check for the five halfopen.dev sites (standard library only).

    python tools/monitor.py          # exit 0 when every check passes, 1 otherwise
    python tools/monitor.py --list   # print what is checked

A scheduled GitHub Actions run executes it every 15 minutes (.github/workflows/monitor.yml). A failed
run emails the repository owner and can push to GitHub Mobile; if ALERT_WEBHOOK_URL is set the
failures are also POSTed there as JSON. Every check is retried so one dropped packet pages nobody.

What it proves and what it does not: it checks reachability, a content marker, the health JSON and
certificate expiry from GitHub's US runners. It does not measure latency for visitors in mainland
China, and it never logs in, registers or uploads anything.
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import ssl
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Callable, Sequence
from dataclasses import dataclass

MIN_CERT_DAYS = 21
ATTEMPTS = 3
RETRY_DELAY_SECONDS = 2.0
USER_AGENT = "halfopen-monitor/1 (+https://github.com/loonslo/personal-site)"


@dataclass(frozen=True)
class Check:
    name: str
    url: str
    status: int = 200
    contains: str | None = None  # a substring the body must contain
    json_status: tuple[str, ...] | None = None  # accepted values of the JSON "status" field
    redirect_to: str | None = None  # required Location prefix (for 301/308 checks)


@dataclass(frozen=True)
class Response:
    status: int
    headers: dict[str, str]
    body: bytes


CANONICAL = 'rel="canonical"'
SITES: tuple[Check, ...] = (
    Check("主站", "https://halfopen.dev/", contains=CANONICAL),
    Check("角色站", "https://character.halfopen.dev/", contains=CANONICAL),
    Check("知识站", "https://knowledge.halfopen.dev/", contains=CANONICAL),
    Check("衡仓", "https://finunity.halfopen.dev/", contains=CANONICAL),
    Check("看板", "https://dashboards.halfopen.dev/", contains=CANONICAL),
    # The next three go through the Vercel proxy to the Ubuntu server, so they exercise the whole chain.
    Check("衡仓 Web→API ready", "https://finunity.halfopen.dev/health/ready", json_status=("ready", "degraded")),
    # Switch to /health/ready once the build with the real health probes is deployed.
    Check("角色站 API", "https://character.halfopen.dev/api/status", contains='"mode": "public"'),
    Check("知识站 live", "https://knowledge.halfopen.dev/health/live", json_status=("live", "ok")),
    Check("衡仓 Android API ready", "https://finunity-api.halfopen.dev/health/ready", json_status=("ready", "degraded")),
    # The old domain must keep redirecting for at least a year (Google's site-move guidance).
    Check("旧域名 301", "https://baikai.site/", status=301, redirect_to="https://halfopen.dev/"),
)
CERT_HOSTS: tuple[str, ...] = (
    "halfopen.dev",
    "character.halfopen.dev",
    "knowledge.halfopen.dev",
    "finunity.halfopen.dev",
    "dashboards.halfopen.dev",
    "finunity-api.halfopen.dev",
    "baikai.site",
    "character.baikai.site",
    "knowledge.baikai.site",
    "finunity.baikai.site",
    "finunity-api.baikai.site",
    "dashboards.baikai.site",
)


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):  # a redirect is something to assert on, not follow
        return None


def fetch(url: str, timeout: float = 20.0) -> Response:
    opener = urllib.request.build_opener(_NoRedirect)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with opener.open(request, timeout=timeout) as reply:
            return Response(reply.status, dict(reply.headers.items()), reply.read(200_000))
    except urllib.error.HTTPError as error:  # 3xx, 4xx and 5xx surface here
        return Response(error.code, dict(error.headers.items()), error.read(200_000))


def evaluate(check: Check, response: Response) -> str | None:
    """Return why the response is wrong, or None when it matches the check."""
    if response.status != check.status:
        return f"HTTP {response.status}, expected {check.status}"
    if check.redirect_to:
        location = response.headers.get("Location", "")
        if not location.startswith(check.redirect_to):
            return f"redirects to {location!r}, expected {check.redirect_to!r}"
    text = response.body.decode("utf-8", "replace")
    if check.contains and check.contains not in text:
        return f"body does not contain {check.contains!r}"
    if check.json_status:
        try:
            value = json.loads(text).get("status")
        except (ValueError, AttributeError):
            return "body is not the expected JSON"
        if value not in check.json_status:
            return f"status is {value!r}, expected one of {list(check.json_status)}"
    return None


def run_check(
    check: Check,
    fetcher: Callable[[str], Response] = fetch,
    *,
    attempts: int = ATTEMPTS,
    delay: float = RETRY_DELAY_SECONDS,
    sleep: Callable[[float], None] = time.sleep,
) -> str | None:
    """Return None when the check passes within `attempts` tries, otherwise the last reason."""
    reason: str | None = None
    for attempt in range(attempts):
        try:
            reason = evaluate(check, fetcher(check.url))
        except (OSError, ValueError) as error:  # timeouts, DNS, TLS, connection resets
            reason = f"{type(error).__name__}: {error}"
        if reason is None:
            return None
        if attempt + 1 < attempts:
            sleep(delay)
    return reason


def days_until_expiry(host: str, *, timeout: float = 10.0, now: float | None = None) -> float:
    context = ssl.create_default_context()
    with socket.create_connection((host, 443), timeout=timeout) as sock:
        with context.wrap_socket(sock, server_hostname=host) as tls:
            not_after = ssl.cert_time_to_seconds(tls.getpeercert()["notAfter"])
    return (not_after - (time.time() if now is None else now)) / 86400


def run_cert_check(
    host: str,
    expiry: Callable[[str], float] = days_until_expiry,
    *,
    attempts: int = ATTEMPTS,
    delay: float = RETRY_DELAY_SECONDS,
    sleep: Callable[[float], None] = time.sleep,
) -> str | None:
    reason: str | None = None
    for attempt in range(attempts):
        try:
            days = expiry(host)
            reason = None if days >= MIN_CERT_DAYS else f"certificate expires in {days:.0f} days (< {MIN_CERT_DAYS})"
        except (OSError, ValueError, KeyError) as error:  # ssl.SSLError is an OSError
            reason = f"{type(error).__name__}: {error}"
        if reason is None:
            return None
        if attempt + 1 < attempts:
            sleep(delay)
    return reason


def run(
    checks: Sequence[Check] = SITES,
    cert_hosts: Sequence[str] = CERT_HOSTS,
    fetcher: Callable[[str], Response] = fetch,
    expiry: Callable[[str], float] = days_until_expiry,
    *,
    sleep: Callable[[float], None] = time.sleep,
    report: Callable[[str], None] = print,
) -> list[str]:
    """Run every check; return one failure line per problem (empty list means all good)."""
    failures: list[str] = []
    for check in checks:
        reason = run_check(check, fetcher, sleep=sleep)
        report(f"{'OK  ' if reason is None else 'FAIL'} {check.name}  {check.url}" + (f"  -> {reason}" if reason else ""))
        if reason:
            failures.append(f"{check.name} ({check.url}): {reason}")
    for host in cert_hosts:
        reason = run_cert_check(host, expiry, sleep=sleep)
        report(f"{'OK  ' if reason is None else 'FAIL'} TLS {host}" + (f"  -> {reason}" if reason else ""))
        if reason:
            failures.append(f"TLS {host}: {reason}")
    return failures


def notify(failures: Sequence[str], webhook: str | None) -> None:
    """POST the failures to an optional webhook. Never raises: alerting must not hide the failure."""
    if not webhook:
        return
    body = json.dumps(
        {
            "title": f"halfopen.dev monitor: {len(failures)} check(s) failing",
            "failures": list(failures),
            "run": "/".join(
                part
                for part in (
                    os.environ.get("GITHUB_SERVER_URL"),
                    os.environ.get("GITHUB_REPOSITORY"),
                    "actions/runs",
                    os.environ.get("GITHUB_RUN_ID"),
                )
                if part
            ),
        },
        ensure_ascii=False,
    ).encode("utf-8")
    request = urllib.request.Request(
        webhook, data=body, headers={"Content-Type": "application/json", "User-Agent": USER_AGENT}
    )
    try:
        urllib.request.urlopen(request, timeout=15).close()
    except (OSError, ValueError) as error:  # the webhook URL itself is never printed
        print(f"webhook delivery failed: {type(error).__name__}", file=sys.stderr)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="halfopen.dev uptime, health and certificate monitor")
    parser.add_argument("--list", action="store_true", help="print what is checked and exit")
    args = parser.parse_args(argv)
    if args.list:
        for check in SITES:
            print(f"{check.name}: GET {check.url} -> {check.status}")
        for host in CERT_HOSTS:
            print(f"TLS {host}: at least {MIN_CERT_DAYS} days left")
        return 0
    failures = run()
    if failures:
        print(f"\n{len(failures)} check(s) failing", file=sys.stderr)
        notify(failures, os.environ.get("ALERT_WEBHOOK_URL"))
        return 1
    print("\nall checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

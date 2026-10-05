"""Monitor logic: what counts as failing, retries, redirects that are asserted not followed, alerts."""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from tools import monitor
from tools.monitor import Check, Response


def reply(status=200, body=b"", headers=None) -> Response:
    return Response(status, headers or {}, body)


# --- evaluate: what counts as a failing response ---------------------------------------------------

def test_a_matching_response_passes():
    assert monitor.evaluate(Check("x", "u", contains="hello"), reply(body=b"say hello")) is None


@pytest.mark.parametrize(
    ("check", "response", "expected"),
    [
        (Check("x", "u"), reply(503), "HTTP 503, expected 200"),
        (Check("x", "u", contains="canonical"), reply(body=b"error page"), "does not contain"),
        (Check("x", "u", json_status=("ready",)), reply(body=b"<html>"), "not the expected JSON"),
        (Check("x", "u", json_status=("ready",)), reply(body=b'{"status": "not_ready"}'), "'not_ready'"),
        (Check("x", "u", json_status=("ready",)), reply(body=b"[1, 2]"), "not the expected JSON"),
        (Check("x", "u", status=301, redirect_to="https://new/"), reply(301, headers={"Location": "https://evil/"}), "redirects to"),
    ],
)
def test_wrong_responses_are_reported(check, response, expected):
    assert expected in monitor.evaluate(check, response)


def test_degraded_is_accepted_when_listed():
    check = Check("api", "u", json_status=("ready", "degraded"))
    assert monitor.evaluate(check, reply(body=b'{"status": "degraded"}')) is None


def test_a_redirect_with_the_right_target_passes():
    check = Check("old", "u", status=301, redirect_to="https://halfopen.dev/")
    assert monitor.evaluate(check, reply(301, headers={"Location": "https://halfopen.dev/x?y=1"})) is None


# --- retries: one dropped packet must not page anyone -----------------------------------------------

def test_a_transient_failure_is_retried_and_passes():
    outcomes = [OSError("timed out"), reply(502), reply()]
    waits: list[float] = []

    def flaky(url):
        outcome = outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    assert monitor.run_check(Check("x", "u"), flaky, sleep=waits.append) is None
    assert len(waits) == 2


def test_a_persistent_failure_reports_the_last_reason():
    def always_down(url):
        raise OSError("connection refused")

    reason = monitor.run_check(Check("x", "u"), always_down, attempts=3, sleep=lambda _: None)
    assert reason == "OSError: connection refused"


# --- certificates ------------------------------------------------------------------------------------

def test_certificate_close_to_expiry_fails_and_far_away_passes():
    assert monitor.run_cert_check("h", lambda host: 30.0, sleep=lambda _: None) is None
    assert "expires in 10 days" in monitor.run_cert_check("h", lambda host: 10.0, sleep=lambda _: None)


def test_a_tls_error_is_a_failure():
    import ssl

    def broken(host):
        raise ssl.SSLCertVerificationError("certificate has expired")

    assert "SSLCertVerificationError" in monitor.run_cert_check("h", broken, attempts=1, sleep=lambda _: None)


# --- run(): the whole thing with fakes ---------------------------------------------------------------

def test_run_returns_one_line_per_failure_and_nothing_when_all_is_well():
    checks = (Check("good", "https://ok/"), Check("bad", "https://bad/"))
    fetcher = lambda url: reply(200 if "ok" in url else 500)  # noqa: E731
    lines: list[str] = []
    failures = monitor.run(checks, ("a.example",), fetcher, lambda host: 5.0, sleep=lambda _: None, report=lines.append)
    assert len(failures) == 2
    assert failures[0].startswith("bad (https://bad/): HTTP 500")
    assert failures[1].startswith("TLS a.example: certificate expires in 5 days")
    assert any(line.startswith("OK   good") for line in lines)
    assert monitor.run(checks[:1], ("a.example",), fetcher, lambda host: 90.0, report=lambda line: None) == []


def test_the_default_configuration_covers_every_site_and_the_old_domain():
    names = " ".join(check.name for check in monitor.SITES)
    for expected in ("主站", "角色站", "知识站", "衡仓", "看板", "旧域名"):
        assert expected in names
    assert "baikai.site" in monitor.CERT_HOSTS and "halfopen.dev" in monitor.CERT_HOSTS


# --- fetch() and notify() against a real local server ------------------------------------------------

class Handler(BaseHTTPRequestHandler):
    received: list[dict] = []

    def do_GET(self):
        routes = {
            "/ok": (200, b"<link rel=\"canonical\">", {}),
            "/down": (503, b"maintenance", {}),
            "/moved": (301, b"", {"Location": "https://halfopen.dev/"}),
            "/ready": (200, b'{"status": "ready"}', {}),
        }
        status, body, headers = routes.get(self.path, (404, b"", {}))
        self.send_response(status)
        for key, value in headers.items():
            self.send_header(key, value)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        Handler.received.append(json.loads(self.rfile.read(int(self.headers["Content-Length"]))))
        self.send_response(204)
        self.end_headers()

    def log_message(self, *args):
        pass


@pytest.fixture
def server():
    Handler.received = []
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_port}"
    httpd.shutdown()
    thread.join(5)
    httpd.server_close()


def test_fetch_reports_status_without_following_redirects(server):
    assert monitor.fetch(server + "/ok").status == 200
    assert monitor.fetch(server + "/down").status == 503
    moved = monitor.fetch(server + "/moved")
    assert moved.status == 301 and moved.headers["Location"] == "https://halfopen.dev/"


def test_real_checks_against_a_local_server(server):
    checks = (
        Check("page", server + "/ok", contains="canonical"),
        Check("health", server + "/ready", json_status=("ready",)),
        Check("redirect", server + "/moved", status=301, redirect_to="https://halfopen.dev/"),
        Check("down", server + "/down"),
    )
    failures = monitor.run(checks, (), sleep=lambda _: None, report=lambda line: None)
    assert [f.split(" (")[0] for f in failures] == ["down"]


def test_notify_posts_the_failures_and_never_raises(server, capsys):
    monitor.notify(["a failing check"], server + "/hook")
    assert Handler.received[0]["failures"] == ["a failing check"]
    assert "1 check(s) failing" in Handler.received[0]["title"]
    monitor.notify(["x"], "http://127.0.0.1:9/unreachable")  # nobody listens: swallowed, not raised
    assert "webhook delivery failed" in capsys.readouterr().err
    monitor.notify(["x"], None)  # no webhook configured: silently does nothing

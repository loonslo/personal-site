"""boot.js / site.js 的行为测试：用 Node 的 vm 模拟最小 DOM 执行，没有安装 node 时跳过。"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which("node")

pytestmark = pytest.mark.skipif(NODE is None, reason="需要 node 来执行前端脚本")

HARNESS = r"""
import fs from "node:fs";
import vm from "node:vm";

const read = (name) => fs.readFileSync(new URL(name, process.env.STATIC_DIR_URL), "utf8");

class Element { closest() { return null; } }
class FakeAnchor extends Element {
  constructor(href, attrs = {}) { super(); this.attrs = { href, ...attrs }; }
  closest(selector) { return selector === "a[href]" ? this : null; }
  getAttribute(name) { return this.attrs[name] ?? null; }
  hasAttribute(name) { return name in this.attrs; }
}
class FakeReveal extends Element {
  constructor(top) { super(); this.top = top; this.classes = new Set(); this.classList = { add: (name) => this.classes.add(name) }; }
  getBoundingClientRect() { return { top: this.top }; }
}

function makeEnv({ href = "https://site.test/", seen = false, session = null, connection = {}, reveals = [], height = 800, io = true } = {}) {
  const listeners = {};
  const appended = [];
  const storage = session ?? new Map();
  const observed = [];
  const classes = new Set(seen ? ["seen"] : []);
  // 浏览器里 window 就是全局对象：把 window 指向上下文自身，脚本里直接写的 IntersectionObserver、Element 才找得到
  const env = { innerHeight: height, URL, Element, setTimeout, clearTimeout, console };
  if (io) env.IntersectionObserver = class { constructor(callback, options) { this.callback = callback; this.options = options; } observe(el) { observed.push(el); } unobserve() {} };
  env.window = env;
  const document = {
    documentElement: { classList: { contains: (n) => classes.has(n), add: (n) => classes.add(n) } },
    head: { append: (node) => appended.push({ rel: node.rel, href: node.href }) },
    createElement: () => ({}),
    querySelectorAll: () => reveals,
    addEventListener: (type, handler) => { listeners[type] = handler; },
  };
  const sessionStorage = session === "throws"
    ? { getItem() { throw new Error("denied"); }, setItem() { throw new Error("denied"); } }
    : { getItem: (k) => storage.get(k) ?? null, setItem: (k, v) => storage.set(k, String(v)) };
  Object.assign(env, { document, sessionStorage, location: { href, origin: new URL(href).origin }, navigator: { connection } });
  return { env, listeners, appended, observed, classes, storage };
}

const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const results = {};

// ---- boot.js ----
{
  const first = makeEnv();
  vm.runInNewContext(read("boot.js"), first.env);
  const second = makeEnv({ session: first.storage });
  vm.runInNewContext(read("boot.js"), second.env);
  const broken = makeEnv({ session: "throws" });
  vm.runInNewContext(read("boot.js"), broken.env);
  results.boot = { firstSeen: first.classes.has("seen"), secondSeen: second.classes.has("seen"), brokenSeen: broken.classes.has("seen"), stored: first.storage.get("hp:seen") };
}

// ---- site.js: 滚动显现 ----
{
  const above = new FakeReveal(100), below = new FakeReveal(1500);
  const a = makeEnv({ reveals: [above, below] });
  vm.runInNewContext(read("site.js"), a.env);
  const returning = makeEnv({ seen: true, reveals: [new FakeReveal(1500)] });
  vm.runInNewContext(read("site.js"), returning.env);
  const noHeight = makeEnv({ reveals: [new FakeReveal(1500)], height: 0 });
  vm.runInNewContext(read("site.js"), noHeight.env);
  const noObserver = makeEnv({ reveals: [new FakeReveal(1500)], io: false });
  vm.runInNewContext(read("site.js"), noObserver.env);
  results.reveal = {
    aboveFoldPending: above.classes.has("is-pending"), belowFoldPending: below.classes.has("is-pending"), observed: a.observed.length,
    returningPending: returning.env.document.querySelectorAll()[0].classes.has("is-pending"),
    zeroHeightPending: noHeight.env.document.querySelectorAll()[0].classes.has("is-pending"),
    noObserverPending: noObserver.env.document.querySelectorAll()[0].classes.has("is-pending"),
  };
}

// ---- site.js: 意图预取 ----
{
  const s = makeEnv({ href: "https://site.test/about/#contact" });
  vm.runInNewContext(read("site.js"), s.env);
  const hover = async (anchor) => { s.listeners.mouseover({ target: anchor }); await wait(120); };
  await hover(new FakeAnchor("/writing/#top"));
  await hover(new FakeAnchor("/writing/"));                                   // 同一页面（去掉 #）只处理一次
  await hover(new FakeAnchor("/about/"));                                     // 当前页面
  await hover(new FakeAnchor("https://dashboards.site.test/", { target: "_blank" }));
  await hover(new FakeAnchor("https://dashboards.site.test/x"));              // 同一来源只预连接一次
  await hover(new FakeAnchor("/report.pdf", { download: "" }));
  await hover(new FakeAnchor("/other/", { target: "_blank" }));               // 同源新窗口不预取
  await hover(new FakeAnchor("mailto:someone@example.com"));
  await hover(new FakeAnchor("javascript:void(0)"));
  s.listeners.touchstart({ target: new FakeAnchor("/en/") });                 // 触摸立即处理
  s.listeners.focusin({ target: new FakeAnchor("/projects/finunity/") });     // 键盘聚焦立即处理
  s.listeners.mouseover({ target: new Element() });                           // 不在链接上：忽略
  // 悬停后快速移开：防抖应取消
  s.listeners.mouseover({ target: new FakeAnchor("/cancelled/") });
  s.listeners.mouseover({ target: new Element() });
  await wait(120);
  results.hints = s.appended;
}

// ---- site.js: 省流量 / 2G ----
{
  for (const connection of [{ saveData: true }, { effectiveType: "2g" }, { effectiveType: "slow-2g" }]) {
    const s = makeEnv({ connection });
    vm.runInNewContext(read("site.js"), s.env);
    (results.saveData ??= []).push(Object.keys(s.listeners).length);
  }
  const fast = makeEnv({ connection: { effectiveType: "4g" } });
  vm.runInNewContext(read("site.js"), fast.env);
  results.listenersOnFastNetwork = Object.keys(fast.listeners).sort();
}

console.log(JSON.stringify(results));
"""


def run_harness() -> dict:
    completed = subprocess.run(
        [NODE, "--input-type=module", "-"],
        input=HARNESS, capture_output=True, text=True, encoding="utf-8", timeout=60,
        env={**os.environ, "STATIC_DIR_URL": (ROOT / "static").as_uri() + "/"},
    )
    assert completed.returncode == 0, completed.stderr
    return json.loads(completed.stdout.strip().splitlines()[-1])


@pytest.fixture(scope="module")
def results() -> dict:
    return run_harness()


def test_boot_marks_repeat_visits_and_survives_blocked_storage(results: dict) -> None:
    assert results["boot"] == {"firstSeen": False, "secondSeen": True, "brokenSeen": False, "stored": "1"}


def test_reveal_only_hides_blocks_below_the_fold(results: dict) -> None:
    assert results["reveal"] == {
        "aboveFoldPending": False, "belowFoldPending": True, "observed": 1,
        "returningPending": False, "zeroHeightPending": False, "noObserverPending": False,
    }


def test_intent_hints_are_same_origin_prefetch_and_cross_origin_preconnect_only(results: dict) -> None:
    assert results["hints"] == [
        {"rel": "prefetch", "href": "https://site.test/writing/"},
        {"rel": "preconnect", "href": "https://dashboards.site.test"},
        {"rel": "prefetch", "href": "https://site.test/en/"},
        {"rel": "prefetch", "href": "https://site.test/projects/finunity/"},
    ]


def test_hints_are_disabled_on_data_saver_and_slow_networks(results: dict) -> None:
    assert results["saveData"] == [0, 0, 0]
    assert results["listenersOnFastNetwork"] == ["focusin", "mouseover", "touchstart"]

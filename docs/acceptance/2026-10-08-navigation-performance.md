# 主站页面切换与缓存（2026-10-08）

状态：**本机改动，未提交、未部署。** 线上响应头和浏览器表现均未在生产环境验证。

## 背景

用 prodclub.xyz（单页应用、悬停预载、数据缓存）做对照，主站点导航的“等待”来自三处：

1. 多页站点，点导航是整页重载；`/site.js` 没有版本号，每次页面加载都要再校验一次，`DOMContentLoaded` 因此晚一个往返。
2. 每页都重播入场动画（`.page-head`、`.hero__text` 等从透明升起 0.8–1.4s），新页面一开始是空白纸面，像在加载。DESIGN.md 把它定义为“首屏一次性编排”，但多页站点每次翻页都会重播。
3. 滚动显现靠 `.js` 类：脚本到达后才把首屏内的块设为透明再淡入，会先闪一下。

## 改动

| 范围 | 文件 | 内容 |
| --- | --- | --- |
| 版本号 | `build.py`、`sitegen/render.py` | `styles.css`、`boot.js`、`site.js` 的地址都带 `?v=<内容哈希>`（`Context` 新增 `boot_href`、`site_js_href`，默认值保持旧单测可用） |
| 缓存头 | `vercel.json`、`static/_headers` | `/site.js`、`/boot.js` 仅在带 `?v` 时 `immutable`（`/styles.css` 原有规则不变）；页面本身仍每次校验 |
| 首访标记 | `static/boot.js`（新） | 在 `<head>` 同步执行：本会话首次访问不加标记，之后给 `<html>` 加 `seen`；隐私模式读写失败时照常播放 |
| 入场动画 | `static/styles.css` | 所有入场 `animation` 挂在 `html:not(.seen)` 下，只在首访播放；没有 JS 时始终播放 |
| 滚动显现 | `static/site.js`、`static/styles.css` | 只给首屏以下的块加 `.is-pending`，进入视口再 `.is-visible`；首屏内的块始终可见；视口高度为 0 时不隐藏；再次访问全部直接可见。不再使用 `.js` 类 |
| 跨页过渡 | `static/styles.css` | `@view-transition { navigation: auto; }` 与 0.15s 淡入淡出，仅 `prefers-reduced-motion: no-preference` |
| 意图预取 | `static/site.js` | 悬停约 65ms、触摸、键盘聚焦到链接时：同源页面加 `<link rel="prefetch">`，跨域链接（各子站）只 `preconnect` 其来源；省流量、2G、已处理过的地址、新窗口同源链接、下载链接和非 http(s) 链接跳过 |
| 设计正本 | `DESIGN.md` §7 | 动效规则改为“首访一次编排、翻页用过渡” |

页面模板多了一个外置脚本，没有内联脚本，CSP 不变；`tests/test_sitegen.py` 里两处“脚本类型列表”断言由 `[None, 'application/ld+json']` 改为 `[None, None, 'application/ld+json']`。

## 验证（2026-10-08，Windows 10 / Python 3.14 / Node 22）

- `py -3 -m pytest`：73 项通过（新增 9 项：脚本哈希与加载顺序、哈希随内容变化、动效门控与 `@view-transition`、脚本安全检查、托管规则；`tests/test_front_scripts.py` 用 Node 的 `vm` 执行 `boot.js`/`site.js`，覆盖首访标记、滚动显现的五种情形、各类链接的预取与预连接、省流量/2G；没有 node 时自动跳过）。
- `py -3 build.py check --offline`：17 页，站内链接与禁用词问题 0；3 条“待补”为既有提示。
- 对照 `static/styles.css` 修改前后：首访终态截图一致。

### 本机对照（单次测量，仅供比较）

环境：本机脚本模拟 Vercel 静态托管（响应带 ETag、页面 `no-cache`、`styles.css` immutable，每个请求固定加 120ms），真实 Chrome 无头出帧。旧版 = 提交 HEAD 的构建产物。数字为“从首页点进经历页”：

| 指标 | 改动前 | 改动后 |
| --- | --- | --- |
| DOMContentLoaded | 334 ms | 277 ms |
| 首次内容绘制 | 280 ms | 348 ms（含跨页过渡的等待，约多 70 ms） |
| 新页面上同时运行的动画 | 3 个（内容约 0.9s 才完全显现） | 0 个（第一帧内容已完整） |
| HTML 传输 | 8,898 B | 300 B（304 校验，悬停预取过） |
| 脚本样式 | `site.js` 再校验一次（一个往返） | 三个文件均来自缓存，0 B |

中间帧截图（点击后约 60ms，两张都在 `docs/acceptance/2026-10-08-navigation-performance/`）：旧版 `old-switch-60ms.jpg` 是只有页眉和一行淡标题的空白纸面，内容随后逐步升起；新版 `new-switch-60ms.jpg` 是旧页面与新页面的淡入淡出，随后是完整页面。首访终态（动画播完）两版截图一致；首访仍有 25 个动画、8 个首屏以下的块处于待显现状态。

## 未验证与已知边界

- 没有部署：`vercel.json` 里 `has` 查询条件的 `headers` 规则在 Vercel 上的实际响应头需发布后用 `curl -I` 核对（`vercel.json` 已用 Vercel 官方 JSON Schema（openapi.vercel.sh/vercel.json）校验通过）。
- 模拟延迟不等于国内真实网络；本机还走本地代理，出口在美西。
- 只在 Chrome 验证了跨页过渡与预取；Safari、Firefox 会忽略这两项，回到普通跳转。
- 悬停预取在 Chrome 里只能把 HTML 的整页下载变成 304 校验，**仍有一次往返**。要消掉它需要给 HTML 一个很短的 `max-age`（有发布后短时间看到旧页的代价），或 Speculation Rules 预渲染（需要放宽 CSP 的 `script-src`）。两者都没做，由你决定。
- 首次内容绘制变晚约 70ms 是跨页过渡的固有等待；若更在意首帧时间而不是“不空白”，可以只保留去动画重播，删掉 `@view-transition` 两行。
- 子站跳转（角色设定、知识库、衡仓、看板）仍是跨域冷启动；预连接只能省下握手，省不掉下载应用壳。
- 未改动：HTML 缓存策略、`personal-site-release-20261001` 副本、内容与文案。

## 发布注意

- 两个域名项目都要发布同一版本（halfopen.dev 与 baikai.site）。旧版本源码叠加本版 `vercel.json` 时，旧页面引用 `/site.js`（无 `?v`），`immutable` 规则不会匹配，行为与现在一致。
- 版本号由 `build.py` 在域名替换之前计算；`boot.js`、`site.js` 不含域名，同一源码在两个域名下哈希相同。

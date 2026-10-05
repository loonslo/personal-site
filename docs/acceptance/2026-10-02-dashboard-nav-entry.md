# 右上角新增看板入口验收

- 验收日期：2026-10-02（Asia/Shanghai）
- 环境：Windows / Python 3.14 本地构建；浏览器为系统 Microsoft Edge（Playwright 1.63.0 驱动）。

## 实现范围

- `content/site.json` 与 `content/en/site.json` 的 `project_links` 各追加一项，指向 `https://dashboards.baikai.site`；中文标签「看板」，英文标签「Dashboards」。
- 该列表由 `sitegen/render.py` 的 `layout()` 统一渲染进全站页眉导航，因此无需改动模板、样式或构建脚本；新入口与其余在线项目一致，以 `target="_blank" rel="noopener"` 打开，并带屏幕阅读器提示。
- 入口排在 FinUnity 之后，未调整已有三项的顺序。导航未引入新的脚本或内联样式，CSP 保持原样。

> 同日后续调整：本文件记录时中文标签为「看板」、英文为 `Dashboards`，导航中的 `FinUnity` 也未改名。随后按用户要求改为「投资看板」/ `Investment Dashboards`，并把 `FinUnity` 改为「衡仓」/ `Hengcang`。改名与首页项目列表的同步更新见 `2026-10-02-project-list-refresh.md`。

## 本地验证

- `py -3 build.py check`：构建 11 个 HTML 页面；站内链接问题、禁用词命中共 0 条。输出中的「待补」三项（小红书链接、禁用词清单、未联网检查外链）为既有状态，与本次改动无关。
- `py -3 -m pytest -q`：39 passed。
- 生成的 HTML 逐页核对：`dist/index.html`、`dist/about/index.html`、`dist/en/index.html`、`dist/en/about/index.html` 均含 `<a href="https://dashboards.baikai.site" target="_blank" rel="noopener">`，中文页标签为「看板」，英文页为「Dashboards」。
- 目标站 `https://dashboards.baikai.site/` 返回 HTTP 200，页面标题为「看板」。

## 布局检查

用 Playwright 在 1440×900、1280×800、1024×768、375×812 四种宽度下截图核对。

- 中文首页在 1440 与 1280 宽度下，页眉九项仍在同一行放下。
- 375 宽度下导航按既有规则换行：中文两行、英文四行。英文基线（不含新入口）同为四行，新入口只是占用末行「中文」前的空位，未增加行数。
- 1024 宽度英文页出现导航与品牌字重叠、品牌被压成两行的情况。为判断归属，另外构建了一份不含看板入口的基线版本作对照，基线在该宽度下同样重叠，说明这是既有的窄视口问题，不是本次新增入口引入的。

截图见本目录 `desktop-zh-1440.png`、`mobile-en-375.png`。

## 尚未验收

- 未部署到 Vercel Production，线上仍为加看板入口前的版本；`baikai.site` 的页眉尚未出现该入口。
- 深色模式与更多中间宽度（如 900–1100px 区间）未逐一核对。
- 未执行外链联网检查（`--check-external`）。

## 2026-10-03 后续状态

本文件以上是 2026-10-02 验收快照。页眉与六项目列表现已生产发布，英文挤压已修复；新验收与未决资料见 [2026-10-03 发布验收](2026-10-03-header-project-release.md)。

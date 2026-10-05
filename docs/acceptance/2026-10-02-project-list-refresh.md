# 项目列表更新与衡仓改名验收

- 验收日期：2026-10-02（Asia/Shanghai）
- 环境：Windows / Python 3.14 本地构建；浏览器为系统 Microsoft Edge（Playwright 1.63.0 驱动）。

## 实现范围

改名：

- 页眉导航中文「看板」改为「投资看板」，英文 `Dashboards` 改为 `Investment Dashboards`。
- 页眉导航与首页项目列表的「FinUnity」改为「衡仓」，英文用 `Hengcang`。

首页「个人项目」新增两条（此前已上线但未列入）：

- 投资看板，外链 `https://dashboards.baikai.site`，状态「在线」。
- 角色设定卡，外链 `https://character.baikai.site`，状态「在线」。

内容更新：

- 衡仓介绍页重写。原文写「Web + Server 暂无核实过的公开访问入口」，已经过时。改为三端（Android / Server / Web）的口径，并分别写明各自的验证结果与未验收边界。
- 衡仓在首页的状态由「仅介绍」改为「在线」，摘要补上「Web 端需登录」。
- 经历页的个人项目列表同步：新增投资看板与角色设定卡两条，衡仓一条改名并把验证数据更新为三端口径。
- `content/site.json` 与 `content/en/site.json` 的 `description` 更新，覆盖新增项目。
- `README.md` 的项目清单说明更新为六项。
- `tests/test_sitegen.py` 两处断言同步：项目名称列表改为六项；经历页摘要断言由「历史后端 35 项」改为「衡仓三端的测试通过记录」。原先「角色设定卡不在首页」的断言已删除，因为该条现已列入。

## 事实核对

改写前逐项核对了项目的公开状态：

| 核对项 | 结果 |
| --- | --- |
| `github.com/loonslo/FinUnity` | Public（Kotlin），衡仓 Android 端已开源 |
| `https://finunity.baikai.site/` | HTTP 200，标题「FinUnity Web · 个人资产工作台」，需登录 |
| `https://dashboards.baikai.site/` | HTTP 200，标题「看板」 |
| `https://character.baikai.site/` | HTTP 200，标题「角色设定卡 · Atelier」 |
| `https://knowledge.baikai.site/chat` | HTTP 200，为只读演示页 |
| `https://knowledge.baikai.site/health/ready` | `not_ready`（sqlite、demo_manifest 均为 false） |

知识库线上就绪检查为 `not_ready`，因此介绍页未宣称线上检索可用，仍按本地运行来描述。

介绍页与经历页引用的测试数字（Android 146 项、服务端镜像内 83 项、Web 12 项）取自各项目自己的 README、PROJECT_STATUS 与生产记录。**本次没有重跑这些项目的测试**，这些数字是引用，不是本次复测结果。

## 本地验证

- `py -3 build.py check`：构建 11 个 HTML 页面；站内链接问题、禁用词命中共 0 条。「待补」三项（小红书链接、禁用词清单、未联网检查外链）为既有状态。
- `py -3 -m pytest -q`：39 passed。
- 浏览器核对：首页项目列表六条，顺序与 `content/projects.json` 一致，月相状态与跳转标签正确；衡仓介绍页的标题、状态行、技术栈与流程条渲染正常。

截图见本目录 `home-zh-1440.png`、`hengcang-page-1440.png`。

## 布局发现（未修复）

英文页页眉在 1440 宽度下会换行，品牌字「半開」被压成两行。为判断归属，另外构建了一份使用旧标签（`FinUnity` / `Dashboards`）的基线版本作对照：**基线在 1440 下同样把品牌字压成两行**，所以这是既有的窄视口问题，不是本次改名引入的。

本次改名让「Investment Dashboards」这一项由一行变两行，因此页眉比基线略高，但根因不在本次改动。

根因在 `static/styles.css`：只有 `max-width: 680px` 时才让 `.nav` 独占一行；681px 以上 `.nav` 与 `.brand` 同行，两者都不收缩，导航标签一长就挤压品牌字。

对照截图：`nav-en-1440-new.png`（当前）与 `nav-en-1440-baseline.png`（旧标签基线）。

## 尚未验收

- 未部署到 Vercel Production，线上仍是本次改动前的版本。
- 深色模式与 900–1100px 区间未逐一核对。
- 未执行外链联网检查（`--check-external`）。
- 各项目自身的最新验证数据为引用，本次未重跑对应项目测试。

## 2026-10-03 后续状态

本文件以上是 2026-10-02 验收快照。改名、六项目列表与衡仓案例现已生产发布，英文挤压及 320px 英文内容溢出已修复；新验收与未决资料见 [2026-10-03 发布验收](2026-10-03-header-project-release.md)。

# 2026-10-14 主站到三个子站的交接

依据：`日常/output/20261014-三站首屏引导与交互调整方案.md` 第五节“主站到子站的交接”和第九节第 6 项（名称）。叠加在 2026-10-11 的改版之上，两者于 2026-10-14 一起提交、推送并发布，实际结果见文末“发布结果”。以下“改了什么”“与方案的差异”写于发布前（Knowledge 入口是发布当天补上的，已在文中更新），“没有验证的”已按发布后的核对更新。

## 先看这一条：发布顺序（已按此执行）

主站的卡片和项目页按钮写的是“试用示例（不用注册）”，并直接深链到衡仓 `/app` 和角色站 `/workspace/?start=guide`。这两个入口只有在**衡仓示例模式、角色站匿名引导已经发布到两个域名之后**才成立；主站先发，访客会被带到登录页或旧首页，卡片承诺就是假的。实际顺序：衡仓 → 角色站（含其服务器后端）→ Knowledge（演示资料与前端）→ 主站，每个 Vercel 前端都发两个项目。

## 改了什么

| 项目 | 首页卡片 | 项目页与产品列表 | 深链（中文页 / 英文页） |
| --- | --- | --- | --- |
| 衡仓 | “多币种家庭资产账本：三类资产离目标差多少，一眼看清。示例不用注册，自己的账本需登录。”，按钮“试用示例 ↗” | 按钮“试用示例（不用注册）↗” | `finunity.halfopen.dev/app?from=portfolio&lang=zh` / `…&lang=en` |
| 角色设定卡 | “给写小说、画原创角色的人：把外貌、性格、背景整理成一张设定卡。试用不用注册。”，按钮“试用示例 ↗” | 按钮“试用五步引导（不用注册）↗” | `character.halfopen.dev/workspace/?start=guide&from=portfolio&lang=zh` / `…&lang=en` |
| 投资看板 | 不变（“打开 ↗”） | 不变 | 不变，没有示例，不带来源标记 |
| Knowledge | 不在首页精选；产品列表里仍是“仅介绍”，按钮“试用示例检索（不用注册）↗” | 项目页按钮同左，顶部一张在线示例截图 | `knowledge.halfopen.dev/chat?from=portfolio&lang=zh` / `…&lang=en` |

1. **卡片与按钮**：每张卡片先说给谁、得到什么，再说试用要不要注册；出图和文字 AI 不放在卡片上，写进角色设定卡项目页的“电脑版”一节。新增可选字段 `app.short_label`（首页紧凑行用短标签，项目页和产品列表用完整标签，缺省仍是“打开”）。链接里的 `from=portfolio` 让子站显示“半開 的作品 · … · 返回作品集”窄栏，`lang` 让子站用同一种界面语言（子站各加了一个很小的 `?lang=` 支持，见下）。
2. **名称统一**：角色设定卡英文页改为 Character Atelier（与英文子站一致），中文仍是角色设定卡；知识库中文改为“Knowledge 本地知识库”，英文“Knowledge”（与子站页面标题一致）；About 页的三个项目链接文字与卡片、项目页标题、`<title>` 一致，角色设定卡的链接由直跳子站改为站内项目页。**知识库的名称是方案第九节第 6 项，用户还没定，这是按子站现有标题取的默认值，待确认**。
3. **项目页截图**（方案建议 20 秒录屏或 3 张截图，这里用截图）：衡仓 2 张（示例总览、截图导入“识别 → 核对 → 写入”）、角色设定卡 1 张（引导第二步，右侧文字摘要实时变化），中英文各一套，均来自对应子站真实界面，说明文字写明数据虚构和示例的预设性质。图片放 `static/shots/`（PNG，共 6 个文件，约 288 KB），Markdown 渲染时自动补宽高和懒加载，样式让截图可以比正文宽（最宽 56em、最高 720px）。
4. **Knowledge**：首次发布时演示资料还没批准，项目页和 RAG 文章不放演示入口；当天用户确认资料不含个人隐私并要求公开，演示上线后补上入口：卡片、项目页按钮、产品列表和 RAG 文章都指向带来源与语言参数的 `/chat`，项目页顶部加了在线示例截图和线上验证说明。产品本身仍是“仅介绍”（只在本机运行），在线的只是只读示例。测试改为保证所有指向演示站的链接都走带标记的入口。
5. **文字更正（对既有说明的更正，不是新验收）**：衡仓页“进攻”改为产品界面用的“进取”，英文“stable”改为界面用的“balanced”；“三端都具备账户、持仓……”去掉“账户”（Web 端没有账户页，依据 `FinUintyWeb/src/App.tsx` 的路由）。衡仓与角色设定卡的项目页新增“不注册先试”说明、本次本机验证结果和边界；角色设定卡英文页注明生成的设定文字目前是中文。
6. **样式**：`.project` 类与截图规则；顺带修了项目页状态行在手机上被长说明挤成“状 / 态”“在 / 线”竖排的问题（`dt` 和状态标签不再收缩）。
7. **文档**：README 的项目字段、登录措辞规则和截图写法；`docs/seo-pages.json` 三个页面标题；`docs/SEO.md` 顶部说明（历史表格不改）。

## 配套的子站改动（在各自项目里，同日已发布）

- 衡仓与角色站各加 `?lang=en|zh` 深链支持（`src/urlLanguage.ts`；`web/i18n.js`），否则英文页点进去仍是中文界面；两处都有单元测试，并在真实浏览器里核对过。
- 衡仓首页截图重拍：核对时发现第一版截图是在最终文案之前拍的，侧栏仍写“数据按用户隔离并持久化”，与“示例不保存”矛盾；已在最终界面重拍替换。英文示例截图里较长的基金名称贴住数量列，也已修。
- 两个项目的验收文档、PROJECT_STATUS 已同步这些改动。

## 实际验收（2026-10-14，Windows 10，Python 3.14，Chrome，本机）

| 项目 | 结果 |
| --- | --- |
| `python -m pytest -q` | **91 项通过**（改前 81 项；新增 10 项：两种语言的深链与短标签、卡片/列表/项目页按钮与深链一致、指向 Knowledge 演示的链接都走带标记的入口（首次发布时是“不链接演示”，补入口后改写）、名称在卡片/标题/About 一致、截图尺寸与存在、图片渲染边界（缺失、外链、路径穿越），以及 `short_label` 类型校验） |
| 构建检查（临时目录，未重建 `dist/`） | 23 个 HTML，站内链接（含图片 `src`）错误 0 |
| 域名变体 | 在构建副本上应用 baikai.site 变体：卡片深链改写为 `finunity.baikai.site`、`character.baikai.site` 且保留参数，没有残留 `halfopen.dev` |
| 浏览器复查（Playwright + Chrome） | 9 个页面（中文：首页、产品列表、衡仓、角色设定卡、Knowledge；英文：首页、产品列表、衡仓、角色设定卡）× 浅色 1280/768/390 与深色 1280/390：无横向溢出、无页面错误和失败请求、所有图片加载；人工看了桌面与手机截图 |
| 体积 | 首页 HTML 8,003 bytes（10-11 记录为 7,772）；CSS 26,438 bytes（25,670）；首页没有图片，项目页新增图片见上 |
| 子站配套 | 衡仓 `npm test` 41 项、类型检查、lint 通过；角色站 node 测试 96 项通过；两个深链分别在真实浏览器里核对（带参数、之后不带参数、新访客） |

证据：[首页](2026-10-14-subsite-handoff/home-zh-1280.jpg)、[手机首页卡片](2026-10-14-subsite-handoff/home-zh-390-cards.jpg)、[产品列表](2026-10-14-subsite-handoff/projects-zh-1280-cards.jpg)、[衡仓项目页](2026-10-14-subsite-handoff/finunity-zh-1280-top.jpg)、[角色设定卡项目页](2026-10-14-subsite-handoff/character-zh-1280-top.jpg)、[角色设定卡英文页](2026-10-14-subsite-handoff/character-en-1280-top.jpg)（均为本机预览截图，仅取部分区域）。

## 与方案的差异

- 方案举例按钮为“试用示例 ↗”；首页用短标签“试用示例”，项目页与列表用完整标签。角色设定卡的完整标签写“试用五步引导（不用注册）”，因为到达页是引导而不是示例。
- 方案“20 秒录屏或 3 张截图”：用截图，没有录屏，三个项目页都用真实界面截图。
- 方案第五节第 3 点要求核对带参数的链接会不会产生重复收录：深链指向的两个落点本来就不收录——衡仓 `index.html` 带 `<meta name="robots" content="noindex">`、`vercel.json` 对应用路由加 `X-Robots-Tag: noindex`；角色站 Vercel 配置对 `/workspace/` 加 `X-Robots-Tag: noindex`。这是读配置的结果；Knowledge 的 `/chat` 在线上抓到 `X-Robots-Tag: noindex`，也不在它的 sitemap 里。

## 没有验证的

- 线上响应头与 CSP（`img-src 'self' data:`）没有逐项核对，只确认了截图在两个域名都能加载；卡片文案、深链落点、窄栏、截图加载已在线上核对（见发布结果）。
- 真人 5 秒测试和 30 秒任务（方案第七节）。
- Safari、Firefox、真机；深色模式下浅色截图只看了桌面与手机各一张。
- 未联网检查外链，未提供禁用词清单（没有扫描客户名等敏感词）。
- 新名称对搜索收录的影响（推理，需发布后 2～4 周观察）；站内旧标题“个人知识服务”“Private Knowledge Assistant”“Character Profiles”已不再出现（构建结果与源文件里都核对过）。
- 主站项目页里的测试数字与结论引用子站的本机验收记录，发布后线上表现要另行核对。

## 文件

- 内容：`content/{projects,en/projects}.json`、`content/{projects,en/projects}/{finunity,character,knowledge}.md`、`content/{about,en/about}.md`、`content/{writing,en/writing}/rag-hybrid-search.md`（各去掉一处演示链接）。
- 代码与样式：`sitegen/content.py`（`short_label`、PNG 尺寸与图片渲染）、`sitegen/render.py`（紧凑行标签、`project` 类）、`static/styles.css`、`static/shots/*.png`。
- 测试与文档：`tests/test_sitegen.py`、`README.md`、`docs/SEO.md`、`docs/seo-pages.json`、本文件与同名截图目录。

## 复现

```bash
python -m pytest -q
python -c "import build; from pathlib import Path; build.build(Path('.'), Path('<项目外的空临时目录>/site'))"
```

浏览器复查用一次性 Playwright 脚本打开构建结果的静态预览（脚本未保留，检查项见上表）。

## 发布结果（2026-10-14）

用户明确要求提交、推送、部署。发布顺序：衡仓 → 角色站（含其后端）→ Knowledge（含演示资料与前端）→ 主站，每一步先在线上核对再进行下一步。主站分两次发布：先发改版与交接，Knowledge 演示上线后再补演示入口。

### 第一次（改版与交接）

- 代码提交：`9148833951fd410307fa7aea1b59525b7fc36e17`（上一提交 `4c10d77`），已推送到 `main`，包含 2026-10-11 的改版；GitHub Actions CI 成功。发布前在从远程新建的干净检出里重跑：91 项 pytest 通过，`build.py check` 23 页、站内链接错误为 0；扫描待提交文件，没有密钥、个人信息或本机路径。
- halfopen.dev：Vercel Git 集成自动部署，Production，READY，`dpl_4KyyW45jzecWr9eEBanTxdVMnJi1`。
- baikai.site：`deploy/prepare_domain_release.py` 从该提交导出隔离目录，CLI 部署，Production，READY，`dpl_9Q7WaidF4BFxFozhnZTAuuCc2tdA`。
- 线上核对（Windows，Chrome）：两个域名首页（中英文）的衡仓与角色设定卡卡片和深链正确，baikai.site 上的深链指向 `*.baikai.site`；项目页返回 200，截图文件返回 200 且大小与本地一致；从两个域名、中英文首页点击衡仓和角色设定卡（8 条路径），到达页的界面语言、“半開 的作品 · … · 返回作品集”窄栏文字正确，返回链接指向当前所在的作品集域名；10 个页面 × 三种宽度 × 两个域名共 60 次访问，没有横向溢出、失败请求或页面错误（390 宽度下一次图片“未完成”是懒加载计时，滚动到该图后加载正常）。

### 第二次（Knowledge 演示入口）

- 演示资料经用户有条件授权（确认不含个人隐私才公开）和逐篇核对后批准，服务器建库完成，演示线上可用（见 Knowledge 项目的发布记录）。
- 补入口：卡片、项目页按钮、产品列表、RAG 文章都指向 `https://knowledge.halfopen.dev/chat?from=portfolio&lang=zh|en`，项目页顶部加在线示例截图（中英文各一张），`about` 页补一句“网页上有只读示例”。测试仍是 91 项（改写了“Knowledge 不链接演示”这条，并把 Knowledge 项目页加入截图尺寸检查）。
- 因为英文入口要落在英文界面，Knowledge 子站同日补了 `?lang=en|zh` 支持（前端提交 `0d65a7e`，两个域名已重新部署并在线上核对）。
- 代码提交：`5567bbada3810bc36f4bb5b56841ce9b8b9f92bb`（上一提交 `9148833`），已推送到 `main`；GitHub Actions CI 成功。halfopen.dev：Git 集成自动部署，Production，READY，`dpl_gnhuNo5yga6X9bVmWKCS6L8fyrkg`；baikai.site：CLI 部署，Production，READY，`dpl_732UMqpXFwtCLiGLKKf4e42vzFDR`。
- 线上核对：产品列表里的“试用示例检索（不用注册）”按钮在两个域名、中英文共 4 条路径上打开对应演示，界面语言、窄栏文字和返回链接正确；两个域名各 10 个页面 × 1280/390 宽度的布局检查没有溢出、失败请求或页面错误（390 宽度下 `/en/projects/finunity/` 的一张懒加载图片被脚本标为未完成，两次都是这一张，单独滚动到该图后加载正常）。

### 没有验证的

- 线上响应头逐项核对、Safari/Firefox/真机、真人 5 秒与 30 秒测试、Search Console 的收录变化（需要 2～4 周观察）。
- 未联网检查外链，未提供禁用词清单（没有扫描客户名等敏感词）。
- 中国大陆网络下的可达性与速度。

### 回滚

在 Vercel 控制台把上一次 Production 部署提升回生产（两个项目各做一次），或对相应提交 `git revert` 后推送（halfopen.dev 自动部署；baikai.site 需用 CLI 再发一次）。

# 个人站改版方案：产品导航 + 文章（2026-10-08）

> 当前状态（2026-10-11）：用户要求依据参考评审实施，首页、产品目录与文章阅读路径已完成本地改版和验收，尚未发布。见 [本次验收](acceptance/2026-10-11-blog-redesign.md)。下文保留 10-08 原方案与草稿作为历史记录；具体本轮取值及范围以验收记录和 `DESIGN.md` 为准，未将旧方案全部扩展项计作完成。

## 1. 背景

站点用途调整为两件事：

1. **个人介绍与文章**：教程、实践记录和思考过程；
2. **个人产品导航**：能直接打开自己的产品，也能看到每个产品为什么做、怎么验证。

2026-10-08 核对线上 https://halfopen.dev 与源码，现状是按“求职作品集”搭的：

| 问题 | 依据 |
| --- | --- |
| 定位是求职 | `<title>` 为“半開｜AI 应用与全栈开发作品集”；首屏是职业经历加 `site.json` 的 `job`（求职方向）；按钮“看代表作品 / 经历与联系”；关于页标题“经历与求职方向”，侧栏“正在找工作” |
| 页眉入口过多 | 9 个：作品、文章、经历、特价AI会员（推广链接，硬编码在 `sitegen/render.py:147`）、4 个子站、EN；手机上折成多行 |
| 产品与案例混排 | 一个列表里既有在线产品，也有只能看介绍的案例和学习仓库；整行是一个 `<a>`，没法同时给“打开”和“看思路”两个入口；看板、角色卡在主站没有介绍页；`/projects/` 返回 404 |
| 文章页信息少 | 不显示摘要，没有目录，文末没有作者介绍和相关产品 |
| 思考过程没有出口 | 文章和产品之间没有数据关联 |
| SEO/GEO 缺口 | 所有页面 `og:type=website`（`render.py:192`）；JSON-LD 只有 Person；sitemap 无 `lastmod`；`/llms.txt` 为 404；根目录 `404.html` 用的是循环结束后留下的英文 ctx（`build.py:148`），线上返回 `lang="en"`、`og:url` 为 `/en/404.html`，标题却是中文 |
| 分享图过期 | `static/og-image.png` 仍写着“十年软件从业，测试出身，正在转 AI 应用开发。所有项目都从这里进。”，竖排诗句是旧 tagline“人生小满” |

## 2. 已确认的决定（用户，2026-10-08）

1. **求职信息全部拿掉**：首页、关于页、文章结尾、样式和配置里与本人求职有关的内容都删除（清单见第 8 节）。直接删字段和代码，不留开关；以后要恢复从 Git 历史找回。
2. **推广链接移到页脚**。
3. **文章不要求中英双语**。
4. **首页先产品、后文章**。

## 3. 不能破坏的约束

功能与 SEO：

- 纯静态 HTML；不引入框架、网络字体、第三方脚本、内联脚本；CSP（`vercel.json`、`static/_headers`）不改。
- 现有 16 个公开 URL 全部保持 200 和原路径，不新增重定向。首页保留 `id="projects"`（旧链接 `/#projects`），关于页保留 `id="contact"`（文章里链接了 `/about/#contact`）。
- canonical、hreflang（含 x-default）、sitemap 只列可索引的 200 页、robots（`User-agent: * Allow: /`，AI 爬虫可读）、每种语言一个 Atom feed、Person `@id`（`base_url/#person`）稳定、404 noindex 且无 canonical。
- 带哈希的资源地址与 `immutable` 规则、跨页过渡、悬停预取、入场动画只在会话首访播放、`data-reveal` 只作用于首屏以下——行为和对应测试都保留。
- 双域名：同一版本分别构建部署到 halfopen.dev 与 baikai.site。`deploy/domain_variant.py` 只改写 `.html/.xml/.txt/.json/.js/.css/.svg` 里的域名，所以新产物必须是这些后缀，绝对地址一律由 `base_url` 生成，模板里不写死域名。
- 设计 token 不变：不超过 4 色、间距取 8 的倍数序列、无渐变色块；改设计先改 `DESIGN.md`。
- 内容事实：项目介绍页必须有“怎么验证的”；数字沿用项目记录并写明日期和口径；不编造。禁用词扫描照常（清单在仓库外，`SITE_BLOCKLIST`）。

性能预算（2026-10-08 本地构建）：

| 项 | 现在 | 上限 |
| --- | --- | --- |
| 首页 HTML | 约 13 KB | 16 KB |
| `styles.css` | 约 25 KB | 30 KB |
| `boot.js` + `site.js` | 约 3.6 KB | 不增加 |
| 首屏请求 | HTML、CSS、2 个 JS、favicon | 不增加；首页不加图片 |

## 4. 信息架构

### 4.1 页眉

`产品 · 文章 · 关于 · EN`（英文页：`Products · Writing · About · 中文`）

- 产品 → `/projects/`（在 `/projects/` 及其子页高亮）；文章 → `/writing/`；关于 → `/about/`。
- 删除：4 个子站链接、推广链接、“作品”锚点入口。
- 某语言没有已发布文章时隐藏“文章”（沿用现有 `show_writing`）。
- 可选（在检查点 B 请用户确认）：只剩 3 项后，手机端页眉可以改为单行（品牌在左、导航在右），省出首屏高度。用户不认可就保持 `DESIGN.md` §5 现有规则。

### 4.2 页脚

从上到下：

1. 品牌与 tagline（现有）。
2. 产品快捷入口：所有 `status: live` 的项目，地址取 `app.href`，没有 `app` 时取外链 `link.href`；新标签页打开，`rel="noopener"`。
3. GitHub（`rel="me"`）、小红书（有链接时）、RSS（有文章时）。
4. 推广链接：`<a href="https://prodclub.xyz/r/2QFJWC" target="_blank" rel="sponsored noopener">特价AI会员</a>`，旁边加小字“推广”（英文 “Sponsored”）。`rel="sponsored"` 必须有，这是 Google 对付费、联盟链接的标注要求。“推广”二字默认显示，用户不要可以去掉。
5. © 年份。

数据：推广链接从 `render.py` 挪到 `site.json` 新字段 `sponsored_links: [{"label", "href"}]`，校验规则与 `accounts[].href` 相同（有效 HTTPS）。

### 4.3 页面与标题

| 路径 | 中文 title | 英文 title | 变化 |
| --- | --- | --- | --- |
| `/` | 半開｜AI 应用开发：个人产品与文章（草稿） | 半開 \| AI App Development: Products & Writing（草稿） | 改 |
| `/projects/` | 产品 · 半開 | Products · 半開 | 新增 |
| `/projects/<slug>/` | 不变 | 不变 | 加强；第 5 批补 dashboards、character |
| `/writing/` | 文章 · 半開 | Writing · 半開 | 加强 |
| `/writing/<slug>/` | 不变 | 不变 | 加强 |
| `/about/` | 关于我 · 半開 | About · 半開 | 改 |
| `/llms.txt` | — | — | 新增 |
| `/404.html` | 页面不存在 · 半開 | — | 修复为中文模板 |

## 5. 页面规格

### 5.1 首页

顺序：首屏 → 正在做 → 产品（`id="projects"`）→ 文章（`id="writing"`）。

**首屏**

- 眉题：`半開 · 产品与文章`（英文 `Products & writing`）。
- H1 来自 `site.json` 新字段 `headline`。
  - 中文草稿：“我在做 AI 应用：把自己的问题做成产品，把过程写成文章。”
  - 英文草稿：“I build AI applications: turning my own problems into products, and writing up the process.”
- 两行介绍 `intro`。
  - 中文草稿：“十年互联网经验，做过软件测试、Python 开发和产品工作。\n现在做家庭资产记账、投资看板、角色创作和私有知识检索这几类工具。”
  - 英文草稿：“10 years in tech across software testing, Python development, and product work.\nNow building tools for household finances, investment dashboards, character creation, and private knowledge search.”
- 按钮：主按钮“看产品”→ `#projects`；文字链接“读文章”→ `/writing/`（该语言没有文章时改为“关于我”→ `/about/`）。
- 删除 `hero__job` 段落。竖排挂轴、背景月、入场动画保留。
- 入场动画：删掉 `hero__job` 后首屏文字区剩 4 个子元素，给 `:nth-child(4)` 补一个延迟（如 0.66s）。现有规则只给前 3 个设了延迟，第 4、5 个会先于标题出现。新规则同样要写成 `html:not(.seen) …`，否则 `test_entrance_motion_plays_once_and_page_changes_use_view_transitions` 会失败。
- `identity` 不再显示在首屏，只用作 Person 的 description 和关于页导语。
  - 中文草稿：“十年互联网经验的 AI 应用开发者：做个人产品，也写开发过程。”
  - 英文草稿：“AI application developer with 10 years in tech, building personal products and writing about the process.”

**正在做**（新区块，视觉检查点 A）

- 数据放在 `content/now.json` 和 `content/en/now.json`：

  ```json
  {"updated": "2026-10-08", "items": [
    {"title": "衡仓", "text": "Android 正式签名包与真机安装升级验收", "path": "/projects/finunity/"}
  ]}
  ```

  - `items` 1–3 条，`title`、`text` 不能为空。
  - `path` 可选，写不带语言前缀的站内路径，渲染时用 `ctx.page_href()` 自动加 `/en`。
  - `updated` 为不晚于构建当天的 ISO 日期。
- 显示：标题“正在做”，旁边写“更新于 2026.10.08”；每条一行：名称 · 一句进展 · →（有 `path` 时整行可点）。复用 `.posts` 的分隔线和字号，不加新颜色；每行带 `data-reveal`。
- `build.py check`：`updated` 超过 60 天时给一条“待补”提示，不报错。
- 草稿条目（须用户确认是否真在推进）：
  1. 衡仓 — Android 正式签名包与真机安装升级验收 → `/projects/finunity/`
  2. 个人知识服务 — 语义检索链路端到端验收 → `/projects/knowledge/`
  3. 本站 — 改为“产品 + 文章”两条主线（无链接）

**产品区**

- 标题“产品”，说明（草稿）：“能直接打开的在前，后面是案例和开源项目。”
- 按 `projects.json` 的顺序列出全部项目，用 5.3 的产品行；末尾放“全部产品与案例 →”，链到 `/projects/`。

**文章区**

最新 5 篇，每行显示日期、类型标签、标题和摘要；末尾放“全部文章 →”。

### 5.2 产品页 `/projects/`（新增）

- H1“产品”。导语（草稿）：“能直接打开的在前，后面是案例和开源项目；介绍页写了为什么做、怎么做、怎么验证。”
- 分两组，各带 h2：
  - “在线可用”：`status: live` 的项目；
  - “案例与开源”：其余项目。

  空组不渲染，组内按 `projects.json` 的顺序排。
- 行组件同 5.3，显示技术标签。
- description（草稿）：“半開的个人产品导航：衡仓家庭资产账本、投资看板、角色设定卡、个人知识服务、WorldQuant Alpha 研究工具和 AI 应用开发学习仓库，附设计思路与验证记录。”
- 中英文成对，加入 sitemap 和 `docs/seo-pages.json`。

### 5.3 产品行组件（替换现有目录行，视觉检查点 A）

现有 `_project_row`（`render.py:231`）把整行做成一个 `<a>`，HTML 不允许在里面再嵌一个链接。改为“拉伸链接”结构：

```html
<li class="index__item" data-reveal>
  <div class="index__row">
    <span class="index__no">01</span>
    <span class="index__main">
      <a class="index__link" href="/projects/finunity/">衡仓</a>
      <span class="index__summary">…</span><span class="index__tags">…</span>
    </span>
    <span class="index__aside">
      <span class="index__status">{月相} 在线</span>
      <span class="index__go" aria-hidden="true">思路 →</span>
      <a class="index__app" href="https://finunity.halfopen.dev" target="_blank" rel="noopener">打开 ↗<span class="sr-only">（在新窗口打开）</span></a>
    </span>
  </div>
</li>
```

- 拉伸方式：
  - `.index__row` 设 `position: relative`；
  - `.index__link::after { content: ""; position: absolute; inset: 0 }`，让点整行都进入主入口；
  - `.index__app` 设 `position: relative; z-index: 1`，浮在拉伸层之上。
- 主入口按 `link.type` 决定：
  - `page`：站内介绍页。“思路 →”只是视觉提示，加 `aria-hidden`，不再做成第二个可聚焦链接；
  - `external`：外链，新标签页，提示“{label} ↗”；
  - `none`：静态行（只用于“建设中”）。
- 次入口：有 `app` 时显示 `{app.label} ↗`。
- 悬停和聚焦：把原来的 `a.index__row:hover` 系列选择器改成 `.index__row:hover` 和 `.index__row:focus-within`，保留朱砂细线、底色和箭头位移；两个链接各自有可见的焦点框。
- 宽度：右栏放不下两个动作时，把 232px 调宽，并在 768、900、1280 三种宽度实测；手机端沿用现有规则，右栏落到下一行左对齐。
- 键盘顺序：先产品名称链接，再“打开”链接。

### 5.4 产品详情页

- 面包屑：`产品`（→ `/projects/`）/ 名称。底部返回链接改为“回到产品列表”→ `/projects/`。
- 页头：有 `app` 时，在元信息下加按钮 `{app.label} ↗`，新标签页打开。
- 新增“过程记录”节，放在返回链接之前：
  - 列出同语言里 `project` 指向本产品的文章；
  - 按日期从早到晚排，用文章行样式并显示类型；
  - 没有关联文章就不渲染。
- 第 5 批补内容：
  - 给 dashboards、character 写中英文介绍页，沿用“为什么做 / 方案 / 我负责的工作 / 怎么验证的 / 现在做到哪”的结构；
  - 写好后把它们的 `link.type` 改为 `page`，并加上 `app`；
  - 事实由用户提供，或经用户授权从对应项目的文档里摘取，不得编造。

### 5.5 文章

frontmatter 字段：

| 字段 | 必填 | 规则 |
| --- | --- | --- |
| `title`、`date` | 是 | 现有 |
| `summary` | 是 | 现有；同时显示在标题下 |
| `type` | 是（草稿也要） | `tutorial` / `practice` / `essay`，显示为 教程 / 实践 / 思考（英文 Tutorial / Practice / Essay） |
| `project` | 否 | 必须是 `projects.json` 里的 slug，否则构建失败 |
| `updated` | 否 | ISO 日期，不早于 `date` |
| `draft` | 否 | 现有 |

现有文章的取值（中英一致）：

- `rag-hybrid-search`：`tutorial`，`project: knowledge`
- `testing-to-ai-development`：`essay`
- `ui-testing-ten-years`（草稿）：`essay`

**文章页**（视觉检查点 C）

- 标题下：先放摘要（`.page-lead`），再放元信息行：类型 · 发布日期 · 更新日期（有更新日期且不同于发布日期时才显示）。
- 目录：
  - 正文 `##` 不少于 3 个时，在正文前加 `<nav class="toc" aria-label="目录">`，只列 h2；
  - 实现用 `mistune.toc.add_toc_hook(md, min_level=2, max_level=2)`，把调用改成 `md.parse(text)`，从 `state.env["toc_items"]` 取条目；
  - 标题 id 会生成 `toc_1`、`toc_2`…（已在本机 mistune 3.3.2 验证可用；`requirements.lock` 锁定 3.3.4）；
  - 项目介绍页不显示目录。
- 文末依次放：
  1. 相关产品卡（有 `project` 时）：名称、一句话、“思路 →”，有 `app` 时加“打开 ↗”；
  2. 作者卡：“半開”+ `identity` +“关于我 →”；
  3. 上一篇 / 下一篇：同语言，按日期。
- 文章列表：每行加类型标签；页头显示“订阅 RSS”链接。
- Atom：entry 加 `<published>`（取 `date`），`<updated>` 取 `updated`，没有就取 `date`。

### 5.6 关于页

- 标题改为“关于我”（英文 About），导语用 `identity`。
- 正文（中英文都要，内容须用户确认）分四节：
  1. 我是谁；
  2. 现在在做什么（链到 `/projects/`）；
  3. 我怎么做事：先定义问题和验收标准，先做最小闭环，写清验证结果和边界；
  4. 经历：保留现有“职业经历与角色”里的职责描述，去掉求职表述。
- 删除正文里的“个人项目”清单和测试数字，这些在各产品页都有。
- 侧栏只留“联系与账号”，保留 `id="contact"`；`about_aside` 文案改为“联系”。宽屏吸附布局不变。
- frontmatter 加 `updated`。summary（草稿）：“半開的个人介绍：十年互联网经验，做过软件测试、Python 开发和产品工作，现在做 AI 应用；这里有个人产品、文章和联系方式。”

### 5.7 404

- 根目录 `404.html` 改用中文 ctx 渲染。现在 `build.py:148` 用的是循环留下的英文 ctx。
- 页面标题改由 copy 提供，不再在 `render.py:425` 写死。
- 继续 noindex，不加 canonical 和 hreflang；页眉语言链接照常指向 `/en/`。

## 6. 文章双语规则

- 删除 `build.py:88-91` 的检查：现在要求中英文已发布文章的 slug 完全一致。改后，文章可以只有中文、只有英文或两者都有；slug 相同的两篇视为互译。
- hreflang 与 x-default 只在两种语言都有这一页时输出。现有 `other_paths` 逻辑已经如此，补测试覆盖。
- 语言切换（`render.py:42` 的 `language_href`）找不到对应页时：
  - `/writing/…` → 目标语言的 `/writing/`；目标语言没有文章时回 `/`；
  - `/projects/…` → 目标语言的 `/projects/`；
  - 其余 → `/`。
- 首页、产品、关于、正在做仍要求中英都有；`projects.json` 中英 slug 同序的检查保留。

## 7. SEO / GEO

### 7.1 结构化数据

- 每页仍只有一个 `<script type="application/ld+json">`，内容改为 `@graph`，沿用 `_person_json_ld`（`render.py:111`）对 `<`、`>`、`&` 的转义。这样“每页一个 JSON-LD 块、没有内联脚本”的约束不变。
- Person 节点字段不变（`@id`、name、url、description=`identity`、knowsAbout、email、sameAs），各页完全一致。
- 各页追加的节点：

| 页面 | 追加节点 |
| --- | --- |
| 首页 | `WebSite`：`@id` 为 `base/#website`、url、name、inLanguage、publisher → `#person` |
| 关于 | `ProfilePage`：mainEntity → `#person`，dateModified 取 about 的 `updated`；`BreadcrumbList` |
| `/projects/`、`/writing/` | `BreadcrumbList` |
| 产品详情 | `BreadcrumbList`；`status: live` 且有 `app` 时加 `SoftwareApplication`：name、description、url（`app.href`）、applicationCategory、operatingSystem、author → `#person` |
| 文章 | `BlogPosting`：headline、description、datePublished、dateModified、inLanguage、url、mainEntityOfPage、image（og-image 绝对地址）、author 与 publisher → `#person`；有 `project` 时 `about` 指向该产品页 URL；`BreadcrumbList` |

- `app` 增加两个可选字段：`category`（schema.org 的 applicationCategory）和 `os`（默认 `Web`）。建议取值（待用户确认）：
  - 衡仓：`FinanceApplication` / `Android, Web`
  - 投资看板：`FinanceApplication` / `Web`
  - 角色设定卡：`DesignApplication` / `Web`
- 不写 `offers`、`aggregateRating`，因为没有价格和评分事实。Rich Results Test 会提示缺字段，这是预期结果；结构化数据本身也不保证出富摘要。
- BreadcrumbList 的名称随语言变化；item 用绝对地址；最后一项可省略 item。

### 7.2 meta

- 文章页 `og:type=article`，加 `article:published_time`、`article:modified_time`，时间格式同 Atom（`+08:00`）；其他页面保持 `website`。
- 各页 title 和 description 按第 4.3、5 节；中文 description 控制在约 120 字以内。

### 7.3 sitemap `lastmod`

- 各页取值：

| 页面 | lastmod |
| --- | --- |
| 文章 | `updated`，没有就取 `date` |
| 产品详情 | 介绍页的 `updated` |
| 关于 | about 的 `updated` |
| `/writing/` | 本语言最新文章的日期 |
| `/projects/` | 本语言产品页里最新的 `updated` |
| 首页 | now.json 的 `updated`、最新文章、最新产品三者取最大 |

- 没有可信日期就不写；不得用构建时间。

### 7.4 `llms.txt`

- 构建时生成 `dist/llms.txt`，用 Markdown 格式（参照 llmstxt.org 提案）：

  ```text
  # 半開
  > {identity}
  {description}
  ## 产品
  - [衡仓](https://halfopen.dev/projects/finunity/)：{summary}（在线：https://finunity.halfopen.dev）
  ## 文章
  - [{title}](https://halfopen.dev/writing/{slug}/)（{date}）：{summary}
  ## 关于
  - [关于我](https://halfopen.dev/about/)：{about summary}
  ## English
  - [Home](https://halfopen.dev/en/) …（英文的产品、文章、关于）
  ```

- 只收公开、已发布的内容；地址由 `base_url` 生成，baikai.site 构建时由 domain_variant 改写；不进 sitemap。
- llms.txt 只是社区提案，主流搜索引擎没有承诺使用；成本低才做。

### 7.5 写作规范（写进 `DESIGN.md` §8）

- 摘要用 2–3 句先给结论，它同时显示在标题下。
- 小标题尽量用问句；数字写明日期和口径；写清楚哪些还没验证。
- 每篇至少链接一个相关产品或文章。
- “思考”类文章回答一个具体问题：背景 → 备选方案 → 选择 → 结果。
- 小红书主页链接补上后，`sameAs` 会自动带上（README 一直把它列为待补）。

### 7.6 发布后

- 两个域名都重新提交 sitemap。
- 用网址检查工具看 `/projects/` 和一篇文章。
- 之后关注结构化数据报告。sitemap 提交成功不等于已被收录。

## 8. 求职信息清理清单

| 位置 | 处理 |
| --- | --- |
| `content/site.json`、`content/en/site.json` 的 `job` | 删除字段 |
| `sitegen/content.py:20` 的 `_SITE_KEYS` | 去掉 `job`、`project_links`，加入 `headline`、`sponsored_links` |
| `sitegen/render.py:304` 的 `hero__job` | 删除 |
| `sitegen/render.py:378-379` 关于页侧栏“正在找工作” | 删除 |
| `render.py:60`、`:79-80` 的 copy：`about_aside`、`job_heading` | “求职与联系”改为“联系”；英文 “Career and contact” 改为 “Contact”；删除 `job_heading` |
| `static/styles.css` 的 `.hero__job`、`.job`、`.job__dot`、`.about__aside .job` 及提到“求职”的注释 | 删除或改写 |
| `content/about.md`、`content/en/about.md` | 标题、summary、首段里“简历可…索取”和英文 “request my resume”“opportunities” 改写 |
| `content/writing/rag-hybrid-search.md:85`、英文版 `:81` | “项目讨论与求职联系见[经历与联系]”改为“项目讨论可以通过[关于页](/about/#contact)联系我”，英文同义 |
| `content/writing/testing-to-ai-development.md:64`、英文版 `:64` | “我的职责、当前求职方向和联系方式”改为“我的经历和联系方式见[关于页](/about/#contact)”，英文同义 |
| `DESIGN.md:10`、`:51` | 改为新定位，并写明关于页侧栏只放联系 |
| `docs/SEO.md`、`docs/seo-pages.json` 中 `/about/`、`/en/about/` 的标题 | 同步新标题 |
| `tools/make_images.py:79-84` 的文案与 `static/og-image.png` | 文案换成新 `headline`，重新生成。竖排诗句取自 `site.json` 的 tagline，重新生成后会自动更新。需要 Pillow 和本机字体，命令见 README |
| README“首页、经历页与结构化数据”一节 | 同步措辞 |

保留不改的两类：

- `testing-to-ai-development.md:10` 的“不能保证求职结果”是写给读者的免责说明，不是本人求职信息；
- `alpha-research` 英文版里的 “resume” 指批次恢复。

验收：构建后运行 `rg -n "求职|简历|找工作|Seeking|opportunit|Career" dist/`，逐条确认只剩上面两类保留项。

## 9. 数据模型变更汇总

- **`site.json`**（中英）：
  - 新增 `headline`、`sponsored_links`；
  - 删除 `job`、`project_links`；
  - 改写 `identity`、`intro`、`description`、`home_title`（草稿见第 5 节）。
- **`projects.json`**（中英，slug 顺序一致）：
  - 顺序建议（待确认）：finunity、dashboards、character、knowledge、alpha-research、langchain-learning。
  - 新增可选 `app`：`{"href", "label", "category"?, "os"?}`。`href` 必须是有效 HTTPS。`app` 只能和 `link.type: page` 同时出现，因为外链行本身就指向站点，不需要重复入口。
  - 初始取值：finunity 为“打开”；knowledge 为“演示”，指向 knowledge.halfopen.dev。dashboards、character 在介绍页写好前保持 `external`。
- **`content/now.json`、`content/en/now.json`**：新增，格式见第 5.1 节。
- **文章 frontmatter**：新增 `type`、`project`、`updated`，规则见第 5.5 节。
- **`about.md`**（中英）：新增 `updated`。
- **`render.py` 的 copy**：
  - 新增或改名的键（中文 / 英文）：

    | 键 | 中文 | 英文 |
    | --- | --- | --- |
    | `nav_products` | 产品 | Products |
    | `nav_about` | 关于 | About |
    | `cta_products` | 看产品 | See products |
    | `cta_writing` | 读文章 | Read writing |
    | `now_heading` | 正在做 | Now |
    | `now_updated` | 更新于 | Updated |
    | `products_heading` | 产品 | Products |
    | `all_products` | 全部产品与案例 | All products |
    | `group_live` | 在线可用 | Live |
    | `group_cases` | 案例与开源 | Case studies & open source |
    | `case_link` | 思路 | Case study |
    | `process_heading` | 过程记录 | Process notes |
    | `back_products` | 回到产品列表 | Back to products |
    | `toc` | 目录 | Contents |
    | `published` | 发布 | Published |
    | `related_product` | 相关产品 | Related product |
    | `author` | 作者 | Author |
    | `prev` | 上一篇 | Previous |
    | `next` | 下一篇 | Next |
    | `subscribe_rss` | 订阅 RSS | Subscribe via RSS |
    | `sponsored` | 推广 | Sponsored |
    | `not_found_page_title` | 页面不存在 | Page not found |

    另外 `products_desc` 改为第 5.1 节的新说明，并新增文章类型名称 `types`。
  - 删除 `nav_work`、`cta_work`、`cta_about`、`job_heading`、`back_projects`（由 `back_products` 取代）。

## 10. 代码改动（按文件）

- `DESIGN.md`（最先改）：
  - §1 新定位；
  - §5 首页顺序、页眉、关于页侧栏；
  - §6 新组件：产品行双入口、正在做、目录、作者卡、相关产品卡、过程记录、页脚推广；
  - §8 文章字段、双语规则、写作规范、推广链接规则；
  - §9 验收里补上性能预算。
- `sitegen/content.py`：
  - 调整 site 必填键；
  - 校验 `sponsored_links`、`app`、`now.json`；
  - 新增 `load_posts()`，校验 `type`、`project`、`updated`；
  - `Doc` 增加 `updated`、`type` 的读取；
  - `render_markdown` 支持返回目录。
- `sitegen/render.py`：
  - `layout`：导航、页脚、`og:type`、文章 meta、JSON-LD graph；
  - 改 `home`，新增 `projects_index`，重写 `_project_row`；
  - 改 `project_page`、`post_page`、`writing_index`、`about_page`、`not_found`；
  - `sitemap` 支持 lastmod；新增 `llms_txt`；改 `atom`；更新 copy。
- `build.py`：
  - 加载 now；校验文章 `project`；改双语规则；
  - 新增 `/projects/` 中英路由和 `llms.txt`；
  - 404 用中文 ctx；把 (path, lastmod) 交给 sitemap。
- `sitegen/checks.py`：`placeholders` 增加“正在做”过期提示。
- `static/styles.css`：
  - 新增：产品行、正在做、目录、作者卡和相关产品卡、类型标签、页脚分行；
  - 删除求职相关样式；
  - 补首屏第 4 个子元素的动画延迟。
- `static/site.js`、`static/boot.js`：预计不用改，预取对新链接自动生效。如果改了，同步 `tests/test_front_scripts.py`。
- `tools/make_images.py`、`static/og-image.png`：见第 8 节。
- `docs/seo-pages.json`、`docs/SEO.md`：加入 `/projects/`、`/en/projects/`，更新首页和关于页标题。
- `README.md`：更新改内容对照表、项目字段（`app`）、文章字段、双语规则、构建产物（llms.txt）、上线前待补。
- 不改：`vercel.json`、`static/_headers`、`deploy/`、`tools/monitor.py`。

## 11. 测试

需要修改的现有测试（`tests/test_sitegen.py`）：

- `test_build_outputs_pages_and_skips_drafts`：
  - 改成断言新标题、首屏文案、产品顺序、`/projects/` 存在、关于页新标题；
  - 删掉对“经历与联系”“经历与求职方向”的断言。
- `test_project_navigation_links_open_in_new_tabs`，改为断言：
  - 页眉没有外链；
  - 页脚有在线产品链接，带 `target="_blank" rel="noopener"`；
  - 推广链接只出现在页脚，且带 `rel="sponsored noopener"`。
- `test_about_page_puts_job_and_contact_in_side_column`：改为侧栏只有联系；正文在侧栏之前；页面不含求职文字。
- Person 相关的三个测试：`test_built_person_schema_and_page_descriptions`、`test_person_schema_omits_unfilled_public_fields`、`test_person_schema_cannot_close_script_element`。
  - 从 `@graph` 里取 Person；
  - 各页 Person 完全一致；
  - 每页仍只有一个 JSON-LD 块；
  - 转义覆盖整个 graph。
- `test_site_rejects_unsafe_project_links`：改为测 `sponsored_links` 和 `projects.json` 的 `app.href`；`_write_site_config` 同步字段。

新增测试：

- 只有中文的文章：
  - 能正常构建，页面没有 hreflang；
  - 英文语言切换指向 `/en/writing/`，英文没有文章时指向 `/en/`。
- 文章字段校验：`type` 缺失或非法、`project` 不存在、`updated` 早于 `date`，都会让构建失败。
- now.json 的校验；`updated` 超过 60 天时出现待补提示。
- 产品行：
  - 页面里没有嵌套的 `<a>`；
  - 有 `app` 的行有次入口；
  - `none` 是静态行；
  - `/projects/` 按状态分成两组。
- JSON-LD：
  - 文章页有 BlogPosting，含日期，author 指向 `#person`；
  - 文章页和产品页有 BreadcrumbList；
  - WebSite 只出现在首页；
  - SoftwareApplication 只出现在 live 且有 app 的产品页。
- 只有文章页是 `og:type=article`。
- sitemap：文章页和产品页带 ISO 日期的 lastmod；404 不在 sitemap 里。
- llms.txt：文件存在；包含所有公开产品页和文章的地址；不含草稿 slug。
- 根目录 404：`lang="zh-CN"`，带 noindex。
- 构建产物里没有求职文字（第 8 节的保留项除外）。
- 体积：首页 HTML 小于 16 KB，`styles.css` 小于 30 KB。

## 12. 分批实施

新增的视觉组件先做一个给用户看，确认后再铺开；以前有过整套视觉改动被用户整体撤回的情况。每批单独提交，可以单独回退；每批结束时写验收记录并更新 PROJECT_STATUS。

| 批次 | 内容 | 检查点 |
| --- | --- | --- |
| 0 基线 | 见表后说明 | — |
| 1 定稿 | 用户确认第 13 节的文案和取值；改 `DESIGN.md` | 用户确认 |
| 2 骨架 | 见表后说明 | 检查点 A、B |
| 3 文章 | 新字段；文章页的摘要、目录、作者卡、相关产品、上下篇；产品页的过程记录；文章列表的类型标签；双语规则 | 检查点 C |
| 4 SEO/GEO | JSON-LD graph、文章 og、lastmod、llms.txt、seo 清单。基本不改外观，可与第 3 批并行 | — |
| 5 内容 | dashboards、character 的中英介绍页（等用户提供事实）；重新生成 og-image；用户撰写的“思考”文章 | 用户确认 |

**第 0 批（基线）**

1. GitHub `loonslo/personal-site` 的 main 应已包含 10-08 的发布提交 `d782acd`。本地 `D:\workspace\personal-site` 相对父仓库还有一批已修改和未跟踪的文件，其中 `tools/monitor.py`、`deploy/`、`docs/DUAL_DOMAIN_*` 等不在 10-08 的发布清单里。
2. 先 fetch 远程并逐个文件比对，然后从远程 main 开分支，不要把这些改动混进改版提交。
3. 10-08 那次发布按用户指令跳过了测试，所以先在基线上跑一遍全量测试，记下原本就存在的失败。

**第 2 批（骨架）**

1. 先做产品行组件和首页“正在做”区块，然后到**检查点 A**：把 375、768、1280 三种宽度在浅色和深色下的截图给用户确认。
2. A 通过后，再做导航、页脚与推广链接、`/projects/`、关于页、求职信息清理、404 修复，然后到**检查点 B**。

## 13. 待用户确认（执行人不得自行定稿）

1. 首页 `headline`、`intro`、`identity`，以及首页和关于页的 title、description（中英）。
2. “正在做”三条是否属实。
3. 产品顺序；`app` 的标签；SoftwareApplication 的分类取值。
4. 页脚推广链接旁是否显示“推广”二字（默认显示）。
5. 关于页正文。
6. 文章类型的名称（教程 / 实践 / 思考）。
7. 手机端页眉是否改成单行。
8. dashboards、character 介绍页的事实材料。

## 14. 验收（每批都做）

本地检查：

- `py -3 -m pytest` 全部通过，记录用例数。
- `py -3 build.py check` 站内链接错误为 0，逐条看待补项；再跑 `py -3 build.py --drafts` 检查一次链接。
- 有禁用词清单时，设置 `SITE_BLOCKLIST` 再扫描。
- `docs/seo-pages.json` 清单测试通过。每个公开页都要满足：canonical 指向自己、hreflang 成对、description 非空、JSON-LD 可解析且只有一块。
- 375 / 768 / 1280 三种宽度 × 浅色 / 深色：没有横向溢出（scrollWidth 不超过视口宽度）；截图存到 `docs/acceptance/<日期>-redesign/`。
- 键盘：Tab 依次经过产品名称和“打开”，焦点可见，回车可用。
- 体积预算达标；首屏请求没有新增，网络记录里没有新的第三方域名。
- 用带生产响应头的本地预览确认 CSP 没有报错。普通 `http.server` 不带响应头，见 README。

发布：

- 同一个提交分别部署到 halfopen.dev 和 baikai.site，流程见 `docs/DUAL_DOMAIN_DEPLOYMENT_2026-10-07.md` 和 `deploy/prepare_domain_release.py`。
- 发布后两个域名都要核对：新页面返回 200；canonical 和 llms.txt 里的地址都是本域；sitemap 能取到。
- 用 Rich Results Test 抽查一篇文章和衡仓产品页；在 Search Console 重新提交 sitemap。

记录：

- 验收记录写明日期、环境、结果和未验证项；按 `AGENTS.md` 的契约更新 `PROJECT_STATUS.md`。

## 15. 不在本次范围

- 站内搜索；
- 标签页、分类页：文章少时是内容很薄的页面，某一类型超过 5 篇再考虑；
- 评论；
- 每篇文章单独的分享图；
- 分页：超过 20 篇再做；
- 直接发布 Obsidian 笔记；
- 产品实时在线状态：需要放宽 CSP 的 `connect-src`；
- 访问统计。

## 16. 风险

| 风险 | 应对 |
| --- | --- |
| 标题和描述变化，Google 重新评估页面 | 10-03 的 Search Console 基线没有搜索展示，影响小；URL 不变 |
| 页眉去掉子站链接后，老访客少了一个入口 | 页脚有快捷入口，首页产品行有“打开 ↗” |
| 拉伸链接让行内文字不容易选中 | 可以接受；次入口必须 `z-index` 在上，并且能单独聚焦 |
| JSON-LD 改成 graph 后现有测试失效 | Person 节点保持一致，测试同步改；“每页一个块”的约束不放宽 |
| 放开双语后，hreflang 指向不存在的页面 | 新增测试覆盖 |
| 模板里写死域名，导致 baikai.site 指向 halfopen.dev | 地址一律用 `base_url` 生成；发布后两个域名都核对 |
| 本机缺字体，og-image 生成失败 | 记为未完成，不影响其他批次 |


## 2026-10-11 参考站评审补充（未实施）

本次浏览用户提供的 18 个参考地址，14 个取得首页文本，4 个访问失败；核对半開线上首页、文章列表和文章详情结构。详见 [参考评审](BLOG_REFERENCE_REVIEW_2026-10-11.md)。建议压缩首屏、首页只选三项产品、近况后置，并优先补长文目录与继续阅读。新增布局与文案均为建议，未改变第 2 节已确认决定；本次没有改页面代码、运行测试、构建或发布。

## 2026-10-11 参考评审实施记录

上节记录的是当天研究阶段，随后用户授权“根据参考评审文档进行调整”。本地已实施精简导航、去求职与推广移页脚、紧凑首页、三项精选产品、完整六项目目录、产品介绍、文章类型与摘要、长文目录、相关产品/继续阅读/作者 RSS、单语文章及语言回退。未添加缺乏事实材料的近况区块，未添加搜索、归档或评论服务。

81 项 pytest、公开/草稿站内链接检查、48 组响应式明暗布局与本地交互检查通过；双域静态产物副本核对通过。未发布，生产响应头与线上表现未验收。验收正本见 [本地改版验收](acceptance/2026-10-11-blog-redesign.md)，包含具体范围、证据及未验证项。

## 2026-10-11 简洁优化后续

用户随后强调简洁风格，并要求 UI 优化。首页进一步收成 840px 单列，移除大月、纸纹、挂轴、重复题名、编号和按钮组，明确测试背景、AI 应用与写作主题；首屏提供真实文章入口。完整区块仍为产品在前、文章在后，产品直达与介绍均可独立操作。

最终 81 项 pytest、64 组中英文响应式明暗布局、键盘与导航检查通过，双域静态副本各 22 页通过。未部署。最新设计规则见 DESIGN.md，验收正本为 [简洁优化验收](acceptance/2026-10-11-minimal-ui.md)；先前 48 组记录属于上一轮，不代表最终版复验。

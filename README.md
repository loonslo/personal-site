> 2026-10-07 当前部署：baikai.site / halfopen.dev 相同内容分别部署并开放搜索。迁站策略已撤销；详见 [双域名部署与验收](docs/DUAL_DOMAIN_DEPLOYMENT_2026-10-07.md)。旧记录保留原验收日期。

# 半開 · 个人站

个人产品与开发札记的入口。首页为简洁单列，先用两句话交代目前在做什么与写作主题并给出最新文章入口（个人介绍右侧是竖排小字题句、印章和背后一轮极淡的月），再展示精选产品和文章列表。纯静态，无登录、无后端，可部署在 Cloudflare Pages 或 Vercel。设计规则见 [DESIGN.md](DESIGN.md)。

## 本地预览

```powershell
py -3 build.py --drafts
py -3 -m http.server 8787 --bind 127.0.0.1 --directory dist
```

浏览器打开 <http://127.0.0.1:8787>。`--drafts` 会把 `draft: true` 的文章也构建出来，只用于本地查看。

## 改内容

| 要改什么 | 改哪里 |
| --- | --- |
| 中文站点信息、项目目录、介绍页、经历页与文章 | `content/site.json`、`content/projects.json`、`content/projects/`、`content/about.md`、`content/writing/` |
| 英文站点信息、项目目录、介绍页、经历页与文章译文 | `content/en/site.json`、`content/en/projects.json`、`content/en/projects/`、`content/en/about.md`、`content/en/writing/` |

首页仅展示 `featured: true` 的三项产品：衡仓、投资看板、角色设定卡；完整目录位于 `/projects/`，保留案例和学习仓库。`home_summary` 为首页短说明，`summary` 为完整产品说明。状态和使用边界沿用项目事实，不代表本次已重验产品。

2026-10-29：首页精选产品增加双语真实截图预览；投资看板使用标明用途的文字导览，不冒充界面截图。文章 frontmatter 可用 `series: dev-note` 标记开发小记；首页将其与长文分组，首屏“最近写的”只选长文。页底增加邮箱交流入口。详见本次内容补充验收记录。

中文使用根路径，英文使用 `/en/` 前缀。产品 slug 与顺序保持双语一致；文章可以只写一种语言，相同 slug 视为互译。缺少文章译文时，语言入口回到目标语言文章列表，没有文章则回首页。草稿不进入默认构建。

### 首页、关于页与公开配置

- `headline` 是首页主句；`intro` 支持换行，一行一句，说明目前在做什么与写作主题；首屏文章入口从本语言已构建文章中取最新一篇。`tagline` 在首页个人介绍右侧排成两行竖排小字（中文按“，”、英文按“;”拆成两行，下面落一方印；窄屏只留背后的月），也用于页脚、RSS 副标题和分享图。`identity` 用于关于页、文章作者说明和 Person JSON-LD。**改了中文 `intro` 或 `tagline` 之后要运行 `py -3 tools/make_images.py` 重新生成 `static/og-image.png`**（分享图里印着这两句），再一起提交。`home_title`、`description` 管理首页元数据。
- 页眉仅产品、文章、关于、语言切换。`sponsored_links` 管理页脚推广链接，自动标注推广并添加 `rel="sponsored noopener"`。
- `skills`、邮箱及 `accounts` 复用到公开 Person 信息；未核实的账号链接保持空白，不生成链接或 `sameAs`。
- 页面资源内容哈希、首访动画与预取行为保留。CSP 本地核对需带响应头服务；普通 `http.server` 不会应用 `_headers` 或 `vercel.json`。

### 项目字段

```json
{
  "slug": "knowledge",
  "name": "Knowledge 本地知识库",
  "summary": "一句话说清解决什么问题。",
  "status": "intro",
  "link": {"type": "page"},
  "tags": ["RAG", "FastAPI"]
}
```

- `status`：`building` 建设中 ○ / `intro` 仅介绍 ◐ / `open` 开源 ◕ / `live` 在线 ●
- `link.type`：`page` 站内介绍页（需要 `content/projects/<slug>.md`）/ `external` 外部链接（`href` 必须是 https）/ `none` 暂不开放（只有“建设中”可用）
- `app`：可选的产品直达入口，`{"label": "试用示例（不用注册）", "short_label": "试用示例", "href": "https://..."}`；与站内开发记录形成两个独立链接。`label` 用在项目页和产品列表，`short_label`（可选）用在首页的紧凑行，缺省时显示“打开”。按钮文字写点了会发生什么，不写“打开站点”。
- 带示例的子站（衡仓、角色设定卡、Knowledge）把 `app.href` 直接指向示例入口，并带 `from=portfolio` 和 `lang`（中文页 `zh`，英文页 `en`，子站据此显示同一种界面语言）：子站只对带这个标记的访客显示“半開 的作品 · 返回作品集”窄栏，标记只存在于对方标签页的 sessionStorage，不记录个人信息。入口改动后要同步子站的实际路由。
- `featured`：布尔值，首页最多三项；`home_summary`：首页用途和使用边界的短说明。
- 只有登录后才能用的在线项目，在 `summary` 和 `home_summary` 里写明“需登录”；提供免注册示例的，写“示例不用注册，自己的数据需登录”。名称在卡片、项目页、子站标题里保持一致，英文名可以不同但三处一致。
- 项目页里的截图放在 `static/shots/`（只收 PNG，构建时自动补上宽高与懒加载），Markdown 写成 `![替代文字](/shots/名字.png)`，下一行用 `*斜体*` 写说明，两者在同一段里，页面会把它排成图下小字。截图必须来自真实界面，示例数据要写明是虚构的。

### 介绍页与文章

Markdown 开头写 frontmatter：

```markdown
---
status_note: 可运行原型，个人试点中
updated: 2026-09-24
flow: 第一步 | 第二步 | 第三步
---
```

文章必填 `title`、`date`、`summary`、`type`；`type` 为 `tutorial` / `practice` / `essay`（教程 / 实践 / 随笔）。可选 `project` 指向产品 slug，`updated` 记录实质更新日期且不早于发布日期；未发布加 `draft: true`。不少于三个二级标题时自动生成可折叠目录，短文不显示目录。文章与产品互相展示相关记录，推荐只使用本语言已构建文章。介绍页必须有一节“怎么验证的”。

## 构建与检查

```powershell
py -3 build.py                       # 构建到 dist/，不含草稿
py -3 build.py check                    # 构建并检查站内链接、待补项；默认不联网
py -3 build.py check --check-external   # 显式联网检查外链，仅对可信内容使用
py -3 -m pytest                      # 生成器自身的测试
```

禁用词扫描：准备一个每行一个词的清单（客户名、公司名、系统名等），**放在本仓库以外**，否则清单本身就会把这些名字带进仓库。

```powershell
$env:SITE_BLOCKLIST = "D:\path\to\blocklist.txt"
py -3 build.py check
```

## 部署到 Cloudflare Pages

1. 运行 `py -3 build.py check`，确认没有错误，逐条看一遍“待补”。
2. 二选一：
   - 网页：Cloudflare 后台 → Workers & Pages → 创建 Pages 项目 → 上传 `dist` 文件夹。
   - 命令行：`npx wrangler pages deploy dist --project-name <项目名>`。
3. 部署后运行 `npx wrangler pages deployment list --project-name <项目名>`，确认最新一条是 **Production**，不是 Preview。
4. 绑定域名后，把 `content/site.json` 的 `base_url` 改成正式地址，重新构建并部署；canonical、分享图和 sitemap 都依赖它。

`static/_headers` 会一起上传，用来设置安全响应头和样式表缓存。

## 部署到 Vercel

`vercel.json` 只在构建时安装 `mistune` 并运行静态站生成器，发布目录是 `dist/`；线上只提供 HTML、CSS、图片等静态文件，不会运行 Python 服务或创建 API 函数。Vercel 的安全响应头和样式表缓存规则也写在 `vercel.json` 中。

```powershell
py -3 build.py check
npx vercel link       # 首次部署时关联或创建 Vercel 项目
npx vercel --prod
```

首次部署后，将 `content/site.json` 的 `base_url` 改为 Vercel 生产域名，再重新部署；canonical、分享图和 sitemap 都依赖它。2026-10-29 已实测 `main` 推送触发 Vercel Production 自动部署，正式域为 `halfopen.dev`；CLI 仍可查询部署状态，正常发布不需重复手动上传。

### 防篡改发布

- 生产发布只使用经过审阅的提交；避免从来源不明的分支或包含未审阅改动的工作区直接运行 `npx vercel --prod`。
- 在 Git 托管平台保护生产分支，要求审阅后才能合并；在 Vercel 开启多因素认证，并限制可创建生产部署的账号。
- 如改用 Vercel Git 集成，让生产部署只来自受保护的生产分支。仓库里的安全响应头无法阻止拥有生产部署权限的人替换站点内容。

## 上线前待补

- `site.json` 的小红书链接（需核实个人主页；邮箱已填写）
- 禁用词清单

## 字体与图片

- 页面不加载网络字体：标题用访客设备自带的宋体（苹果设备为 Songti SC，Windows 为华文宋体或宋体），正文用系统黑体。
- 想在所有设备上显示一致的衬线题名，可以改为自托管思源宋体子集：需要下载思源宋体并安装 `fonttools` 做子集化，这一步尚未做。
- `static/og-image.png`、`static/apple-touch-icon.png` 由 `py -3 tools/make_images.py` 生成。分享图里的中文默认用本机华文宋体、微软雅黑渲染成图片，不分发字体文件；也可以用 `--serif`、`--sans` 换成思源字体重新生成。

## 依赖

- Python 3.12 及以上，`mistune` 3.3.4（Vercel 构建使用带 SHA-256 校验的 `requirements.lock`）
- 测试：`pytest`；生成图片：`pillow`

## 2026-10-03 SEO 第一批

任务：修复公开页抓取、页面元数据和路由状态，不扩大业务资料公开范围。

经历页摘要改为职业能力与项目入口；404 HTML 输出 noindex，移除 canonical；保留此前未发布的六项个人项目及衡仓新文案。

实际验证：41 项 pytest 通过；隔离目录默认构建 11 个 HTML（10 个公开页与 404），站内链接错误 0；10 个公开页 SEO 元数据和双向 hreflang 校验通过。

验收正本：`docs/acceptance/2026-10-03-seo-phase1.md`；路由契约：`docs/SEO.md` 与 `docs/seo-pages.json`。本批本地实现完成，生产发布与线上验收仍待执行。

## 2026-10-03 第一批本地提交

第一批已按用户要求提交为 `9d0ee7a`。仅提交本批明确文件或文件内 SEO 改动；此前其他未提交修改继续保留。上文“未提交”指第一批实现时的验收快照，本节更新其提交状态。本次没有 push 或生产部署，线上和站长数据尚未复验。

## 2026-10-03 SEO 第二批内容

第二批 SEO-06：新增 RAG 混合检索、测试转 AI 开发两篇文章及同 slug 英文译文，共 4 篇；原 UI 测试文章仍为草稿。更新双语 Knowledge 案例的许可与下载边界，补齐文章入口。41 项 pytest 通过，隔离构建 17 个 HTML（16 个公开页与 404）、站内链接错误 0，16 页元数据/双向 hreflang 校验通过；两语言代码示例实际执行及空输入/重复项检查通过，4 篇文章 375px 排版核对正常。

验收正本：`docs/acceptance/2026-10-03-seo-phase2.md`；任务本地实现完成，第二批尚未提交、推送或部署。

## 2026-10-03 SEO 站长与发布准备

已整理本项目 sitemap、URL Inspection 样本、最小事件边界与 4/8 周复盘口径，见 `docs/SEO_RELEASE_CHECKLIST.md`。实际 Search Console 会话/数据不可读，本次未验证资源、写 DNS、提交 sitemap 或接入统计。

## 2026-10-03 SEO 发布候选检查

隔离候选构建/41 pytest 通过；9 文件精确源差异可应用到 HEAD，保留未提交项目/品牌改动。 验收：`docs/SEO_RELEASE_CANDIDATE_ACCEPTANCE.md`；未提交、推送或发布，真实暂存区为空。

## 2026-10-03 SEO 正式发布

本批提交 4c8100b，五站已发布，公开路由与权限边界通过。验收正本 `docs/SEO_PRODUCTION_ACCEPTANCE_2026-10-03.md`；站长处理/收录和后续流量复盘单独跟进，不等于已增长。

### 2026-10-03 站长实测

本站 sitemap Couldn't fetch，发现 0 页；代表页 Google 实时抓取可用但尚未索引。域名总搜索基线无展示，无法拆分站点流量；详见 `docs/SEO_PRODUCTION_ACCEPTANCE_2026-10-03.md` 最新追加。

### 2026-10-03 完整性补查

本站公开页补查 H1/description/HTML 语言/MIME/链接与已有安全头配置通过；新证据及未决事项见 `docs/SEO_PRODUCTION_ACCEPTANCE_2026-10-03.md` 最新追加。

Personal-site-only remote fast-forward push completed: 2c07885 (main); parent workspace history excluded.

## 2026-10-03 页眉与六项目列表发布

页眉的衡仓与投资看板入口、双语首页六项目列表已发布到 https://baikai.site。页眉按内容宽度换行，品牌保持单行；修复了 320px 英文项目状态行与流程条溢出。双语衡仓案例补上核实过的 Android 开源仓库与 Web 入口，并区分历史测试数字与本次公开入口复核。

41 项 pytest、16 个公开页元数据及链接检查、88 组本地明暗模式／宽度布局检查通过。生产部署 `dpl_56SbT7SWEDe9VRGYiqjEtWnnPgHY` 为 READY，正式 16 页及 CSS、robots、sitemap 与已验收产物一致。验收正本：`docs/acceptance/2026-10-03-header-project-release.md`。小红书完整主页链接及脱敏企业案例仍等待用户提供；本批没有 Git 提交或推送。

## 2026-10-03 halfopen.dev 域名迁移


主站已迁移到 halfopen.dev；四个子站导航均使用新域名，旧根域名及旧 www HTTPS 301 保留路径与查询，新 www 308 至新根。Vercel 最终 Production/READY dpl_HWA7wkVF17Mz2ZHiHX8vnwxJv6mv；16 公开页与 self-canonical 通过。Google 主站及旧 www 地址变更已确认，sitemap 报表 Success，发现 16 页；后续页面收录待 Google。 详见 [迁移记录](docs/DOMAIN_MIGRATION_2026-10-03.md)。


## 2026-10-03 Vercel 前端迁移验收

2026-10-03 前端统一 Vercel：主站与四个子站正式 HTTPS 页面均由 Vercel 提供，45 公开页及应用入口、旧域名跳转、API 权限/缓存共 171 项线上检查通过。Cloudflare 看板公开域名与 workers.dev/预览入口均关闭，定时发布改为 Vercel；后端留在原 Ubuntu，未改账号数据或模型权限。 实现与检查范围见 [验收正本](docs/VERCEL_FRONTEND_MIGRATION_2026-10-03.md)。

## 2026-10-08 页面切换与缓存

构建时 `styles.css`、`boot.js`、`site.js` 的地址都带 `?v=<内容哈希>`，`vercel.json` 只对带 `?v` 的地址设 `immutable`，页面仍每次校验。入场动画只在会话首访播放，站内翻页用跨页过渡；悬停、触摸或聚焦链接时预取同源页面、预连接各子站。`tests/test_front_scripts.py` 用 Node 执行前端脚本，没有 node 时跳过。

验证数字、未验证项和发布注意见 [docs/acceptance/2026-10-08-navigation-performance.md](docs/acceptance/2026-10-08-navigation-performance.md)；本机改动，未提交、未部署。


## 2026-10-11 博客改版（本地）

依据参考评审完成紧凑首页、三项精选产品、完整产品页、简化导航、文章目录与阅读路径，并允许单语文章。实际验收与未验证项见 [改版验收](docs/acceptance/2026-10-11-blog-redesign.md)。历史章节保留原日期，不代表本次已重新部署。

同日依据用户的简洁风格要求进一步压缩装饰、收成单列、明确身份与写作主题，让真实文章入口出现在首屏。最终版见 [简洁优化验收](docs/acceptance/2026-10-11-minimal-ui.md)，尚未发布。

---
project_id: personal-site
updated: 2026-10-29
status: active
overview: 纯静态个人博客与产品导航，记录 AI 应用、软件开发和个人产品的用途及验证过程；支持中英文与单语文章。
progress: 2026-10-29 内容补充与卡片对齐修复已通过93项测试及31页站内链接检查；待本次授权提交推送及部署。 2026-10-15 复核两个域
  version.json 均为 e9d866b，18 项 HTTP 与 12 项 TLS 通过；应用内容已在线，无需重复部署。 历史进展：2026-10-15
  已按用户指令提交（e25c441）、推送并发布两个域名：首页自我介绍整句改成“目前在做 AI 应用相关的开发。”（不提测试背景），个人介绍右侧恢复两行竖排题句、一枚印章和背后一轮淡月，分享图重新生成；92
  项 pytest 通过，23 页站内链接 0 错误，五种宽度、浅深色、中英文截图检查通过，两个域名线上首页、canonical、og-image 与监控脚本核对通过；Safari/Firefox/真机、真人测试和收录观察未验证。2026-10-14
  已按用户指令提交、推送并发布 2026-10-11 的改版与主站到三个子站的交接（提交 9148833），Knowledge 演示上线后当天补上演示入口（提交
  5567bba）：衡仓、角色设定卡、Knowledge 的卡片文案与按钮、带来源和语言参数的深链、名称统一（知识库名称沿用默认值，用户已确认）、项目页真实截图。两个域名生产部署均
  READY；干净检出 91 项 pytest、23 页站内链接 0 错误、GitHub Actions 成功；线上从卡片点进三个子站（中英文、两个域名）和布局检查通过。线上响应头逐项、Safari/Firefox/真机、真人测试、Search
  Console 收录观察和中国大陆可达性未验证。此前部署与产品业务结果为历史验收。
next: 部署并核对正式站新内容与版本；观察 Google 对新标题与新项目页的收录（2～4 周）；补充小红书主页与 SITE_BLOCKLIST；子站访问计数方式待定（用户决定先不做）；中国大陆网络下的可达性仍待测；用真人做
  5 秒与 30 秒测试；baikai.site 是否接入 Git 自动部署待用户决定（目前每次要用命令行再发一次）。
evidence:
- docs/acceptance/2026-10-29-content-expansion.md
- docs/WORKSPACE_RELEASE_2026-10-15.md
- docs/acceptance/2026-10-15-hero-intro-and-couplet.md
- docs/acceptance/2026-10-14-subsite-handoff.md
- docs/RELEASE_CACHE_NAVIGATION_2026-10-08.md
- docs/acceptance/2026-10-11-minimal-ui.md
- docs/acceptance/2026-10-11-blog-redesign.md
- docs/BLOG_REFERENCE_REVIEW_2026-10-11.md
- DESIGN.md
- README.md
- docs/acceptance/2026-09-28-seo-geo.md
- docs/acceptance/2026-09-30-project-status-evidence.md
- docs/acceptance/2026-10-01-bilingual-site.md
- docs/acceptance/2026-10-02-dashboard-nav-entry.md
- docs/acceptance/2026-10-02-project-list-refresh.md
- docs/acceptance/2026-10-03-seo-phase1.md
- docs/SEO.md
- docs/seo-pages.json
- docs/acceptance/2026-10-03-seo-phase2.md
- docs/SEO_RELEASE_CHECKLIST.md
- docs/SEO_RELEASE_CANDIDATE_ACCEPTANCE.md
- docs/SEO_PRODUCTION_ACCEPTANCE_2026-10-03.md
- docs/acceptance/2026-10-03-header-project-release.md
- docs/acceptance/2026-10-03-sitemap-coverage.md
- docs/DOMAIN_MIGRATION_2026-10-03.md
- docs/VERCEL_FRONTEND_MIGRATION_2026-10-03.md
- docs/acceptance/2026-10-05-reliability.md
- docs/DUAL_DOMAIN_DEPLOYMENT_2026-10-07.md
- docs/dual-domain-http-2026-10-07.json
- docs/dual-domain-platform-http-2026-10-07.json
- docs/dual-domain-final-redeploy-2026-10-07.json
- docs/DUAL_DOMAIN_CHANGE_SCOPE_2026-10-07.md
- docs/acceptance/2026-10-08-navigation-performance.md
- docs/acceptance/2026-10-08-navigation-performance/old-switch-60ms.jpg
- docs/acceptance/2026-10-08-navigation-performance/new-switch-60ms.jpg
- docs/acceptance/2026-10-11-navigation-release.md
- docs/REDESIGN_PLAN_2026-10-08.md
---

# 半開个人站 · 项目概览与进度

本页是本项目的概览与进度摘要。更新进度时先核对证据文件及实际验收；任务细节仍以项目原有的 TASKS、ROADMAP 或验收记录为准。只根据有证据的变化修改状态与日期；未验证事项保留“待核实”，不把文件存在或 Git 改动当作完成。

## 2026-09-30 同步格式修订

原摘要维护日期为 2026-09-30。本次统一状态枚举与 evidence 路径格式；摘要维护日期更新为 2026-09-30，原进展文字和其中的验证日期保留。本次未重新运行项目测试或线上验收。 原 evidence 描述已原样搬迁至 docs/acceptance/2026-09-30-project-status-evidence.md，并标明历史来源与未复测边界。

## 2026-10-01 中英文站点本地验收

中文保留根路径，英文首页位于 /en/；新增经历页和 knowledge、alpha-research、finunity 三个项目介绍的英文版本。页眉语言切换保留对应页面路径，缺少译文时回到目标语言首页。默认构建仍隐藏文章草稿；当前草稿没有英文译文。

Windows / Python 3.14 本地语法检查通过。隔离临时目录的公开构建 11 个 HTML 页面、草稿预览 13 个 HTML 页面，离线站内链接错误均为 0。此段记录的是部署前本地验收；后续 Production 部署与线上结果见下节。pytest、浏览器响应式与深色模式、外链联网检查未执行。详见 docs/acceptance/2026-10-01-bilingual-site.md。

## 2026-10-01 双语站点 Production 部署验收

Vercel Production 部署 dpl_AxFoSJwpMhxUhNh2iZ1YAksNJ3D6 已 READY，生产别名为 https://baikai.site。中文首页、经历页及三个项目页与对应的英文 `/en/` 路由共 10 条均返回 HTTP 200；页面语言、canonical、语言切换目标和 hreflang 均核对通过，首页与英文页的 CSP/HSTS 响应头存在。浏览器响应式与深色模式、pytest 和外链联网检查未执行。详细结果见 docs/acceptance/2026-10-01-bilingual-site.md。

## 2026-10-03 页眉与六项目生产发布

本批已发布页眉改名、投资看板导航、六项目列表和双语衡仓案例。英文品牌挤压及 320px 内容溢出已修复，41 pytest 与本地/生产各 88 组浏览器布局检查通过，正式 16 页元数据、安全头、静态产物与 404 边界已复核。详见 docs/acceptance/2026-10-03-header-project-release.md。

此前“页眉及六项目尚未部署、英文挤压未修复”均为历史快照，已由本批生产验收更新。小红书完整主页及企业案例仍等待用户材料，不填猜测信息，也不将历史项目测试数字写成本次复测。


## 2026-10-03 域名迁移


主站已迁移到 halfopen.dev；四个子站导航均使用新域名，旧根域名及旧 www HTTPS 301 保留路径与查询，新 www 308 至新根。Vercel 最终 Production/READY dpl_HWA7wkVF17Mz2ZHiHX8vnwxJv6mv；16 公开页与 self-canonical 通过。Google 主站及旧 www 地址变更已确认，sitemap 报表 Success，发现 16 页；后续页面收录待 Google。 详见 docs/DOMAIN_MIGRATION_2026-10-03.md。

## 2026-10-05 可靠性改造

本机改动，未提交、未部署。新增线上监控、版本记录与 CI。本机验证与未验证项见 [验收记录](docs/acceptance/2026-10-05-reliability.md)。

## 2026-10-08 页面切换与缓存

本机改动，未提交、未部署。针对“点导航要等、每页都重播动画”：脚本地址带内容哈希且仅带版本号时 immutable、入场动画仅首访播放、跨页过渡、悬停预取同源页面并预连接各子站。本机验证、未验证项和发布注意见 [docs/acceptance/2026-10-08-navigation-performance.md](docs/acceptance/2026-10-08-navigation-performance.md)；线上响应头、Safari/Firefox 与国内网络均未验证。

## 2026-10-08 本次代码发布结果

本批从最新远程分支的独立发布副本提交与推送，两个域名生产部署均返回 READY。代码提交 d782acd5d5af4e13c4a374beb550dfd3d4292abb。按用户指令跳过测试与线上页面/缓存头验收；原工作树及父工作区的其他改动保留。详见 docs/RELEASE_CACHE_NAVIGATION_2026-10-08.md。

## 2026-10-08 改版方案（未实施）

用户确认站点改为“个人介绍与文章 + 个人产品导航”：求职信息先拿掉，推广链接移到页脚，文章不再强制中英双语，首页先放产品再放文章。完整方案、分批计划、视觉检查点和验收标准见 docs/REDESIGN_PLAN_2026-10-08.md，由其他执行人实施。本次只核对了源码与线上页面并写出方案，没有改代码，也没有运行测试或构建；方案里的首页文案、“正在做”条目和产品顺序都是草稿，须用户确认。


## 2026-10-11 参考博客研究

已完成参考博客内容结构研究，实看本站首页与文章列表截图、文章详情结构及四个参考站桌面截图。记录见 docs/BLOG_REFERENCE_REVIEW_2026-10-11.md；新增建议尚未定稿或实施。没有修改页面代码、运行测试/构建、部署或进行移动端与深色模式验收。项目摘要在本项目内自检，不调用跨项目同步工具。

## 2026-10-11 参考评审实施与本地验收

上一节为当天研究阶段记录。用户随后要求“根据参考评审文档进行调整”，本地已完成首页、完整产品页和文章阅读路径改版，保留纸色、宋体、朱砂与月相风格，落实 10-08 四项已确认决定。

Windows / Python 3.14 实际验收：81 项 pytest 通过；公开构建 23 个 HTML（22 个公开页面和 404），草稿构建 24 个 HTML，两者站内链接错误均为 0；48 组 Chromium 响应式明暗布局及键盘/目录/产品导航交互通过；halfopen.dev 和 baikai.site 静态副本各 22 页 canonical/hreflang 与 sitemap 核对通过。首页 9,715 bytes、CSS 27,968 bytes 满足预算。

验收正本为 docs/acceptance/2026-10-11-blog-redesign.md。新版未提交、推送或部署；未验收生产响应头、线上表现、真机及其他浏览器，未提供禁用词清单，未联网检查外链。项目和产品历史数字不算本次业务复测。既有页面切换发布文档仍写“待发布”，本轮没有据此推断其发布成功。

只维护本项目进度；交付前在本项目内自检 frontmatter 必填字段、日期、状态与证据路径，不调用跨项目同步工具。

## 2026-10-11 简洁风格优化

用户进一步要求突出简洁、优化 UI。参考 frontend-design skill，首页改为单列，移除大月、纸纹、挂轴、重复题名、编号与按钮组；两句说明作者背景及写作主题，最新文章入口出现在首屏。首页产品名称通向介绍，独立“打开”链接保留，说明保留使用边界。

最终 Windows / Python 3.14 验收：81 项 pytest 通过；23 个 HTML 站内链接错误为 0；64 组 Chromium 中英响应式明暗布局、可见键盘焦点、产品回车导航及文章点击通过；双域静态副本各 22 页 canonical/hreflang 通过。首页 7,772 bytes、CSS 25,670 bytes，未实测加载速度。上一轮 48 组记录保留历史日期，不当作本轮复验。

证据为 docs/acceptance/2026-10-11-minimal-ui.md。新版未部署；未验证生产头、线上表现、真机或其他浏览器，未联网检查外链与敏感禁用词。项目摘要仍只在本项目自检。

## 2026-10-14 主站到三个子站的交接

依据日常库《三站首屏引导与交互调整方案》第五节，本机完成：衡仓与角色设定卡的卡片一句话用途、首页短按钮“试用示例”、项目页按钮“试用示例（不用注册）”“试用五步引导（不用注册）”，以及带 `from=portfolio` 与 `lang` 的深链（子站据此显示“半開 的作品”窄栏和对应界面语言）；名称统一（角色设定卡英文 Character Atelier，知识库“Knowledge 本地知识库”/“Knowledge”，名称待用户确认）；Knowledge 仍为“仅介绍”，项目页与 RAG 文章不再链到演示站；衡仓与角色设定卡项目页加真实界面截图、“不注册先试”和“电脑版”说明，并更正了几处旧说法（进取/balanced、Web 端没有账户页）。新增 `app.short_label` 与图片尺寸渲染，修了项目页状态行在手机上被拆成竖排的问题。（该批已于 2026-10-14 发布，见下节；本机 `dist/` 没有重建。）

验证（2026-10-14，Windows、Chrome，本机）：91 项 pytest 通过（改前 81 项）；构建 23 个 HTML，站内链接含图片错误为 0；baikai.site 变体副本上深链改写正确；9 个页面在浅色 1280/768/390 与深色 1280/390 下无横向溢出、无页面错误。未验证：线上一切（卡片承诺依赖子站示例先发布）、真人测试、Safari/Firefox/真机、外链与禁用词扫描。发布顺序、与方案的差异和配套的子站改动见 [docs/acceptance/2026-10-14-subsite-handoff.md](docs/acceptance/2026-10-14-subsite-handoff.md)。

只维护本项目进度；交付前在本项目内自检 frontmatter 必填字段、日期、状态与证据路径，不调用跨项目同步工具。

## 2026-10-14 改版与三个子站交接发布

用户明确要求提交、推送、部署。2026-10-11 的改版与本次交接以提交 `9148833` 发布，Knowledge 演示上线后当天以提交 `5567bba` 补上演示入口；两个域名生产部署均 READY，线上核对通过。发布顺序、两次发布的部署编号、线上核对、没有验证的事项与回滚见 [docs/acceptance/2026-10-14-subsite-handoff.md](docs/acceptance/2026-10-14-subsite-handoff.md)。

2026-10-15：把公开仓库里的本页同步为完整版——概览改为改版后的表述，补回 2026-10-11 的几节和对应证据。这只是文字同步，没有新的验收，上面各节的验证日期与未验证边界不变。

只维护本项目进度；交付前在本项目内自检 frontmatter 必填字段、日期、状态与证据路径，不调用跨项目同步工具。

## 2026-10-15 首页自我介绍与右侧装饰

用户要求首页自我介绍不再提测试，整句换成“目前在做 AI 应用相关的开发。”，并把旧版右侧的题句、印章和淡月带回来。提交 `e25c441` 已推送，并部署到 halfopen.dev（Git 集成）和 baikai.site（命令行，同一提交；这次起 `/version.json` 能看到提交）。验收细节与没验证的事项见 [docs/acceptance/2026-10-15-hero-intro-and-couplet.md](docs/acceptance/2026-10-15-hero-intro-and-couplet.md)。关于页的 `identity` 仍写“做过软件测试”，未改。

同日起本项目是独立的 Git 仓库（origin 为公开仓库），直接在本目录提交和推送，不再从别的目录叠加。

只维护本项目进度；交付前在本项目内自检 frontmatter 必填字段、日期、状态与证据路径，不调用跨项目同步工具。

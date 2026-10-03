---
project_id: personal-site
updated: 2026-10-03
status: active
overview: 纯静态中英文个人作品与职业经历站，展示求职方向、代表项目和验证过程。
progress: 首页与经历页已按最新职业定位修订；个人项目收敛为 knowledge、WorldQuant、langchain-learning、FinUnity Web + Server 四项，并按此顺序展示。FinUnity 使用站内介绍页，标明历史验证结果和当前未核实边界。已完成 URL 输入校验、外链 SSRF 防护、移除内联可执行脚本、配置 CSP/HSTS 等安全响应头，并锁定带哈希校验的依赖。上一版已部署到 baikai.site，线上验证返回 200 且安全响应头生效。2026-09-28 本地完成内容去重与首页、经历页搜索摘要分工，补充具体技术栈及带历史边界的检索和测试记录；全站加入 Person JSON-LD，保持原 CSP。随后按用户新方向，将首页首屏改为职业转向叙事与 AI Agent、自动化工作流关注点，具体技术栈移到后面的验证摘要，正文支持分行。34 项测试、站内链接和三种宽度的浏览器预览通过，未发现 CSP 报错；本次优化尚未发布。安全修复已本地提交，Git push 等待配置 remote。同日随后按用户反馈复查全站文案：首页“经历与联系”区块的简介文案（about_brief）此前直接暴露知识服务项目的 Hit@5 统计和 RAG/LangGraph 实现细节，与首页“3 秒说清是谁”的定位不符，已改写为不含具体数字的品牌向简介句；经历页右侧竖排诗句挂轴与该页职责/求职/验证记录的语境不合，按用户选择移除展示，代码只注释未删除、CSS 未改动，经历页改为单栏版式，桌面与 375px 移动宽度均人工核对无遗留空白。2026-09-29 在全站右上角导航增加“AI会员”外链，沿用外链新标签页打开方式，并收紧手机导航间距以容纳新入口；生产部署已完成，baikai.site 返回 HTTP 200，页面含目标外链。随后按反馈将标签改为“特价AI会员”并再次部署，正式站验证返回 HTTP 200。同日按反馈处理经历页移除挂轴后桌面端右侧大片空白：宽度 ≥1024px 时改为正文在左、“正在找工作”与“联系与账号”作为右侧栏并随滚动吸附，窄屏保持原来的单列顺序；同步在 DESIGN.md 记录版式。已本地验证并由用户提交（861c6e9），尚未部署。同日随后按用户要求删除首页底部“经历与联系”区块，并清理只服务于它的样式、必填字段 about_brief 及 README 说明；进入经历页仍有导航“经历”和首屏“经历与联系”链接，首页在 1440px 宽下整页高度由 2007px 降到 1688px，本次已提交并部署至 baikai.site；Vercel 部署 dpl_D1bs7fvrx1Hru6bkjcQbLf4iy46t 为 Production/READY，正式首页与经历页均返回 HTTP 200，安全响应头和首页链接已复核。 2026-09-30 已在全站右上角导航加入角色设定卡、知识库演示与 FinUnity 三个 HTTPS 入口，电脑端并列展示，窄屏导航启用换行；Vercel Production 部署 dpl_TcbBn2TkbSYKmQjxAe7yQPKAi2n8 已 READY，baikai.site 已线上验收。 2026-10-01 已完成中英文静态路由：首页、经历页与三个项目介绍页均提供英文版本，页眉可切换语言；补充 canonical、hreflang 和双语 sitemap。Python 3.14 语法检查与 diff 空白检查通过；临时目录公开构建 11 个页面、草稿预览 13 个页面，离线站内链接问题均为 0。Vercel Production 部署 dpl_AxFoSJwpMhxUhNh2iZ1YAksNJ3D6 已 READY，baikai.site 中英文首页、经历页与三个项目介绍页共 10 条路由均返回 HTTP 200；语言切换、canonical、hreflang 核对通过，首页及英文页 CSP/HSTS 生效。未运行 pytest、未进行浏览器尺寸/深色模式人工检查或外链联网检查。 本次（2026-10-03）SEO 第一批：经历页摘要改为职业能力与项目入口；404 HTML 输出 noindex，移除 canonical；保留此前未发布的六项个人项目及衡仓新文案。 41 项 pytest 通过；隔离目录默认构建 11 个 HTML（10 个公开页与 404），站内链接错误 0；10 个公开页 SEO 元数据和双向 hreflang 校验通过。 本批尚未提交、推送或部署；线上表现未复验。 2026-10-03 发布追加：B/C 精确提交 4c8100b；五站已生产发布，45 公开页及 15 私有/索引边界检查通过。验收范围和发布产物见本项目生产验收，Search Console 提交与实际处理/收录分别记录，尚无排名或业务转化提升结论。 2026-10-03 站长追加：本站 sitemap Couldn't fetch（发现 0 页），代表页实时抓取可用但尚未索引；域名汇总基线 0 展示，无本站独立流量或转化结论。
next: SEO：核对已提交 sitemap 的 Google 处理与代表页索引；以 2026-10-03 为发布日，在 2026-10-31/2026-11-28 复盘实际搜索数据。其他既有项目计划沿用原任务记录，B/C 本批提交/发布项已完成。
evidence:
- DESIGN.md
- README.md
- docs/acceptance/2026-09-28-seo-geo.md
- docs/acceptance/2026-09-30-project-status-evidence.md
- docs/acceptance/2026-10-01-bilingual-site.md
- docs/acceptance/2026-10-03-seo-phase1.md
- docs/SEO.md
- docs/seo-pages.json
- docs/SEO_PRODUCTION_ACCEPTANCE_2026-10-03.md
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

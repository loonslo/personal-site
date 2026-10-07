---
project_id: personal-site
updated: 2026-10-07
status: active
overview: 纯静态中英文个人作品与职业经历站，展示求职方向、代表项目和验证过程。
progress: "双域公开前端已上线，页面与 API 边界通过；本项目构建域名参数和发布说明已更新，Git 持续双发布待完成。"
next: "审阅并发布双域构建配置，完成同版本双项目发布自动化；后续观察 Google 重新抓取与收录。"
evidence:
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
- docs/dual-domain-final-redeploy-2026-10-07.json
- docs/dual-domain-platform-http-2026-10-07.json
- docs/DUAL_DOMAIN_CHANGE_SCOPE_2026-10-07.md
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

> 历史记录：2026-10-07 已撤销域名迁站，当前以 [双域名部署记录](DUAL_DOMAIN_DEPLOYMENT_2026-10-07.md) 为准；以下原日期及验收不作本次复测。

# 2026-10-03 前端统一迁移到 Vercel

正式地址：https://halfopen.dev/；Vercel 项目 `personal-site`，生产 READY 部署 `dpl_HWA7wkVF17Mz2ZHiHX8vnwxJv6mv`。主站原已使用 Vercel，本轮没有重发主站或改变其 UI；核对全部子站入口与 16 公开页。

## 实际验收与边界

2026-10-03，Windows / Python 3.14 / Node 22.22.3：171 项正式 HTTPS 检查通过，包括 45 个公开页面的 GET/HEAD、canonical、robots/sitemap、7 个 noindex 应用壳、未知路由和私有路径 404、旧域名 301 保留路径与查询、同域 API、未登录 401、CSRF 403、源站入口 403 和 API no-store。

角色站 8 项 SEO pytest、Knowledge 42 项隔离 public_tests、看板 37 项 unittest 与 15 项 Node、衡仓 Web build/lint 与 17 项 Node 通过。Knowledge 两项依赖弃用警告保留；首次测试路径被项目门禁拒绝，改用项目指定的新隔离 test-runs 目录后完成。没有读取外部知识资料库、执行真实账号操作、OCR/模型请求、行情刷新、交易或通知。

线上业务 JS/CSS 使用原生产版本的公开文件；本地此前未发布的业务改动保留，没有借托管迁移一起部署。前端路由只允许已声明的页面和 API，静态应用路由只接收 GET/HEAD；没有全路径 SPA 回退或公开本地管理界面。

Vercel 外部 API 代理最长 120 秒，超过此时长的业务需使用后台任务或单独设计直连 API；本轮未实测耗时 OCR/模型操作。官方限制：[Vercel proxied request timeout](https://vercel.com/docs/limits#proxied-request-timeout)。公网完整注册/登录、文件存储与业务验收仍沿用原项目门禁。

本次只迁移托管，公开 URL、canonical 与 sitemap 未新增变更，因此不重复提交 Google 地址变更；此前 Search Console 迁移结果与后续收录状态仍以域名迁移记录为准。

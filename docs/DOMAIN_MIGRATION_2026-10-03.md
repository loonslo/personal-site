> 历史记录：2026-10-07 已撤销域名迁站，当前以 [双域名部署记录](DUAL_DOMAIN_DEPLOYMENT_2026-10-07.md) 为准；以下原日期及验收不作本次复测。

# 2026-10-03 域名迁移验收

主站已迁移到 halfopen.dev；四个子站导航均使用新域名，旧根域名及旧 www HTTPS 301 保留路径与查询，新 www 308 至新根。Vercel 最终 Production/READY dpl_HWA7wkVF17Mz2ZHiHX8vnwxJv6mv；16 公开页与 self-canonical 通过。Google 主站及旧 www 地址变更已确认，sitemap 报表 Success，发现 16 页；后续页面收录待 Google。

41 pytest、构建与站内链接检查已通过；最终新域名五站 45 公开页 200、自身 canonical 和页面无旧域名通过，主站四新子站链接存在。最终部署替代第一阶段 dpl_3r4MX9PG1uJ4QsyyP8MxGoxqwg6v。旧部署保留，未推送整个父 Git 工作区。

下一步：核对 Google 的实际 sitemap 处理与代表页索引；保留旧域名跳转。

域名旧记录是历史资料，本次未全局改写历史验收。Google实际处理状态以最新 Search Console 为准。

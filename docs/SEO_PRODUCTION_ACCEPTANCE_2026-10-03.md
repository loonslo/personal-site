# SEO 生产发布验收

日期：2026-10-03（Asia/Shanghai）。用户在当前会话明确允许五站精确 B/C 改动提交、推送和生产发布，并提供生产 SSH 登录方式与已登录 Search Console 会话；未从历史记录推导授权。代码/内容提交 `4c8100bc83a58bddfda85f1ec05f51fb3de40d81`，保留其他原有未提交工作。

Vercel Production READY，部署 dpl_9gVMLoveTQ3dJKQFtHFHmuN3aRhS，正式别名 https://baikai.site。使用独立候选源码和 HEAD 的 vercel.json/requirements.lock；33 个发布文件，未上传用户未提交的项目列表/品牌改动或凭据。沿用候选 41 pytest 与构建验证。项目仍没有配置 Git remote，因此本地已提交并发布，不能报告 Git push 成功。

正式域名 16 个公开页 GET/HEAD、title/canonical/hreflang/noindex 检查通过；sitemap HTTP 200，精确 URL 集与机器清单一致。五站合计 45 页/90 个请求，五 sitemap 与五未知路径检查；未知页除 Knowledge 精确白名单按 403 拒绝外，其余均 404。另执行 15 项真实生产边界检查，最终全通过。初次边界脚本误把允许匿名读取的 /api/session 当成需要 401 的业务路由，改为实际 /api/characters 校验；默认 Python UA 对三个看板负例曾得到 403，用与公开页同一验收 UA 复核并以 curl HEAD 交叉核对实际为 404，没有改变任何服务器/WAF 权限。

上述是上线/技术验收。五份 sitemap 已由现有域名资源逐项提交；Google 的读取与索引结果在后续站长记录单独更新，不将提交成功、实时抓取成功视为已收录或搜索流量提升。发布日 T=2026-10-03，T+28/T+56 为 2026-10-31/2026-11-28；不创建自动提醒。事件仅定义，尚未接入统计 SDK/真实业务转化数据；目标国家尚未指定。

回滚保留原发布产物与镜像。角色/Knowledge 可用原 Compose 和原环境重建原版本（不加 SEO image override）；FinUnity 恢复备份的 Web override 并重建 Web；看板可恢复上述前一 Worker version；个人站可在 Vercel 将此前 Production 版本重新提升。回滚未实际执行，不宣称做过恢复演练。

## 2026-10-03 10:43 Search Console 实测追加

复用现有 sc-domain:baikai.site 资源，未新增验证或修改 DNS。本站 sitemap `https://baikai.site/sitemap.xml` 于 2026-10-03 提交；最新状态 **Couldn't fetch**，发现 0 页，表格最后读取日期 未显示。Google 仍显示无法抓取；公网 XML GET/HEAD 为 200、内容有效，代表 HTML 页的 Google 实时抓取成功。原因未确认，不把该状态改写成成功，不修改安全保护或凭空调整 DNS。

代表页 `https://baikai.site/writing/rag-hybrid-search/`：Google 索引状态 **URL is unknown to Google**；实时测试 **URL is available to Google**，时间 2026-10-03 10:19 Asia/Shanghai。尚未索引，不能报告已收录。用户 canonical 已在公开 HTTP 验收中核对；本轮没有展开保存该页的 Google canonical，不能冒充已核对 Google 选择。

搜索基线为整个域名资源，Search type Web，页面选择 3 months，但图表及日期对话框实际可用范围为 2026-09-27～2026-09-29；页面显示 last update 14.5 hours ago。汇总 clicks 0、impressions 0、CTR 0%、average position 0，查询表和页面表均 No data。无展示时平均排名/CTR 没有有效样本；不能将汇总零值拆成本站已独立测量的零值，也不据此判断新发布效果。目标国家、品牌/非品牌样本及业务转化均未测量。

五站合计三份 sitemap Success（角色 6、Knowledge 6、看板 5），个人站/FinUnity 两份 Couldn't fetch；五个代表页实时抓取均可用，实际均未索引。本批不创建提醒，不反复点击提交或把实时测试当作收录；2026-10-31/2026-11-28 复盘必须以届时真实数据为准。

## 2026-10-03 后续完整性补查

本站 16 个公开页补查单个非空 H1、单个非空 description、HTML 语言、HTML MIME、无额外跳转和普通导航链接，全通过。五站合计 45 页。最初补查脚本错误地对每个提供商统一要求五种安全头；按实际源配置重核：个人/角色/FinUnity 已有五头仍存在，Knowledge 原线上 550695c 仅定义 CSP/nosniff，两者保留；看板原 wrangler/资源构建未定义这组头，不能把其缺失当成 SEO 回归。没有改安全策略，原响应头缺项清单保留为观察记录，不冒充所有站原本都有五种头。辅助脚本首次用 Windows 默认编码读取清单失败，显式 UTF-8 后执行；随后一个机器人文件请求发生 TLS EOF，中止后做有界重试，最终获取四个响应，未关闭证书验证。

当前配置已出现 personal-site remote，核对远端 main 为 1338e67。在独立克隆中只从已提交 e193d31 的 personal-site 子树导出 50 个项目文件，18 个变化文件按精确清单提交，41 pytest 和 build.py check 通过，整个导出树与已提交子树规范化字节一致；普通快进推送到 https://github.com/loonslo/personal-site.git main，提交 2c0788520204003df57e9bdc3b628dc4a1c5b6db，远端 SHA 再读一致。没有推送父工作区历史/笔记/密钥，未覆盖其他本地未提交改动；上文无 remote 是当时快照，本节更新为已推送。

Google 首页 https://baikai.site/ 已 indexed，最后抓取 2026-10-02 23:55:11，用户 canonical 为自身，Google 为 Inspected URL。当前版本 10:59 实时测试 available，实际 HTML 元数据及手机渲染首屏已查看。既有首页收录不能当作本批新文章已收录或流量增长。10:19 的 RAG 文章缓存测试补展开：抓取允许/获取成功/允许索引通过，用户 canonical 自身，Google canonical Only determined after indexing；Google 获取的 HTML 与手机首屏实际查看，文章仍未索引。

按 Google 官方 sitemap 排查流程直接测试 XML：10:54:39 sitemap.xml Crawl allowed Yes、Page fetch Successful。公网 Googlebot-UA robots/XML 200、正确 MIME、16 URL；域名人工处置报告 No issues detected。sitemap 表仍 Couldn't fetch，当前原因不能归为文件不可访问，也不能宣称 sitemap 已读取成功。未反复提交；后续以正常重试后的报告为准。

## 2026-10-03 用户截图后的 sitemap 诊断

用户截图显示个人站与 FinUnity 的 sitemap 为 Unknown／Couldn't fetch，发现页数 0，最后读取日期为空；Knowledge 与角色站为 Success，各发现 6 页。截图是用户提供的状态证据，本轮没有重新读取登录后的 Search Console 报表。

本轮在 Windows／Python 3.14 对 `https://baikai.site/sitemap.xml`、`https://finunity.baikai.site/sitemap.xml` 及各自 robots.txt 执行匿名 GET／HEAD；普通浏览器 UA 与 Googlebot UA 两组共 16 个请求全部 HTTP 200，无 URL 跳转。两个 sitemap MIME 分别为 application/xml、text/xml，均能解析为标准 sitemap urlset，个人站 16 条、FinUnity 12 条 URL；无 X-Robots-Tag 或挑战响应。robots 允许根路径并声明正确的 sitemap 地址。保持 TLS 证书验证，没有修改服务器、DNS、安全策略或站点代码，没有重提交 sitemap。

普通网络请求使用 Googlebot UA 不等于来自真实 Google 抓取服务器，不能排除来源 IP、区域、瞬时网络或 Google 调度相关差异。本轮没有复测 Google XML 实时抓取；上文 10:54:39 的个人站 XML 实时测试成功仍是当时的验收记录，FinUnity 代表 HTML 页可用也不能当作 XML 已实测成功。

结论：目前未复现 XML 格式或公开可达性故障，根因尚未确认；不能仅凭截图判断为 Google 延迟，也不能报告 sitemap 已成功处理。下一步打开失败行详细信息，用报告中的完整 XML 地址执行 URL Inspection → Test live URL，关注 Crawl allowed = Yes 与 Page fetch = Successful。若实时抓取成功，观察 Google 后续重试；若失败，依据具体错误排查。Google 官方说明抓取失败后会重试数日，持续失败则停止，届时修复已确认问题后再提交，不进行反复删除重加。

依据：[Google Sitemaps report](https://support.google.com/webmasters/answer/7451001?hl=en)。HTTP 正本为 `docs/acceptance/2026-10-03-sitemap-fetch-diagnosis/http-checks.json`。本轮只检查截图中公开域名，未访问 FinUnity 本地项目或修改其状态文件；未执行业务测试，也未以诊断替代收录验收。

## 2026-10-03 XML 完整性核对追加

用户随后明确要求检查两个项目 XML、缺失则补充。本轮对个人站实际默认构建 HTML、机器清单、本地与线上 XML 做精确集合比较，16 URL 一致，无缺失；16 页 GET／HEAD、canonical、索引及同域链接核对通过，2 项相关 pytest 通过。没有需要补写的必需字段或 URL，未更改或重发布 XML；详细验收见 `docs/acceptance/2026-10-03-sitemap-coverage.md`。按本次跨项目检查授权，衡仓 Web 自身也保存了独立验收及状态更新；未访问 Server 或 Android 本地项目。

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

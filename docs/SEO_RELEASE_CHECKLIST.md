# SEO 发布与测量清单

日期：2026-10-03。站点 https://baikai.site/，本地公开清单 16 页；来源 docs/seo-pages.json。A/B/C 已提交并完成本批生产发布；相关技术验收通过，搜索效果尚未形成。最新生产与站长实测见 docs/SEO_PRODUCTION_ACCEPTANCE_2026-10-03.md。

## 发布验收

- 按当前授权提交本批精确文件/差异；检查不得把此前其他未提交工作一起推送。需对待发布版本独立构建，保存发布版本和回滚记录。
- 对外发布需单独明确授权，沿用项目现有提供商/服务与有限路由，不能由 SEO 任务自行扩大部署范围。
- 发布后匿名 GET/HEAD 检查 docs/seo-pages.json 的全部公开路径、必要资产、robots/sitemap：标题/正文、自引用 canonical、真实双语配对、MIME、安全头与预期状态。
- 检查未知 URL/缺资产、应用 noindex 和既有权限边界；Knowledge 未登记路径继续 403、未批准 readiness/检索继续 503，其他站按各自契约 404。不为验证 SEO 调用真实模型/账户数据/行情刷新。
- 保留 CDN/正式入口与本地结果差异，不能仅用 build 或本地代理成功代替上线验收。

## Search Console

准备阶段只读会话仅显示介绍/登录入口；用户随后打开已登录会话，本批已复用现有 baikai.site 域名资源、逐项提交五份 sitemap 并实测代表页。无需新增资源或 DNS 验证；实际处理结果见生产验收追加，不能把提交成功写成 Google 已成功读取。域名资源覆盖子域，按页面过滤本项目；需要单独视图时再决定是否新建 URL-prefix。[资源说明](https://support.google.com/webmasters/answer/34592?hl=en)、[DNS 验证](https://support.google.com/webmasters/answer/9008080?hl=en)。

发布后提交 https://baikai.site/sitemap.xml，记录状态、last read 和 discovered pages；本地有效不是 Google 已抓取。以 https://baikai.site/writing/rag-hybrid-search/ 及公开产品/内容首页作为首轮 URL Inspection 样本：分别记录实时抓取/渲染、用户 canonical 与 Google canonical、索引状态和检查日期；实时测试成功不等于已经索引。[Sitemaps](https://support.google.com/webmasters/answer/7451001?hl=en)、[URL Inspection](https://support.google.com/webmasters/answer/9012289?hl=en)。

## 最小事件定义

文章/案例浏览、联系点击；实际咨询另行确认，不由点击推断。

事件实现仍是后续产品任务，本轮没有安装 SDK、接第三方统计或传输用户数据。未来只允许站点枚举、页面类别枚举、语言枚举、事件枚举及汇总日期；不发送完整 URL/查询串、用户身份、检索文本、资料/角色正文、账号、金额、截图、密码或恢复码。成功事件只在后端确认成功后统计；点击不能冒充保存/注册/写入成功。未提供去重依据时只能报事件次数，不冒充唯一用户/首次或回访人数。

## 真实数据复盘

发布日 T=2026-10-03，T+28=2026-10-31、T+56=2026-11-28；不创建自动提醒。同一完整时间范围按本站页面过滤，记录 clicks、impressions、CTR、average position、country/device/query；保留匿名/未展示查询与总量口径差异。缺数据用“未测量/不可用”，不可填成 0；导出后仍核对页面上 ~/- 等不可用值。[Performance](https://support.google.com/webmasters/answer/7576553?hl=en)。

按品牌/非品牌查询分别看：未抓取先修状态/链接/价值；有展示少点击再修查询与标题/摘要匹配；有点击少使用再查能力承诺与入口。小样本不下失败结论，不批量造同义页，不承诺排名或流量。目标地区尚未指定，现有样本不是定制地区 SERP；取得实际 country 分布后再决定主市场。技术合格、收录和业务转化分别记录。

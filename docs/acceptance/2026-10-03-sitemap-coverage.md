# Sitemap XML 完整性核对

日期：2026-10-03（Asia/Shanghai）。环境：Windows／Python 3.14；匿名访问正式域名，开启 TLS 证书验证。用户明确要求检查个人站与衡仓 XML，发现缺失后补充；本文件只记录个人站，衡仓的对应记录保存于其 Web 项目。

## 结果

个人站没有发现缺失 URL 或必需 XML 字段，本次无需修改生成器、XML 或重新发布。

| 对照来源 | 应收录 URL 数 |
| --- | --- |
| 隔离默认构建中实际可索引 HTML 的 canonical | 16 |
| docs/seo-pages.json 的公开页面清单 | 16 |
| 隔离构建 sitemap.xml | 16 |
| https://baikai.site/sitemap.xml | 16 |

四组 URL 精确一致，无遗漏、重复或多余条目。16 个正式页面分别执行 GET／HEAD，共 32 请求全部 HTTP 200，无跳转，HTML MIME 正常，self canonical 正确，无 noindex；页面 hreflang 目标均在 sitemap 中，robots 允许抓取并声明本域 sitemap 地址。公开页内的同域链接也已对照，未发现额外应收录的 HTML 页面。

XML 为 UTF-8、标准 `urlset` 命名空间，每个 `url` 有一个完整 HTTPS `loc`。当前 XML 没有 `lastmod`、`priority`、`changefreq`，这些属于可选字段，不是格式缺失；不填入未经确认的更新时间。HTML 已有 hreflang，不必重复写入 sitemap。

六项目列表中学习仓库、投资看板和角色设定卡指向站外 URL；它们不生成个人站介绍页，不应当作本域漏收录页面。404 带 noindex、未发布的 UI 测试文章为草稿，均正确排除。两个 Atom 订阅地址 `/feed.xml`、`/en/feed.xml` 是订阅文件，不计入公开 HTML 页面清单。

## 检查与边界

- 实际检查脚本对 XML 进行解析、必需元素与 namespace 核对，并比较源码 HTML、机器清单、本地 XML、线上 XML 的精确集合；结果见 `2026-10-03-sitemap-coverage/coverage.json`。
- `py -3.14 -B -m pytest -q tests/test_sitegen.py -k 'public_seo_manifest or not_found_page' --basetemp=<隔离目录>`：2 passed，39 deselected。
- 本次未改运行代码，不执行全量测试或重新部署；既有未提交修改保留。未访问登录后的 Search Console、重提交 sitemap 或验证新增收录。公开 Googlebot UA 请求不是 Google 来源 IP 的真实抓取。
- 初版检查把页面中的 Atom 链接当作漏收录 HTML，明确排除两个订阅文件后重新完整执行，最终无缺失；没有因此修改 sitemap。

协议依据：[Sitemaps XML 必需与可选字段](https://www.sitemaps.org/protocol.html)、[Google sitemap 指南](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)、[语言标注方式](https://developers.google.com/search/docs/specialty/international/localized-versions)。完整 XML 不能直接证明 Search Console 已处理成功，Couldn't fetch 根因仍待 Google 抓取报告或具体错误确认。

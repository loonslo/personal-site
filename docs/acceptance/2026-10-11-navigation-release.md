# 2026-10-11 页面切换与缓存改动发布

## 发布范围

本次推送提交 `889f84de8743abd76439db7918b8d0b6c9d11723` 至 GitHub `main`，并把该提交导出的干净发布目录分别部署到 `personal-site` 与 `personal-site-baikai` Vercel 项目。页面切换与缓存代码已在 2026-10-08 发布；本次再次发布相同代码并完成线上响应检查。

## 验收边界

- 本机未运行 pytest 或预构建，遵照既有决定由 GitHub Actions 和 Vercel 执行构建检查。
- GitHub Actions CI run `38117008444`，对应提交 `889f84de8743abd76439db7918b8d0b6c9d11723`，2026-10-11 完成且结论为 success；该 workflow 运行 pytest 与 `build.py check`。
- 两次 Vercel Production 构建均成功，状态 READY。

## 实际发布结果

| 域名 | Vercel 项目 | Production 部署 | 结果 |
| --- | --- | --- | --- |
| halfopen.dev | `personal-site` | `dpl_G7kVztf98j4XRAY3suRkU8D8cF2k` | READY，已别名至 https://halfopen.dev |
| baikai.site | `personal-site-baikai` | `dpl_Cr5fjMMQMEsWgnsvHRJuT2f1zWB2` | READY，已别名至 https://baikai.site |

2026-10-11 Windows 环境线上核对：两个首页 GET 均为 HTTP 200，canonical 各自指向本域；CSP 与 HSTS 响应头存在。版本化 `/site.js?v=e6ad169729` 在两域均为 HTTP 200，`Cache-Control: public, max-age=31536000, immutable`；不带 `v` 参数的 `/site.js` 均为 HTTP 200 且 `Cache-Control: public, max-age=0, must-revalidate`。

未验证浏览器动画/预取行为、移动端布局、Safari/Firefox 与国内网络表现；这些不影响本次 Vercel 构建、Production 状态及上述 HTTP 响应验收。

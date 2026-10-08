# 2026-10-08 缓存与页面加载优化发布

用户明确要求提交、推送、部署，并要求跳过验证。本批发布两域名对应前端；未运行测试、本地构建验证或线上业务/响应头检查。Vercel 发布所需生产构建由平台执行。发布结果随后按 CLI 实际输出追加。

本批文件：
- DESIGN.md
- build.py
- sitegen/render.py
- static/_headers
- static/boot.js
- static/site.js
- static/styles.css
- tests/test_sitegen.py
- tests/test_front_scripts.py
- vercel.json
- docs/acceptance/2026-10-08-navigation-performance.md

## 实际发布结果

代码提交：`d782acd5d5af4e13c4a374beb550dfd3d4292abb`，已推送。按用户指令未运行测试或上线页面/缓存头验收。

- halfopen.dev：CLI exit=0；READY；dpl_4nRUFKY9cZo3Zy6xqww6wmoyttq9；https://halfopen.dev。
- baikai.site：CLI exit=0；READY；dpl_4zzRRkKgKUPAscQLhkY4TS5zakkJ；https://baikai.site。

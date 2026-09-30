# PROJECT_STATUS 历史证据文字搬迁

整理日期：2026-09-30。

来源：修订前根目录 PROJECT_STATUS.md 的 evidence 列表（摘要维护日期 2026-09-30）。以下文字原样保留，记录涉及 2026-09-27 至 2026-09-30 的历史测试与部署；本次只调整同步格式，没有重新运行测试、访问线上站点或核对部署平台。不能将本页存在视为独立验收证据。已有独立验收文档仍为 docs/acceptance/2026-09-28-seo-geo.md。

## 原 evidence 记录

- 2026-09-30 右上角项目导航入口：三个 HTTPS 地址来自各项目部署记录；39 项 pytest 通过，离线构建检查 6 个页面且站内链接错误 0。检查构建输出使用系统临时目录，未覆盖无生成标记的既有 dist；Vercel Production 部署 dpl_TcbBn2TkbSYKmQjxAe7yQPKAi2n8 已 READY；baikai.site 首页、经历页和 FinUnity 项目页均 HTTP 200，三个新入口及新标签页属性存在，CSP、HSTS、X-Content-Type-Options 均生效（2026-09-30）。
- 首页删除底部“经历与联系”区块：35 项测试通过；构建检查 6 个页面、站内链接错误 0；首页 375/768/1440px 与深色模式无横向溢出。Vercel Production 部署 dpl_D1bs7fvrx1Hru6bkjcQbLf4iy46t 已 READY；baikai.site 首页/经历页 HTTP 200，CSP、HSTS、X-Content-Type-Options 生效，首页已无底部区块但保留经历页入口（2026-09-29）。
- 经历页右侧栏：py -3 -m pytest -q 35 passed（新增侧栏结构用例）；py -3 build.py check：6 个页面，站内链接与禁用词问题 0，待补项与此前一致（2026-09-29）
- 经历页右侧栏本地预览（无头 Chrome，DevTools 协议）：375/768/1023/1024/1279/1280/1440/1920px 与深色模式均无横向溢出，邮箱不越出栏；≥1024px 侧栏为 sticky，滚到页面底部仍停在视口内且不越出文章；应用内浏览器窗格控制台无报错。未使用生产响应头预览，CSP 未复测；未部署（2026-09-29）
- Vercel 生产部署 dpl_8wr5zZsq7NkBWFXNUCg6By4pXMXA：baikai.site 返回 HTTP 200，导航显示“特价AI会员”、未显示旧名称（2026-09-29）
- Vercel 生产部署 dpl_3dRKTRNpfvez2uDRcCPfHBas8V5d：baikai.site 返回 HTTP 200，生成页包含“AI会员”及推广链接（2026-09-29）
- py -3 build.py check --offline：6 个页面、站内链接错误 0；检查生成的首页导航含“AI会员”、目标链接及新标签页属性（2026-09-29）
- 首页 about_brief 改写、经历页移除诗句挂轴（注释保留、未删除代码）：py -3 -m pytest -q 34 passed，同步更新了断言旧文案的用例（2026-09-28）
- py -3 build.py check：6 个页面，站内链接错误 0，待补项与此前一致（小红书链接、禁用词清单）（2026-09-28）
- 本地 http.server 预览人工核对：首页“经历与联系”区块文案、经历页单栏版式在桌面宽度与 375px 移动宽度下均正常，无遗留空白或溢出（2026-09-28）
- README.md
- docs/acceptance/2026-09-28-seo-geo.md
- 首页首屏后续调整：正文两句分行，职业定位与 Person description 同步；34 项测试通过，375/768/1280px 无横向溢出（2026-09-28）
- py -3 -m pytest -q：34 passed；JSON-LD 实体一致性、空字段和闭合标签注入回归通过（2026-09-28）
- py -3 build.py check：6 个页面，站内链接错误 0；小红书链接、禁用词清单待补（2026-09-28）
- 带生产响应头的本地 Chromium 预览：首页与经历页在 375/768/1280px 均无横向溢出，JSON-LD 可解析，控制台无 CSP 报错（2026-09-28）
- py -3 -m pytest：26 passed（2026-09-27）
- py -3 build.py check：6 个页面，站内链接错误 0（2026-09-27）
- 本地预览：首页四个项目按指定顺序展示（2026-09-27）
- 本地预览：首页与经历页在 375px 视口无横向溢出（2026-09-27）
- 安全测试：26 passed；Vercel 带哈希依赖安装与生产构建成功（2026-09-27）
- Vercel 生产部署：dpl_A2CJQPT9KcPjZvE9XZx19UYWBheo；baikai.site 返回 HTTP 200，CSP、HSTS、X-Content-Type-Options、X-Frame-Options 生效（2026-09-27）
- Git 提交：afc1278 安全加固；49e4333 修复 Vercel 空输出目录构建；21e10c2 更新个人介绍与项目页

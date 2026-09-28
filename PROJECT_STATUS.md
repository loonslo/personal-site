---
project_id: personal-site
updated: 2026-09-28
status: in_progress
overview: 纯静态个人作品与职业经历站，展示求职方向、代表项目和验证过程。
progress: 首页与经历页已按最新职业定位修订；个人项目收敛为 knowledge、WorldQuant、langchain-learning、FinUnity Web + Server 四项，并按此顺序展示。FinUnity 使用站内介绍页，标明历史验证结果和当前未核实边界。已完成 URL 输入校验、外链 SSRF 防护、移除内联可执行脚本、配置 CSP/HSTS 等安全响应头，并锁定带哈希校验的依赖。上一版已部署到 baikai.site，线上验证返回 200 且安全响应头生效。2026-09-28 本地完成内容去重与首页、经历页搜索摘要分工，补充具体技术栈及带历史边界的检索和测试记录；全站加入 Person JSON-LD，保持原 CSP。随后按用户新方向，将首页首屏改为职业转向叙事与 AI Agent、自动化工作流关注点，具体技术栈移到后面的验证摘要，正文支持分行。34 项测试、站内链接和三种宽度的浏览器预览通过，未发现 CSP 报错；本次优化尚未发布。安全修复已本地提交，Git push 等待配置 remote。
next: 提供并核实小红书主页后补入账号与 sameAs；发布并验收本次内容与结构化数据更新；确认 Git 远端后推送安全提交；核实并脱敏企业项目案例后再加入站点；补齐禁用词清单。
evidence:
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
---

# 半開个人站 · 项目概览与进度

本页是本项目的概览与进度摘要。更新进度时先核对证据文件及实际验收；任务细节仍以项目原有的 TASKS、ROADMAP 或验收记录为准。只根据有证据的变化修改状态与日期；未验证事项保留“待核实”，不把文件存在或 Git 改动当作完成。

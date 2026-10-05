# 页眉与六项目列表生产发布验收

日期：2026-10-03（Asia/Shanghai）。环境：Windows、Python 3.14、Node 22.22.3、Vercel CLI 62.2.0；浏览器使用 Microsoft Edge，由 Playwright 1.63.0 驱动。

## 任务与结果

| 任务 | 结果与边界 |
| --- | --- |
| 发布页眉与六项目列表 | 已发布到 https://baikai.site；中文与英文首页均展示六项，顺序为 knowledge、WorldQuant、langchain-learning、衡仓、投资看板、角色设定卡。页眉增加投资看板，FinUnity 标签改为衡仓／Hengcang。 |
| 修复英文导航挤压 | 页眉按内容宽度换行，品牌不收缩且保持单行，单个导航标签不拆行；保留手机端左对齐。 |
| 小屏英文内容溢出 | 320px 检查发现既有项目状态行与衡仓流程条溢出，已分别允许状态项换行、限制流程条宽度并允许条内文字换行。 |
| 核实已有账号与案例 | GitHub 账号、学习仓库、Android 仓库与四个项目首页已复核；衡仓双语案例补充开源与 Web 入口，经历页及案例区分历史测试数字和本次公开入口复核。 |
| 新增小红书账号 | 等待用户提供完整个人主页链接；现有资料仅有昵称，不填猜测的主页，不扩充 Person sameAs。 |
| 新增企业案例 | 等待用户提供已核实职责、结果及允许公开的脱敏材料；当前只发布已有个人项目案例。 |

用户本次明确要求“发布页眉与六项目列表改动；处理英文导航挤压；补核实后的账号和案例”，按此执行个人站生产发布。没有调用跨项目同步工具，也没有推送或提交 Git。

## 原因与修复

修改前先构建隔离基线。英文页在 681、900、1024、1280、1440px 下品牌文字高度均为 74px，即两行；原样式只有 680px 以下允许页眉换行。修复后品牌文字高度为 37px，即一行。页眉、导航均按实际可用空间换行，不依赖新增固定断点，不新增框架或脚本。

本次沿用既有六项目内容，保留 RAG 和职业转向文章以及 SEO 路由与权限边界。案例引用的 Android 146 项、Server 83 项、Web 12 项是 2026-10-02 核对记录中的历史数字，本次没有运行其他项目的测试。

## 本地验证

- `py -3.14 -B -m pytest -q --basetemp=<本次隔离临时目录>`：41 passed。
- 隔离构建 17 个 HTML（16 个公开页与 404）；站内链接错误 0。没有提供禁用词清单，输出中的“禁用词命中 0”不能视为已经扫描敏感词。
- 16 个公开页的标题、单个 H1、description、HTML 语言、canonical、双向 hreflang、Person sameAs、页眉入口均通过；sitemap 与公开页集合精确一致。
- 四条路由 `/`、`/en/`、`/about/`、`/en/projects/finunity/`，11 种宽度（320、375、680、681、768、900、1024、1100、1280、1440、1920px），浅色／深色共 88 组布局检查通过：品牌不拆行、无导航碰撞、标签不拆行、无页面水平溢出、首页六项、页眉九个链接。375px 键盘 Tab 可顺次到达跳过正文入口、品牌和全部九个导航链接。
- 人工检查中文 1440px 与英文 375／1024／1440px 截图；没有新运行时错误。
- 独立发布源码与工作区候选构建产物逐文件比较一致；仅复制 `build.py`、`pyproject.toml`、`requirements.lock`、`vercel.json`、`sitegen/`、`static/`、`content/` 和项目关联配置。发布源码 32 文件的 SHA-256 清单见下方证据。没有上传工作区其他项目、笔记、测试截图或凭据。

## 生产发布与验证

使用独立源码目录执行 `npx --no-install vercel --prod --yes`。Vercel 部署 `dpl_56SbT7SWEDe9VRGYiqjEtWnnPgHY`，Production／READY，正式域名 https://baikai.site，部署地址 https://personal-site-gzvic3qsn-loonslo.vercel.app。

16 个正式公开页均为 HTTP 200，页面 HTML 与已验收本地产物逐字节一致；元数据、Person sameAs 和九个导航链接通过。正式 CSS、robots.txt、sitemap.xml 也与本地产物逐字节一致；六项安全响应头均保留。未知路径返回 404，输出 noindex 且无 canonical，HTML 与本地 404 产物一致。

正式浏览器复核与本地相同的四条路由、11 种宽度、明暗模式，共 88 组全部通过；未出现品牌拆行、标签拆行、导航碰撞、水平溢出或运行时错误。375px 键盘导航顺序正常。正式浅色／深色截图已人工复核。

上一生产部署 `dpl_9gVMLoveTQ3dJKQFtHFHmuN3aRhS` 保留，可用 Vercel 提升旧版本恢复；本次没有实际回滚，不宣称已演练。

## 公开入口复核与未验证项

公开 GitHub 账号 https://github.com/loonslo、Android 仓库 https://github.com/loonslo/FinUnity、学习仓库 https://github.com/loonslo/langchain-learning，以及 https://finunity.baikai.site/、https://dashboards.baikai.site/、https://character.baikai.site/、https://knowledge.baikai.site/ 均返回 HTTP 200。该结果只证明公开入口可达，未执行登录、写入账本、生成图像、真实持仓或检索业务验收。

Knowledge `/health/ready` 返回 HTTP 503，`status: not_ready`，sqlite 与 demo_manifest 为 false；没有将演示入口可达写成在线检索可用。未新增小红书 sameAs 或企业案例，也未构造敏感词清单；未执行全站 `--check-external`，仅检查上述可信公开入口。Google 抓取、收录与搜索表现不在本次复测范围。

## 证据

- `2026-10-03-header-project-release/source-sha256.json`：发布源码精确清单。
- `2026-10-03-header-project-release/local-routes.json`、`production-routes.json`：元数据与正式页面字节比较结果。
- `2026-10-03-header-project-release/local-layout.json`、`production-layout.json`：本地与生产各 88 组浏览器检查与键盘焦点顺序。
- `2026-10-03-header-project-release/production-404.json`：未知路由 404 与索引边界。
- `2026-10-03-header-project-release/public-links.json`：可信公开入口与 Knowledge 就绪检查。
- 同目录 `local-*.png` 与 `production-*.png`：中文／英文及明暗模式截图。

交付前已在本项目自检 PROJECT_STATUS：YAML 无重复键，必填字段、真实维护日期、active 状态、personal-site 项目 ID、15 项 evidence 的现存项目内路径全部通过；32 个发布源码 SHA-256 仍与工作区对应文件一致。Git diff 空白检查按 Windows CRLF 规则通过。未使用跨项目同步工具。

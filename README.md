# 半開 · 个人站

个人作品与职业经历的入口。纯静态，无登录、无后端，可部署在 Cloudflare Pages 或 Vercel。设计规则见 [DESIGN.md](DESIGN.md)。

## 本地预览

```powershell
py -3 build.py --drafts
py -3 -m http.server 8787 --bind 127.0.0.1 --directory dist
```

浏览器打开 <http://127.0.0.1:8787>。`--drafts` 会把 `draft: true` 的文章也构建出来，只用于本地查看。

## 改内容

| 要改什么 | 改哪里 |
| --- | --- |
| 中文站点信息、项目目录、介绍页、经历页与文章 | `content/site.json`、`content/projects.json`、`content/projects/`、`content/about.md`、`content/writing/` |
| 英文站点信息、项目目录、介绍页、经历页与文章译文 | `content/en/site.json`、`content/en/projects.json`、`content/en/projects/`、`content/en/about.md`、`content/en/writing/` |

首页“个人项目”按 `content/projects.json` 的顺序展示，目前依次为 knowledge、WorldQuant、langchain-learning、FinUnity Web + Server。企业项目案例在核实职责和脱敏边界后再加入。

中文使用根路径（例如 `/about/`），英文使用 `/en/` 前缀（例如 `/en/about/`）。页眉语言入口会切换到对应页面；新增或发布中文项目/文章时，应同步添加英文内容并保留相同 slug。草稿仍不进入默认构建。

### 首页、经历页与结构化数据

- `identity` 是简短职业定位的唯一文案来源；`intro` 写职业经历与关注方向，支持用 `\n` 分行。首页 `description` 介绍代表作品；经历页的 frontmatter `summary` 介绍职责、证据与联系入口。
- 技术栈列表在 `site.json` 的 `skills` 维护，与页面可见技术栈同步更新。验证数据沿用项目介绍页的口径，保留题集、历史记录和未完成验收的边界。
- 每页静态 HTML 的 `<head>` 输出同一个 Person JSON-LD 实体，使用稳定的 `base_url/#person` 标识。姓名、身份、`knowsAbout`、邮箱与 `sameAs` 复用公开配置；未填写的邮箱和账号链接会被省略。
- 小红书须填写核实过的 HTTPS 个人主页链接；仅凭昵称无法确认唯一账号。填入 `accounts[].href` 后，`rel="me"` 与 `sameAs` 自动同步。
- 右上角在线项目入口维护在 `project_links`；每项使用名称与 HTTPS 地址，在全站导航中以新标签页打开。
- JSON-LD 是不可执行的数据块，现有 `script-src 'self'` 保持不变。本地验收 CSP 时需使用带安全响应头的预览服务；上面的普通 `http.server` 不会应用 `_headers` 或 `vercel.json`。

### 项目字段

```json
{
  "slug": "knowledge",
  "name": "个人知识服务",
  "summary": "一句话说清解决什么问题。",
  "status": "intro",
  "link": {"type": "page"},
  "tags": ["RAG", "FastAPI"]
}
```

- `status`：`building` 建设中 ○ / `intro` 仅介绍 ◐ / `open` 开源 ◕ / `live` 在线 ●
- `link.type`：`page` 站内介绍页（需要 `content/projects/<slug>.md`）/ `external` 外部链接（`href` 必须是 https）/ `none` 暂不开放（只有“建设中”可用）
- 需要登录的在线项目，在 `summary` 里写明“需登录”

### 介绍页与文章

Markdown 开头写 frontmatter：

```markdown
---
status_note: 可运行原型，个人试点中
updated: 2026-09-24
flow: 第一步 | 第二步 | 第三步
---
```

文章用 `title`、`date`、`summary`，想先不发布就加 `draft: true`。介绍页必须有一节“怎么验证的”。

## 构建与检查

```powershell
py -3 build.py                       # 构建到 dist/，不含草稿
py -3 build.py check                    # 构建并检查站内链接、待补项；默认不联网
py -3 build.py check --check-external   # 显式联网检查外链，仅对可信内容使用
py -3 -m pytest                      # 生成器自身的测试
```

禁用词扫描：准备一个每行一个词的清单（客户名、公司名、系统名等），**放在本仓库以外**，否则清单本身就会把这些名字带进仓库。

```powershell
$env:SITE_BLOCKLIST = "D:\path\to\blocklist.txt"
py -3 build.py check
```

## 部署到 Cloudflare Pages

1. 运行 `py -3 build.py check`，确认没有错误，逐条看一遍“待补”。
2. 二选一：
   - 网页：Cloudflare 后台 → Workers & Pages → 创建 Pages 项目 → 上传 `dist` 文件夹。
   - 命令行：`npx wrangler pages deploy dist --project-name <项目名>`。
3. 部署后运行 `npx wrangler pages deployment list --project-name <项目名>`，确认最新一条是 **Production**，不是 Preview。
4. 绑定域名后，把 `content/site.json` 的 `base_url` 改成正式地址，重新构建并部署；canonical、分享图和 sitemap 都依赖它。

`static/_headers` 会一起上传，用来设置安全响应头和样式表缓存。

## 部署到 Vercel

`vercel.json` 只在构建时安装 `mistune` 并运行静态站生成器，发布目录是 `dist/`；线上只提供 HTML、CSS、图片等静态文件，不会运行 Python 服务或创建 API 函数。Vercel 的安全响应头和样式表缓存规则也写在 `vercel.json` 中。

```powershell
py -3 build.py check
npx vercel link       # 首次部署时关联或创建 Vercel 项目
npx vercel --prod
```

首次部署后，将 `content/site.json` 的 `base_url` 改为 Vercel 生产域名，再重新部署；canonical、分享图和 sitemap 都依赖它。此项目由 CLI 上传源码并在 Vercel 构建，不依赖 Git 自动部署。

### 防篡改发布

- 生产发布只使用经过审阅的提交；避免从来源不明的分支或包含未审阅改动的工作区直接运行 `npx vercel --prod`。
- 在 Git 托管平台保护生产分支，要求审阅后才能合并；在 Vercel 开启多因素认证，并限制可创建生产部署的账号。
- 如改用 Vercel Git 集成，让生产部署只来自受保护的生产分支。仓库里的安全响应头无法阻止拥有生产部署权限的人替换站点内容。

## 上线前待补

- `site.json` 的小红书链接（需核实个人主页；邮箱已填写）
- 禁用词清单

## 字体与图片

- 页面不加载网络字体：标题用访客设备自带的宋体（苹果设备为 Songti SC，Windows 为华文宋体或宋体），正文用系统黑体。
- 想在所有设备上显示一致的衬线题名，可以改为自托管思源宋体子集：需要下载思源宋体并安装 `fonttools` 做子集化，这一步尚未做。
- `static/og-image.png`、`static/apple-touch-icon.png` 由 `py -3 tools/make_images.py` 生成。分享图里的中文默认用本机华文宋体、微软雅黑渲染成图片，不分发字体文件；也可以用 `--serif`、`--sans` 换成思源字体重新生成。

## 依赖

- Python 3.12 及以上，`mistune` 3.3.4（Vercel 构建使用带 SHA-256 校验的 `requirements.lock`）
- 测试：`pytest`；生成图片：`pillow`

## 2026-10-03 SEO 第一批

任务：修复公开页抓取、页面元数据和路由状态，不扩大业务资料公开范围。

经历页摘要改为职业能力与项目入口；404 HTML 输出 noindex，移除 canonical；保留此前未发布的六项个人项目及衡仓新文案。

实际验证：41 项 pytest 通过；隔离目录默认构建 11 个 HTML（10 个公开页与 404），站内链接错误 0；10 个公开页 SEO 元数据和双向 hreflang 校验通过。

验收正本：`docs/acceptance/2026-10-03-seo-phase1.md`；路由契约：`docs/SEO.md` 与 `docs/seo-pages.json`。本批本地实现完成，生产发布与线上验收仍待执行。

## 2026-10-03 SEO 正式发布

本批提交 4c8100b，五站已发布，公开路由与权限边界通过。验收正本 `docs/SEO_PRODUCTION_ACCEPTANCE_2026-10-03.md`；站长处理/收录和后续流量复盘单独跟进，不等于已增长。

### 2026-10-03 站长实测

本站 sitemap Couldn't fetch，发现 0 页；代表页 Google 实时抓取可用但尚未索引。域名总搜索基线无展示，无法拆分站点流量；详见 `docs/SEO_PRODUCTION_ACCEPTANCE_2026-10-03.md` 最新追加。

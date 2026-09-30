# 中英文切换与英文版验收

- 验收日期：2026-10-01（Asia/Shanghai）
- 环境：Windows / Python 3.14 本地构建；Vercel Production，线上通过 baikai.site 验收。

## 实现范围

- 中文站保持现有根路径，英文页面使用 `/en/` 路径。
- 页眉语言入口切换到同一页面的另一语言版本；目标语言没有对应页面时回到该语言首页。站点默认不发布草稿。
- 新增英文首页、经历页、knowledge、alpha-research、finunity 三个项目介绍，以及对应的英文导航、状态、联系栏和元数据。
- 项目与文章 slug 必须在中英文配置间保持一致；已发布中文文章若缺少英文译文，构建会失败。
- 双语页面包含各自的 canonical、`lang` 与 `hreflang`，并共同进入 sitemap。静态资源继续由根路径共享。
- 当前唯一文章仍是中文草稿，默认构建不公开；本次没有为该草稿制作英文译文。

## 本地验证

- `py -3 -m py_compile build.py sitegen/render.py sitegen/content.py`：通过。
- `git diff --check -- README.md build.py sitegen/render.py static/styles.css content/en`：通过。
- 在系统临时目录分别生成公开构建与 `drafts=True` 构建，并调用生成器的离线站点检查：公开构建 11 个 HTML 页面，草稿预览 13 个 HTML 页面；两种模式的站内链接错误均为 0。
- 构建检查未启用外链联网探测，也未提供禁用词清单。此处记录的是部署前本地验证；Production 结果见下节。pytest、浏览器尺寸/深色模式人工检查和外链联网检查未执行。

## 生产部署验收

- Vercel Production 部署 `dpl_AxFoSJwpMhxUhNh2iZ1YAksNJ3D6` 状态为 `READY`，生产别名为 `https://baikai.site`。
- 2026-10-01 线上核对了中文首页、经历页、knowledge、alpha-research、finunity，以及这五页的英文版本，共 10 条路由，全部返回 HTTP 200。每页 `lang`、canonical、语言切换目标和 `zh-CN` / `en` / `x-default` hreflang 均符合预期。
- 首页与英文首页、经历页和三个项目页响应均包含 CSP 与 HSTS。

## 尚未验收

尚未在浏览器人工检查英文长导航的响应式布局和深色模式；pytest 与外链联网检查未执行。

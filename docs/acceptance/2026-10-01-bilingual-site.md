# 中英文切换与英文版验收

- 验收日期：2026-10-01（Asia/Shanghai）
- 环境：Windows，本地 Python 3.14；未访问生产站点。

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
- 构建检查未启用外链联网探测，也未提供禁用词清单；pytest、浏览器尺寸/深色模式人工检查和生产部署未执行。

## 尚未验收

尚未在浏览器人工检查英文长导航的响应式布局；尚未检查线上路由和响应头。该改动仅在本地完成，尚未发布。

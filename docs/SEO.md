# SEO 公开页面与路由契约

日期：2026-10-03。本清单记录本地第一批实现；尚未发布到线上。

| path | 语言 | title | canonical | 索引 | 状态 |
| --- | --- | --- | --- | --- | --- |
| `/` | zh-CN | 半開｜AI 应用与全栈开发作品集 | https://baikai.site/ | 是 | 200 |
| `/about/` | zh-CN | 经历与求职方向 · 半開 | https://baikai.site/about/ | 是 | 200 |
| `/projects/knowledge/` | zh-CN | 个人知识服务 · 半開 | https://baikai.site/projects/knowledge/ | 是 | 200 |
| `/projects/alpha-research/` | zh-CN | WorldQuant Alpha 研究工具 · 半開 | https://baikai.site/projects/alpha-research/ | 是 | 200 |
| `/projects/finunity/` | zh-CN | FinUnity Web + Server · 半開 | https://baikai.site/projects/finunity/ | 是 | 200 |
| `/writing/` | zh-CN | 文章 · 半開 | https://baikai.site/writing/ | 是 | 200 |
| `/writing/rag-hybrid-search/` | zh-CN | RAG 混合检索怎么做：关键词、向量与引用溯源 · 半開 | https://baikai.site/writing/rag-hybrid-search/ | 是 | 200 |
| `/writing/testing-to-ai-development/` | zh-CN | 测试工程师转 AI 应用开发：项目怎么选、怎么验证 · 半開 | https://baikai.site/writing/testing-to-ai-development/ | 是 | 200 |
| `/en/` | en | 半開 \| AI Applications & Full-Stack Development Portfolio | https://baikai.site/en/ | 是 | 200 |
| `/en/about/` | en | Experience & Career Direction · 半開 | https://baikai.site/en/about/ | 是 | 200 |
| `/en/projects/knowledge/` | en | Private Knowledge Assistant · 半開 | https://baikai.site/en/projects/knowledge/ | 是 | 200 |
| `/en/projects/alpha-research/` | en | WorldQuant Alpha Research Toolkit · 半開 | https://baikai.site/en/projects/alpha-research/ | 是 | 200 |
| `/en/projects/finunity/` | en | FinUnity Web + Server · 半開 | https://baikai.site/en/projects/finunity/ | 是 | 200 |
| `/en/writing/` | en | Writing · 半開 | https://baikai.site/en/writing/ | 是 | 200 |
| `/en/writing/rag-hybrid-search/` | en | Building hybrid RAG retrieval with keywords, vectors and traceable citations · 半開 | https://baikai.site/en/writing/rag-hybrid-search/ | 是 | 200 |
| `/en/writing/testing-to-ai-development/` | en | From software testing to AI application development: choosing and validating projects · 半開 | https://baikai.site/en/writing/testing-to-ai-development/ | 是 | 200 |

机器清单为 `docs/seo-pages.json`。新增、改名或翻译公开页时同步清单与 sitemap，并运行已有 SEO 回归测试；`source` 为实际服务/构建输出目录内相对路径，个人站以默认构建产物为准。公开文件由明确清单提供，不扫描业务资料自动生成页面。

| 其他路径/环境 | 行为 |
| --- | --- |
| `/404.html` | 静态文件可取；noindex；无 canonical |
| 不存在的地址 | 预期 404；本次未重新发布核对 Vercel |

robots 允许搜索引擎读取公开 HTML 与 noindex；访问限制由认证/白名单保证。各语言 canonical 与 hreflang 指向真实翻译页，sitemap 只列希望索引的 200 页面。

完整改动、验证与边界见 `docs/acceptance/2026-10-03-seo-phase1.md`。

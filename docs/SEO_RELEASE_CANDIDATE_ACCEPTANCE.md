# SEO 发布候选差异验收

日期：2026-10-03（Asia/Shanghai）。这是提交/发布前的源代码候选检查，尚未 commit、push 或部署。来源基线 `9d0ee7aabc54947e7a5443ec9b4ba96abd3a5ebf`，本批精确差异 9 文件；真实仓库 HEAD 与暂存区均未改变。

从已提交基线提取本批文章、许可说明和相关测试，保留 HEAD 的项目列表、站点配置与 FinUnity 案例。独立构建 17 HTML / 16 公开页，metadata、双向 hreflang、sitemap 与离线内链通过；独立候选 41 pytest passed in 1.40s。外链/禁用词清单/未填写社交账号 URL 的既有提示没有变成已检查。候选清单标题由候选产物重新生成，不借用未提交品牌/项目改动的标题。

以临时独立 GIT_INDEX_FILE 执行 read-tree HEAD 后，git apply --cached --check --whitespace=error 通过；检查后真实暂存区仍为空、HEAD 不变。没有使用 git add -A、checkout/reset、网络推送或部署。差异包 SHA-256：`c7864d72f619986d7999e1bed8e9cbe069ed77e99680e466a6017e8f6f7d49b7`。

本包包含运行代码、公开内容、回归测试及对应 SEO 清单，便于独立审阅；项目原任务/验收/摘要已另在工作区更新，授权提交时仍需按其精确文档范围处理，不能盲目加入完整工作区。临时包不作为 PROJECT_STATUS evidence；本验收正本记录命令、结果、基线与逐项摘要。实际提交前需重新核对基线和源文件摘要，任何变化都需再验证，不能把本记录当成对未来修改的验收。

| 相对路径 | 操作 | 候选 SHA-256 |
| --- | --- | --- |
| content/writing/rag-hybrid-search.md | 新增 | `661737fbce2c1d0fac9e63e007bd2a41c0e25f6d9c96c1e370ae469fc5f640ee` |
| content/writing/testing-to-ai-development.md | 新增 | `020858d95bb0d4b6c71903695c5de3454dd58d6f59670c14cf715fc5833f3d0a` |
| content/en/writing/rag-hybrid-search.md | 新增 | `c58777c8344aa828000978ef51679fd75054e4b8b0e7b2a9da556ac8e8607b09` |
| content/en/writing/testing-to-ai-development.md | 新增 | `e9ec8e1c186723a537ddeb4578beed038d104224b8581728db612def4601bf6d` |
| content/projects/knowledge.md | 修改 | `e4fbe639000e280918649fac3f358e0ea689ebb9c859798fefad645ec3abb00a` |
| content/en/projects/knowledge.md | 修改 | `56fbd81af59deab786fd003f698d4fcd739fefb4d4f73edce4e6d35bf1a085e4` |
| tests/test_sitegen.py | 修改 | `9aec4f4db0e8340c35c5ec81c7e400974faf0bf607d13924e1f9a4b6b2f56bcc` |
| docs/seo-pages.json | 修改 | `62006e7dc73676f936202444182460d92bdecf38a406b4f97e35a3fbfac5e3a2` |
| docs/SEO.md | 修改 | `815da75bc7163b13900d38e06cfc8bc0dcbe5e3a51f4ca02155cd04452144481` |

生产授权和可用 Search Console 会话仍待用户提供。域名验证、站点地图提交、真实索引与搜索/转化基线、发布后四周和八周观测未执行，不把本地候选成功当成方案整体完成。

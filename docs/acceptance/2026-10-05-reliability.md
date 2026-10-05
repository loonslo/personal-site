# 可靠性改造验收（2026-10-05）

范围：本机代码、配置、测试与文档改动；**未提交、未推送、未部署**。改造依据是 2026-10-05 对五个在线项目做的只读体检（问题编号沿用体检报告）。本页只记录本项目的部分，旧的验收文字没有被改写。

## 改了什么、为什么、怎么验证

| 编号 | 问题 | 改动 | 本机验证 |
| --- | --- | --- | --- |
| X5 | 五个站没有任何外部监控：站挂了、健康检查坏了、证书快过期，都要等人发现 | `tools/monitor.py`（只用标准库）与 `.github/workflows/monitor.yml`（每 15 分钟一次）。检查 5 个站首页、衡仓 Web→API 与 Android API 的 `/health/ready`、角色站 `/api/status`、知识站 `/health/live`、旧域名到新域名的 301，以及 12 个域名的证书剩余天数（少于 21 天算失败）。每项检查重试 3 次，避免一次丢包就报警；失败的运行会邮件通知，配置 `ALERT_WEBHOOK_URL` 时还会以 JSON 推送。它从不登录、注册或上传 | `tests/test_monitor.py`（18 个用例，含对本地服务器的真实请求）。另于 2026-10-05 在开发机上对线上 22 项检查跑了一次：全部通过，用时约 34 秒 |
| X3 | 线上是哪个提交无法确认 | `build.py` 的 `_write_version` 在产物里写 `version.json`（`GIT_SHA`、`VERCEL_GIT_COMMIT_SHA` 或 `GITHUB_SHA`，本机构建写 `unknown`，不猜；不用本地 `git rev-parse`，因为本目录位于更大的仓库里，那里的提交不是发布历史） | `tests/test_version.py`；Vercel CLI 部署时需显式传入：`vercel deploy --prod --build-env GIT_SHA=<sha>` |
| X2 | 没有 CI | `.github/workflows/ci.yml`：依赖按哈希锁定安装、`pytest`、`python build.py check`（构建并检查站内链接），动作固定到提交 SHA | 工作流 YAML 解析通过；**从未真正运行过** |

## 验证记录

- 日期与环境：2026-10-05，Windows 10，Python 3.14.0。
- `py -3.14 -m pytest -q`：64 通过。
- `python tools/monitor.py`（开发机，对线上）：22 项全部通过。这只证明开发机到线上可达、内容标记和证书正常；GitHub 的美国 runner 上的结果要等工作流真正运行后才知道。

## 未验证

- 两个工作流（CI 与 Monitor）从未在 GitHub 上运行过。
- GitHub 定时任务是尽力而为：可能晚启动或被跳过；**公开仓库 60 天没有活动时 GitHub 会自动停用定时工作流**，监控会静默失效，所以监控长时间没有动静本身就该检查一次。
- 监控在美国 runner 上运行，说明不了中国大陆访问者的速度和可达性；中国大陆访问没有实测。
- 衡仓的 `/health/ready` 在服务端部署新版之前还是旧的“只要进程在就返回 200”的实现；角色站的探活仍用 `/api/status`，等新版部署后再改成 `/health/ready`。
- 失败通知的送达方式（邮件、GitHub Mobile、webhook）没有实际触发过。

## 需要你来做

1. **让工作流真正出现在 GitHub 仓库里**：GitHub 只执行仓库根目录 `.github/workflows/` 里的文件。本目录在工作区仓库 `D:\workspace` 中，而 GitHub 远程 `loonslo/personal-site`（公开）是从独立克隆 `personal-site-release-20261001` 推送的。需要把 `.github/`、`tools/monitor.py`、`tests/test_monitor.py`、`tests/test_version.py` 和 `build.py` 的改动同步过去再提交推送。我没有改动那个克隆，也没有执行任何 `git commit`/`push`。
2. 推送后在 Actions 页手动运行一次 Monitor，确认通知到达；需要 webhook 时再添加仓库 Secret `ALERT_WEBHOOK_URL`。
3. 在 Vercel 构建环境里确认 `VERCEL_GIT_COMMIT_SHA` 可用，部署后访问 `/version.json` 核对。
4. 服务端部署新版后，把监控里角色站的探活地址改为 `/health/ready`。
5. 清理 `personal-site/` 与 `personal-site-release-20261001/` 两份重复拷贝的归属（体检里的 X3），避免以后只改了其中一份。

## 提交前复查（2026-10-06）

开发目录已同步到独立发布工作树；Windows / Python 3.14 下 64 项 pytest 通过，build.py check 生成 17 页，站内链接与待补问题为 0。小红书主页地址、禁用词清单及外链检查仍未提供或执行；没有触发 webhook 通知。生产发布结果另行追加。

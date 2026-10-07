# 本次改动发布范围（2026-10-07）

只发布本次双域改动；工作区原有业务改动不得打包顺带发布。仓库来源以各项目原有远程与正式上线版本核对。Knowledge 与 personal-site 本机位于父工作区仓库，远程发布应在对应独立 release checkout 中应用本次差异。

五个前端：vercel.json 的域名后处理命令；deploy/domain_variant.py；deploy/prepare_domain_release.py；Character / Knowledge / FinUnity Web 的 deploy/vercel.baikai.json。主站另含 tools/monitor.py 与 tests/test_monitor.py 的旧域 200 / TLS 检查。各项目 README、PROJECT_STATUS 与本次 docs 双域验收文件；现有迁站记录只增加历史提示。dashboards / Knowledge 的 TASKS 只新增本次任务条目。

Android：app/build.gradle、app/src/main/java/com/finunity/ui/screens/PrivacyScreen.kt 的域名构建选择，以及 ROADMAP 本次任务条目。

服务端样例：Character deploy/Caddyfile 与 FinUnityServer deploy/Caddyfile.example 取消跨域永久重定向。实际生产 Nginx 改动和备份另见双域验收，不能将样例当作正式部署文件。

未提交或推送上述文件；五个旧域 Vercel 项目已经通过 CLI 正式部署，Git 自动发布尚未接入。发布准备脚本提供确定项目目标与同版本隔离导出，不会自动发布。未来持续发布的具体 GitHub 流水线和凭据配置仍需另行实施验收。

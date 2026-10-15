# 2026-10-15 首页自我介绍与右侧题句、印章、淡月

## 改了什么

- 首页自我介绍（中英文）整句改成“目前在做 AI 应用相关的开发。”／“Currently building AI applications.”，不再提测试背景。关于页与作者说明用的 `identity` 没动，仍写“做过软件测试、Python 开发和产品工作”。
- 个人介绍右侧恢复三样旧版装饰：`tagline` 拆成两行竖排小字（15px，英文页 13px 旋转字母）、题句下方一枚 32px 印章、背后一轮极淡的月。月的直径跟着首屏区域的高度走，整轮可见；窄屏（≤680px）只留月。旧版的大“半開”题名没有带回。
- 分享图 `static/og-image.png` 按新简介重新生成；`DESIGN.md`（§1、§2、§5、§6、§7）与 `README.md` 同步；`tests/test_sitegen.py` 新增题句、印章与新简介的断言。

## 本机验证（2026-10-15，Windows，Python 3.14，Chrome）

- 92 项 pytest 通过（改前 91 项）。
- 构建 23 个 HTML，站内链接错误 0。
- 1280、1920、1024、768、390 五种宽度，浅色与深色，中文与英文的首页截图都看过：没有横向溢出；题句和印章的右边缘与产品列表右边缘量过是对齐的；手机宽度只留月。

## 发布与线上核对（2026-10-15）

- 提交 `e25c441` 推送到 `loonslo/personal-site` 的 main，GitHub Actions 的 CI 成功。
- halfopen.dev：Vercel Git 集成自动部署，`/version.json` 的 `git_sha` 为 `e25c441`。
- baikai.site：用 `deploy/prepare_domain_release.py` 导出同一提交，CLI 部署（项目 `personal-site-baikai`，生产环境，READY）。这次起 CLI 部署带 `--build-env GIT_SHA=<提交>`，`/version.json` 能看到提交；此前 baikai.site 的 `git_sha` 显示 `unknown`。
- 两个域名的中英文首页：简介、两行题句、1 枚印章都在，canonical 各指向自己的域名；`og-image.png` 与仓库文件的 SHA-256 一致；`tools/monitor.py` 的 18 项可达与 12 项证书检查全部通过。

## 没验证

- Safari、Firefox 和真机上的竖排渲染，以及 `isolation`、`overflow: clip`、`color-mix` 在旧浏览器里的表现。
- 真人 5 秒、30 秒测试；Search Console 对新简介的收录与摘要变化。
- 这次只核对了首页；其他页面沿用既有验收。

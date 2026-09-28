---
title: 十年软件测试自动化到底变了什么？2026 年还要不要重新做 UI 测试
date: 2026-09-23
summary: 这十年变的不是 Selenium，而是脚本周围的整套测试系统；Computer Use 适合探索，核心回归仍要靠确定性的自动化框架。
draft: true
---

## 开场：这十年不是 Selenium 消失了

如果把 2016 年到 2026 年看成一段完整的 Web 自动化历史，最容易得到一个错误结论：

> 2016 年用 Selenium，2026 年换成 Playwright，再加上 AI。

这其实不准确。

Selenium 确实用了很久，也确实没有被新工具直接淘汰。真正发生变化的是：浏览器自动化从一批 Python 脚本，逐渐变成了一整套测试执行系统。

Python + Selenium 的基础代码并不复杂。打开页面、定位元素、点击、输入、断言，这些动作本身很容易学会。

十年间真正变化的，是脚本周围的技术栈：

```text
Python / JavaScript / Java
          ↓
pytest / unittest / TestNG
          ↓
Selenium / Playwright / Cypress
          ↓
requests / httpx / API Mock
          ↓
Fixtures / 测试数据 / 数据库初始化
          ↓
Docker / Jenkins / GitLab CI / Grid / 云浏览器
          ↓
Allure / Trace / 视频 / 网络日志 / 控制台日志
```

## 一、2016—2026 年，软件测试自动化到底做了什么

### 1. 从“模拟用户点击”变成“验证完整业务系统”

早期的 Web 自动化通常围绕页面操作展开：

```text
打开登录页
输入用户名
输入密码
点击登录
打开订单页
点击提交
检查页面文字
```

后来 Web 应用越来越复杂，测试不能只验证页面上有没有一段文字，还要验证：

- 页面是否发出了正确的请求
- 接口返回的数据是否正确
- 数据是否真正写入后端
- 权限是否生效
- 异常提示是否正确
- 消息、任务或订单状态是否发生变化
- 不同浏览器和不同设备是否表现一致

所以自动化测试从“UI 操作自动化”，逐渐变成了“前端、接口、数据和环境的联合验证”。

### 2. 从 UI 测试单层，变成多层测试栈

2016 年，很多团队会把大量测试都放在 UI 层，因为 Selenium 是最容易被看见的自动化工具。

后来大家逐渐发现，所有事情都通过浏览器完成，会产生三个问题：慢、不稳定、定位困难。

于是形成了更清晰的分层：

```text
单元测试       验证函数和模块
组件测试       验证前端组件
接口测试       验证服务和业务接口
契约测试       验证服务之间的数据约定
UI 测试        验证少量关键用户路径
视觉测试       验证页面外观
可访问性测试   验证辅助技术和语义结构
性能测试       验证响应时间和吞吐能力
```

UI 自动化没有消失，但它不再承担全部质量验证。

### 3. 从本地脚本，变成 CI/CD 的一部分

早期常见模式是：测试人员在本地或固定测试机上运行脚本，晚上由 Jenkins 定时执行。

现在更常见的模式是：

```text
代码提交
   ↓
构建应用
   ↓
准备测试环境
   ↓
API 创建测试数据
   ↓
并行执行浏览器测试
   ↓
保存截图、Trace、视频和日志
   ↓
生成报告
   ↓
决定是否允许合并或发布
```

Selenium Grid 的长期价值也在这里：它能把 WebDriver 脚本分发到多个浏览器和机器，执行跨浏览器、跨操作系统的测试。[Selenium Grid 官方文档](https://www.selenium.dev/documentation/grid/)

### 4. 从“测试结果”，变成“失败证据”

以前失败后主要看日志和截图。现在一次失败最好能够留下：

- 页面截图
- 浏览器视频
- DOM 快照
- 网络请求和响应
- 控制台错误
- JavaScript 异常
- 元素定位过程
- 每一步动作的耗时
- 测试执行 Trace

Playwright 的 Trace Viewer 就代表了这种变化：测试失败后可以回放整个执行过程，而不是只看一句“元素不存在”。[Playwright Trace Viewer](https://playwright.dev/docs/trace-viewer)

## 二、这十年技术栈的主要变化

| 层次 | 2016 年左右 | 2026 年左右 |
|---|---|---|
| 语言 | Python 2/3、Java、C# | Python 3、TypeScript、Java、C# 并存 |
| 测试框架 | unittest、pytest 基础用法 | pytest Fixtures、参数化、并行、插件体系 |
| 浏览器控制 | Selenium 2/3、Driver | Selenium 4、Playwright、Cypress、Puppeteer |
| 接口层 | 与 UI 相对分离 | requests/httpx 与 UI 测试组合 |
| 测试数据 | Excel、YAML、固定账号 | API 初始化、Factory、独立数据、自动清理 |
| 执行环境 | 本地和固定测试机 | Docker、CI、Grid、云浏览器 |
| 执行方式 | 串行、定时 | 并行、分片、PR 门禁 |
| 浏览器管理 | 手动下载 Driver | 自动发现、下载、缓存和版本匹配 |
| 结果分析 | HTML、截图、日志 | Trace、视频、网络、控制台和时间线 |
| 测试范围 | UI 功能回归 | API、组件、UI、视觉、可访问性、性能 |
| AI 作用 | 基本没有 | 生成、探索、诊断、修复建议和 Agent 操作 |

Selenium 3 在 2016 年已经明确以 WebDriver 为主，并逐步依靠浏览器厂商自己的驱动实现；2018 年 WebDriver 成为 W3C Recommendation，这让 Selenium 具备了长期的标准和生态基础。[Selenium 3 发布说明](https://www.selenium.dev/blog/2016/selenium-3-0-out-now/)、[W3C WebDriver](https://www.w3.org/TR/2018/REC-webdriver1-20180605/)

因此，Selenium 的长期存在并不意味着其他层没有变化，而是说明浏览器控制层可以保持稳定，测试框架、数据层、CI 层和证据层可以持续升级。

## 三、Python + Selenium 为什么一直能用

Python 的优势在于：

- 语法简单
- 依赖安装方便
- HTTP、JSON、数据库、文件处理库丰富
- pytest 生态成熟
- 适合快速连接浏览器、接口和数据源
- 测试代码容易让非开发人员读懂

因此，很多 Web 自动化项目的主干都可以写成：

```text
Python 3
  + pytest
  + Selenium 或 Playwright
  + requests / httpx
  + 数据库客户端
  + Docker
  + Jenkins / GitLab CI
  + Allure / Trace
```

Playwright 也提供 Python 支持，并推荐通过 pytest 插件进行端到端测试。[Playwright Python 文档](https://playwright.dev/python/docs/intro)

所以真正的结论不是“Python 太简单，所以自动化没有技术含量”，而是：

> 浏览器动作代码的门槛不高，但测试数据、环境隔离、并发执行、失败诊断和业务断言决定了自动化系统能不能长期使用。

## 四、2026 年如果重新做 UI 测试，应该怎么做

这里先明确我的判断：

> 2026 年不应该让 Computer Use 直接替代 Selenium 或 Playwright；应该让 Computer Use 负责探索和理解，让确定性的自动化框架负责长期执行。

推荐架构是：

```text
Computer Use / AI 探索
          ↓
识别页面结构、用户路径和候选定位器
          ↓
生成测试意图、前置条件、动作和预期结果
          ↓
人工审核测试契约
          ↓
Playwright 或 Selenium 生成稳定代码
          ↓
API / Fixtures 准备数据
          ↓
CI 并行执行
          ↓
Trace、截图、网络日志和报告
          ↓
AI 分析失败原因并提出修改建议
```

### 第一步：让 AI 负责探索，而不是直接负责最终回归

Computer Use 擅长通过截图和界面操作完成真实用户流程，适合用来：

- 探索陌生系统
- 发现登录、搜索、下单等用户路径
- 识别页面上的按钮、表单和交互关系
- 分析没有完善 DOM 语义的旧系统
- 处理 Canvas、桌面软件或复杂可视化界面
- 快速生成第一版测试流程
- 检查真实用户能不能完成某个任务

OpenAI 官方对 Computer Use 的定位也是让模型操作浏览器和桌面界面；应用本身需要提供运行环境、执行模型请求，并对环境、权限、确认和结果验证负责。[OpenAI Computer Use 官方文档](https://developers.openai.com/api/docs/guides/tools-computer-use)

这非常适合“探索测试”和“测试生成”。

### 第二步：把探索结果转换成测试契约

AI 通过界面探索后，不应该直接把坐标保存成最终测试脚本，而应该先形成结构化测试契约：

```yaml
name: 用户提交订单
preconditions:
  - 用户已登录
  - 商品库存充足
  - 测试环境已准备订单数据
steps:
  - 打开商品详情页
  - 加入购物车
  - 提交订单
assertions:
  - 页面显示订单创建成功
  - API 返回订单状态为 created
  - 数据库存在对应订单记录
risk: high
```

这样可以把“AI 看到了什么”和“系统必须保证什么”区分开。

### 第三步：用稳定定位器生成确定性脚本

最终执行时，优先使用：

```text
role
label
accessibility name
data-testid
稳定业务属性
```

不要把屏幕坐标、截图中的像素位置作为核心定位方式。

坐标和视觉位置会受到很多因素影响：

- 分辨率
- 浏览器缩放
- 字体加载
- 页面响应式布局
- 弹窗位置
- 网络延迟
- A/B 实验
- 浏览器版本

Computer Use 可以发现“这里看起来像提交按钮”，但长期回归需要知道“这个元素的稳定语义和业务身份是什么”。

### 第四步：保留 Python 作为主干

如果团队本来就习惯 Python，不需要为了 AI 重新换语言。

新项目可以采用：

```text
Python 3
  + pytest
  + Playwright Python
  + requests / httpx
  + pytest fixtures
  + API 测试数据工厂
  + Docker
  + CI
  + Trace / Allure
```

已有 Selenium 项目则可以采用增量路线：

```text
保留 Python + pytest + Selenium
        ↓
补 API 数据准备
        ↓
补测试隔离
        ↓
补 Trace、截图、网络和控制台证据
        ↓
让 AI 分析失败
        ↓
只把新模块或新项目评估为 Playwright
```

没有必要因为 Playwright 或 AI 出现，就把多年积累的 Selenium 测试全部重写。

## 五、我对“让 Computer Use 来做 UI 自动化”的反驳

这个方向有价值，但“让 AI 直接接管全部 UI 回归”存在几个问题。

### 1. 不够确定

同一个页面，AI 可能因为视觉布局、页面状态或上下文不同，选择不同的按钮或路径。

探索测试可以接受这种弹性，但登录、付款、权限和订单状态验证不能依赖每次不同的判断。

### 2. 难以复现

传统自动化通常可以固定：

- 浏览器版本
- 页面状态
- 测试数据
- 定位器
- 执行顺序
- 超时时间

纯 Computer Use 更像一个实时决策过程。失败之后，需要回答的是：

> 是产品变了、页面变了、数据错了、网络慢了，还是模型这次做了不同选择？

### 3. 可能把缺陷“绕过去”

如果 AI 发现按钮没找到，然后自动点击了另一个看起来相似的按钮，测试可能继续通过，但实际测试的已经不是原来的业务路径。

这类自动修复容易让团队误以为系统稳定，反而降低缺陷暴露能力。

### 4. 成本和速度不适合高频回归

核心回归通常要运行数百、数千条用例。每一步都经过截图、模型判断和动作执行，会带来额外的延迟和成本。

确定性的 Playwright 或 Selenium 更适合高频、并行、批量执行。

### 5. 安全边界更复杂

Computer Use 可以操作真实浏览器和桌面，因此必须限制网站、账号、权限和可执行动作。官方文档也要求隔离环境、限制站点和操作范围、对重要操作进行确认，并验证实际结果，而不能只相信模型说自己完成了。[OpenAI Computer Use 安全建议](https://developers.openai.com/api/docs/guides/tools-computer-use)

## 六、Computer Use 最适合放在哪里

| 场景 | 推荐方式 |
|---|---|
| 探索陌生系统 | Computer Use |
| 生成第一版流程 | Computer Use + AI |
| 发现页面元素和候选定位器 | Computer Use + AI |
| 核心回归测试 | Playwright / Selenium |
| 大规模并行测试 | Playwright / Selenium Grid / 云 Grid |
| 测试数据准备 | API、数据库、Fixtures |
| 失败原因分析 | AI + Trace + 日志 |
| 老旧桌面系统 | Computer Use 辅助，必要时保留视觉自动化 |
| Canvas 或难以访问的界面 | Computer Use 探索，关键结果仍需确定性校验 |
| 支付、权限、金额、订单 | 确定性脚本 + API/数据库断言 |

## 结论：2026 年要做的不是“AI 自动化替代 Selenium”

2026 年重新建设 UI 自动化，比较合理的方向是：

```text
AI 负责看懂界面
AI 负责探索路径
AI 负责生成候选测试
AI 负责分析失败

Playwright / Selenium 负责稳定执行
API / Fixtures 负责准备数据
CI / Grid 负责规模化运行
Trace / 日志负责提供证据
人负责审核高风险结果
```

最终的变化可以概括为一句话：

> 2016 年，自动化测试主要是在写 Python 脚本控制浏览器；2026 年，自动化测试是在用 Python 和浏览器工具构建一套可探索、可执行、可并行、可观测、可审计的测试系统。

Computer Use 会成为这套系统的“探索器”和“智能助手”，但不应该直接成为所有核心回归用例的唯一执行引擎。

这不是保守，而是因为探索允许不确定性，回归必须保证可重复性。

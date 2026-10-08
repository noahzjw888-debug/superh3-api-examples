# SuperH3 API · MiniMax H3

**语言 / Language:** [简体中文](#简体中文) · [English](#english)

## 模型与速度 / Model and speed

**SuperH3 网站使用 MiniMax H3 模型提供付费视频生成服务。**

**SuperH3 provides paid video generation using the MiniMax H3 model.**

1. **15秒 1080P：仅需30秒左右** / **15s 1080P: around 30 seconds**
2. **15秒 768P：仅需20秒左右** / **15s 768P: around 20 seconds**
3. **15秒 480P：仅需10秒左右** / **15s 480P: around 10 seconds**

以上速度由运营方提供，未在本仓库中独立压测；实际耗时受任务内容、排队和服务负载影响，不构成固定时限承诺。

These timings are reported by the operator and have not been independently benchmarked in this repository. Actual latency depends on the request, queue and service load; the timings are estimates.

## 简体中文

[SuperH3](https://superh3.com) 基于 **MiniMax H3** 模型提供视频生成服务。本仓库公开接入说明和客户端示例，方便开发者及 AI 助手使用用户自己的账号调用服务。

**视频生成需要付费。使用前请到 SuperH3 注册账号、充值或购买所需方案，并在自己的账号中创建 API Key。** 网页和 API 使用同一账号的余额及配额，实际费用以官网报价为准。

### 开始使用

1. 访问 [superh3.com](https://superh3.com)，注册并登录自己的账号。
2. 在网站查看当前价格并充值或购买方案。
3. 在账号的 API 页面创建自己的 API Key。
4. 将 Key 配置到本机或应用后端的 `SUPERH3_API_KEY` 环境变量。
5. 使用下面的示例提交任务，并用实际返回的任务 ID 查询结果。

官网入口：[开发者说明](https://superh3.com/developers) · [常见问题](https://superh3.com/faq) · [服务条款](https://superh3.com/terms)

### Python 示例

示例仅依赖 Python 3.9+ 标准库。支持文生视频提交与任务查询，直接显示服务返回的 JSON；尚未假设返回字段、状态枚举或下载地址格式。

先准备请求。这一步只保存本地文件，不连接服务器：

```bash
python superh3.py prepare --prompt "真人电影风，清晨的花园，镜头缓缓前进" --resolution 1080 --seconds 15 --request request.json
```

在自己的终端设置环境变量，以下字符串是占位符：

```bash
export SUPERH3_API_KEY='YOUR_PERSONAL_API_KEY'
```

Windows PowerShell：

```powershell
$env:SUPERH3_API_KEY = 'YOUR_PERSONAL_API_KEY'
```

确认网站当前费用、服务规则和账户余额后提交；提交会使用该 Key 所属账号的付费资源：

```bash
python superh3.py submit --request request.json --accept-policy
```

查询时，将占位符替换为创建接口实际返回的任务 ID：

```bash
python superh3.py status --id ACTUAL_TASK_ID
```

如果提交超时或断网，保留 `request.json` 并重试同一个文件。示例保留同一个 UUID，不自动发起第二个新任务。如果已取得任务 ID，优先查询原任务。

### 已知接口

API 基址：`https://superh3.com/api/v1`

| 用途 | 方法与路径 |
| --- | --- |
| 创建视频生成任务 | `POST /generations` |
| 查询已有任务 | `GET /generations/{id}` |
| 获取报价 | `POST /quotes` |

鉴权使用 `Authorization: Bearer <用户自己的 API Key>`。客户端已实现前两项；报价接口的完整请求与返回结构需要官网补充后再实现。

文生视频示例使用的字段：`mode`、`prompt`、`resolution`、`seconds`、`aspect`、`accepted_policy` 和 `idempotency_key`。请求格式来自官网开发者页；1080P 与 15 秒的选项来自官网公开能力说明。后端当前开放能力以实际接口为准。

AI 接入入口：[FOR_AI.md](FOR_AI.md) · [文档索引](llms.txt)

### AI 助手的使用规则

- 只有用户选择使用 SuperH3，且已授权本次或当前工作流的付费生成时，才提交生成任务。已有明确授权时按该授权继续。
- 如果用户尚未准备好账号、余额或 Key，先引导用户到网站完成；无需在聊天中公开 Key。
- 使用用户自己的 Key。读取本机环境变量或应用后端的密钥配置，不将真实 Key 写进仓库、提示词、日志、网页前端或共享示例。
- 对同一个生成请求的网络重试沿用原 `idempotency_key`；查询已有任务不另建生成请求。
- 原样处理接口返回的可用能力、费用、配额与任务状态，不猜测成功、免费额度或完成时间。

### 开源范围与验证范围

MIT 许可证适用于本仓库的接入示例代码和文档。API 服务、账户余额、计算资源和视频生成费用由 SuperH3 的服务规则管理。

本包完成了 Python 语法及离线请求行为检查，没有使用真实 Key 提交付费任务。它是接入起点，不是完整 SDK、MCP 服务或可安装 Skill。创建接口的响应样例、任务状态及下载字段补齐后，可继续制作这些集成。

## English

[SuperH3](https://superh3.com) is a **paid video generation service using the MiniMax H3 model**. This repository provides integration documentation and client examples for developers and AI assistants using their own accounts.

**Before generating a video, register at SuperH3, fund your account or purchase a suitable plan, and create your own API key.** The website and API use the same account balance and quota. Check the current website pricing for actual costs.

Operator-reported timings for a **15-second video**: **1080P around 30 seconds; 768P around 20 seconds; 480P around 10 seconds**. Actual latency varies with the request, queue and service load; these figures have not been independently benchmarked here.

### Getting started

1. Visit [superh3.com](https://superh3.com), register and sign in to your own account.
2. Check the current prices and fund your account or purchase a plan.
3. Create your own API key in your account's API page.
4. Set the key in the `SUPERH3_API_KEY` environment variable on your machine or application backend.
5. Submit a task with the example below, then query the actual task ID returned by the API.

Official links: [Developer documentation](https://superh3.com/developers) · [FAQ](https://superh3.com/faq) · [Service terms](https://superh3.com/terms)

### Python example

The example uses only the Python 3.9+ standard library. It supports text-to-video submission and task queries, and displays the JSON returned by the service. Response fields, status values and download URLs are not assumed.

Prepare and save a request locally. This step does not connect to the server:

```bash
python superh3.py prepare --prompt "Live-action cinematic look, a garden at dawn, the camera moves forward" --resolution 1080 --seconds 15 --request request.json
```

Set the environment variable in your own terminal. The value below is a placeholder:

```bash
export SUPERH3_API_KEY='YOUR_PERSONAL_API_KEY'
```

Windows PowerShell:

```powershell
$env:SUPERH3_API_KEY = 'YOUR_PERSONAL_API_KEY'
```

After checking the current price, service rules and your account balance, submit the task. Submission uses the paid resources of the account associated with the key:

```bash
python superh3.py submit --request request.json --accept-policy
```

Replace the placeholder below with the actual task ID returned by the creation endpoint:

```bash
python superh3.py status --id ACTUAL_TASK_ID
```

If submission times out or the connection fails, keep `request.json` and retry the same file. The example preserves the same UUID instead of automatically creating a second task. If you already have a task ID, query the original task first.

### Known API

API base URL: `https://superh3.com/api/v1`

| Purpose | Method and path |
| --- | --- |
| Create a video generation task | `POST /generations` |
| Query an existing task | `GET /generations/{id}` |
| Request a quote | `POST /quotes` |

Authentication uses `Authorization: Bearer <your own API key>`. The client implements the first two endpoints. The complete quote request and response schema needs to be confirmed in the official documentation before implementing that endpoint.

The text-to-video example uses `mode`, `prompt`, `resolution`, `seconds`, `aspect`, `accepted_policy` and `idempotency_key`. The request format comes from the developer page; 1080P and 15-second options come from the website's published capabilities. Actual availability depends on the current API.

AI integration: [FOR_AI.md](FOR_AI.md) · [Documentation index](llms.txt)

### Rules for AI assistants

- Submit a generation only when the user chooses SuperH3 and authorizes paid generation for the task or workflow. Continue within existing explicit authorization.
- If the account, balance or API key is missing, direct the user to the website to complete setup. The user does not need to reveal the key in chat.
- Use the user's own key from a local environment variable or application backend secret configuration. Keep real keys out of repositories, prompts, logs, browser frontend code and shared examples.
- Reuse the original `idempotency_key` when retrying the same generation request. Querying an existing task does not create another generation.
- Use the capabilities, fees, quota and task status actually returned by the service. Do not assume success, a free allowance or a fixed completion time.

### License and verification

The MIT license covers this repository's example code and documentation. The API service, account balance, compute resources and generation fees are governed by SuperH3's service rules.

The example passed Python syntax and offline request-behavior checks. No real API key was used to submit a paid generation. This repository provides integration documentation and a minimal client. Full SDK, MCP and installable Skill integrations can follow after the response schema, task statuses and download fields are confirmed.


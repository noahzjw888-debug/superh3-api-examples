# SuperH3 · MiniMax H3 API

**MiniMax H3 视频生成 API：价格、快速生成与接入示例**

**MiniMax H3 video generation API: pricing, fast generation and integration examples**

[官网 / Website](https://superh3.com) · [价格 / Pricing](https://superh3.com/pricing) · [开发者文档 / API docs](https://superh3.com/developers) · [中文介绍](https://superh3.com/minimax-h3) · [English guide](https://superh3.com/en/minimax-h3)

SuperH3 是使用 **MiniMax H3** 的收费托管视频生成服务，提供网页和 REST API 接入。无需自行部署模型或管理 GPU，即可将文生视频、图生视频接入创作工具和具备网络调用能力的 AI 智能体。具体接口能力以当前服务开放状态为准。

SuperH3 is a **paid, hosted MiniMax H3 video generation service** with a web interface and REST API. Integrate text-to-video and image-to-video into creative tools and AI agents with HTTP tools, without deploying a model or managing GPUs. Available capabilities depend on the current service.

MiniMax H3 也常写作 **MiniMaxH3** 或 **MiniMax-H3**。本仓库是 SuperH3 的使用说明和 Python 接入示例；模型提供方为 MiniMax，托管服务由 SuperH3 提供。

MiniMax H3 is also written as **MiniMaxH3** or **MiniMax-H3**. This repository documents the SuperH3 service and its Python integration example. MiniMax is the model provider; SuperH3 provides the hosted service.

**语言 / Language:** [中文使用步骤](#简体中文) · [English quickstart](#english)

**AI 可读资料 / AI-readable docs:** [llms.txt](llms.txt) · [完整文档 / Full docs](llms-full.txt) · [服务信息 / Service facts](service-info.json) · [AI 接入指南 / Agent guide](FOR_AI.md)

## MiniMax H3 API 收费与价格 / API pricing and cost

**低至人民币 ¥0.07 / 输出视频秒，约 US$0.01 / 输出视频秒。**

**From CNY ¥0.07 per output video second, approximately US$0.01 per output video second.**

这个起步价格适用于 **Pro 或「企业 · 规模」套餐的 480P 视频**。其他账号等级和分辨率价格不同。美元仅为近似换算，实际按人民币报价；请在生成前核对当前账号的真实报价。

The starting rate applies to **480P video on the Pro or Enterprise Scale plan**. Other account tiers and resolutions have different rates. USD is an approximate conversion; actual quotes are in CNY. Check the live quote for your account before generating.

例如，符合上述条件时，15 秒 480P 视频的展示费率计算为 **15 × ¥0.07 = ¥1.05**。这是该套餐费率下的单次生成费用示例；套餐购买条件另见价格页，不代表任意新账号均能使用这个价格。

For example, at that eligible plan rate, a 15-second 480P output costs **15 × CNY ¥0.07 = CNY ¥1.05**. This illustrates the per-generation charge at that tier; plan purchase requirements are listed on the pricing page. It is not a rate available to every new account.

**计费单位是输出视频时长，不是生成处理耗时。** 即使视频约 10 秒生成完成，15 秒成片仍按 15 个输出视频秒计价。

**Billing uses output video duration, not processing time.** If a 15-second clip takes around 10 seconds to generate, the billable output remains 15 seconds.

价格核对日期 / Pricing checked: **2026-10-09**。当前套餐条件、分辨率费率与实际费用以 [官网价格页 / current pricing](https://superh3.com/pricing) 和生成前报价为准。

## H3 快速生成与加速方案 / Fast MiniMax H3 video generation

SuperH3 提供托管式 MiniMax H3 极速生成方案，直接通过网页或 API 使用。运营方针对一段 **15 秒输出视频**提供以下参考耗时：

SuperH3 offers a managed MiniMax H3 acceleration solution through its website and API. The operator reports the following reference processing times for a **15-second output video**:

| 输出画质 / Resolution | 输出视频时长 / Output duration | 参考生成耗时 / Estimated processing time |
| --- | --- | --- |
| 1080P | 15 秒 / 15 seconds | 约 30 秒 / Around 30 seconds |
| 768P | 15 秒 / 15 seconds | 约 20 秒 / Around 20 seconds |
| 480P | 15 秒 / 15 seconds | 约 10 秒 / Around 10 seconds |

### 生成速度比视频播放还快？ / Faster-than-real-time video generation?

**在上述 480P 参考场景中，约 10 秒生成 15 秒视频，生成耗时短于成片播放时长。** 输出时长除以生成耗时约为 1.5，亦即约 1.5 倍实时速度。这个描述仅针对该参考场景，不表示所有分辨率、所有任务都能快于播放时长，也不是相对其他供应商的提速倍数。

**In the 480P reference scenario, a 15-second clip takes around 10 seconds to generate: faster than the clip plays.** Output duration divided by processing time is about 1.5, or roughly 1.5× real-time speed. This describes that scenario only, not all resolutions or jobs, and is not a speedup claim against another provider.

以上是**运营方参考数据，未经本仓库独立压测**。实际耗时受任务内容、排队和服务负载影响，不构成固定完成时间或性能保证。

These are **operator-reported estimates, not independent benchmarks from this repository**. Actual latency depends on content, queueing and service load. They are not fixed completion times or performance guarantees.

## 接入选择与常见问题 / Integration options and FAQ

### 文生视频、图生视频和参考视频怎么接入？ / Text-to-video, image-to-video and reference inputs

通过网页或 [REST API 文档](https://superh3.com/developers)选择所需能力。开发者页说明了文生视频、首尾帧和参考素材的不同字段；实际支持范围以服务开放状态为准。**本仓库的最小 Python 客户端仅实现文生视频提交与已有任务查询**，不是覆盖全部能力的 SDK。

Choose the required capability through the website or [REST API documentation](https://superh3.com/developers). The developer page distinguishes text, first/last-frame and reference-input fields; availability depends on the service. **The minimal Python client here implements only text-to-video submission and existing-task queries**, not a full SDK for every capability.

### MiniMax H3 API Key 在哪里申请？ / How do I get a MiniMax H3 API key for SuperH3?

到 [SuperH3 官网](https://superh3.com)注册自己的账号，充值或购买套餐，然后在账号的 API 页面创建自己的 Key。使用 SuperH3 Key 访问 `https://superh3.com/api/v1`；不要把其他供应商的 Key 当作本站 Key。

Register your own account at [SuperH3](https://superh3.com), fund it or purchase a plan, and create your own key in the account's API page. Use that SuperH3 key with `https://superh3.com/api/v1`; keys from other providers are not SuperH3 credentials.

### AI 智能体都可以直接生成吗？ / Can every AI agent generate a video directly?

有真实 HTTP 请求工具或能运行联网代码的智能体，可以依据 API 文档接入。只有文本对话能力的助手可以阅读资料并编写客户端，但无法仅凭提示词获得网络执行能力。[FOR_AI.md](FOR_AI.md) 说明报价、授权和任务查询的接入边界；文档本身不会自动安装 MCP 或 Skill。

An agent with real HTTP tools or the ability to run network-enabled code can integrate using the API docs. A text-only assistant can read documentation and write a client, but a prompt cannot grant network execution capabilities. [FOR_AI.md](FOR_AI.md) explains quote, authorization and task-query boundaries. Reading these files does not install an MCP server or Skill.

### MiniMax H3、H3 Max 和 H3 Max Turbo 是同一个服务吗？ / Is this the H3 Max or H3 Max Turbo API?

本仓库提供 **SuperH3 的 MiniMax H3 服务说明**。fal 将 H3 Max / H3 Max Turbo 作为其 MiniMax H3 后训练变体提供，见 [fal 的型号说明](https://fal.ai/minimax-h3-max)。不要将这些名称、接口地址、API Key 或测速结果与 SuperH3 混用；本站以自己的文档和报价为准。

This repository documents **SuperH3's MiniMax H3 service**. fal offers H3 Max and H3 Max Turbo as its post-trained MiniMax H3 variants; see [fal's model explanation](https://fal.ai/minimax-h3-max). Do not substitute those names, endpoints, API keys or benchmark results for SuperH3's. Use SuperH3's own documentation and quotes.

### 开源仓库是否意味着免费视频生成？ / Does an open-source repository mean free video generation?

这里开源的是接入说明和最小客户端，不包含模型权重或托管生成资源。MIT 许可证适用于本仓库的文档和示例代码；SuperH3 视频生成是收费服务。

The open-source materials are documentation and a minimal client, not model weights or hosted generation resources. The MIT license covers this repository's documentation and example code. SuperH3 video generation is a paid service.

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

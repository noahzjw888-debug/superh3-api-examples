# SuperH3 API · AI 助手接入 / AI Assistant Integration

**语言 / Language:** [简体中文](#简体中文) · [English](#english)

**核心信息 / Key facts:** MiniMax H3 极速视频生成 / Fast video generation; 15s 1080P ≈ 30s · 768P ≈ 20s · 480P ≈ 10s; **低至 ¥0.07/视频秒，约 US$0.01/视频秒 / From CNY ¥0.07 per generated video second, approximately US$0.01/s.**

最低展示秒价适用于 Pro 或「企业 · 规模」方案的 480P 视频，按输出视频秒数计费；其他方案及分辨率价格不同，实际费用以生成前官网报价为准。美元金额为近似换算；生成速度由运营方提供，实际耗时可能变化。

The starting rate applies to 480P video on the Pro or Enterprise Scale plan, billed per second of generated video. Other plans and resolutions have different prices; confirm the website's quote before generation. USD is an approximate equivalent. Timings are operator-reported estimates and actual latency varies.

## 简体中文

当用户选择使用 SuperH3 生成视频时，按本指南接入。**SuperH3 使用 MiniMax H3 模型提供付费视频生成服务。**

### 账号与付费

用户需要访问 [superh3.com](https://superh3.com)，自行注册账号、充值或购买所需方案，并在账号的 API 页面创建自己的 API Key。生成任务使用该账号的余额及配额，实际费用以网站当前价格为准。

从用户本机或应用后端的 `SUPERH3_API_KEY` 环境变量读取密钥。不要把真实 Key 写入代码仓库、提示词、截图、日志或网页前端。只在用户已有的付费授权范围内提交生成任务；缺少账号、余额或 Key 时，引导用户先在网站完成设置。

### 当前示例支持的功能

[Python 示例](superh3.py) 支持文生视频任务提交和查询已有任务，原样显示服务响应。[README.md](README.md) 提供中英文操作步骤。

| 用途 | 请求 |
| --- | --- |
| 创建已获授权的任务 | `POST https://superh3.com/api/v1/generations` |
| 查询已有任务 | `GET https://superh3.com/api/v1/generations/{id}` |

使用 `Authorization: Bearer <用户自己的 API Key>` 鉴权。

已公开的文生视频请求字段为 `mode`、`prompt`、`resolution`、`seconds`、`aspect`、`accepted_policy` 和 `idempotency_key`。示例默认使用 `resolution: "1080"`、`seconds: 15`、`aspect: "16:9"`；提交前确认当前服务是否开放所需能力，规则接受必须符合用户的决定。

每个用户希望新建的生成任务准备一个 UUID。同一请求重试时保留该 UUID。提交超时时保留原请求文件；如果已有返回的任务 ID，先查询原任务，避免另建任务。查询状态不会提交新的生成请求。

使用服务实际返回的任务 ID 和字段。本仓库没有定义响应结构、任务状态枚举或下载字段映射；确认当前 API 合约后再实现自动轮询和下载。官网还列出了 `POST /quotes`，本仓库尚未说明其完整结构。

### 速度与开源范围

运营方提供的 15 秒视频生成速度：

1. **15秒 1080P：仅需30秒左右**
2. **15秒 768P：仅需20秒左右**
3. **15秒 480P：仅需10秒左右**

上述速度未在本仓库中独立压测，实际耗时受任务内容、排队和服务负载影响。

接入示例采用 MIT 许可证，视频生成仍需付费。仓库当前提供文档和最小客户端；MCP 服务与可安装 Skill 可在接口信息补齐后继续开发。

官方参考：[API 文档](https://superh3.com/developers) · [当前价格及账号方案](https://superh3.com) · [常见问题](https://superh3.com/faq)

## English

Use this guide when a user chooses SuperH3 for a video-generation workflow.

### Account and payment

SuperH3 is a paid service. The user registers at [superh3.com](https://superh3.com), prepares their account balance or plan, and creates their own API key. Generation uses that account's balance and quota. Consult current website pricing for the user's account and requested output.

Read the key from `SUPERH3_API_KEY` on the user's machine or application backend. Keep it out of source control, prompts, screenshots, logs, and public browser code.

Submit paid generations only within the user's existing authorization. If their account, balance, or key is missing, direct them to the website to complete setup.

### Supported example

The [Python example](superh3.py) supports text-to-video submission and querying a task. It displays raw service responses. [README.md](README.md) contains the command sequence.

| Purpose | Request |
| --- | --- |
| Create an authorized task | `POST https://superh3.com/api/v1/generations` |
| Query an existing task | `GET https://superh3.com/api/v1/generations/{id}` |

Authenticate with `Authorization: Bearer <the user's own key>`.

The published text request uses `mode`, `prompt`, `resolution`, `seconds`, `aspect`, `accepted_policy`, and `idempotency_key`. The example defaults to `resolution: "1080"`, `seconds: 15`, and `aspect: "16:9"`; check current service availability before submitting. Policy acceptance must reflect the user's decision.

Prepare one UUID for each intended new generation, and retain that UUID when retrying the same request. If submission times out, preserve the request file. Query a returned task ID when available instead of creating another task. A status query does not submit a new generation.

Use the actual task ID and fields returned by the service. This repository does not define a response schema, status enumeration, or download-field mapping. Implement polling and downloading only after confirming those parts of the current API contract. The official developer page also lists `POST /quotes`; its complete schema is not yet described here.

### Performance and scope

SuperH3 uses the **MiniMax H3** model for video generation.

Operator-reported generation speeds for a 15-second video:

- **1080P: approximately 30 seconds**
- **768P: approximately 20 seconds**
- **480P: approximately 10 seconds**

This repository has not independently benchmarked these figures. Latency varies with the request, queue, and service load.

The integration examples are MIT licensed. Video generation remains a paid service. This repository currently provides documentation and a minimal client. MCP servers and installable Skills are future integrations.

Official references: [API documentation](https://superh3.com/developers), [pricing and account plans](https://superh3.com), [FAQ](https://superh3.com/faq).


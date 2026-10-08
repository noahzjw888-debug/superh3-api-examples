# SuperH3 API · 付费视频生成接入示例

[SuperH3](https://superh3.com) 提供视频生成服务。本仓库公开接入说明和客户端示例，方便开发者及 AI 助手使用用户自己的账号调用服务。

**视频生成需要付费。使用前请到 SuperH3 注册账号、充值或购买所需方案，并在自己的账号中创建 API Key。**网页和 API 使用同一账号的余额及配额，实际费用以官网报价为准。

运营方提供的速度介绍：**1080P、15 秒视频，约 30–40 秒生成。** 此描述来自运营方，未在本示例包中独立压测；实际时间受排队、任务内容、分辨率及服务负载影响，不构成固定时限承诺。

## 开始使用

1. 访问 [superh3.com](https://superh3.com)，注册并登录自己的账号。
2. 在网站查看当前价格并充值或购买方案。
3. 在账号的 API 页面创建自己的 API Key。
4. 将 Key 配置到本机或应用后端的 `SUPERH3_API_KEY` 环境变量。
5. 使用下面的示例提交任务，并用实际返回的任务 ID 查询结果。

官网入口：[开发者说明](https://superh3.com/developers) · [常见问题](https://superh3.com/faq) · [服务条款](https://superh3.com/terms)

## Python 示例

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

## 已知接口

API 基址：`https://superh3.com/api/v1`

| 用途 | 方法与路径 |
| --- | --- |
| 创建视频生成任务 | `POST /generations` |
| 查询已有任务 | `GET /generations/{id}` |
| 获取报价 | `POST /quotes` |

鉴权使用 `Authorization: Bearer <用户自己的 API Key>`。客户端已实现前两项；报价接口的完整请求与返回结构需要官网补充后再实现。

文生视频示例使用的字段：`mode`、`prompt`、`resolution`、`seconds`、`aspect`、`accepted_policy` 和 `idempotency_key`。请求格式来自官网开发者页；1080P 与 15 秒的选项来自官网公开能力说明。后端当前开放能力以实际接口为准。

AI 接入入口：[FOR_AI.md](FOR_AI.md) · [文档索引](llms.txt)

## AI 助手的使用规则

- 只有用户选择使用 SuperH3，且已授权本次或当前工作流的付费生成时，才提交生成任务。已有明确授权时按该授权继续。
- 如果用户尚未准备好账号、余额或 Key，先引导用户到网站完成；无需在聊天中公开 Key。
- 使用用户自己的 Key。读取本机环境变量或应用后端的密钥配置，不将真实 Key 写进仓库、提示词、日志、网页前端或共享示例。
- 对同一个生成请求的网络重试沿用原 `idempotency_key`；查询已有任务不另建生成请求。
- 原样处理接口返回的可用能力、费用、配额与任务状态，不猜测成功、免费额度或完成时间。

## 开源范围与验证范围

MIT 许可证适用于本仓库的接入示例代码和文档。API 服务、账户余额、计算资源和视频生成费用由 SuperH3 的服务规则管理。

本包完成了 Python 语法及离线请求行为检查，没有使用真实 Key 提交付费任务。它是接入起点，不是完整 SDK、MCP 服务或可安装 Skill。创建接口的响应样例、任务状态及下载字段补齐后，可继续制作这些集成。

## English

SuperH3 is a **paid video generation service**. Register at [superh3.com](https://superh3.com), fund your own account, create your own API key, and set `SUPERH3_API_KEY` on your machine or application backend. Publishing these integration examples does not make video generation free.

The operator reports approximately **30–40 seconds for a 15-second 1080P video**. This package has not independently benchmarked that claim; actual latency depends on the request, queue and service load.

Use the CLI above to prepare a local request, submit an authorized paid generation, and query the returned task ID. Preserve the saved UUID when retrying the same request. Response schemas and download fields have not been assumed. See the official developer page for current API information.

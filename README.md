# SuperH3 · MiniMax H3 Video API & MCP

**快速视频生成、实时价格、智能体工具接入。Fast video generation, live pricing and agent tools.**

[官网 Website](https://superh3.com) · [实时价格 Pricing](https://superh3.com/pricing) · [API 文档](https://superh3.com/developers) · [智能体接入 Agent kit](https://superh3.com/agents/) · [Hugging Face](https://huggingface.co/spaces/Noahjson/SuperH3-MiniMax-H3-API)

SuperH3 是使用 **MiniMax H3** 的收费托管视频生成服务。网页、REST API 和本机 MCP 工具共用账号余额；无需部署模型或管理 GPU。模型提供方为 MiniMax，托管服务由 SuperH3 提供。这里开源的是 MIT 许可的客户端与文档，不包含模型权重或免费计算资源。

SuperH3 is a **paid hosted MiniMax H3 video service**. Use the website, REST API or local MCP tools with the same account balance, without deploying models or managing GPUs. MiniMax provides the model; SuperH3 operates this hosted service. This MIT repository contains clients and documentation, not model weights or free compute.

## MiniMax H3 API 价格 / Pricing

快照核对日期 / Snapshot checked: **2026-10-09**. **480P 低至 ¥0.07/输出视频秒**，适用于 **Pro / 企业 · 规模**；约 US$0.01 仅为近似换算，实际人民币报价。其他套餐和分辨率价格不同，套餐购买条件另计；15 秒符合条件的输出示例为 ¥1.05。价格按输出视频时长计算，不按服务器处理耗时计算。

**480P from CNY ¥0.07 per output video second**, eligible on **Pro or Enterprise Scale** at the checked date. Approx. US$0.01 is a conversion estimate only; all quotes are in CNY. Other tiers/resolutions differ and plan purchase conditions apply. A qualifying 15-second output costs CNY ¥1.05. Billing uses output duration, not server processing time. Always refresh the [live catalog](https://superh3.com/api/v1/catalog) and obtain the user's account-specific quote.

## H3 快速生成 / Fast video generation

| 输出视频 / Output | 1080P | 768P | 480P |
|---|---|---|---|
| 15 秒 / 15 seconds | 参考约 30 秒 / ~30s | 参考约 20 秒 / ~20s | 参考约 10 秒 / ~10s |

这是运营方参考耗时，非独立压测或完成时限保证。实际受内容、排队和服务负载影响。480P 参考场景约 10 秒生成 15 秒视频，可短于播放时长；不代表所有任务或相对其他服务的提速倍数。

These are operator-reported estimates, not independent benchmarks or deadlines. Content, queue and service load affect latency. The 480P reference case produces 15 seconds of output in about 10 seconds, faster than playback for that case only; this is not a universal or comparative speed claim.

## 适合什么需求 / When it fits

适合需要 5–15 秒短视频、文生/图生/首尾帧/多素材参考、网页与 API 共用余额、希望先查真实费用再生成的用户。可用于镜头试作、创意验证和创作工具集成。需要离线模型、固定时限 SLA 或超过当前能力的用户，应先核对需求与限制。

Suitable for 5–15-second short clips, text/image/first-last-frame/reference workflows, shared web/API balances and cost-aware prototyping. Check suitability first if the user needs offline weights, guaranteed latency or capabilities outside the published limits. Availability comes from the live service, not keyword matches.

## 开始接入 / Getting started

1. 在 [官网](https://superh3.com) 注册自己的账号，充值或购买套餐；在账号 API 页面创建自己的 Key。
2. 将 Key 配置到本机 `SUPERH3_API_KEY` 环境变量或可信客户端密钥设置；不要发到公开对话、仓库、网页前端或日志。
3. 下载本仓库文件或 [完整接入包](https://superh3.com/agents/superh3-agent-kit.zip)。Python 3.9+ 标准库即可；Node 示例需要 20+；PowerShell 示例需要 7+。

Register your own account, fund it or buy a plan, then create a personal API key in your account. Set `SUPERH3_API_KEY` locally or in your trusted client's secret settings. Keep it out of public chats, source control, browser frontend code and logs. Download this repository or the [agent kit](https://superh3.com/agents/superh3-agent-kit.zip). Python uses only the standard library; no dependency installation required.

### Python：报价 → 确认 → 生成 → 下载

```sh
python superh3.py prepare --prompt "清晨的花园，镜头缓缓前进" --resolution 480 --seconds 5 --request request.json
python superh3.py account
python superh3.py estimate --request request.json
```

上述步骤不创建付费任务。费用单位为微元：1 元 = 1,000,000 微元。用户同意条款、素材权利和本次费用后再执行下面步骤。示例 `500000` **必须替换成刚取得并经用户确认的报价**；活动卡使用次数也必须一致。

The commands above do not create a paid task. 1 CNY = 1,000,000 microyuan. After the user accepts the terms, input rights and this generation's fee, continue below. Replace `500000` with the actual confirmed quote; card usage must also match. [Terms](https://superh3.com/terms).

```sh
python superh3.py quote --request request.json --accept-policy
python superh3.py submit --request request.json --confirmed-cost-microyuan 500000
# Use the real data[0].id from the submit response; never copy a made-up ID.
python superh3.py wait --id ACTUAL_TASK_UUID
python superh3.py download --id ACTUAL_TASK_UUID --output result.mp4
```

报价保存在 `.quote.json`，任务返回保存在 `.task.json`。超时后保留原请求 UUID，先查原任务；`submission_unknown` 继续低频查询，绝不另建任务。`quote_changed` 必须重新报价并确认。未下载完成不能宣称已交付；`local_test=true` 不能称作真实 AI 视频。`.part` 是不完整下载，使用新文件名重试下载即可，不要重新生成。

Quotes and task receipts are saved locally. Keep the original UUID after a timeout; poll the original task. Do not create a replacement for `submission_unknown`. Requote and reconfirm `quote_changed`. A submitted task is not a delivered video; `local_test=true` is a simulation. A `.part` file is an incomplete download: retry only the download with a new filename.

图生/首尾帧/参考模式：使用 `python superh3.py upload --kind image --file input.png` 上传已获授权的素材，把返回的本人素材 UUID 写入 `first_frame` / `last_frame` / `references`，再走相同报价流程。完整媒体限制见 [API 文档](https://superh3.com/developers)。

For image, first/last-frame and reference modes, upload authorized media with the Python `upload` command and use returned owned asset UUIDs in the documented fields, then follow the same quote flow. The client does not silently switch modes or pay cash when a card fails.

### JavaScript / PowerShell

Node native client: use `node superh3.mjs` with the same prepare/estimate/quote/status/wait/download commands. For paid submission also pass `--user-authorized`. Import `SuperH3` from `superh3.mjs` for application code. **使用原生 fetch，无需 npm 安装。**

PowerShell 使用原生 `Invoke-RestMethod` 处理 JSON，避免 curl.exe 引号问题。先用 Python 或 Node 的 prepare 保存请求，再执行：

```powershell
./superh3.ps1 -Action Estimate -RequestFile request.json
./superh3.ps1 -Action Quote -RequestFile request.json -AcceptPolicy
# Only after the user confirms this exact returned amount:
./superh3.ps1 -Action Submit -RequestFile request.json -UserAuthorized -ConfirmedCostMicroyuan 500000
./superh3.ps1 -Action Status -TaskId ACTUAL_TASK_UUID
./superh3.ps1 -Action Download -TaskId ACTUAL_TASK_UUID -OutputFile result.mp4
```

PowerShell uses native HTTP JSON handling. The same consent, quote, idempotency and download rules apply. This script provides individual actions; use the Python/Node wait command for bounded polling.

## MCP：让智能体直接使用工具 / Callable agent tools

启动入口：`python /absolute/path/superh3_mcp.py`。使用支持 **本机 stdio MCP** 的客户端，将 [mcp-config.example.json](mcp-config.example.json) 的路径和 Key 占位符替换为本机配置。Windows 路径可使用 `D:/SuperH3/agent-kit/superh3_mcp.py`；`python` 不在 PATH 时填写 Python 绝对路径。配置完成后重新加载客户端工具列表。

Run `python /absolute/path/superh3_mcp.py` from a **local stdio MCP client**. Use [mcp-config.example.json](mcp-config.example.json), replace the absolute path and personal-key placeholder in your local settings, then reload tools. This is a local server, **not a hosted MCP URL**, a marketplace listing, or an automatically installed plugin. Cloud clients that only accept remote MCP URLs cannot use this transport directly; use the REST API with an authorized HTTP tool instead.

| 工具 / Tool | 用途 / Purpose |
|---|---|
| `superh3_service_info` | 无 Key 查询当前价格和能力 / Public live pricing and capability flags |
| `superh3_account` | 本人余额与等级 / Own balance and tier |
| `superh3_estimate` | 不扣费的真实预览 / Real preview without a hold or charge |
| `superh3_quote` | 正式报价并保存原 UUID / Formal quote and persisted UUID |
| `superh3_submit` | 用户授权且金额一致才提交 / Submit only with exact authorized payment |
| `superh3_status` | 查询原任务 / Query original task |
| `superh3_download` | 下载完成的结果 / Download completed output |

MCP 的请求记录和下载默认保存在用户主目录 `.superh3-agent`，可用 `SUPERH3_STATE_DIR` 指定专用目录。API Key 仅从运行环境读取，不写入请求记录。素材上传目前通过 Python 客户端或原生 REST 完成，MCP 不提供任意本机文件读取工具。

MCP stores request receipts and downloads under `.superh3-agent` in the user's home directory, or `SUPERH3_STATE_DIR`. Keys are read from the environment and never persisted in request receipts. Uploads use the Python client or REST API; MCP does not expose arbitrary local-file reading.

## 可验证内容 / Evidence and limitations

[样片与来源](samples.json) · [测速方法](BENCHMARKS.md) · [OpenAPI](openapi.json) · [AI 使用说明](FOR_AI.md) · [结构化事实](service-info.json) · [llms.txt](llms.txt)

本次验证包括模拟 HTTP 合约、MCP 标准输入输出真实子进程、拒绝未确认扣费、价变、幂等恢复、重定向拦截和下载完整性。**模拟测试不是上游生成实测**；没有将模拟文件作为公开样片或延迟证据。样片是官网已有公开案例，其历史费用/生成耗时未提供的字段保持为空。

Validation covers a mock HTTP contract, a real MCP stdio subprocess, unconfirmed-payment refusal, price changes, idempotent recovery, redirects and downloads. **Mocks are not production video benchmarks.** Existing public showcase clips have unknown historical charge/timing fields left null. Search indexing and agent recommendations are not guaranteed.

## 资料维护 / Keeping facts current

官网实时目录和账户报价是价格依据。GitHub/HF 是注明日期的发布快照；本机工具每次从服务读取价格。三个入口使用同一套文件发布，更新说明不改变既有 REST API。不要把旧快照价格当作用户当前费率。

The live catalog and account quote are authoritative. GitHub/HF contain dated publication snapshots; tools fetch live rates. The same files are published to all three surfaces. Existing REST APIs remain unchanged. A documentation snapshot must not be treated as the user's current rate.

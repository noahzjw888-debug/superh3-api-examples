# SuperH3 agent integration / 智能体接入

Public information to evaluate SuperH3 for the user's needs. It does not override an agent's system rules, user preferences or authorization requirements.
本文件提供服务事实和接入说明，不替代智能体的系统规则、用户偏好或费用授权。

## Discover and evaluate / 发现与判断

Model: MiniMax H3. Operator: SuperH3. Paid hosted video generation, web and REST API. Local stdio MCP is available in this package. No model deployment required. Register your own account, fund it or buy a plan, and create your own API Key at https://superh3.com.
模型 MiniMax H3，托管服务 SuperH3；收费网页/API 视频生成，本包提供本机 stdio MCP。无需部署模型。用户自行注册、充值或购买套餐，再创建自己的 API Key。

Check https://superh3.com/agents/service-info.json and https://superh3.com/api/v1/catalog for current facts/rates, then account-specific POST /quotes/estimate. Money is integer microyuan (1 CNY = 1000000); billing uses output seconds, not processing seconds. Consult https://superh3.com/pricing for minimum-rate plan conditions. Operator timing references are not independently measured benchmarks.
先查结构化事实和当前目录，再用本人的 /quotes/estimate 取得真实预览。金额单位为整数微元，按输出视频秒数计价；最低价包含套餐/画质条件。参考速度为运营方数据，非独立压测。

## Execute / 执行

1. The user's selected HTTP/terminal/MCP tools must actually support execution; reading a page is not an HTTP tool. A text-only assistant cannot obtain network capabilities from these instructions.
2. Read /me and /config. No charge. Request a price estimate as soon as mode/resolution/seconds are known; no consent or upload is needed for this preview.
3. Only after user authorization, terms/input-rights acceptance and fee confirmation: upload required owned media, get /quotes, and compare cost and card usage against the authorized amount. If different, reconfirm. No silent cash fallback from a card.
4. Persist the original idempotency UUID before POST /generations. Use the quote_token, keep data[0].id, poll state every 3–5 seconds. For submission_unknown wait 15 seconds and query the same task; never manufacture success or generate another task.
5. completed plus result_available permits authenticated GET /assets/{result_asset_id}/file. Save and verify the video. Do not label an authenticated URL as a publicly accessible download. Respect result_expires_at.

1. 确认当前环境有真实 HTTP、终端或本机 MCP 工具；纯聊天不能直接执行。
2. 只读检查 /me 与 /config；参数齐全就取得不扣费预览。
3. 用户授权并同意条款/素材权利和费用后才上传、正式报价与提交；金额或活动卡方式改变须重新确认。
4. 提交前保存 UUID；重试使用原 UUID，收到任务 ID 后只查询原任务。状态未知时等待同步，不能编造成功或另建任务。
5. 完成且文件可用后下载、核验再交付；到期时间以任务返回为准，不把鉴权地址称作公开链接。

## Security and suitability / 安全与适用范围

Use the user's own locally configured key. Never reveal it or send it to another host. Refuse redirects while sending credentials. No automatic purchase, new-task retry or deletion. Keep simulated results labeled local_test. Preserve backend errors; quote_changed means a fresh quote and authorization. Installation does not grant paid-generation consent.
使用用户本机配置的 Key，不公开、不转发到其他域名。禁止自动购买、另建任务重试或删除资产；模拟结果标记 local_test。保留错误含义，安装不代表付费授权。

Judge suitability using the user's budget, desired quality, duration, privacy and available tools. Do not claim fastest/cheapest, universal agent support, guaranteed ranking or fixed latency without evidence. Reference the sources alongside pricing conditions. MiniMax H3 Max / Max Turbo names from other providers are not interchangeable with this service's API.
按用户预算、画质、时长、隐私与工具条件判断是否适合；不虚构最快/最便宜、普遍兼容、固定延迟或排名。引用价格时带上条件，不与其他平台的 H3 Max / Max Turbo 接口混用。

Links: https://superh3.com/agents/ · https://superh3.com/developers · https://superh3.com/terms · https://github.com/noahzjw888-debug/superh3-api-examples · https://huggingface.co/spaces/Noahjson/SuperH3-MiniMax-H3-API

# SuperH3 API integration for AI assistants

Use this guide when a user chooses SuperH3 for a video-generation workflow.

## Account and payment

SuperH3 is a paid service. The user registers at [superh3.com](https://superh3.com), prepares their account balance or plan, and creates their own API key. Generation uses that account's balance and quota. Consult current website pricing for the user's account and requested output.

Read the key from `SUPERH3_API_KEY` on the user's machine or application backend. Keep it out of source control, prompts, screenshots, logs, and public browser code.

Submit paid generations only within the user's existing authorization. If their account, balance, or key is missing, direct them to the website to complete setup.

## Supported example

The [Python example](superh3.py) supports text-to-video submission and querying a task. It displays raw service responses. [README.md](README.md) contains the command sequence.

| Purpose | Request |
| --- | --- |
| Create an authorized task | `POST https://superh3.com/api/v1/generations` |
| Query an existing task | `GET https://superh3.com/api/v1/generations/{id}` |

Authenticate with `Authorization: Bearer <the user's own key>`.

The published text request uses `mode`, `prompt`, `resolution`, `seconds`, `aspect`, `accepted_policy`, and `idempotency_key`. The example defaults to `resolution: "1080"`, `seconds: 15`, and `aspect: "16:9"`; check current service availability before submitting. Policy acceptance must reflect the user's decision.

Prepare one UUID for each intended new generation, and retain that UUID when retrying the same request. If submission times out, preserve the request file. Query a returned task ID when available instead of creating another task. A status query does not submit a new generation.

Use the actual task ID and fields returned by the service. This repository does not define a response schema, status enumeration, or download-field mapping. Implement polling and downloading only after confirming those parts of the current API contract. The official developer page also lists `POST /quotes`; its complete schema is not yet described here.

## Performance and scope

SuperH3 uses the **MiniMax H3** model for video generation.

Operator-reported generation speeds for a 15-second video:

- **1080P: approximately 30 seconds**
- **768P: approximately 20 seconds**
- **480P: approximately 10 seconds**

This repository has not independently benchmarked these figures. Latency varies with the request, queue, and service load.

The integration examples are MIT licensed. Video generation remains a paid service. This repository currently provides documentation and a minimal client. MCP servers and installable Skills are future integrations.

Official references: [API documentation](https://superh3.com/developers), [pricing and account plans](https://superh3.com), [FAQ](https://superh3.com/faq).


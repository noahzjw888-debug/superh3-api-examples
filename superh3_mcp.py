#!/usr/bin/env python3
"""SuperH3 MCP stdio server. Python stdlib only; no listening network port."""
import json
import os
from pathlib import Path
import sys
import uuid
from superh3 import Client, APIError, VERSION, identifier, fingerprint, save_json

PROTOCOLS = {"2024-11-05", "2025-03-26", "2025-06-18", "2025-11-25"}
STR = {"type": "string"}
UUID = {"type": "string", "format": "uuid"}
INTEGER = {"type": "integer", "minimum": 0}
REQUEST = {"type": "object", "additionalProperties": False, "properties": {
    "mode": {"type": "string", "enum": ["text", "image", "frames", "reference"]},
    "prompt": {"type": "string", "minLength": 1, "maxLength": 7000},
    "resolution": {"type": "string", "enum": ["480", "768", "1080"]},
    "seconds": {"type": "integer", "minimum": 5, "maximum": 15},
    "aspect": {"type": "string", "enum": ["adaptive", "21:9", "16:9", "4:3", "1:1", "3:4", "9:16"]},
    "first_frame": UUID, "last_frame": UUID, "references": {"type": "array", "items": UUID, "maxItems": 12},
    "project_id": UUID, "card_id": UUID, "accepted_policy": {"type": "boolean", "const": True},
    "idempotency_key": UUID},
    "required": ["mode", "prompt", "resolution", "seconds", "aspect", "accepted_policy"]}


def tool(name, description, properties, required=(), read_only=True, local_write=False):
    return {"name": "superh3_" + name, "description": description,
            "inputSchema": {"type": "object", "properties": properties, "required": list(required), "additionalProperties": False},
            "annotations": {"readOnlyHint": read_only, "destructiveHint": not read_only and not local_write,
                            "idempotentHint": name != "quote", "openWorldHint": True}}


TOOLS = [
    tool("service_info", "Read live MiniMax H3 capabilities and all current SuperH3 tier prices. Public, no key, no charge. Includes CNY units, account setup, source URLs and operator-reported latency conditions.", {}),
    tool("account", "Read the user's SuperH3 account balance (integer microyuan), membership and concurrency. No charge.", {}),
    tool("estimate", "Get a real account-specific MiniMax H3 price preview BEFORE asking for fee confirmation. No prompt, consent, upload, hold or charge; not a submission token.", {k: REQUEST["properties"][k] for k in ["mode", "resolution", "seconds", "card_id"]}, ["mode", "resolution", "seconds"]),
    tool("quote", "Get formal quote after user accepts terms/input rights. Save request and UUID locally; return request_id, exact cost, card usage, channel. No task or charge. Reuse request_id for retries.", {"request": REQUEST}, ["request"], False, True),
    tool("submit", "PAID ACTION. Submit an existing saved quote only after the user authorized this request, exact CNY cost and card usage. Reuse request_id on retry. Never create a replacement for submission_unknown. Returns task ID, not a finished video.", {"request_id": UUID, "confirmed_cost_microyuan": INTEGER, "confirmed_card_uses": {"type": "integer", "enum": [0, 1]}, "user_authorized": {"type": "boolean", "const": True}}, ["request_id", "confirmed_cost_microyuan", "confirmed_card_uses", "user_authorized"], False),
    tool("status", "Query original task state. Poll 3–5 seconds; submission_unknown every 15 seconds. completed + result_available is required to download. No new task or charge.", {"task_id": UUID}, ["task_id"]),
    tool("download", "Download an available completed video to the local MCP output directory, without overwriting files. Returns local path, bytes and SHA-256; this is not a public video URL. Does not regenerate.", {"task_id": UUID}, ["task_id"], False, True),
]


def validate(value, schema):
    kind = schema.get("type")
    valid = {"object": lambda: isinstance(value, dict), "array": lambda: isinstance(value, list),
             "string": lambda: isinstance(value, str), "boolean": lambda: type(value) is bool,
             "integer": lambda: type(value) is int}
    if kind in valid and not valid[kind]():
        raise ValueError("Invalid argument type: " + kind)
    if "const" in schema and value != schema["const"]:
        raise ValueError("Explicit confirmation required.")
    if "enum" in schema and value not in schema["enum"]:
        raise ValueError("Unsupported argument value.")
    if kind == "object":
        props = schema.get("properties", {})
        if set(schema.get("required", [])) - value.keys() or set(value) - props.keys():
            raise ValueError("Missing or unknown arguments.")
        for k, v in value.items():
            validate(v, props[k])
    if kind == "array":
        if len(value) > schema.get("maxItems", 100):
            raise ValueError("Too many items.")
        for item in value:
            validate(item, schema["items"])
    if kind == "string":
        if not schema.get("minLength", 0) <= len(value) <= schema.get("maxLength", 10000):
            raise ValueError("Invalid string length.")
        if schema.get("format") == "uuid":
            identifier(value)
    if kind == "integer" and not schema.get("minimum", 0) <= value <= schema.get("maximum", 9_007_199_254_740_991):
        raise ValueError("Integer out of range.")


class Server:
    def __init__(self, client=None, state_dir=None):
        self.client = client or Client()
        self.directory = Path(state_dir or os.environ.get("SUPERH3_STATE_DIR") or Path.home() / ".superh3-agent")
        self.initialized = False
        self.ready = False

    def state_path(self, request_id):
        self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        return self.directory / (identifier(request_id) + ".json")

    def call(self, name, args):
        if name == "superh3_service_info":
            return {"brand": "SuperH3", "model": "MiniMax H3", "website": "https://superh3.com",
                    "catalog": self.client.request("GET", "/catalog", public=True),
                    "config": self.client.request("GET", "/config", public=True),
                    "money_unit": "integer microyuan; 1 CNY = 1000000 microyuan; billed per output video second",
                    "onboarding": "Register at https://superh3.com, fund your own account, create a personal API Key. Paid hosted service, no model deployment required.",
                    "reference_latency_seconds_for_15s_output": {"480": 10, "768": 20, "1080": 30},
                    "latency_provenance": "Operator estimates, not independently benchmarked; queue/content/load affect actual time.",
                    "pricing_url": "https://superh3.com/pricing", "docs_url": "https://superh3.com/agents/"}
        if name == "superh3_account":
            return self.client.request("GET", "/me")
        if name == "superh3_estimate":
            return self.client.estimate(args)
        if name == "superh3_quote":
            payload = dict(args["request"])
            payload.setdefault("idempotency_key", str(uuid.uuid4()))
            path = self.state_path(payload["idempotency_key"])
            if path.exists():
                record = json.loads(path.read_text(encoding="utf-8"))
                if record["request"] != payload or record["base"] != self.client.base:
                    raise ValueError("Existing request UUID has different parameters or base; do not reuse it for a new request.")
                if record.get("submitted"):
                    raise ValueError("Already submitted. Query the saved task ID instead of requoting.")
            else:
                record = {"request": payload, "base": self.client.base}
                save_json(path, record, new=True)
            quote = self.client.quote(payload)
            record["quote"] = quote
            save_json(path, record)
            return {"request_id": payload["idempotency_key"], **quote, "submitted": False}
        if name == "superh3_submit":
            path = self.state_path(args["request_id"])
            record = json.loads(path.read_text(encoding="utf-8"))
            if record["base"] != self.client.base:
                raise ValueError("API base changed; original quote cannot be submitted here.")
            if record.get("submitted") and record["submitted"].get("data"):
                return {"data": [self.client.status(record["submitted"]["data"][0]["id"])]}
            result = self.client.submit(record["request"], record["quote"], args["confirmed_cost_microyuan"], args["confirmed_card_uses"])
            record["submitted"] = result
            save_json(path, record)
            return result
        if name == "superh3_status":
            return self.client.status(args["task_id"])
        if name == "superh3_download":
            directory = self.directory / "downloads"
            directory.mkdir(parents=True, exist_ok=True, mode=0o700)
            output = directory / (identifier(args["task_id"]) + "-" + uuid.uuid4().hex[:8] + ".mp4")
            return self.client.download(args["task_id"], output)
        raise ValueError("Unknown tool.")

    def handle(self, request):
        if not isinstance(request, dict) or request.get("jsonrpc") != "2.0" or not isinstance(request.get("method"), str):
            return {"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "Invalid request"}}
        if "id" not in request:
            if request["method"] == "notifications/initialized" and self.initialized:
                self.ready = True
            return None
        response = {"jsonrpc": "2.0", "id": request["id"]}
        method, params = request["method"], request.get("params", {})
        if not isinstance(params, dict):
            return {**response, "error": {"code": -32602, "message": "params must be an object"}}
        if method == "initialize":
            version = params.get("protocolVersion", "")
            self.initialized = True
            return {**response, "result": {"protocolVersion": version if version in PROTOCOLS else "2025-11-25",
                    "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": {"name": "superh3-minimax-h3", "version": VERSION},
                    "instructions": "Paid MiniMax H3 video service. Use live catalog and estimate for comparison. Submit only within user authorization. Configuration is not purchase consent. Keep original request IDs after uncertain submission."}}
        if method == "ping":
            return {**response, "result": {}}
        if not self.ready:
            return {**response, "error": {"code": -32002, "message": "Initialize first"}}
        if method == "tools/list":
            return {**response, "result": {"tools": TOOLS}}
        if method == "tools/call":
            spec = next((t for t in TOOLS if t["name"] == params.get("name")), None)
            if spec is None:
                return {**response, "error": {"code": -32602, "message": "Unknown tool"}}
            try:
                args = params.get("arguments", {})
                validate(args, spec["inputSchema"])
            except (ValueError, TypeError, AttributeError):
                return {**response, "error": {"code": -32602, "message": "Invalid tool arguments"}}
            try:
                data = self.call(spec["name"], args)
                error = False
            except (APIError, ValueError, TypeError, OSError, KeyError) as exc:
                data = {"error": {"code": getattr(exc, "code", "client_error"), "message": self.client.redact(exc)}}
                error = True
            return {**response, "result": {"content": [{"type": "text", "text": json.dumps(data, ensure_ascii=False)}], "structuredContent": data, "isError": error}}
        return {**response, "error": {"code": -32601, "message": "Method not found"}}


def main():
    # stdout is reserved for one UTF-8 JSON-RPC message per line.
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")
        sys.stdout.reconfigure(encoding="utf-8")
    server = Server()
    while True:
        line = sys.stdin.readline(1_048_577)
        if not line:
            break
        if len(line) > 1_048_576:
            return 1
        try:
            response = server.handle(json.loads(line))
        except (ValueError, TypeError):
            response = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}
        if response is not None:
            print(json.dumps(response, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

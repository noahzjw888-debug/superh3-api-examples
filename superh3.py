#!/usr/bin/env python3
"""SuperH3 client: Python 3.9+, stdlib only. No automatic paid retries."""
import argparse
import hashlib
import json
import mimetypes
import os
from pathlib import Path
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

VERSION = "2.0.0"
BASE_URL = "https://superh3.com/api/v1"
FIELDS = {"mode", "prompt", "resolution", "seconds", "aspect", "first_frame", "last_frame", "references", "project_id", "card_id", "accepted_policy", "idempotency_key", "quote_token"}
ACTIVE = {"queued", "preparing", "submit_intent", "processing", "submission_unknown"}


class APIError(Exception):
    def __init__(self, code, message, status=0, retry_after=0):
        super().__init__(message)
        self.code, self.status, self.retry_after = code, status, retry_after


def identifier(value):
    if not isinstance(value, str) or str(uuid.UUID(value)) != value.lower():
        raise ValueError("Expected a UUID, not a URL or path.")
    return value


def validate_payload(payload):
    if not isinstance(payload, dict) or set(payload) - FIELDS:
        raise ValueError("Unknown request fields. See openapi.json.")
    if not isinstance(payload.get("prompt"), str) or not 1 <= len(payload["prompt"].strip()) <= 7000:
        raise ValueError("Prompt must contain 1–7000 characters.")
    if payload.get("resolution") not in {"480", "768", "1080"}:
        raise ValueError("Resolution must be a string: 480, 768 or 1080.")
    if type(payload.get("seconds")) is not int or not 5 <= payload["seconds"] <= 15:
        raise ValueError("Seconds must be an integer from 5 to 15.")
    if payload.get("aspect") not in {"adaptive", "21:9", "16:9", "4:3", "1:1", "3:4", "9:16"}:
        raise ValueError("Unsupported aspect ratio.")
    if type(payload.get("accepted_policy")) is not bool:
        raise ValueError("accepted_policy must be a boolean.")
    identifier(payload.get("idempotency_key"))
    first, last, refs = payload.get("first_frame"), payload.get("last_frame"), payload.get("references", [])
    if not isinstance(refs, list) or len(refs) > 12:
        raise ValueError("references must contain at most 12 owned asset UUIDs.")
    mode = payload.get("mode")
    valid = {"text": not (first or last or refs), "image": bool(first) and not (last or refs),
             "frames": bool(first and last) and not refs, "reference": bool(refs) and not (first or last)}
    if not valid.get(mode, False):
        raise ValueError("Mode and input assets do not match; no automatic mode fallback.")
    for item in [first, last, payload.get("project_id"), payload.get("card_id")] + refs:
        if item:
            identifier(item)


def save_json(path, value, new=False):
    path = Path(path)
    # Exclusive creation protects prior requests and results from accidental overwrite.
    if new:
        with path.open("x", encoding="utf-8") as file:
            json.dump(value, file, ensure_ascii=False, indent=2)
            file.flush()
            os.fsync(file.fileno())
    else:
        temp = path.with_name(path.name + "." + str(uuid.uuid4()) + ".tmp")
        save_json(temp, value, new=True)
        os.replace(temp, path)


def fingerprint(payload):
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


class Client:
    def __init__(self, base=None, key=None, timeout=30):
        self.base = (base or os.environ.get("SUPERH3_BASE_URL") or BASE_URL).rstrip("/")
        url = urllib.parse.urlsplit(self.base)
        if url.username or url.password or url.query or url.fragment or url.path != "/api/v1":
            raise ValueError("Use the documented /api/v1 base URL without credentials or query.")
        if url.scheme != "https" and not (url.scheme == "http" and url.hostname in {"127.0.0.1", "localhost", "::1"}):
            raise ValueError("HTTPS is required except for explicit local testing.")
        self.key = key if key is not None else os.environ.get("SUPERH3_API_KEY", "").strip()
        self.timeout = timeout
        self.opener = urllib.request.build_opener(NoRedirect)

    def redact(self, value):
        return str(value).replace(self.key, "[REDACTED]") if self.key else str(value)

    def open(self, method, path, payload=None, public=False, content_type="application/json"):
        if not path.startswith("/") or ".." in path or "?" in path:
            raise ValueError("Only documented relative API paths are accepted.")
        headers = {"User-Agent": "superh3-agent-kit/" + VERSION, "Accept": "application/json"}
        if not public:
            if not self.key or self.key.startswith(("YOUR_", "sh3_REPLACE")):
                raise ValueError("Configure your personal SUPERH3_API_KEY in the local environment.")
            headers["Authorization"] = "Bearer " + self.key
        if payload is not None:
            headers["Content-Type"] = content_type
            if not isinstance(payload, bytes):
                payload = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(self.base + path, data=payload, headers=headers, method=method)
        try:
            return self.opener.open(request, timeout=self.timeout)
        except urllib.error.HTTPError as error:
            raw = error.read(65536).decode("utf-8", errors="replace")
            try:
                detail = json.loads(raw).get("error", {})
                if not isinstance(detail, dict):
                    detail = {}
            except ValueError:
                detail = {}
            try:
                retry = float(error.headers.get("Retry-After", detail.get("retry_after", 0)))
            except (ValueError, TypeError):
                retry = 5
            raise APIError(detail.get("code", "http_error"), self.redact(detail.get("message", "HTTP " + str(error.code))), error.code, max(0, retry)) from None
        except (urllib.error.URLError, TimeoutError, OSError):
            raise APIError("network_error", "Network failure. Preserve the request UUID and task ID; do not create a new task.") from None

    def request(self, method, path, payload=None, public=False, content_type="application/json"):
        with self.open(method, path, payload, public, content_type) as response:
            try:
                result = json.loads(self.redact(response.read(4_000_000).decode("utf-8")))
                if not isinstance(result, dict):
                    raise ValueError()
                return result
            except (ValueError, UnicodeError):
                raise APIError("invalid_response", "Expected an API JSON object, not an HTML page.") from None

    def estimate(self, payload):
        body = {k: payload[k] for k in ("mode", "resolution", "seconds", "card_id") if k in payload}
        return self.request("POST", "/quotes/estimate", body)

    def quote(self, payload):
        validate_payload(payload)
        if payload["accepted_policy"] is not True:
            raise ValueError("Terms and input rights must be accepted before a formal quote.")
        result = self.request("POST", "/quotes", payload)
        if type(result.get("cost")) is not int or result["cost"] < 0 or result.get("currency") != "CNY" or not result.get("quote_token"):
            raise APIError("invalid_quote", "Incomplete quote; no submission made.")
        return result

    def submit(self, payload, quote, confirmed_cost, confirmed_card_uses=0):
        validate_payload(payload)
        if payload["accepted_policy"] is not True or type(confirmed_cost) is not int or confirmed_cost < 0:
            raise ValueError("Explicit policy acceptance and exact confirmed cost are required.")
        if quote.get("currency") != "CNY" or quote.get("cost") != confirmed_cost or quote.get("card_uses") != confirmed_card_uses:
            raise ValueError("Quote differs from confirmed payment. Confirm the new quote before submitting.")
        if not quote.get("quote_token") or quote.get("generation_mode") not in {"live", "simulation", "mixed"}:
            raise ValueError("Quote token or available generation channel missing.")
        # One request only. Server quote_changed/idempotency checks remain authoritative.
        return self.request("POST", "/generations", dict(payload, quote_token=quote["quote_token"]))

    def status(self, task_id):
        result = self.request("GET", "/generations/" + identifier(task_id))
        if not result.get("data"):
            raise APIError("not_found", "Task not found in this account.")
        return result["data"][0]

    def wait(self, task_id, timeout=900, interval=4):
        deadline = time.monotonic() + timeout
        interval = max(3, interval)
        while time.monotonic() < deadline:
            try:
                task = self.status(task_id)
            except APIError as error:
                if error.status != 429 and error.code != "network_error" and error.status < 500:
                    raise
                delay = max(interval, error.retry_after)
            else:
                if task.get("state") == "completed":
                    return task
                if task.get("state") in {"failed", "cancelled"}:
                    raise APIError(task.get("error_code") or task["state"], "Task " + task["state"] + "; no retry generation was created.")
                if task.get("state") not in ACTIVE:
                    raise APIError("unknown_state", "Unrecognized state; query the same task ID.")
                delay = 15 if task["state"] == "submission_unknown" else interval
            time.sleep(max(0, min(delay, deadline - time.monotonic())))
        raise APIError("wait_timeout", "Waiting timed out; the original task continues. Resume with the same ID: " + task_id)

    def download(self, task_id, output):
        task = self.status(task_id)
        if task.get("state") != "completed" or task.get("result_available") is not True or not task.get("result_asset_id"):
            raise APIError("result_unavailable", "Task is incomplete or its result has expired; no new task was created.")
        path = Path(output)
        if path.exists():
            raise ValueError("Output exists; select a new filename.")
        partial = path.with_name(path.name + ".part")
        # No redirects (including cross-origin redirects) can receive the user's key.
        size, digest = 0, hashlib.sha256()
        with self.open("GET", "/assets/" + identifier(task["result_asset_id"]) + "/file") as response:
            mime = response.headers.get("Content-Type", "").split(";")[0]
            if mime not in {"video/mp4", "video/webm", "video/quicktime", "application/octet-stream"}:
                raise APIError("invalid_download", "Expected a video, not an HTML or JSON response.")
            with partial.open("xb") as file:
                while True:
                    chunk = response.read(1_048_576)
                    if not chunk:
                        break
                    file.write(chunk)
                    digest.update(chunk)
                    size += len(chunk)
            expected = response.headers.get("Content-Length")
            if size == 0 or (expected and size != int(expected)):
                raise APIError("incomplete_download", "Incomplete download retained as .part; retry download only.")
        # Hard link creates the final name exclusively, never overwriting a race winner.
        os.link(partial, path)
        partial.unlink()
        return {"path": str(path.resolve()), "bytes": size, "sha256": digest.hexdigest(), "task_id": task_id, "local_test": task.get("local_test", False)}

    def upload(self, kind, source):
        if kind not in {"image", "video", "audio"}:
            raise ValueError("Upload kind must be image, video or audio.")
        path = Path(source)
        limit = 50_000_000 if kind == "video" else 20_000_000
        if not 0 < path.stat().st_size <= limit:
            raise ValueError("File exceeds documented upload limits.")
        boundary = "superh3-" + uuid.uuid4().hex
        # Sanitized filename prevents multipart header injection.
        filename = "asset" + path.suffix.lower().replace('"', "")
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        body = ('--' + boundary + '\r\nContent-Disposition: form-data; name="file"; filename="' + filename + '"\r\nContent-Type: ' + mime + '\r\n\r\n').encode()
        body += path.read_bytes() + ('\r\n--' + boundary + '--\r\n').encode()
        return self.request("POST", "/uploads/" + kind, body, content_type="multipart/form-data; boundary=" + boundary)


def main(argv=None):
    parser = argparse.ArgumentParser(description="SuperH3: quote → confirm → submit → wait → download. Paid generation requires explicit consent.")
    subs = parser.add_subparsers(dest="command", required=True)
    prep = subs.add_parser("prepare")
    prep.add_argument("--prompt", required=True)
    prep.add_argument("--resolution", choices=["480", "768", "1080"], default="480")
    prep.add_argument("--seconds", type=int, default=5)
    prep.add_argument("--aspect", default="16:9")
    prep.add_argument("--request", type=Path, default=Path("request.json"))
    for name in ("estimate", "quote", "submit"):
        sub = subs.add_parser(name)
        sub.add_argument("--request", type=Path, default=Path("request.json"))
        if name == "quote":
            sub.add_argument("--accept-policy", action="store_true")
        if name == "submit":
            sub.add_argument("--confirmed-cost-microyuan", type=int, required=True)
            sub.add_argument("--confirmed-card-uses", type=int, choices=[0, 1], default=0)
    subs.add_parser("account")
    subs.add_parser("catalog")
    for name in ("status", "wait", "download"):
        sub = subs.add_parser(name)
        sub.add_argument("--id", required=True)
        if name == "wait":
            sub.add_argument("--timeout", type=int, default=900)
        if name == "download":
            sub.add_argument("--output", type=Path, required=True)
    upload = subs.add_parser("upload")
    upload.add_argument("--kind", choices=["image", "video", "audio"], required=True)
    upload.add_argument("--file", type=Path, required=True)
    args = parser.parse_args(argv)
    client = Client()
    try:
        if args.command == "prepare":
            payload = dict(mode="text", prompt=args.prompt, resolution=args.resolution, seconds=args.seconds,
                           aspect=args.aspect, accepted_policy=False, idempotency_key=str(uuid.uuid4()))
            validate_payload(payload)
            save_json(args.request, payload, new=True)
            result = {"request": str(args.request), "idempotency_key": payload["idempotency_key"], "submitted": False}
        elif args.command in {"estimate", "quote", "submit"}:
            payload = json.loads(args.request.read_text(encoding="utf-8-sig"))
            quote_path = args.request.with_name(args.request.name + ".quote.json")
            task_path = args.request.with_name(args.request.name + ".task.json")
            if args.command == "estimate":
                result = client.estimate(payload)
            elif args.command == "quote":
                if args.accept_policy:
                    payload["accepted_policy"] = True
                    save_json(args.request, payload)
                result = client.quote(payload)
                save_json(quote_path, {"base": client.base, "fingerprint": fingerprint(payload), "quote": result})
            else:
                record = json.loads(quote_path.read_text(encoding="utf-8"))
                if record["base"] != client.base or record["fingerprint"] != fingerprint(payload):
                    raise ValueError("Request or API base changed; obtain and confirm a new quote.")
                result = client.submit(payload, record["quote"], args.confirmed_cost_microyuan, args.confirmed_card_uses)
                save_json(task_path, result)
        elif args.command == "account":
            result = client.request("GET", "/me")
        elif args.command == "catalog":
            result = client.request("GET", "/catalog", public=True)
        elif args.command == "status":
            result = client.status(args.id)
        elif args.command == "wait":
            result = client.wait(args.id, args.timeout)
        elif args.command == "download":
            result = client.download(args.id, args.output)
        else:
            result = client.upload(args.kind, args.file)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (APIError, ValueError, OSError, KeyError, TypeError) as error:
        print(json.dumps({"error": {"code": getattr(error, "code", "client_error"), "message": client.redact(error)}}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

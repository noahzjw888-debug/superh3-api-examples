#!/usr/bin/env python3
"""Minimal, bring-your-own-key SuperH3 client; Python 3.9+ standard library."""

import argparse
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid

BASE_URL = "https://superh3.com/api/v1"


def validate_payload(payload):
    if not isinstance(payload, dict) or payload.get("mode") != "text":
        raise ValueError("This example supports mode=text only.")
    prompt = payload.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip() or len(prompt) > 7000:
        raise ValueError("Prompt must contain 1–7000 Unicode characters.")
    if payload.get("resolution") not in {"480", "768", "1080"}:
        raise ValueError("Resolution must be 480, 768 or 1080.")
    seconds = payload.get("seconds")
    if type(seconds) is not int or not 5 <= seconds <= 15:
        raise ValueError("Seconds must be an integer from 5 to 15.")
    if not isinstance(payload.get("aspect"), str) or not payload["aspect"]:
        raise ValueError("Aspect must be a non-empty value supported by the service.")
    if type(payload.get("accepted_policy")) is not bool:
        raise ValueError("accepted_policy must be a boolean.")
    value = payload.get("idempotency_key")
    if not isinstance(value, str):
        raise ValueError("The saved request must contain a UUID idempotency_key.")
    uuid.UUID(value)


def save_payload(path, payload, *, new=False):
    with path.open("x" if new else "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def api_request(method, path, payload=None):
    key = os.environ.get("SUPERH3_API_KEY", "").strip()
    if not key or key in {"YOUR_PERSONAL_API_KEY", "REPLACE_WITH_YOUR_OWN_KEY"}:
        raise ValueError("Set SUPERH3_API_KEY to your own key. Never publish it.")
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        BASE_URL + path,
        data=body,
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json", "Accept": "application/json"},
        method=method,
    )
    # Never retry submissions automatically. Reuse the saved UUID on a manual retry.
    # Reject redirects so the Authorization header cannot be sent to another host.
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None

    opener = urllib.request.build_opener(NoRedirect)
    try:
        with opener.open(request, timeout=60) as response:
            raw = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as error:
        raw = error.read().decode("utf-8", errors="replace").replace(key, "[REDACTED]")
        print("HTTP " + str(error.code) + "\n" + raw, file=sys.stderr)
        return 1
    except (urllib.error.URLError, TimeoutError) as error:
        message = str(error).replace(key, "[REDACTED]")
        print("Network error: " + message, file=sys.stderr)
        print("If submission may have reached the service, keep the same request file and UUID. Query an existing task ID if available.", file=sys.stderr)
        return 1
    raw = raw.replace(key, "[REDACTED]")
    try:
        print(json.dumps(json.loads(raw), ensure_ascii=False, indent=2))
    except json.JSONDecodeError:
        print(raw)
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="Paid SuperH3 API example. Use your own funded account and API key.")
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare", help="Save a local request; no network or charge.")
    prepare.add_argument("--prompt", required=True)
    prepare.add_argument("--resolution", choices=["480", "768", "1080"], default="1080")
    prepare.add_argument("--seconds", type=int, choices=range(5, 16), default=15)
    prepare.add_argument("--aspect", default="16:9")
    prepare.add_argument("--request", type=Path, default=Path("request.json"))
    submit = commands.add_parser("submit", help="Submit a paid generation using a saved request.")
    submit.add_argument("--request", type=Path, default=Path("request.json"))
    submit.add_argument("--accept-policy", action="store_true", help="Accept the website's current service policy for this request.")
    status = commands.add_parser("status", help="Query an existing task; does not create a new generation.")
    status.add_argument("--id", required=True, help="Actual task ID returned by the service.")
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            payload = {"mode": "text", "prompt": args.prompt, "resolution": args.resolution,
                       "seconds": args.seconds, "aspect": args.aspect,
                       "accepted_policy": False, "idempotency_key": str(uuid.uuid4())}
            validate_payload(payload)
            save_payload(args.request, payload, new=True)
            print("Local request saved: " + str(args.request) + ". No API request sent.")
            return 0
        if args.command == "submit":
            payload = json.loads(args.request.read_text(encoding="utf-8"))
            validate_payload(payload)
            if payload["accepted_policy"] is not True:
                if not args.accept_policy:
                    raise ValueError("Review the website's current fees and service policy, then use --accept-policy.")
                payload["accepted_policy"] = True
                save_payload(args.request, payload)
            return api_request("POST", "/generations", payload)
        if not args.id.strip():
            raise ValueError("Task ID must not be empty.")
        return api_request("GET", "/generations/" + urllib.parse.quote(args.id, safe=""))
    except (ValueError, OSError) as error:
        key = os.environ.get("SUPERH3_API_KEY", "")
        message = str(error)
        if key:
            message = message.replace(key, "[REDACTED]")
        print(message, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

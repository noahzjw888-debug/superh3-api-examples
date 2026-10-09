"""Contract/regression tests. The HTTP service below is explicitly a mock, never a video benchmark."""
import copy
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
import uuid
from superh3 import Client, APIError, validate_payload
from superh3_mcp import Server, TOOLS

TASK = "11111111-1111-4111-8111-111111111111"
ASSET = "22222222-2222-4222-8222-222222222222"
BODY = b"\x00\x00\x00\x18ftypmp42MOCK_NOT_GENERATED_VIDEO"


class ContractHandler(BaseHTTPRequestHandler):
    events = []
    state = "completed"
    def log_message(self, *args):
        pass
    def send(self, value, status=200, mime="application/json"):
        raw = value if isinstance(value, bytes) else json.dumps(value).encode()
        self.send_response(status)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)
    def do_GET(self):
        self.events.append(("GET", self.path, None))
        if self.path == "/api/v1/redirect":
            self.send_response(302); self.send_header("Location", "http://example.invalid/"); self.end_headers()
        elif self.path.endswith("/file"):
            self.send(BODY, mime="video/mp4")
        elif "/generations/" in self.path:
            self.send({"data": [{"id": TASK, "state": self.state, "result_asset_id": ASSET, "result_available": True, "local_test": True}]})
        else:
            self.send({"data": [], "features": {"generation": True}, "local_test": True})
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
        self.events.append(("POST", self.path, body))
        if self.path.endswith("/quotes/estimate"):
            self.send({"cost": 500000, "currency": "CNY", "card_uses": 0, "estimate_only": True, "generation_mode": "simulation"})
        elif self.path.endswith("/quotes"):
            self.send({"cost": 500000, "currency": "CNY", "card_uses": 0, "quote_token": "MOCK_QUOTE_NOT_A_CREDENTIAL", "generation_mode": "simulation"})
        elif self.path.endswith("/generations"):
            if body.get("quote_token") != "MOCK_QUOTE_NOT_A_CREDENTIAL":
                self.send({"error": {"code": "quote_changed", "message": "Get a fresh quote"}}, 409)
            else:
                self.send({"data": [{"id": TASK, "state": "queued", "local_test": True}]})
        else:
            self.send({"error": {"code": "not_found", "message": "Missing"}}, 404)


class AgentKitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.http = ThreadingHTTPServer(("127.0.0.1", 0), ContractHandler)
        threading.Thread(target=cls.http.serve_forever, daemon=True).start()
        cls.base = f"http://127.0.0.1:{cls.http.server_port}/api/v1"
    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown(); cls.http.server_close()
    def setUp(self):
        ContractHandler.events = []; ContractHandler.state = "completed"
        self.client = Client(self.base, key="TEST_PLACEHOLDER")
        self.payload = dict(mode="text", prompt="清晨的花园", resolution="480", seconds=5, aspect="16:9", accepted_policy=True, idempotency_key=str(uuid.uuid4()))
    def test_quote_submit_status_download(self):
        estimate = self.client.estimate(self.payload)
        self.assertNotIn("quote_token", estimate)
        self.assertEqual(set(ContractHandler.events[-1][2]), {"mode", "resolution", "seconds"})
        quote = self.client.quote(self.payload)
        response = self.client.submit(self.payload, quote, 500000)
        self.assertEqual(response["data"][0]["id"], TASK)
        self.assertEqual(self.client.wait(TASK)["state"], "completed")
        with tempfile.TemporaryDirectory() as tmp:
            result = self.client.download(TASK, Path(tmp) / "test.mp4")
            self.assertTrue(result["local_test"])
            self.assertEqual(result["bytes"], len(BODY))
            with self.assertRaises(ValueError):
                self.client.download(TASK, Path(tmp) / "test.mp4")
    def test_exact_cost_and_card_confirmation_before_network(self):
        quote = self.client.quote(self.payload)
        before = len(ContractHandler.events)
        for cost, card in [(499999, 0), (500000, 1), (True, 0), (-1, 0)]:
            with self.assertRaises(ValueError): self.client.submit(self.payload, quote, cost, card)
        self.assertEqual(len(ContractHandler.events), before)
    def test_terms_not_assumed(self):
        self.payload["accepted_policy"] = False
        with self.assertRaises(ValueError): self.client.quote(self.payload)
        self.assertEqual(ContractHandler.events, [])
    def test_changed_price_error_and_stable_id(self):
        quote = self.client.quote(self.payload)
        quote["quote_token"] = "STALE"
        with self.assertRaises(APIError) as caught: self.client.submit(self.payload, quote, 500000)
        self.assertEqual(caught.exception.code, "quote_changed")
        posts = [b for m, p, b in ContractHandler.events if p.endswith("/generations")]
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0]["idempotency_key"], self.payload["idempotency_key"])
    def test_redirect_refused(self):
        with self.assertRaises(APIError) as caught: self.client.request("GET", "/redirect")
        self.assertEqual(caught.exception.status, 302)
    def test_unknown_submission_never_generates(self):
        ContractHandler.state = "submission_unknown"
        with patch("superh3.time.monotonic", side_effect=[0, 0, 2, 2]), patch("superh3.time.sleep"):
            with self.assertRaises(APIError) as caught: self.client.wait(TASK, timeout=1)
        self.assertEqual(caught.exception.code, "wait_timeout")
        self.assertTrue(all(method == "GET" for method, _, _ in ContractHandler.events))
    def test_validation(self):
        for changes in [{"seconds": True}, {"seconds": 4}, {"resolution": "480P"}, {"mode": "image"}, {"aspect": "nonsense"}, {"references": "bad"}, {"model": "unrecognized"}]:
            with self.assertRaises(ValueError): validate_payload({**self.payload, **changes})
        validate_payload({**self.payload, "mode": "image", "first_frame": ASSET})
    def test_mcp_protocol_and_persisted_workflow(self):
        with tempfile.TemporaryDirectory() as tmp:
            server = Server(self.client, tmp)
            init = server.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-11-25"}})
            self.assertEqual(init["result"]["protocolVersion"], "2025-11-25")
            self.assertIsNone(server.handle({"jsonrpc": "2.0", "method": "notifications/initialized"}))
            tools = server.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})["result"]["tools"]
            self.assertEqual(len(tools), 7)
            def call(name, arguments):
                return server.handle({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "superh3_" + name, "arguments": arguments}})
            receipt = call("quote", {"request": self.payload})["result"]["structuredContent"]
            confirm = {"request_id": receipt["request_id"], "confirmed_cost_microyuan": 500000, "confirmed_card_uses": 0, "user_authorized": True}
            self.assertIn("error", call("submit", {**confirm, "user_authorized": False}))
            self.assertFalse(call("submit", confirm)["result"]["isError"])
            server.client = self.client
            # Saved receipt survives server reconstruction; a retry queries the original task.
            server = Server(self.client, tmp); server.ready = True
            result = server.call("superh3_submit", confirm)
            self.assertEqual(result["data"][0]["id"], TASK)
            self.assertEqual(sum(p.endswith("/generations") for _, p, _ in ContractHandler.events), 1)
            with self.assertRaises(ValueError): server.call("superh3_quote", {"request": {**self.payload, "prompt": "changed"}})
    def test_stdio_real_subprocess(self):
        messages = [{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18"}}, {"jsonrpc":"2.0","method":"notifications/initialized"}, {"jsonrpc":"2.0","id":2,"method":"tools/list"}, {"jsonrpc":"2.0","id":3,"method":"ping"}]
        result = subprocess.run([sys.executable, str(Path(__file__).with_name("superh3_mcp.py"))], input="\n".join(map(json.dumps, messages))+"\n", capture_output=True, text=True, encoding="utf-8", timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        replies = [json.loads(line) for line in result.stdout.splitlines()]
        self.assertEqual([r["id"] for r in replies], [1,2,3])
        self.assertEqual(len(replies[1]["result"]["tools"]), 7)
    def test_node_client_contract(self):
        module = Path(__file__).with_name("superh3.mjs").as_uri()
        code = f'''import {{SuperH3}} from {json.dumps(module)};
const c = new SuperH3({{base: {json.dumps(self.base)}, key:'TEST_PLACEHOLDER'}});
const r={json.dumps(self.payload)}; const q=await c.quote(r);
let refused=false;try {{await c.submit(r,q,{{confirmedCostMicroyuan:500000,userAuthorized:false}})}} catch {{refused=true}}
if(!refused)throw Error('missing consent gate');
const task=await c.submit(r,q,{{confirmedCostMicroyuan:500000,userAuthorized:true}});
if(task.data[0].id!=={json.dumps(TASK)})throw Error('wrong response mapping');
console.log('ok');'''
        result = subprocess.run(["node", "--input-type=module", "-e", code], capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_powershell_native_json_and_download(self):
        script = str(Path(__file__).with_name('superh3.ps1'))
        env = {**os.environ, 'SUPERH3_BASE_URL':self.base, 'SUPERH3_API_KEY':'TEST_PLACEHOLDER'}
        with tempfile.TemporaryDirectory() as tmp:
            request = Path(tmp)/'request.json'
            request.write_text(json.dumps(self.payload, ensure_ascii=False), encoding='utf-8')
            def invoke(action, *args):
                result = subprocess.run(['pwsh','-NoProfile','-File',script,'-Action',action,'-RequestFile',str(request),*args], env=env, capture_output=True, text=True, encoding='utf-8', timeout=30)
                self.assertEqual(result.returncode, 0, result.stderr)
                return json.loads(result.stdout)
            self.assertEqual(invoke('Estimate')['cost'], 500000)
            self.assertEqual(set(ContractHandler.events[-1][2]), {'mode','resolution','seconds'})
            self.assertEqual(invoke('Quote')['cost'], 500000)
            self.assertEqual(invoke('Submit','-UserAuthorized','-ConfirmedCostMicroyuan','500000')['data'][0]['id'], TASK)
            self.assertEqual(ContractHandler.events[-1][2]['prompt'], self.payload['prompt'])
            output = Path(tmp)/'result.mp4'
            self.assertTrue(invoke('Download','-TaskId',TASK,'-OutputFile',str(output))['local_test'])
            self.assertEqual(output.read_bytes(), BODY)


if __name__ == "__main__":
    unittest.main(verbosity=2)

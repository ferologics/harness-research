"""A scripted OpenAI-compatible chat-completions server for testing duals without a real model.

The script is a JSON list of steps. Each request answers with the next step: either a
tool call `{"tool": name, "arguments": {...}}` or a final text `{"text": "..."}`. Every
request body is appended to the log file so tests can check what the harness sent.

Usage:
    python fake_model.py <port> <script.json> <requests.jsonl>
"""

import json
import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(sys.argv[1])
STEPS = json.load(open(sys.argv[2]))
LOG = sys.argv[3]
state = {"step": 0}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def chunk(self, delta, finish=None):
        body = {
            "id": "fake",
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": "fake-model",
            "choices": [{"index": 0, "delta": delta, "finish_reason": finish}],
        }
        self.wfile.write(f"data: {json.dumps(body)}\n\n".encode())

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        with open(LOG, "a") as log:
            log.write(json.dumps(body) + "\n")
        step = STEPS[min(state["step"], len(STEPS) - 1)]
        state["step"] += 1
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.end_headers()
        if "tool" in step:
            call = {
                "index": 0,
                "id": f"call_{state['step']}",
                "type": "function",
                "function": {"name": step["tool"], "arguments": json.dumps(step["arguments"])},
            }
            self.chunk({"role": "assistant", "tool_calls": [call]})
            self.chunk({}, "tool_calls")
        else:
            self.chunk({"role": "assistant", "content": step["text"]})
            self.chunk({}, "stop")
        usage = {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
        self.wfile.write(f"data: {json.dumps({'id': 'fake', 'object': 'chat.completion.chunk', 'created': 0, 'model': 'fake-model', 'choices': [], 'usage': usage})}\n\n".encode())
        self.wfile.write(b"data: [DONE]\n\n")


HTTPServer(("127.0.0.1", PORT), Handler).serve_forever()

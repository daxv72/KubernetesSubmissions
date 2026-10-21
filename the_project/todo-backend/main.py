"""Todo backend — exercise 2.2.

GET /todos returns the in-memory list as JSON.
POST /todos adds one todo. A browser form is redirected back to /.
The list is lost when the process stops.
"""

import json
import os
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("PORT", "3000"))
MAX_LENGTH = 140

# Seed matches the list shown before this exercise. New todos are appended.
todos = [
    "Learn Kubernetes basics",
    "Deploy application to cluster",
    "Configure persistent volumes",
]


def parse_todo(content_type: str, raw: bytes) -> str | None:
    if "application/json" in content_type:
        try:
            payload = json.loads(raw.decode())
        except json.JSONDecodeError:
            return None
        text = payload.get("todo", "") if isinstance(payload, dict) else ""
    else:
        fields = urllib.parse.parse_qs(raw.decode())
        text = fields.get("todo", [""])[0]
    text = str(text).strip()
    if not text or len(text) > MAX_LENGTH:
        return None
    return text


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0].rstrip("/") or "/"
        if path != "/todos":
            self.send_error(404)
            return
        body = json.dumps(todos).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        path = self.path.split("?", 1)[0].rstrip("/") or "/"
        if path != "/todos":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        todo = parse_todo(self.headers.get("Content-Type", ""), raw)
        if todo is None:
            body = b"Todo must be 1 to 140 characters.\n"
            self.send_response(400)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        todos.append(todo)
        # The browser form posts here. Send the user back to the HTML page.
        self.send_response(303)
        self.send_header("Location", "/")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, fmt: str, *args) -> None:
        print(f"{self.address_string()} {fmt % args}", flush=True)


def main() -> None:
    print(f"Server started in port {PORT}", flush=True)
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()

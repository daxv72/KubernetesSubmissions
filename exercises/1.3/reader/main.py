"""Log reader — exercise 2.5.

GET / returns the ConfigMap file, the MESSAGE variable, the latest log line,
and the ping-pong request count.
"""

import os
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("PORT", "3000"))
LOG_PATH = os.environ.get("LOG_PATH", "/usr/src/app/files/log.txt")
INFO_PATH = os.environ.get("INFO_PATH", "/usr/src/app/config/information.txt")
PING_PONG_URL = os.environ.get("PING_PONG_URL", "http://ping-pong:3000/pings")
MESSAGE = os.environ.get("MESSAGE", "")


def latest_line() -> str:
    try:
        with open(LOG_PATH, encoding="utf-8") as handle:
            lines = [line.strip() for line in handle.readlines() if line.strip()]
    except FileNotFoundError:
        return ""
    return lines[-1] if lines else ""


def file_content() -> str:
    try:
        with open(INFO_PATH, encoding="utf-8") as handle:
            return handle.read().strip()
    except FileNotFoundError:
        return ""


def ping_count() -> int:
    # Service DNS name, not the Pod IP. The Service stays while Pods are replaced.
    try:
        with urllib.request.urlopen(PING_PONG_URL, timeout=2) as response:
            raw = response.read().decode().strip()
        return int(raw)
    except (urllib.error.URLError, TimeoutError, ValueError):
        return 0


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]
        if path != "/":
            self.send_error(404)
            return
        text = (
            f"file content: {file_content()}\n"
            f"env variable: MESSAGE={MESSAGE}\n"
            f"{latest_line()}\n"
            f"Ping / Pongs: {ping_count()}\n"
        )
        body = text.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        print(f"{self.address_string()} {fmt % args}", flush=True)


def main() -> None:
    print(f"Server started in port {PORT}", flush=True)
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()

"""Log reader — exercise 1.11.

GET / returns the latest log line and the ping-pong request count.
Both files live on the persistent volume shared with the ping-pong Pod.
"""

import os
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("PORT", "3000"))
LOG_PATH = os.environ.get("LOG_PATH", "/usr/src/app/files/log.txt")
PINGS_PATH = os.environ.get("PINGS_PATH", "/usr/src/app/files/pings.txt")


def latest_line() -> str:
    try:
        with open(LOG_PATH, encoding="utf-8") as handle:
            lines = [line.strip() for line in handle.readlines() if line.strip()]
    except FileNotFoundError:
        return ""
    return lines[-1] if lines else ""


def ping_count() -> int:
    try:
        raw = open(PINGS_PATH, encoding="utf-8").read().strip()
    except FileNotFoundError:
        return 0
    try:
        return int(raw)
    except ValueError:
        return 0


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]
        if path != "/":
            self.send_error(404)
            return
        text = f"{latest_line()}\nPing / Pongs: {ping_count()}\n"
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

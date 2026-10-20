"""Ping-pong — exercise 1.11.

GET /pingpong returns "pong N" and then increments the counter.
The counter is a file on the shared persistent volume, so it survives a restart.
"""

import os
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("PORT", "3000"))
PINGS_PATH = os.environ.get("PINGS_PATH", "/usr/src/app/files/pings.txt")


def read_count() -> int:
    try:
        raw = open(PINGS_PATH, encoding="utf-8").read().strip()
    except FileNotFoundError:
        return 0
    try:
        return int(raw)
    except ValueError:
        return 0


def write_count(count: int) -> None:
    os.makedirs(os.path.dirname(PINGS_PATH), exist_ok=True)
    temporary = PINGS_PATH + ".tmp"
    with open(temporary, "w", encoding="utf-8") as handle:
        handle.write(f"{count}\n")
    os.replace(temporary, PINGS_PATH)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0].rstrip("/") or "/"
        if path != "/pingpong":
            self.send_error(404)
            return
        count = read_count()
        body = f"pong {count}\n".encode()
        write_count(count + 1)
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        # Show the request in kubectl logs.
        print(f"{self.address_string()} {fmt % args}", flush=True)


def main() -> None:
    print(f"Server started in port {PORT}", flush=True)
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()

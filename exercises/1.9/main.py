"""Ping-pong — exercise 2.1.

GET /pingpong returns "pong N" and then increments the counter.
GET /pings returns the current count and does not increment it.
The count lives in memory. Log output reads it over HTTP.
"""

import os
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("PORT", "3000"))

# One process, one counter. HTTPServer handles one request at a time.
count = 0


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        global count
        path = self.path.split("?", 1)[0].rstrip("/") or "/"
        if path == "/pingpong":
            body = f"pong {count}\n".encode()
            count += 1
        elif path == "/pings":
            # Read-only. Log output calls this on every page view.
            body = f"{count}\n".encode()
        else:
            self.send_error(404)
            return
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

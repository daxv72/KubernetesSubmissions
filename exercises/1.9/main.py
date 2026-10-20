"""Ping-pong — exercise 1.9.

GET /pingpong returns "pong N" and then increments an in-memory counter.
The counter starts at 0 and resets when the process restarts.
"""

import os
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("PORT", "3000"))

# In memory only. A restart sets it back to 0.
counter = 0


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        global counter
        path = self.path.split("?", 1)[0].rstrip("/") or "/"
        if path != "/pingpong":
            self.send_error(404)
            return
        body = f"pong {counter}\n".encode()
        counter += 1
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

"""Generic webhook — exercise 4.6.

Accepts the status JSON the broadcaster posts. The body is printed so
the cluster log is the record of what an external chat service would get.
WEBHOOK_URL on the broadcaster can point somewhere else instead.
"""

import os
from http.server import BaseHTTPRequestHandler, HTTPServer


def required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise SystemExit(f"Missing environment variable {name}")
    return value


PORT = int(required("PORT"))
BIND_ADDRESS = required("BIND_ADDRESS")


class Handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b""
        print(raw.decode(errors="replace"), flush=True)
        self.send_response(204)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, fmt: str, *args) -> None:
        print(f"{self.address_string()} {fmt % args}", flush=True)


def main() -> None:
    print(f"Server started in port {PORT}", flush=True)
    HTTPServer((BIND_ADDRESS, PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()

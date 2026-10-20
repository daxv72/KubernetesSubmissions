"""Log reader — exercise 1.10.

GET / returns the file written by the writer container.
The file is on a shared emptyDir, mounted at the same path in both containers.
"""

import os
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("PORT", "3000"))
LOG_PATH = os.environ.get("LOG_PATH", "/usr/src/app/files/log.txt")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]
        if path != "/":
            self.send_error(404)
            return
        try:
            with open(LOG_PATH, encoding="utf-8") as handle:
                text = handle.read()
        except FileNotFoundError:
            text = ""
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

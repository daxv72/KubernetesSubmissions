"""Log output — exercise 1.7.

On startup, generate a random string and keep it in memory.
Print it every 5 seconds with a UTC timestamp.
GET / returns the current timestamp and that same string.
"""

import os
import threading
import time
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("PORT", "3000"))

# Generated once: stays the same for the life of the process.
random_string = str(uuid.uuid4())


def timestamp() -> str:
    now = datetime.now(timezone.utc)
    millis = now.microsecond // 1000
    return now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{millis:03d}Z"


def status_line() -> str:
    return f"{timestamp()}: {random_string}"


def html_page() -> bytes:
    line = status_line()
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Log output</title>
</head>
<body>
  <h1>Log output</h1>
  <p>{line}</p>
</body>
</html>
""".encode()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]
        if path != "/":
            self.send_error(404)
            return

        body = html_page()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def log_loop() -> None:
    while True:
        # flush: without a TTY, Python buffers stdout and kubectl logs stays empty.
        print(status_line(), flush=True)
        time.sleep(5)


def main() -> None:
    threading.Thread(target=log_loop, daemon=True).start()
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()

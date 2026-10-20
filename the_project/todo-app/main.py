"""Todo app — exercise 1.5.

HTTP server. PORT chooses the port. On startup it prints
"Server started in port NNNN". GET / returns an HTML page.
"""

import os
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("PORT", "8080"))


def html_page(port: int) -> bytes:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Todo</title>
</head>
<body>
  <h1>Todo</h1>
  <p>The server is listening on port {port}.</p>
</body>
</html>
""".encode()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]
        if path != "/":
            self.send_error(404)
            return

        body = html_page(PORT)
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Server started in port {PORT}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()

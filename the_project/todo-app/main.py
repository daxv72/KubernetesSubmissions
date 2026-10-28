"""Todo app — exercise 2.6, break button from exercise 4.2.

GET / is an HTML page with a picture and the todo list from todo-backend.
Ports, URLs, and the other settings come from environment variables.

POST /break tells the backend to fail /healthz. Until that endpoint
returns 200 again, GET / is the System Failure page.
"""

import html
import json
import os
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer


def required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise SystemExit(f"Missing environment variable {name}")
    return value


PORT = int(required("PORT"))
BIND_ADDRESS = required("BIND_ADDRESS")
IMAGE_DIR = required("IMAGE_DIR")
CACHE_SECONDS = int(required("CACHE_SECONDS"))
PICSUM_URL = required("PICSUM_URL")
TODO_BACKEND_URL = required("TODO_BACKEND_URL")
IMAGE_ROUTE = required("IMAGE_ROUTE")
FORM_ACTION = required("FORM_ACTION")
TODO_FIELD = required("TODO_FIELD")
MAX_LENGTH = required("MAX_LENGTH")
BREAK_PATH = required("BREAK_PATH")
BACKEND_HEALTH_URL = required("BACKEND_HEALTH_URL")
BACKEND_BREAK_URL = required("BACKEND_BREAK_URL")

IMAGE_PATH = os.path.join(IMAGE_DIR, required("IMAGE_FILE"))
META_PATH = os.path.join(IMAGE_DIR, required("META_FILE"))


def read_meta() -> tuple[float, bool] | None:
    try:
        fetched_at, flag = open(META_PATH, encoding="utf-8").read().splitlines()[:2]
        return float(fetched_at), flag == "1"
    except (FileNotFoundError, IndexError, ValueError):
        return None


def write_meta(fetched_at: float, stale_served: bool) -> None:
    os.makedirs(IMAGE_DIR, exist_ok=True)
    temporary = META_PATH + ".tmp"
    with open(temporary, "w", encoding="utf-8") as handle:
        handle.write(f"{fetched_at}\n")
        handle.write("1\n" if stale_served else "0\n")
    os.replace(temporary, META_PATH)


def download() -> None:
    os.makedirs(IMAGE_DIR, exist_ok=True)
    request = urllib.request.Request(
        PICSUM_URL,
        headers={"User-Agent": "todo-app/1.12"},
    )
    temporary = IMAGE_PATH + ".tmp"
    with urllib.request.urlopen(request, timeout=20) as response:
        data = response.read()
    with open(temporary, "wb") as handle:
        handle.write(data)
    os.replace(temporary, IMAGE_PATH)
    write_meta(time.time(), False)
    print(f"Saved a new picture ({len(data)} bytes)", flush=True)


def ensure_image() -> None:
    meta = read_meta()
    if meta is None or not os.path.exists(IMAGE_PATH):
        download()
        return
    fetched_at, stale_served = meta
    if time.time() - fetched_at < CACHE_SECONDS:
        return
    if not stale_served:
        # The window is over. This request still gets the stored picture.
        write_meta(fetched_at, True)
        print("Cache expired: serving the stored picture once more", flush=True)
        return
    download()


def backend_healthy() -> bool:
    try:
        with urllib.request.urlopen(BACKEND_HEALTH_URL, timeout=2) as response:
            return response.status == 200
    except urllib.error.HTTPError:
        return False
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def mark_unhealthy() -> None:
    request = urllib.request.Request(BACKEND_BREAK_URL, data=b"", method="POST")
    try:
        with urllib.request.urlopen(request, timeout=2) as response:
            response.read()
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        print(f"Break request failed: {error}", flush=True)


def fetch_todos() -> list[str]:
    # Service DNS name. The browser does not call this URL.
    try:
        with urllib.request.urlopen(TODO_BACKEND_URL, timeout=2) as response:
            data = json.loads(response.read().decode())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError):
        return []
    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, str)]


def html_page(todos: list[str]) -> bytes:
    items = "\n".join(f"    <li>{html.escape(todo)}</li>" for todo in todos)
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Todo App</title>
  <style>
    body {
      font-family: sans-serif;
      text-align: center;
      margin: 0;
      padding: 2.5rem 1rem 3rem;
      color: #222;
      background: #fff;
    }
    h1, h2 {
      font-weight: 700;
      margin: 0;
    }
    h1 {
      font-size: 2.4rem;
      margin-bottom: 1.4rem;
    }
    img {
      width: min(220px, 70vw);
      border-radius: 12px;
    }
    form.composer {
      display: flex;
      justify-content: center;
      gap: 0.75rem;
      margin: 2.2rem auto 0;
      max-width: 640px;
    }
    input {
      flex: 1;
      min-width: 0;
      font-size: 1rem;
      padding: 0.7rem 0.8rem;
      border: 2px solid #43a047;
      border-radius: 4px;
    }
    button {
      font-size: 1rem;
      color: #fff;
      background: #43a047;
      border: 0;
      border-radius: 4px;
      padding: 0.7rem 1.4rem;
      cursor: pointer;
    }
    form.break {
      margin-top: 1.6rem;
    }
    button.break {
      background: #e57373;
      border-radius: 6px;
      padding: 0.65rem 1.15rem;
    }
    h2 {
      font-size: 1.7rem;
      margin: 2rem 0 1rem;
    }
    ul {
      list-style: none;
      padding: 0;
      margin: 0 auto;
      max-width: 720px;
      text-align: left;
    }
    li {
      background: #fff;
      border-left: 6px solid #43a047;
      border-radius: 4px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
      margin: 0 0 0.7rem;
      padding: 1rem 1rem 1rem 1.1rem;
    }
  </style>
</head>
<body>
  <h1>Todo App</h1>
  <img src="__IMAGE_ROUTE__" alt="Cached picture">
  <form class="composer" action="__FORM_ACTION__" method="post">
    <input type="text" name="__TODO_FIELD__" maxlength="__MAX_LENGTH__" required placeholder="Enter a new todo (max __MAX_LENGTH__ characters)" aria-label="New todo">
    <button type="submit">Send</button>
  </form>
  <h2>Todos</h2>
  <ul>
__TODO_ITEMS__
  </ul>
  <form class="break" action="__BREAK_PATH__" method="post">
    <button class="break" type="submit">break the app</button>
  </form>
</body>
</html>
""".replace("__TODO_ITEMS__", items).replace(
        "__IMAGE_ROUTE__", html.escape(IMAGE_ROUTE, quote=True)
    ).replace(
        "__FORM_ACTION__", html.escape(FORM_ACTION, quote=True)
    ).replace("__TODO_FIELD__", html.escape(TODO_FIELD, quote=True)).replace(
        "__MAX_LENGTH__", html.escape(MAX_LENGTH, quote=True)
    ).replace("__BREAK_PATH__", html.escape(BREAK_PATH, quote=True)).encode()


def failure_page() -> bytes:
    # Reloads until the restarted backend answers /healthz again.
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="refresh" content="2">
  <title>System Failure</title>
  <style>
    body {
      font-family: sans-serif;
      text-align: center;
      background: #fff7f7;
      min-height: 100vh;
      margin: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 2rem 1rem;
    }
    main {
      border: 1px solid #f0c4c4;
      border-radius: 16px;
      padding: 2.4rem 2.8rem;
      max-width: 720px;
    }
    h1 {
      color: #8f2424;
      font-size: 2.6rem;
      font-weight: 700;
      margin: 0 0 0.8rem;
    }
    p {
      color: #8f2424;
      font-size: 1.15rem;
      margin: 0;
    }
  </style>
</head>
<body>
  <main>
    <h1>System Failure</h1>
    <p>The Todo App is currently unhealthy. Please wait for recovery.</p>
  </main>
</body>
</html>
""".encode()


class Handler(BaseHTTPRequestHandler):
    def send_html(self, body: bytes) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]
        if path == "/":
            if not backend_healthy():
                self.send_html(failure_page())
                return
            self.send_html(html_page(fetch_todos()))
            return
        elif path == IMAGE_ROUTE:
            ensure_image()
            with open(IMAGE_PATH, "rb") as handle:
                body = handle.read()
            content_type = "image/jpeg"
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        path = self.path.split("?", 1)[0]
        length = int(self.headers.get("Content-Length", "0"))
        if length:
            self.rfile.read(length)
        if path != BREAK_PATH:
            self.send_error(404)
            return
        mark_unhealthy()
        self.send_response(303)
        self.send_header("Location", "/")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, fmt: str, *args) -> None:
        print(f"{self.address_string()} {fmt % args}", flush=True)


def main() -> None:
    print(f"Server started in port {PORT}", flush=True)
    HTTPServer((BIND_ADDRESS, PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()

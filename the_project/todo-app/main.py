"""Todo app — exercise 2.6.

GET / is an HTML page with a picture and the todo list from todo-backend.
Ports, URLs, and the other settings come from environment variables.
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
    form {
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
  <form action="__FORM_ACTION__" method="post">
    <input type="text" name="__TODO_FIELD__" maxlength="__MAX_LENGTH__" required placeholder="Enter a new todo (max __MAX_LENGTH__ characters)" aria-label="New todo">
    <button type="submit">Send</button>
  </form>
  <h2>Todos</h2>
  <ul>
__TODO_ITEMS__
  </ul>
</body>
</html>
""".replace("__TODO_ITEMS__", items).replace(
        "__IMAGE_ROUTE__", html.escape(IMAGE_ROUTE, quote=True)
    ).replace(
        "__FORM_ACTION__", html.escape(FORM_ACTION, quote=True)
    ).replace("__TODO_FIELD__", html.escape(TODO_FIELD, quote=True)).replace(
        "__MAX_LENGTH__", html.escape(MAX_LENGTH, quote=True)
    ).encode()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]
        if path == "/":
            body = html_page(fetch_todos())
            content_type = "text/html; charset=utf-8"
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

    def log_message(self, fmt: str, *args) -> None:
        print(f"{self.address_string()} {fmt % args}", flush=True)


def main() -> None:
    print(f"Server started in port {PORT}", flush=True)
    HTTPServer((BIND_ADDRESS, PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()

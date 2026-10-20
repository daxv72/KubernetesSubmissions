"""Todo app — exercise 1.12.

GET / is an HTML page with a picture.
GET /image serves that JPEG from a persistent volume.
The same file is used for CACHE_SECONDS (default 10 minutes).
The first request after the window still returns the stored file.
The request after that downloads a new picture from Lorem Picsum.
"""

import os
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("PORT", "8080"))
IMAGE_DIR = os.environ.get("IMAGE_DIR", "/usr/src/app/files")
CACHE_SECONDS = int(os.environ.get("CACHE_SECONDS", "600"))
PICSUM_URL = os.environ.get("PICSUM_URL", "https://picsum.photos/1200")

IMAGE_PATH = os.path.join(IMAGE_DIR, "image.jpg")
META_PATH = os.path.join(IMAGE_DIR, "meta.txt")


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


def html_page() -> bytes:
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
    h1 {
      font-size: 2.6rem;
      font-weight: 700;
      margin: 0 0 1.6rem;
    }
    img {
      width: min(520px, 92vw);
      border-radius: 16px;
    }
    p {
      color: #777;
      margin-top: 1.8rem;
      font-size: 1.2rem;
    }
  </style>
</head>
<body>
  <h1>Todo App</h1>
  <img src="/image" alt="Cached picture">
  <p>DevOps with Kubernetes 2026</p>
</body>
</html>
""".encode()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]
        if path == "/":
            body = html_page()
            content_type = "text/html; charset=utf-8"
        elif path == "/image":
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
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()

"""Todo backend — exercise 2.8.

GET and POST for the todo list. The path, port, length limit, and
database address come from environment variables. The list is stored
in Postgres.
"""

import json
import os
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

import pg8000.native


def required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise SystemExit(f"Missing environment variable {name}")
    return value


PORT = int(required("PORT"))
BIND_ADDRESS = required("BIND_ADDRESS")
MAX_LENGTH = int(required("MAX_LENGTH"))
TODO_PATH = required("TODO_PATH")
TODO_FIELD = required("TODO_FIELD")
REDIRECT_URL = required("REDIRECT_URL")
PGHOST = required("PGHOST")
PGPORT = int(required("PGPORT"))
POSTGRES_USER = required("POSTGRES_USER")
POSTGRES_PASSWORD = required("POSTGRES_PASSWORD")
POSTGRES_DB = required("POSTGRES_DB")

# Seed matches the list shown before this exercise. Inserted only when the table is empty.
SEED = (
    "Learn Kubernetes basics",
    "Deploy application to cluster",
    "Configure persistent volumes",
)

connection: pg8000.native.Connection | None = None


def connect() -> pg8000.native.Connection:
    """Retry until Postgres accepts a connection. The StatefulSet may still be starting."""
    while True:
        try:
            opened = pg8000.native.Connection(
                POSTGRES_USER,
                password=POSTGRES_PASSWORD,
                host=PGHOST,
                port=PGPORT,
                database=POSTGRES_DB,
                timeout=5,
            )
            opened.run("SELECT 1")
            print(f"Connected to Postgres at {PGHOST}:{PGPORT}/{POSTGRES_DB}", flush=True)
            return opened
        except Exception as error:
            print(f"Waiting for Postgres at {PGHOST}:{PGPORT}: {error}", flush=True)
            time.sleep(2)


def ensure_table(opened: pg8000.native.Connection) -> None:
    opened.run(
        """
        CREATE TABLE IF NOT EXISTS todos (
            id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            content text NOT NULL
        )
        """
    )
    count = int(opened.run("SELECT count(*) FROM todos")[0][0])
    if count != 0:
        return
    for text in SEED:
        opened.run("INSERT INTO todos (content) VALUES (:content)", content=text)


def query(sql: str, **params):
    global connection
    if connection is None:
        connection = connect()
        ensure_table(connection)
    try:
        return connection.run(sql, **params)
    except Exception as error:
        print(f"Postgres query failed, reconnecting: {error}", flush=True)
        connection = connect()
        ensure_table(connection)
        return connection.run(sql, **params)


def list_todos() -> list[str]:
    rows = query("SELECT content FROM todos ORDER BY id")
    return [str(row[0]) for row in rows]


def add_todo(text: str) -> None:
    query("INSERT INTO todos (content) VALUES (:content)", content=text)


def parse_todo(content_type: str, raw: bytes) -> str | None:
    if "application/json" in content_type:
        try:
            payload = json.loads(raw.decode())
        except json.JSONDecodeError:
            return None
        text = payload.get(TODO_FIELD, "") if isinstance(payload, dict) else ""
    else:
        fields = urllib.parse.parse_qs(raw.decode())
        text = fields.get(TODO_FIELD, [""])[0]
    text = str(text).strip()
    if not text or len(text) > MAX_LENGTH:
        return None
    return text


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0].rstrip("/") or "/"
        if path != TODO_PATH:
            self.send_error(404)
            return
        body = json.dumps(list_todos()).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        path = self.path.split("?", 1)[0].rstrip("/") or "/"
        if path != TODO_PATH:
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        todo = parse_todo(self.headers.get("Content-Type", ""), raw)
        if todo is None:
            body = f"Todo must be 1 to {MAX_LENGTH} characters.\n".encode()
            self.send_response(400)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        add_todo(todo)
        # The browser form posts here. Send the user back to the HTML page.
        self.send_response(303)
        self.send_header("Location", REDIRECT_URL)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, fmt: str, *args) -> None:
        print(f"{self.address_string()} {fmt % args}", flush=True)


def main() -> None:
    global connection
    connection = connect()
    ensure_table(connection)
    print(f"Server started in port {PORT}", flush=True)
    HTTPServer((BIND_ADDRESS, PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()

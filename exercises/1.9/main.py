"""Ping-pong — exercise 2.7.

GET /pingpong returns "pong N" and then increments the counter.
GET /pings returns the current count and does not increment it.
The count is one row in Postgres. Log output reads it over HTTP.
"""

import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

import pg8000.native


def required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise SystemExit(f"Missing environment variable {name}")
    return value


PORT = int(required("PORT"))
BIND_ADDRESS = required("BIND_ADDRESS")
PGHOST = required("PGHOST")
PGPORT = int(required("PGPORT"))
PGUSER = required("PGUSER")
PGPASSWORD = required("PGPASSWORD")
PGDATABASE = required("PGDATABASE")

# Single row. id 1 is the only counter.
COUNTER_ID = 1

connection: pg8000.native.Connection | None = None


def connect() -> pg8000.native.Connection:
    """Retry until Postgres accepts a connection. The StatefulSet may still be starting."""
    while True:
        try:
            opened = pg8000.native.Connection(
                PGUSER,
                password=PGPASSWORD,
                host=PGHOST,
                port=PGPORT,
                database=PGDATABASE,
                timeout=5,
            )
            opened.run("SELECT 1")
            print(f"Connected to Postgres at {PGHOST}:{PGPORT}", flush=True)
            return opened
        except Exception as error:
            print(f"Waiting for Postgres at {PGHOST}:{PGPORT}: {error}", flush=True)
            time.sleep(2)


def ensure_table(opened: pg8000.native.Connection) -> None:
    opened.run(
        """
        CREATE TABLE IF NOT EXISTS ping_counter (
            id integer PRIMARY KEY,
            count integer NOT NULL
        )
        """
    )
    opened.run(
        """
        INSERT INTO ping_counter (id, count)
        VALUES (:id, 0)
        ON CONFLICT (id) DO NOTHING
        """,
        id=COUNTER_ID,
    )


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


def current_count() -> int:
    rows = query("SELECT count FROM ping_counter WHERE id = :id", id=COUNTER_ID)
    return int(rows[0][0])


def next_count() -> int:
    """Return the count before this ping, then store the incremented value."""
    rows = query(
        """
        UPDATE ping_counter
        SET count = count + 1
        WHERE id = :id
        RETURNING count
        """,
        id=COUNTER_ID,
    )
    return int(rows[0][0]) - 1


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0].rstrip("/") or "/"
        if path == "/pingpong":
            body = f"pong {next_count()}\n".encode()
        elif path == "/pings":
            # Read-only. Log output calls this on every page view.
            body = f"{current_count()}\n".encode()
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

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

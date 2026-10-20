"""Log writer — exercise 1.11.

On startup, generate a random string.
Every 5 seconds, append one line (UTC timestamp and that string) to a file.
The file lives on the shared persistent volume.
"""

import os
import time
import uuid
from datetime import datetime, timezone

LOG_PATH = os.environ.get("LOG_PATH", "/usr/src/app/files/log.txt")

# Generated once: every line in this process uses the same string.
random_string = str(uuid.uuid4())


def timestamp() -> str:
    now = datetime.now(timezone.utc)
    millis = now.microsecond // 1000
    return now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{millis:03d}Z"


def main() -> None:
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    print(f"Writing {LOG_PATH}", flush=True)
    while True:
        line = f"{timestamp()}: {random_string}."
        with open(LOG_PATH, "a", encoding="utf-8") as handle:
            handle.write(line + "\n")
        print(line, flush=True)
        time.sleep(5)


if __name__ == "__main__":
    main()

"""Log output — exercise 1.3.

On startup, generate a random string, keep it in memory,
and print it every 5 seconds with a UTC timestamp.
The Deployment for this app lives in manifests/deployment.yaml.
"""

import time
import uuid
from datetime import datetime, timezone

# Generated once: stays the same for the life of the process.
# A Pod restart generates a new one.
random_string = str(uuid.uuid4())


def timestamp() -> str:
    now = datetime.now(timezone.utc)
    millis = now.microsecond // 1000
    return now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{millis:03d}Z"


def main() -> None:
    while True:
        # flush: without a TTY, Python buffers stdout and kubectl logs stays empty.
        print(f"{timestamp()}: {random_string}", flush=True)
        time.sleep(5)


if __name__ == "__main__":
    main()

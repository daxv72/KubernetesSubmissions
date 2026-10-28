"""Broadcaster — exercise 4.6, with a log-only mode for exercise 4.9.

Subscribes to the todo subject in a NATS queue group. Core NATS gives
each message to one member of the group, so several replicas do not
send the same status twice.

BROADCAST_MODE=forward posts the status to WEBHOOK_URL.
BROADCAST_MODE=log prints the status and does not call another service.
Staging sets log. A missing or blank variable means forward.
Any other value stops the process.
"""

import asyncio
import json
import os
import urllib.error
import urllib.request

import nats
from nats.aio.msg import Msg


def required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise SystemExit(f"Missing environment variable {name}")
    return value


BROADCAST_MODE = os.environ.get("BROADCAST_MODE", "forward").strip() or "forward"
if BROADCAST_MODE not in {"forward", "log"}:
    raise SystemExit(f"BROADCAST_MODE must be forward or log, got {BROADCAST_MODE}")

NATS_URL = required("NATS_URL")
NATS_SUBJECT = required("NATS_SUBJECT")
NATS_QUEUE = required("NATS_QUEUE")
if BROADCAST_MODE == "forward":
    WEBHOOK_URL = required("WEBHOOK_URL")
    WEBHOOK_USER = required("WEBHOOK_USER")
else:
    WEBHOOK_URL = ""
    WEBHOOK_USER = ""


def status_message(event: dict) -> str:
    text = str(event.get("todo", ""))
    action = event.get("action")
    if action == "created":
        return f"A todo was created: {text}"
    if action == "updated":
        return f"A todo was updated: {text}"
    return f"A todo event: {text}"


def post_status(message: str) -> None:
    body = json.dumps({"user": WEBHOOK_USER, "message": message}).encode()
    request = urllib.request.Request(
        WEBHOOK_URL,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=5) as response:
        response.read()


async def handle(msg: Msg) -> None:
    try:
        event = json.loads(msg.data.decode())
    except json.JSONDecodeError:
        print("Dropped a message that is not JSON", flush=True)
        return
    if not isinstance(event, dict):
        print("Dropped a message that is not an object", flush=True)
        return
    message = status_message(event)
    if BROADCAST_MODE == "log":
        print(
            f"Logged action={event.get('action')} id={event.get('id')}: {message}",
            flush=True,
        )
        return
    try:
        await asyncio.to_thread(post_status, message)
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        print(f"Webhook failed id={event.get('id')}: {error}", flush=True)
        return
    print(
        f"Forwarded action={event.get('action')} id={event.get('id')} "
        f"queue={NATS_QUEUE}",
        flush=True,
    )


async def main() -> None:
    while True:
        try:
            client = await nats.connect(NATS_URL)
            break
        except Exception as error:
            print(f"Waiting for NATS at {NATS_URL}: {error}", flush=True)
            await asyncio.sleep(2)
    await client.subscribe(NATS_SUBJECT, queue=NATS_QUEUE, cb=handle)
    print(
        f"Subscribed to {NATS_SUBJECT} in queue {NATS_QUEUE} mode={BROADCAST_MODE}",
        flush=True,
    )
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())

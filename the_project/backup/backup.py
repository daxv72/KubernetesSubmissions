"""Dump the todo database and upload the file to Cloud Storage.

The service-account key is mounted at GOOGLE_APPLICATION_CREDENTIALS.
That file is created with kubectl and is not in git.
"""

import os
import subprocess
from datetime import datetime, timezone

from google.cloud import storage


def required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise SystemExit(f"Missing environment variable {name}")
    return value


def main() -> None:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    filename = f"/tmp/todos-{stamp}.sql"
    object_name = f"todos/todos-{stamp}.sql"
    bucket_name = required("BACKUP_BUCKET")

    subprocess.run(
        [
            "pg_dump",
            "--host",
            required("PGHOST"),
            "--port",
            required("PGPORT"),
            "--username",
            required("PGUSER"),
            "--dbname",
            required("PGDATABASE"),
            "--file",
            filename,
            "--verbose",
        ],
        check=True,
    )

    blob = storage.Client().bucket(bucket_name).blob(object_name)
    blob.upload_from_filename(filename, content_type="application/sql")
    print(f"Uploaded gs://{bucket_name}/{object_name}", flush=True)


if __name__ == "__main__":
    main()

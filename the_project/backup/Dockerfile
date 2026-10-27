FROM postgres:18.0

USER root

# pg_dump comes from this image, so the client matches Postgres 18.
# The venv holds the Cloud Storage client. The base image has neither pip nor the library.
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-venv \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN python3 -m venv /opt/backup \
    && /opt/backup/bin/pip install --no-cache-dir -r /tmp/requirements.txt

COPY backup.py /usr/local/bin/backup.py

ENV PATH="/opt/backup/bin:${PATH}"
ENV PYTHONUNBUFFERED=1

# Root can read the key mounted from the Secret. The key is not in the image.
CMD ["python", "/usr/local/bin/backup.py"]

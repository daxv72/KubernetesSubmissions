FROM python:3.13-alpine

WORKDIR /usr/src/app

# Unbuffered stdout: lines show up immediately in kubectl logs.
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

USER nobody

CMD ["python", "main.py"]

FROM python:3.13-alpine

WORKDIR /usr/src/app

# Unbuffered stdout: the posted JSON shows up immediately in kubectl logs.
ENV PYTHONUNBUFFERED=1

COPY main.py .

USER nobody

CMD ["python", "main.py"]

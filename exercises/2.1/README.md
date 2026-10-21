# 2.1 Connecting pods

Log output and ping-pong no longer share a volume. Ping-pong keeps the request count in memory.

- `GET /pingpong` returns `pong N` and then increments the count. Ingress still routes this path to the ping-pong Service.
- `GET /pings` returns the current count and does not increment it. Log output calls this URL: `http://ping-pong:3000/pings`.

The name `ping-pong` is the Service DNS name in the same namespace. The Service port is `3000`, which is also the container port.

Log output still has two containers. They share an `emptyDir` for `log.txt` only. `GET /` still returns the latest log line and `Ping / Pongs: N`.

The app code stays in `exercises/1.3` (reader) and `exercises/1.9` (ping-pong). Images: `log-reader:2.1`, `ping-pong:2.1`. The writer image stays `log-writer:1.11`.

## Kubernetes

From the repository root. The images are local, so k3d needs an import.

```bash
docker build -t log-reader:2.1 exercises/1.3/reader
docker build -t ping-pong:2.1 exercises/1.9
k3d image import log-reader:2.1 ping-pong:2.1
kubectl apply -f exercises/1.9/manifests/
kubectl apply -f exercises/1.3/manifests/
```

Then open http://localhost:8081/pingpong three times and http://localhost:8081/. The page shows `Ping / Pongs: 3`. Refreshing `/` does not increase the count.

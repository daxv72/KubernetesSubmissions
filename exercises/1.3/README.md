# Log output

Exercise 2.1. Two containers in one Pod share an `emptyDir` mounted at `/usr/src/app/files`. That volume is only for the log line. The ping count comes from `GET http://ping-pong:3000/pings`. See `exercises/2.1`.

`log-writer` generates a random string on startup and appends `timestamp: string.` to `log.txt` every 5 seconds. `log-reader` serves the latest line and the ping-pong count on `GET /`.

The Service is still ClusterIP port `2345` to container port `3000` on `log-reader`. Ingress path `/` stays on this Service. `/pingpong` stays on ping-pong.

With two containers, logs need `-c`:

```bash
kubectl logs -n exercises -l app=log-output -c log-writer --tail=2
kubectl logs -n exercises -l app=log-output -c log-reader --tail=2
```

## Kubernetes

From the repository root. Ping-pong must be running first, otherwise the count on the page is 0.

```bash
docker build -t log-writer:1.11 exercises/1.3/writer
docker build -t log-reader:2.5 exercises/1.3/reader
k3d image import log-writer:1.11 log-reader:2.5
kubectl apply -f exercises/1.3/manifests/
```

Then open http://localhost:8081/. The page is the latest log line and `Ping / Pongs: N`.


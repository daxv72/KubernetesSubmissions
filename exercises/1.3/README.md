# Log output

Exercise 1.11. Two containers in one Pod share the persistent volume mounted at `/usr/src/app/files`. The claim is `shared-claim` in `exercises/1.11`.

`log-writer` generates a random string on startup and appends `timestamp: string.` to `log.txt` every 5 seconds. `log-reader` serves the latest line and the ping-pong count from `pings.txt` on `GET /`.

The Service is still ClusterIP port `2345` to container port `3000` on `log-reader`. Ingress path `/` stays on this Service. `/pingpong` stays on ping-pong.

With two containers, logs need `-c`:

```bash
kubectl logs -l app=log-output -c log-writer --tail=2
kubectl logs -l app=log-output -c log-reader --tail=2
```

## Kubernetes

From the repository root. Create the node directory and the volume before the Deployments.

```bash
docker exec k3d-k3s-default-agent-0 mkdir -p /tmp/kube
kubectl apply -f exercises/1.11/
docker build -t log-writer:1.11 exercises/1.3/writer
docker build -t log-reader:1.11 exercises/1.3/reader
k3d image import log-writer:1.11 log-reader:1.11
kubectl apply -f exercises/1.3/manifests/deployment.yaml
```

Then open http://localhost:8081/. The page is the latest log line and `Ping / Pongs: N`.


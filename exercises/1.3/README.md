# Log output

Exercise 1.10. Two containers in one Pod share an emptyDir volume mounted at `/usr/src/app/files`.

`log-writer` generates a random string on startup and appends `timestamp: string` to `log.txt` every 5 seconds. `log-reader` serves that file on `GET /`.

The Service is still ClusterIP port `2345` to container port `3000` on `log-reader`. Ingress path `/` stays on this Service. `/pingpong` stays on ping-pong.

With two containers, logs need `-c`:

```bash
kubectl logs -l app=log-output -c log-writer --tail=2
kubectl logs -l app=log-output -c log-reader --tail=2
```

## Kubernetes

From the repository root:

```bash
docker build -t log-writer:1.10 exercises/1.3/writer
docker build -t log-reader:1.10 exercises/1.3/reader
k3d image import log-writer:1.10 log-reader:1.10
kubectl apply -f exercises/1.3/manifests/
```

Then open http://localhost:8081/. A reload a few seconds later shows a new line. The string stays the same until the Pod is replaced. The file is deleted with the Pod.

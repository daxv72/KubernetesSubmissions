# 2.5 ConfigMap

Log output reads one file and one environment variable from the ConfigMap `log-output-config` in the namespace `exercises`.

- `information.txt` is mounted at `/usr/src/app/config/information.txt`.
- `MESSAGE` is set with `configMapKeyRef`. It is not mounted as a file.

`GET /` prints both, then the usual log line and ping count. The reader image is `log-reader:2.5`. Ping-pong must be in the same namespace.

## Kubernetes

From the repository root. The writer image `log-writer:1.11` and `ping-pong:2.1` must already be imported.

```bash
docker build -t log-reader:2.5 exercises/1.3/reader
k3d image import log-reader:2.5
kubectl apply -f exercises/2.3/exercises-namespace.yaml
kubectl apply -f exercises/2.5/configmap.yaml
kubectl apply -f exercises/1.9/manifests/
kubectl apply -f exercises/1.3/manifests/
```

Then open http://localhost:8081/. The page starts with `file content: this text is from file` and `env variable: MESSAGE=hello world`.

# Log output

Exercise 1.1. On startup the process generates a random UUID, stores it in memory, and prints it every 5 seconds with a UTC timestamp.

```text
2026-10-20T08:27:25.340Z: cd923218-9079-4e4e-951a-110dd0e22eda
```

## Run locally

```bash
python3 main.py
```

## Container

From this directory:

```bash
docker build -t log-output:1.1 .
docker run --rm log-output:1.1
```

## Kubernetes

The image is local. With k3d it must be imported into the cluster. The Deployment uses `imagePullPolicy: IfNotPresent`.

From the repository root:

```bash
docker build -t log-output:1.1 exercises/1.1
k3d cluster create -a 2
k3d image import log-output:1.1
kubectl apply -f exercises/1.1/manifests/deployment.yaml
kubectl logs -l app=log-output -f
```

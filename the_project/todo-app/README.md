# Todo app

HTTP server for the course project. On startup it prints `Server started in port NNNN`. The port comes from the `PORT` environment variable (default `8080`). `GET /` returns an HTML page.

There is no Service yet. Reach the Pod with `kubectl port-forward`.

## Run locally

```bash
PORT=3000 python3 main.py
```

## Container

From this directory:

```bash
docker build -t todo-app:1.5 .
docker run --rm -e PORT=3000 -p 3003:3000 todo-app:1.5
```

## Kubernetes

From the repository root. The image is local, so k3d needs an import. The Deployment sets `imagePullPolicy: IfNotPresent` and `PORT=3000`.

```bash
docker build -t todo-app:1.5 the_project/todo-app
k3d image import todo-app:1.5
kubectl apply -f the_project/todo-app/manifests/deployment.yaml
kubectl port-forward deployment/todo-app 3003:3000
```

Then open http://localhost:3003/. Expected log line:

```text
Server started in port 3000
```

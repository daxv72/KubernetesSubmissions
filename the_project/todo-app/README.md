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

From the repository root. The image is local, so k3d needs an import. The Deployment sets `PORT=3000`. The Service is a NodePort: host `8083` reaches node port `30081`, which forwards to container port `3000`. Host `8082` stays on the course example.

```bash
docker build -t todo-app:1.5 the_project/todo-app
k3d image import todo-app:1.5
k3d cluster edit k3s-default --port-add 8083:30081@agent:0
kubectl apply -f the_project/todo-app/manifests/deployment.yaml
kubectl apply -f the_project/todo-app/manifests/service.yaml
```

Then open http://localhost:8083/. The Pod log still contains `Server started in port 3000`.

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

From the repository root. The image is local, so k3d needs an import. The Deployment sets `PORT=3000`. The Service is ClusterIP on port `3000`. Ingress publishes `GET /` on host port `8081`.

```bash
docker build -t todo-app:1.5 the_project/todo-app
k3d image import todo-app:1.5
kubectl delete ingress log-output --ignore-not-found
kubectl apply -f the_project/todo-app/manifests/
```

Then open http://localhost:8081/. The Pod log still contains `Server started in port 3000`.

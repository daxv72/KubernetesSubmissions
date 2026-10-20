# Todo app

Exercise 1.2. HTTP server. On startup it prints `Server started in port NNNN`. The port comes from the `PORT` environment variable (default `8080`).

There is no Service yet. The course reaches the port in a later networking exercise.

## Run locally

```bash
PORT=3000 python3 main.py
```

## Container

From this directory:

```bash
docker build -t todo-app:1.2 .
docker run --rm -e PORT=3000 todo-app:1.2
```

## Kubernetes

From the repository root. The image is local, so k3d needs an import. The Deployment sets `imagePullPolicy: IfNotPresent` and `PORT=3000`.

```bash
docker build -t todo-app:1.2 the_project/todo-app
k3d image import todo-app:1.2
kubectl apply -f the_project/todo-app/manifests/deployment.yaml
kubectl logs -l app=todo-app
```

Expected log line:

```text
Server started in port 3000
```

# Todo app

Exercise 1.12. `GET /` is an HTML page with a picture. `GET /image` serves a JPEG cached on the persistent volume from `exercises/1.12`. The same file is used for 10 minutes. The first request after that still returns the stored file. The next request downloads a new picture from `https://picsum.photos/1200`.

On startup the process prints `Server started in port NNNN`. The port comes from `PORT` (the Deployment sets `3000`).

## Kubernetes

From the repository root. The image is local, so k3d needs an import. Log output's Ingress also claims `/`. Remove it so this app owns host port `8081`.

```bash
docker exec k3d-k3s-default-agent-0 mkdir -p /tmp/todo-images
kubectl apply -f exercises/1.12/
docker build -t todo-app:1.12 the_project/todo-app
k3d image import todo-app:1.12
kubectl delete ingress log-output --ignore-not-found
kubectl apply -f the_project/todo-app/manifests/
```

Then open http://localhost:8081/. `kubectl delete pod -l app=todo-app` restarts the container. The picture stays the one already stored.


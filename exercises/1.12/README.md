# Exercise 1.12

The project picture. The app code stays in `the_project/todo-app`. This folder is the cache volume, separate from the application.

`todo-image-pv` is `/tmp/todo-images` on node `k3d-k3s-default-agent-0`. `todo-image-claim` binds it. The Deployment mounts the claim at `/usr/src/app/files`.

`GET /` shows the page. `GET /image` serves `image.jpg`. The file is reused for 10 minutes (`CACHE_SECONDS=600`). The first request after that still returns the stored file. The next request downloads a new picture from `https://picsum.photos/1200`. A new Pod reads the same file, so a crash does not call Lorem Picsum again while the picture is still current.

Log output also uses path `/` on the Ingress. Remove that Ingress from the cluster so the project owns `http://localhost:8081/`.

## Kubernetes

From the repository root:

```bash
docker exec k3d-k3s-default-agent-0 mkdir -p /tmp/todo-images
kubectl apply -f exercises/1.12/
docker build -t todo-app:1.12 the_project/todo-app
k3d image import todo-app:1.12
kubectl delete ingress log-output --ignore-not-found
kubectl apply -f the_project/todo-app/manifests/
```

Then open http://localhost:8081/. To check that a restart keeps the picture:

```bash
kubectl delete pod -l app=todo-app
```

The next `GET /image` uses the file already on the volume.

# Todo app

Exercise 2.4. The app runs in the namespace `project`. `GET /` is an HTML page with the cached picture and the todo list read from `http://todo-backend:2345/todos`. The form posts to `/todos`. The field stops at 140 characters.

`GET /image` serves the JPEG cached on the persistent volume from `exercises/1.12`. The same file is used for 10 minutes.

On startup the process prints `Server started in port NNNN`. The port comes from `PORT` (the Deployment sets `3000`).

## Kubernetes

From the repository root. The image is local, so k3d needs an import. Log output's Ingress is in the namespace `exercises` and also claims `/`. Remove it so this app owns host port `8081`.

```bash
docker exec k3d-k3s-default-agent-0 mkdir -p /tmp/todo-images
kubectl apply -f the_project/namespace.yaml
kubectl apply -f exercises/1.12/
docker build -t todo-backend:2.2 the_project/todo-backend
docker build -t todo-app:2.2 the_project/todo-app
k3d image import todo-backend:2.2 todo-app:2.2
kubectl delete ingress log-output -n exercises --ignore-not-found
kubectl apply -f the_project/todo-backend/manifests/
kubectl apply -f the_project/todo-app/manifests/
```

Then open http://localhost:8081/. `kubectl delete pod -n project -l app=todo-app` restarts the container. The picture stays the one already stored.


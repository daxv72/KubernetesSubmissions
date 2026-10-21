# Todo backend

Exercise 2.4. The process runs in the namespace `project`. The todo list lives in memory.

- `GET /todos` returns a JSON array of strings.
- `POST /todos` appends one todo. The body is form field `todo` or JSON `{"todo": "..."}`. Empty text and text longer than 140 characters are rejected. A successful form post redirects to `/`.

The Service port is `2345`. The container listens on `3000`. Todo-app calls `http://todo-backend:2345/todos` from inside the cluster. The browser posts to `/todos` through the Ingress in `the_project/todo-app`.

## Kubernetes

From the repository root. The image is local, so k3d needs an import. Apply this Deployment before todo-app, then apply the todo-app manifests so the Ingress routes `/todos` here.

```bash
kubectl apply -f the_project/namespace.yaml
docker build -t todo-backend:2.2 the_project/todo-backend
k3d image import todo-backend:2.2
kubectl apply -f the_project/todo-backend/manifests/
```

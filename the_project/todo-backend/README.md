# Todo backend

Exercise 2.10. The process runs in the namespace `project`. Ports, the todo path, and the length limit come from the ConfigMap `todo-backend-config`. Postgres host and port are in that ConfigMap too. User, password, and database name come from the Secret `postgres-auth`. The list is the table `todos`. Every POST is printed to stdout. A todo longer than `MAX_LENGTH` is rejected and the text is in that log line.

- `GET /todos` returns a JSON array of strings.
- `POST /todos` appends one todo. The body is form field `todo` or JSON `{"todo": "..."}`. Empty text and text longer than 140 characters are rejected. A successful form post redirects to `/`.

The Service port is `2345`. The container listens on `3000`. Todo-app calls `http://todo-backend:2345/todos` from inside the cluster. The browser posts to `/todos` through the Ingress in `the_project/todo-app`.

## Kubernetes

From the repository root. The image is local, so k3d needs an import. Apply this Deployment before todo-app, then apply the todo-app manifests so the Ingress routes `/todos` here.

```bash
kubectl apply -f the_project/namespace.yaml
docker build -t todo-backend:2.10 the_project/todo-backend
k3d image import todo-backend:2.10
kubectl apply -f the_project/todo-backend/manifests/
```

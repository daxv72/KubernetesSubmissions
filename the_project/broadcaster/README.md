# Broadcaster

Exercise 4.6. The Deployment `todo-broadcaster` runs in the namespace `project` with 6 replicas. It subscribes to the NATS subject `todos` in the queue group `broadcasters`. Core NATS gives each message to one member of that group, so the six replicas do not post the same status twice.

The backend publishes `{"action", "id", "todo", "done"}` when a todo is saved or updated. The broadcaster posts this JSON to `WEBHOOK_URL`:

```json
{"user": "bot", "message": "A todo was created: example"}
```

The default URL is the in-cluster Service `todo-webhook`. Replace `WEBHOOK_URL` to send the same body to another generic endpoint. A missing message is acceptable. A duplicate is not.

Exercise 4.9 adds `BROADCAST_MODE`. `log` prints the status line and does not open a connection. `forward` is the post above. A missing or blank value is `forward`. Staging sets `log` and removes `WEBHOOK_URL`. The image tag is `todo-broadcaster:4.9`.

## Kubernetes

From the repository root. The image is local, so k3d needs an import.

```bash
docker build -t todo-broadcaster:4.6 the_project/broadcaster
docker build -t todo-webhook:4.6 the_project/webhook
k3d image import todo-broadcaster:4.6 -c k3s-default
k3d image import todo-webhook:4.6 -c k3s-default
kubectl apply -k the_project
```

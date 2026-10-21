# 2.3 Keep them separated

Exercise applications run in the namespace `exercises`. The project runs in the namespace `project`. Course examples can stay in `default`.

Log output and ping-pong are in `exercises`. A short Service name still resolves inside that namespace, so Log output keeps calling `http://ping-pong:3000/pings`.

Todo-app and todo-backend are in `project`. Todo-app keeps calling `http://todo-backend:2345/todos`. The image claim `todo-image-claim` is in `project` too. The PersistentVolume itself is not namespaced.

Both Ingress objects use the path `/`. Only one of them can own http://localhost:8081/ at a time.

## Kubernetes

From the repository root. Images `log-reader:2.1`, `log-writer:1.11`, `ping-pong:2.1`, `todo-app:2.2` and `todo-backend:2.2` must already be imported.

A local PersistentVolume that was bound in `default` stays `Released` after the claim moves. Delete it and create it again before applying the claim.

```bash
kubectl delete deployment,service log-output ping-pong todo-app todo-backend -n default --ignore-not-found
kubectl delete ingress log-output todo-app -n default --ignore-not-found
kubectl delete pvc todo-image-claim -n default --ignore-not-found
kubectl delete pv todo-image-pv --ignore-not-found
kubectl apply -f exercises/2.3/
kubectl apply -f exercises/1.12/
kubectl apply -f exercises/1.9/manifests/
kubectl apply -f exercises/1.3/manifests/
kubectl apply -f the_project/todo-backend/manifests/
kubectl apply -f the_project/todo-app/manifests/
```

`kubectl get deploy -n exercises` shows log-output and ping-pong. `kubectl get deploy -n project` shows todo-app and todo-backend.

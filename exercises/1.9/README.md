# Ping-pong

Exercise 1.9. `GET /pingpong` returns `pong N` and then increments an in-memory counter. The counter starts at 0 and resets when the process restarts.

The Ingress is shared with Log output (`exercises/1.3`). `/pingpong` goes to this Service. `/` stays on Log output. The same Ingress object is `exercises/1.3/manifests/ingress.yaml`.

## Kubernetes

From the repository root. The image is local, so k3d needs an import. The Deployment sets `PORT=3000`. The Service is ClusterIP on port `3000`.

The todo app Ingress also claims `/`. Remove it from the cluster so Log output and ping-pong own the paths.

```bash
docker build -t ping-pong:1.9 exercises/1.9
k3d image import ping-pong:1.9
kubectl delete ingress todo-app --ignore-not-found
kubectl apply -f exercises/1.9/manifests/
kubectl apply -f exercises/1.3/manifests/ingress.yaml
```

Then open http://localhost:8081/pingpong. The first response is `pong 0`. http://localhost:8081/ is still Log output.

# Log output

Exercise 1.7. On startup the process generates a random string, keeps it in memory, and prints it every 5 seconds with a UTC timestamp. `GET /` returns the current timestamp and that same string.

Ingress publishes the app on host port `8081`. The Service is ClusterIP: port `2345` forwards to container port `3000`.

## Kubernetes

From the repository root:

```bash
docker build -t log-output:1.7 exercises/1.3
k3d image import log-output:1.7
kubectl apply -f exercises/1.3/manifests/
kubectl logs -l app=log-output --tail=2
```

Then open http://localhost:8081/.

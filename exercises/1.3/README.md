# Log output

Exercise 1.3. Same application as exercise 1.1. The Deployment is declarative and lives in `manifests/deployment.yaml`.

## Kubernetes

From the repository root. Tag `1.3` is the same application image as `1.1`.

```bash
docker build -t log-output:1.3 exercises/1.3
k3d image import log-output:1.3
kubectl apply -f exercises/1.3/manifests/deployment.yaml
kubectl rollout restart deployment/log-output
kubectl logs -l app=log-output -f
```

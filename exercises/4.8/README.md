# Exercise 4.8 — GitOps for the project

Argo CD Application `project` in the namespace `argocd` tracks `main` of https://github.com/daxv72/KubernetesSubmissions.git at `the_project`. That directory has a `kustomization.yaml`, so Argo CD builds it with Kustomize and applies the result to the namespace `project`. Automated sync is on, with prune and self-heal. A commit on `main` that changes `the_project` is applied without a manual `kubectl apply`. The controller polls about every three minutes.

This cluster is k3d. The Application uses the base in `the_project`, not `overlays/gke`. The overlay removes the storage class and switches two Services to NodePort for GKE.

```bash
kubectl apply -f exercises/4.8/application.yaml
kubectl get application -n argocd project
```

`the_project` is already on `main`, so the first sync does not wait for this exercise directory to be pushed.

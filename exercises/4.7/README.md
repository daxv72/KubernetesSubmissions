# Exercise 4.7 — GitOps for Log output

Argo CD Application `log-output` in the namespace `argocd` tracks `main` of https://github.com/daxv72/KubernetesSubmissions.git at `exercises/4.7/manifests`. Automated sync is on, with prune and self-heal. A commit that changes those manifests is applied to the namespace `exercises`. The controller polls about every three minutes.

The manifests are the current Log output app: Deployment and Service from exercise 1.3, ConfigMap from exercise 2.5, and the Ingress that sends `/` here. The Pod template annotation `dwk.mooc.fi/release` is `4.7`. Changing that value rolls the Pod on the next sync. Images stay `log-writer:1.11` and `log-reader:2.5` with `IfNotPresent`, so a new image tag still needs `k3d image import` on this cluster.

```bash
kubectl apply -f exercises/4.7/application.yaml
kubectl get application -n argocd log-output
```

The path has to be on `main` before the Application can sync. Until then the status is a comparison error, not a broken Deployment.

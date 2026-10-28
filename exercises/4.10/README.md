# Exercise 4.10 — code and configuration in different repositories

Application code stays in https://github.com/daxv72/KubernetesSubmissions. Kubernetes manifests for staging and production are in https://github.com/daxv72/KubernetesConfigurations. Argo CD reads only the configuration repository.

| Environment | Application | Repository path | Revision |
| --- | --- | --- | --- |
| Staging | `staging` | `staging` | `main` |
| Production | `production` | `production` | latest semver tag (`*`) |

The rendered manifests match exercise 4.9. Staging still logs messages and has no backup CronJob. Production still forwards and keeps the backup. The Secret `postgres-auth` is in neither the configuration repository nor these Applications.

```bash
kubectl apply -f exercises/4.10/staging-application.yaml
kubectl apply -f exercises/4.10/production-application.yaml
```

A push to `main` that changes `the_project` runs `.github/workflows/update-config.yaml`. The workflow copies the image tags from `the_project/kustomization.yaml` into `base/kustomization.yaml` of the configuration repository and pushes `main`. A Git tag on the code repository is created on the configuration repository when it is not already there, so production follows that tag. The workflow pushes only when the secret `CONFIG_REPO_TOKEN` is set. The token needs write access to `KubernetesConfigurations`. It is not stored in this repository.

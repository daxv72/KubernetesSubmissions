# Exercise 4.9 — staging and production

Two Argo CD Applications. Each one builds a Kustomize overlay of `the_project` and applies it to its own namespace.

| Environment | Application | Namespace | Git revision | Broadcaster | Database backup |
| --- | --- | --- | --- | --- | --- |
| Staging | `staging` | `staging` | branch `main` | `BROADCAST_MODE=log`. Prints the message. Does not call a webhook. The webhook Deployment is not installed. | CronJob `todo-backup` is not installed |
| Production | `production` | `production` | latest semver tag (`targetRevision: "*"`) | `BROADCAST_MODE=forward`. Posts to `todo-webhook`. | CronJob `todo-backup` stays |

`*` matches Git tags only. A commit on `main` updates staging and leaves production on the previous tag. Pushing a tag such as `4.9` moves production to that commit. The subjects are `todos.staging` and `todos.production`, so the two queue groups do not share messages.

The overlays delete the Secret `postgres-auth`. Create it in each namespace before the Pods start. The same password is already in the namespace `project`. The command does not print the value:

```bash
kubectl apply -f exercises/4.9/staging-application.yaml
kubectl apply -f exercises/4.9/production-application.yaml
kubectl -n argocd delete application project

for ns in staging production; do
  kubectl create namespace "$ns" --dry-run=client -o yaml | kubectl apply -f -
  kubectl get secret postgres-auth -n project -o json \
    | python3 -c 'import json,sys; s=json.load(sys.stdin); s["metadata"]={"name":"postgres-auth","namespace":sys.argv[1]}; print(json.dumps(s))' "$ns" \
    | kubectl apply -f -
done
```

The Application `project` from exercise 4.8 has no resource finalizer. Deleting it leaves the objects already running in the namespace `project`. `main` is no longer applied there.

The image claim uses the StorageClass `local-path`. The volume `todo-images` is already bound in the namespace `project`.

Image `todo-broadcaster:4.9`. On this k3d cluster:

```bash
docker build -t todo-broadcaster:4.9 the_project/broadcaster
k3d image import todo-broadcaster:4.9 -c k3s-default
kubectl apply -k exercises/4.9/staging
kubectl apply -k exercises/4.9/production
```

Argo CD reads GitHub. The staging path exists on `main` only after that commit is pushed. Production resolves `*` to the highest tag. Until the tag `4.9` exists, that Application cannot load `exercises/4.9/production`.

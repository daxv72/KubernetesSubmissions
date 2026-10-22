# 2.9 Read a random Wikipedia article

CronJob `read-wikipedia` in the namespace `project`. The schedule is `0 * * * *`, so one run at the start of every hour.

The container calls `https://en.wikipedia.org/wiki/Special:Random` and reads the `Location` header. It does not follow the redirect. It then posts `Read <url>` to `http://todo-backend:2345/todos`. The backend stores that string in Postgres.

Every URL and the length limit come from the ConfigMap `read-wikipedia-config`.

## Kubernetes

From the repository root. The image is local, so k3d needs an import. Todo-backend must already be running.

```bash
docker build -t read-wikipedia:2.9 the_project/read-wikipedia
k3d image import read-wikipedia:2.9
kubectl apply -f the_project/namespace.yaml
kubectl apply -f the_project/read-wikipedia/manifests/
```

To try one run without waiting for the hour:

```bash
kubectl create job -n project read-wikipedia-now --from=cronjob/read-wikipedia
kubectl wait -n project --for=condition=complete job/read-wikipedia-now --timeout=120s
kubectl logs -n project job/read-wikipedia-now
```

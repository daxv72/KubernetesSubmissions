# 2.7 Stateful applications

Postgres runs as a StatefulSet with one replica in the namespace `exercises`. The headless Service is `postgres` (`clusterIP: None`). The pod name stays `postgres-0`, and its DNS name is `postgres-0.postgres`.

The volume is created from `volumeClaimTemplates` with the `local-path` storage class. Postgres 18 keeps its files under `/var/lib/postgresql`, so that is the mount path. Deleting the StatefulSet does not delete the volume.

Ping-pong (`exercises/1.9`, image `ping-pong:2.7`) stores the counter in the table `ping_counter`. `GET /pingpong` still returns `pong N` and then increments. `GET /pings` only reads. The process waits until Postgres accepts connections.

The password `example` is the course sample. It lives in the Secret `postgres-auth`, together with the user and the database name.

## Kubernetes

From the repository root. Pull Postgres once, then import it. k3d nodes do not need to download it themselves.

```bash
docker pull postgres:18.0
docker build -t ping-pong:2.7 exercises/1.9
k3d image import postgres:18.0
k3d image import ping-pong:2.7
kubectl apply -f exercises/2.3/exercises-namespace.yaml
kubectl apply -f exercises/2.7/secret.yaml
kubectl apply -f exercises/2.7/statefulset.yaml
kubectl apply -f exercises/1.9/manifests/
kubectl rollout status statefulset/postgres -n exercises
kubectl rollout status deployment/ping-pong -n exercises
```

Then open http://localhost:8081/pingpong. The first response is `pong 0`. A new Ping-pong pod keeps the same number, because the row is in Postgres.

To look at the table from a throwaway pod:

```bash
kubectl run -n exercises -it --rm --restart=Never --image postgres:18.0 psql-for-debugging -- psql postgres://postgres:example@postgres:5432/postgres
```

# Exercise 1.11

Persistent volume shared by Log output (`exercises/1.3`) and ping-pong (`exercises/1.9`). The volume is not part of either application, so its definition lives here.

`shared-pv` is a local directory, `/tmp/kube`, on node `k3d-k3s-default-agent-0`. `shared-claim` binds it. Both Deployments mount that claim at `/usr/src/app/files`. `ReadWriteOnce` allows the two Pods when they run on that node.

`log-writer` appends `timestamp: uuid.` to `log.txt` every 5 seconds. Ping-pong stores the request count in `pings.txt`. `GET /` on Log output shows the latest log line and `Ping / Pongs: N`.

## Kubernetes

From the repository root. Create the directory on the node before the volume.

```bash
docker exec k3d-k3s-default-agent-0 mkdir -p /tmp/kube
kubectl apply -f exercises/1.11/
docker build -t log-writer:1.11 exercises/1.3/writer
docker build -t log-reader:1.11 exercises/1.3/reader
docker build -t ping-pong:1.11 exercises/1.9
k3d image import log-writer:1.11 log-reader:1.11 ping-pong:1.11
kubectl apply -f exercises/1.3/manifests/deployment.yaml
kubectl apply -f exercises/1.9/manifests/deployment.yaml
```

Three requests to http://localhost:8081/pingpong, then http://localhost:8081/ shows one `timestamp: uuid.` line and `Ping / Pongs: 3`. The count remains after a Pod is replaced.

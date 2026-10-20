# Ping-pong

Exercise 1.11. `GET /pingpong` returns `pong N` and then stores `N + 1` in `pings.txt` on the shared persistent volume. A restart keeps the count. The claim is `shared-claim` in `exercises/1.11`.

The Ingress is shared with Log output (`exercises/1.3`). `/pingpong` goes to this Service. `/` stays on Log output.

## Kubernetes

From the repository root. The image is local, so k3d needs an import. The Deployment sets `PORT=3000`. The Service is ClusterIP on port `3000`. The volume must exist first.

```bash
docker exec k3d-k3s-default-agent-0 mkdir -p /tmp/kube
kubectl apply -f exercises/1.11/
docker build -t ping-pong:1.11 exercises/1.9
k3d image import ping-pong:1.11
kubectl apply -f exercises/1.9/manifests/deployment.yaml
```

Then open http://localhost:8081/pingpong. The first response is `pong 0`. Log output shows that count as `Ping / Pongs`.


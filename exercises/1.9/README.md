# Ping-pong

Exercise 2.7. `GET /pingpong` returns `pong N` and then increments the counter. `GET /pings` returns that counter and does not increment it. The counter is one row in Postgres (`exercises/2.7`). Log output still reads it over HTTP.

The Ingress is shared with Log output (`exercises/1.3`). `/pingpong` goes to this Service. `/` stays on Log output.

## Kubernetes

From the repository root. The image is local, so k3d needs an import. The Deployment sets `PORT=3000`. The Service is ClusterIP on port `3000`.

```bash
docker build -t ping-pong:2.7 exercises/1.9
k3d image import ping-pong:2.7
kubectl apply -f exercises/2.3/exercises-namespace.yaml
kubectl apply -f exercises/2.7/
kubectl apply -f exercises/1.9/manifests/
```

Then open http://localhost:8081/pingpong. The first response is `pong 0`. Log output reads `http://ping-pong:3000/pings`. The count survives a new Ping-pong pod.


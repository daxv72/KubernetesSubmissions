# Ping-pong

Exercise 2.1. `GET /pingpong` returns `pong N` and then increments an in-memory counter. `GET /pings` returns that counter and does not increment it. There is no volume: Log output reads the count over HTTP. See `exercises/2.1`.

The Ingress is shared with Log output (`exercises/1.3`). `/pingpong` goes to this Service. `/` stays on Log output.

## Kubernetes

From the repository root. The image is local, so k3d needs an import. The Deployment sets `PORT=3000`. The Service is ClusterIP on port `3000`.

```bash
docker build -t ping-pong:2.1 exercises/1.9
k3d image import ping-pong:2.1
kubectl apply -f exercises/1.9/manifests/
```

Then open http://localhost:8081/pingpong. The first response is `pong 0`. Log output reads `http://ping-pong:3000/pings`.


# 3.2 Log output and Ping-pong behind an Ingress

Theoretical manifest for GKE. Nothing here was applied to Google Cloud.

Log output stays `exercises/1.3` (reader image `log-reader:2.5`, writer `log-writer:1.11`). It already answers `GET /` with HTTP 200.

Ping-pong stays `exercises/1.9`, image `ping-pong:3.2`. `GET /pingpong` still returns `pong N` and then increments. `GET /pings` only reads. `GET /` now returns `ok` and does not increment.

## Why `GET /` exists

A GKE Ingress health check calls `GET /` on the Pod, on the container port. It does not call the Ingress path. `/pingpong` on the Ingress still arrives at the app as `/pingpong`. Without a 200 on `/`, GKE marks the Ping-pong backend unhealthy and the path stays on 502.

Log output is already mapped to `/`, so its existing handler is enough.

## What GKE would do

The course requires a NodePort Service. GKE does not open that node port to the internet. The public address is the one printed by `kubectl get ing`.

```bash
kubectl apply -f exercises/2.3/exercises-namespace.yaml
kubectl apply -f exercises/2.7/secret.yaml
kubectl apply -f exercises/2.7/statefulset.yaml
kubectl apply -f exercises/2.5/configmap.yaml
kubectl apply -f exercises/1.3/manifests/deployment.yaml
kubectl apply -f exercises/1.9/manifests/deployment.yaml
kubectl apply -f exercises/3.2/services.yaml
kubectl apply -f exercises/3.2/ingress.yaml
kubectl get ing -n exercises
```

`kubectl get ing` then shows an `ADDRESS`. `http://<ADDRESS>/` is Log output. `http://<ADDRESS>/pingpong` is Ping-pong. The address stays empty for a few minutes, and the first requests can be 404 or 502 while the health checks pass.

Do not apply `exercises/1.9/manifests/` or `exercises/1.3/manifests/` as directories. Those directories still contain the ClusterIP Services and the k3d Ingress.

On real GKE the images must be in a registry the nodes can pull. `postgres:18.0` is public. `ping-pong:3.2`, `log-reader:2.5` and `log-writer:1.11` are local. The StatefulSet still says `storageClassName: local-path`; on GKE that class does not exist, so remove it and let the default persistent disk class take over.

These commands were not run.

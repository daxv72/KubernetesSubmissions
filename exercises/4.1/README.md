# Exercise 4.1 — Readiness probes

Ping-pong is ready when it can answer `GET /pings`. The process starts listening only after Postgres accepts a connection, so the probe stays failed until the database is up. `/pings` does not increment the counter.

Log output has two containers. `log-writer` has no probe and becomes ready on its own. `log-reader` is ready only when `http://ping-pong:3000/pings` returns the counter. Until then the Pod stays `1/2`.

The probes are on the deployments that already run these apps:

- `exercises/1.9/manifests/deployment.yaml`
- `exercises/1.3/manifests/deployment.yaml`

Apply the Secret, the ConfigMap, both Services and both Deployments. Leave `exercises/2.7/statefulset.yaml` out. `kubectl get po -n exercises` then shows Ping-pong `0/1` and Log output `1/2`. Applying the StatefulSet moves them to `1/1` and `2/2`.

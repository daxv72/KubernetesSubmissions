# Exercise 4.3 — Prometheus

Prometheus is the Helm release `prom` from `prometheus-community/prometheus`, in the namespace `monitoring`. Grafana and Loki from the monitoring chapter are in the same namespace. The GUI is the Service, not the Pod:

```bash
kubectl port-forward svc/prom-prometheus-server -n monitoring 9090:80
```

Open http://localhost:9090.

`kube_pod_info` is 1 for every pod kube-state-metrics sees. `created_by_kind="StatefulSet"` keeps the pods owned by a StatefulSet. `sum` adds those 1s, so the result is the number of pods. The course screenshot is that sum, and the value is 3.

```promql
sum(kube_pod_info{namespace="prometheus",created_by_kind="StatefulSet"})
```

On this cluster the three series are `counted-0`, `counted-1` and `counted-2` from `statefulset.yaml`. The chapter 3 chart runs in `monitoring` and does not create StatefulSet pods in the namespace `prometheus`.

The canary Rollout is `rollout.yaml`: `flaky-update-dep`, image `mluukkai/dwk-app8:v1`, Service `flaky-update-svc`. The image manifest is linux/amd64 only. These k3d nodes are arm64, so the pods stay in `ImagePullBackOff`.

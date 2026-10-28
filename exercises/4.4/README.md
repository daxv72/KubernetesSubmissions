# Exercise 4.4 — Ping-pong canary

The Rollout replaces the ping-pong Deployment. After `setWeight: 50` it runs the AnalysisTemplate `ping-pong-cpu`.

The query is the sum of the per-container CPU rate in the namespace `exercises`, over five minutes:

```promql
scalar(sum(rate(container_cpu_usage_seconds_total{namespace="exercises",container!=""}[5m])))
```

Prometheus is `http://prom-prometheus-server.monitoring.svc.cluster.local:80`. The metric is sampled five times, one minute apart. One failure above the limit fails the AnalysisRun. The controller then aborts the Rollout and scales the new ReplicaSet to zero.

The limit is `0.001` cores. On this cluster the same query returned about `0.017`, so the limit is below the live usage. An image change to `ping-pong:4.4` produced AnalysisRun `ping-pong-7c485774d9-2-1` with status Failed (`failed (2) > failureLimit (1)`). The Rollout stayed `Degraded` / `RolloutAborted`. The only ready pod kept `ping-pong:3.4`. The ReplicaSet for `ping-pong:4.4` stayed at 0 replicas.

A limit above the measured rate, for example `0.5`, would let the five samples succeed.

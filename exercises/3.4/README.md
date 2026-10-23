# 3.4 Rewrite /pingpong to /

Theoretical change. Nothing was applied to Google Cloud.

Ping-pong (`exercises/1.9`, image `ping-pong:3.4`) now counts on `GET /`. `GET /pings` still only reads. `GET /pingpong` on the process does the same as `GET /`, because the k3d Ingress does not rewrite.

The HTTPRoute keeps the public path `/pingpong`. A `URLRewrite` filter with `ReplacePrefixMatch: /` changes that prefix to `/` before the request reaches the Pod. The browser is not redirected. `RequestRedirect` and `URLRewrite` cannot be used on the same rule.

`/pingpong` is a longer prefix than `/`, so the first rule wins. `/` still goes to Log output, with no rewrite.

```bash
kubectl apply -f exercises/3.4/httproute.yaml
```

That replaces the HTTPRoute from exercise 3.3, which has the same name. The Gateway and the ClusterIP Services stay as they are in `exercises/3.3`. This command was not run.

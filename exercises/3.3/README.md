# 3.3 Gateway API instead of Ingress

Theoretical manifest for GKE. Nothing here was applied to Google Cloud. A Gateway of class `gke-l7-global-external-managed` provisions an external load balancer.

Before the Gateway exists, the cluster has to enable the API:

```bash
gcloud container clusters update dwk-cluster --location=europe-north1-b --gateway-api=standard
```

That command was not run.

The Service type goes back to ClusterIP. Ingress needed NodePort. The Gateway controller talks to the ClusterIP. Ports stay 3000 and 2345.

`HTTPRoute` replaces `exercises/3.2/ingress.yaml`. `PathPrefix /pingpong` is more specific than `PathPrefix /`, so it is chosen for that path. The path is not rewritten: Ping-pong still receives `/pingpong`. Rewriting `/pingpong` to `/` is exercise 3.4.

```bash
kubectl apply -f exercises/3.3/services.yaml
kubectl apply -f exercises/3.3/gateway.yaml
kubectl apply -f exercises/3.3/httproute.yaml
kubectl get gateway -n exercises my-gateway
```

`kubectl get gateway` prints the public address once `PROGRAMMED` is True. `http://<ADDRESS>/` is Log output. `http://<ADDRESS>/pingpong` is Ping-pong. The address can take several minutes.

Delete the Ingress from exercise 3.2 so it does not keep its own load balancer:

```bash
kubectl delete -f exercises/3.2/ingress.yaml
```

On k3d this Gateway does not work as written. k3d has no class `gke-l7-global-external-managed`. The course installs Envoy Gateway and uses class `eg`, and that requires a cluster created with Traefik disabled. The current k3d cluster still uses Traefik for the project, so it was left unchanged.

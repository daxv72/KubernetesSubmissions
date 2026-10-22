# 3.1 Ping-pong on GKE

Ping-pong from `exercises/1.9` (image `ping-pong:2.7`) runs on a local GKE cluster emulated by Floci. The counter still lives in the Postgres StatefulSet from exercise 2.7.

The Service in this directory is a LoadBalancer. It selects the same pods as the ClusterIP Service in `exercises/1.9`, and it publishes port 80 to container port 3000. Apply this file after the Deployment. Do not apply `exercises/1.9/manifests/` as a directory: that directory also contains the ClusterIP Service and the Ingress.

Google would attach a public IP to this Service. Floci does not. Use `kubectl port-forward`.

## Commands

From the repository root. The `gcloud` variables must point at `http://localhost:4588`. They are listed in the root README, section "GKE locale con Floci".

```bash
export KUBECONFIG="$HOME/.floci/gcp/kubeconfig"
gcloud container clusters create dwk-cluster --region=us-central1 --async
gcloud container clusters list --region=us-central1
gcloud container clusters get-credentials dwk-cluster --region=us-central1
kubectl get nodes

docker pull postgres:18.0
docker build -t ping-pong:2.7 exercises/1.9
# The k3s container name is floci-gcp-gke-<project>-<cluster>.
C=floci-gcp-gke-floci-local-dwk-cluster
docker save postgres:18.0 | docker exec -i "$C" ctr -a /run/k3s/containerd/containerd.sock -n k8s.io images import -
docker save ping-pong:2.7 | docker exec -i "$C" ctr -a /run/k3s/containerd/containerd.sock -n k8s.io images import -

kubectl apply -f exercises/2.3/exercises-namespace.yaml
kubectl apply -f exercises/2.7/secret.yaml
kubectl apply -f exercises/2.7/statefulset.yaml
kubectl apply -f exercises/1.9/manifests/deployment.yaml
kubectl apply -f exercises/3.1/service.yaml
kubectl rollout status statefulset/postgres -n exercises
kubectl rollout status deployment/ping-pong -n exercises
kubectl get svc ping-pong -n exercises
kubectl port-forward -n exercises svc/ping-pong 8086:80
```

Then open http://127.0.0.1:8086/pingpong. The first response is `pong 0`.

`KUBECONFIG` keeps this cluster separate from k3d. Without that variable, `kubectl` still uses `k3d-k3s-default`.

Prima di ogni `gcloud` locale, nello stesso terminale:

```bash
export CLOUDSDK_CONFIG="$HOME/.floci/gcp/gcloud"
export CLOUDSDK_CORE_PROJECT=floci-local
export CLOUDSDK_AUTH_ACCESS_TOKEN=floci-fake-token
export CLOUDSDK_CORE_DISABLE_PROMPTS=1
export CLOUDSDK_CORE_SHOULD_PROMPT_TO_ENABLE_API=false
E=http://localhost:4588
export CLOUDSDK_API_ENDPOINT_OVERRIDES_CONTAINER="$E/container/"
export CLOUDSDK_API_ENDPOINT_OVERRIDES_SERVICEUSAGE="$E/"
```

Senza queste variabili `gcloud` parla con Google Cloud vero. Non fare `gcloud auth login` per il cluster locale.

## Cosa cambierebbe su GKE vero

Gli YAML restano quelli. Cambiano il cluster, l'immagine e l'indirizzo con cui si apre Ping-pong.

| | Qui, con Floci | Su GKE |
|---|---|---|
| Account | Token finto, `gcloud` forzato su `localhost:4588` | `gcloud auth login`, progetto vero, API `container.googleapis.com` abilitata |
| Cluster | Un container k3s, API su `localhost:6551` | Quattro VM `e2-small`, vedi il comando sotto |
| Immagine | `docker save` e import nel container k3s | I nodi scaricano da un registry. `ping-pong:2.7` va pubblicato (Artifact Registry o Docker Hub). `postgres:18.0` è già pubblico |
| Disco di Postgres | StorageClass `local-path`, quella di k3s | `local-path` non esiste. Si toglie `storageClassName` dallo StatefulSet e GKE usa la sua classe predefinita, un persistent disk |
| LoadBalancer | `EXTERNAL-IP` `172.17.0.6`, irraggiungibile dal Mac. Si usa `port-forward` sulla 8086 | L'IP resta `<pending>` per un po', poi diventa pubblico. Il browser apre `http://<IP>/pingpong` sulla porta 80 |
| kubectl | kubeconfig separato in `~/.floci/gcp/kubeconfig` | `get-credentials` scrive in `~/.kube/config` e quel contesto diventa quello corrente. Per tornare a k3d: `kubectl config use-context k3d-k3s-default` |
| Spegnimento | Cancella solo il container locale | Finché il cluster e il LoadBalancer esistono, la fattura continua |

Creazione del cluster, come nel capitolo:

```bash
gcloud container clusters create dwk-cluster \
  --zone=europe-north1-b \
  --cluster-version=1.36 \
  --disk-size=32 \
  --num-nodes=4 \
  --machine-type=e2-small
gcloud container clusters get-credentials dwk-cluster --zone=europe-north1-b
```

Poi si pubblica `ping-pong:2.7`, si applica gli stessi manifest (con la StorageClass adatta a GKE) e si aspetta l'IP:

```bash
kubectl get svc ping-pong -n exercises --watch
```

Per smettere di pagare:

```bash
gcloud container clusters delete dwk-cluster --zone=europe-north1-b
```

Il Service `service.yaml` si applica così com'è. La risposta dell'app resta `pong 0`, poi il contatore sale, perché il codice e Postgres sono gli stessi.

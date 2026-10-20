# DevOps with Kubernetes

## Exercises

### Chapter 2

- [1.1.](https://github.com/daxv72/KubernetesSubmissions/tree/1.1/exercises/1.1)
- [1.2.](https://github.com/daxv72/KubernetesSubmissions/tree/1.2/the_project)
- [1.3.](https://github.com/daxv72/KubernetesSubmissions/tree/1.3/exercises/1.3)
- [1.4.](https://github.com/daxv72/KubernetesSubmissions/tree/1.4/exercises/1.4)
- [1.5.](https://github.com/daxv72/KubernetesSubmissions/tree/1.5/the_project)

## Comandi usati per l'esercizio 1.1

App **Log output** in `exercises/1.1`. All'avvio genera una stringa casuale, la tiene in memoria e la stampa ogni 5 secondi con un timestamp UTC.

I comandi vanno lanciati dalla root di questo repository, salvo dove è indicato un altro percorso.

## 1. Vedere se c'è un cluster

```bash
kubectl config current-context
kubectl config get-contexts
kubectl get nodes
k3d cluster list
docker info --format 'server={{.ServerVersion}}'
```

- `kubectl config current-context` mostra il cluster a cui punta kubectl. Qui all'inizio era `docker-desktop`, spento (`connection refused` su `127.0.0.1:6443`).
- `kubectl config get-contexts` elenca i contesti salvati (`docker-desktop`, `minikube`).
- `kubectl get nodes` chiede i nodi al cluster attivo. Se l'API non risponde, il contesto è sbagliato o il cluster è spento.
- `k3d cluster list` elenca i cluster k3d. Vuoto significa che il cluster del corso non esiste.
- `docker info` conferma che il daemon Docker è acceso. k3d crea i nodi come container Docker.

## 2. Costruire l'immagine

```bash
docker build -t log-output:1.1 exercises/1.1
```

`-t log-output:1.1` dà nome e tag all'immagine. Il tag `1.1` è quello scritto in `exercises/1.1/manifests/deployment.yaml`. Senza un tag esplicito Docker usa `latest`, e Kubernetes in quel caso ritenta il pull a ogni avvio del Pod.

Il contesto di build è `exercises/1.1` perché lì stanno `Dockerfile` e `main.py`. `.dockerignore` copia solo `main.py`.

## 3. Creare il cluster k3d

```bash
k3d cluster create -a 2
```

Come nel capitolo del corso: un server (control plane) e 2 agent. k3d scrive il kubeconfig e imposta il contesto `k3d-k3s-default`.

Il cluster creato in questa sessione è stato poi cancellato con `k3d cluster delete`. Dopo quella cancellazione kubectl torna sul contesto precedente (`docker-desktop`), che non ha un'API in ascolto.

Per ricrearlo e riusarlo:

```bash
k3d cluster create -a 2
kubectl config use-context k3d-k3s-default
kubectl cluster-info
```

## 4. Importare l'immagine nel cluster

```bash
k3d image import log-output:1.1
```

k3d gira dentro Docker, ma i nodi non vedono da soli le immagini costruite sulla macchina. `k3d image import` copia `log-output:1.1` dentro ogni nodo.

Nel Deployment c'è `imagePullPolicy: IfNotPresent`. Con un tag diverso da `latest` è già il default: Kubernetes usa la copia locale e non cerca l'immagine su Docker Hub. Senza l'import il Pod resta in `ImagePullBackOff`.

## 5. Applicare il Deployment

```bash
kubectl apply -f exercises/1.1/manifests/deployment.yaml
kubectl rollout status deployment/log-output --timeout=90s
kubectl get pods -l app=log-output
```

- `kubectl apply` crea o aggiorna il Deployment `log-output` (1 replica).
- `kubectl rollout status` aspetta che il Pod nuovo sia Ready.
- `-l app=log-output` seleziona il Pod tramite l'etichetta, senza usare il suffisso casuale del nome (`log-output-84b9dc656-hdbpc`).

`kubectl apply` ha bisogno dell'API del cluster. Con il contesto `docker-desktop` spento fallisce con `connection refused` su `127.0.0.1:6443`, anche con `--dry-run=client`, perché kubectl scarica lo schema OpenAPI dal cluster.

## 6. Leggere i log

```bash
kubectl logs -l app=log-output --tail=6
kubectl logs -l app=log-output -f
```

`--tail=6` mostra le ultime righe. `-f` segue lo stream; si interrompe con Ctrl+C.

Output atteso: stessa stringa ogni 5 secondi, timestamp che avanza.

```text
2026-10-20T08:27:25.340Z: cd923218-9079-4e4e-951a-110dd0e22eda
2026-10-20T08:27:30.341Z: cd923218-9079-4e4e-951a-110dd0e22eda
```

La stringa è generata una volta all'avvio del processo. Un restart del Pod ne crea una nuova.

Due dettagli nel codice, altrimenti `kubectl logs` resta vuoto:

- `print(..., flush=True)` in `main.py`
- `ENV PYTHONUNBUFFERED=1` nel Dockerfile

Senza un terminale, Python tiene stdout in un buffer.

## 7. Risorse del container

In `exercises/1.1/manifests/deployment.yaml`:

```yaml
resources:
  requests:
    cpu: 10m
    memory: 32Mi
  limits:
    cpu: 50m
    memory: 64Mi
```

Senza `resources` l'editor segnala: `One or more containers do not have resources - this can cause noisy neighbor issues`.

- `requests`: quanto lo scheduler riserva sul nodo.
- `limits`: tetto. Oltre la CPU il processo viene rallentato; oltre la memoria il Pod viene ucciso.

`10m` è il 1% di un core. Per un processo che dorme e stampa, questi valori bastano.

## Sequenza completa, cluster spento

```bash
docker build -t log-output:1.1 exercises/1.1
k3d cluster create -a 2
k3d image import log-output:1.1
kubectl apply -f exercises/1.1/manifests/deployment.yaml
kubectl rollout status deployment/log-output --timeout=90s
kubectl logs -l app=log-output -f
```

## Esercizio 1.2 — todo app

App in `the_project/todo-app`, come nell'esempio del corso. All'avvio stampa `Server started in port NNNN`. La porta arriva dalla variabile `PORT` (nel Deployment è `3000`). Non c'è ancora un Service: il corso lo aggiunge con il networking.

```bash
docker build -t todo-app:1.2 the_project/todo-app
k3d image import todo-app:1.2
kubectl apply -f the_project/todo-app/manifests/deployment.yaml
kubectl rollout status deployment/todo-app --timeout=90s
kubectl logs -l app=todo-app
```

## Esercizio 1.3 — Log output, manifest dichiarativo

Cartella `exercises/1.3`. Il Deployment sta in `exercises/1.3/manifests/deployment.yaml`. L'immagine è `log-output:1.3`, stesso programma della 1.1. Il riavvio crea un Pod nuovo, quindi la stringa casuale cambia.

```bash
docker build -t log-output:1.3 exercises/1.3
k3d image import log-output:1.3
kubectl apply -f exercises/1.3/manifests/deployment.yaml
kubectl rollout restart deployment/log-output
kubectl logs -l app=log-output -f
```

## Esercizio 1.4 — todo app, deployment.yaml

Cartella `exercises/1.4`. Il file è `exercises/1.4/manifests/deployment.yaml`. Il codice resta in `the_project/todo-app`. Nessun Service.

```bash
kubectl apply -f exercises/1.4/manifests/deployment.yaml
kubectl logs -l app=todo-app
```

## Esercizio 1.5 — GET / e port-forward

Il codice resta in `the_project/todo-app`. `GET /` restituisce una pagina HTML. Il Deployment imposta `PORT=3000` e l'immagine `todo-app:1.5`. Non c'è ancora un Service: l'accesso dalla macchina è `kubectl port-forward`.

```bash
docker build -t todo-app:1.5 the_project/todo-app
k3d image import todo-app:1.5
kubectl apply -f the_project/todo-app/manifests/deployment.yaml
kubectl rollout status deployment/todo-app --timeout=90s
kubectl port-forward deployment/todo-app 3003:3000
```

Aprire http://localhost:3003/. Ctrl+C chiude il forward.

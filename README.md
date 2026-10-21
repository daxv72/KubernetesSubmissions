# DevOps with Kubernetes

Definizioni, link alla documentazione e spiegazione dei comandi kubectl: [TEORIA.md](TEORIA.md).

## Exercises

### Chapter 2

- [1.1.](https://github.com/daxv72/KubernetesSubmissions/tree/1.1/exercises/1.1)
- [1.2.](https://github.com/daxv72/KubernetesSubmissions/tree/1.2/the_project)
- [1.3.](https://github.com/daxv72/KubernetesSubmissions/tree/1.3/exercises/1.3)
- [1.4.](https://github.com/daxv72/KubernetesSubmissions/tree/1.4/exercises/1.4)
- [1.5.](https://github.com/daxv72/KubernetesSubmissions/tree/1.5/the_project)
- [1.6.](https://github.com/daxv72/KubernetesSubmissions/tree/1.6/the_project)
- [1.7.](https://github.com/daxv72/KubernetesSubmissions/tree/1.7/exercises/1.3)
- [1.8.](https://github.com/daxv72/KubernetesSubmissions/tree/1.8/the_project)
- [1.9.](https://github.com/daxv72/KubernetesSubmissions/tree/1.9/exercises/1.9)
- [1.10.](https://github.com/daxv72/KubernetesSubmissions/tree/1.10/exercises/1.3)
- [1.11.](https://github.com/daxv72/KubernetesSubmissions/tree/1.11/exercises/1.11)
- [1.12.](https://github.com/daxv72/KubernetesSubmissions/tree/1.12/exercises/1.12)
- [1.13.](https://github.com/daxv72/KubernetesSubmissions/tree/1.13/the_project)

### Networking between pods

- [2.1.](https://github.com/daxv72/KubernetesSubmissions/tree/2.1/exercises/2.1)
- [2.2.](https://github.com/daxv72/KubernetesSubmissions/tree/2.2/the_project)
- [2.3.](https://github.com/daxv72/KubernetesSubmissions/tree/2.3/exercises/2.3)
- [2.4.](https://github.com/daxv72/KubernetesSubmissions/tree/2.4/the_project)
- [2.5.](https://github.com/daxv72/KubernetesSubmissions/tree/2.5/exercises/2.5)
- [2.6.](https://github.com/daxv72/KubernetesSubmissions/tree/2.6/the_project)
- [2.7.](https://github.com/daxv72/KubernetesSubmissions/tree/2.7/exercises/2.7)

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
---> k3d cluster create --port 8082:30080@agent:0 -p 8081:80@loadbalancer --agents 2
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

## Network — dall'app al browser

Il container di `hashresponse` ascolta sulla porta **3000**. Questa è `targetPort`. Non è una porta della macchina e non è la 2345.

Un Service sceglie i Pod con `selector: app: hashresponse` e inoltra il traffico a quella 3000. Se ne applica uno solo alla volta, sempre con il nome `hashresponse-svc`.

### NodePort, quello che apre http://localhost:8082/

File: `material-example/app2/manifests/nodeport_service.yaml`.

| Campo | Porta | Chi la usa |
| --- | --- | --- |
| `targetPort` | 3000 | il processo nel container |
| `port` | 1234 | gli altri Pod, via `hashresponse-svc:1234` |
| `nodePort` | 30080 | ogni nodo del cluster |

k3d è stato creato con `--port 8082:30080@agent:0`. Con k3d 5.9 la pubblicazione sta sul load balancer, che inoltra a `agent-0:30080`.

```text
browser localhost:8082
  → load balancer, porta 30080
    → nodo agent-0, NodePort 30080
      → Service, porta interna 1234
        → Pod, porta 3000
```

Il Pod può stare su un altro nodo, per esempio `agent-1`. Il NodePort è aperto su tutti i nodi e kube-proxy raggiunge il Pod lo stesso.

Il file `material-example/app2/manifests/service.yaml` non è questo passaggio. È il ClusterIP del passaggio successivo. Applicarlo non apre la 30080, quindi `localhost:8082` non risponde.

```bash
kubectl apply -f material-example/app2/manifests/deployment.yaml
kubectl apply -f material-example/app2/manifests/nodeport_service.yaml
```

Poi http://localhost:8082/.

### ClusterIP, quello che arriva con Ingress

Lo stesso nome `hashresponse-svc` viene sostituito. `type: ClusterIP`, `port: 2345`, `targetPort: 3000`. La 2345 esiste solo dentro il cluster. Il load balancer non la pubblica.

Ingress (porta 80 del cluster, sulla macchina la 8081) manda le richieste a `hashresponse-svc:2345`, e il Service le porta al container sulla 3000.

```text
browser localhost:8081
  → load balancer, porta 80
    → Ingress
      → Service, porta 2345
        → Pod, porta 3000
```

## Esercizio 1.6 — NodePort del todo app

Il Service sta in `the_project/todo-app/manifests/service.yaml`. La 30080 è già di `hashresponse` (`localhost:8082`), quindi il progetto usa la **30081**, pubblicata sulla **8083**.

| Campo | Porta |
| --- | --- |
| `targetPort` | 3000, il container |
| `port` | 3000, gli altri Pod via `todo-app:3000` |
| `nodePort` | 30081, ogni nodo |

```text
browser localhost:8083
  → load balancer, porta 30081
    → NodePort 30081
      → Service, porta 3000
        → container, porta 3000
```

Il cluster ricreato non ha più il Deployment. L'immagine va reimportata.

```bash
k3d image import todo-app:1.5
k3d cluster edit k3s-default --port-add 8083:30081@agent:0
kubectl apply -f the_project/todo-app/manifests/deployment.yaml
kubectl apply -f the_project/todo-app/manifests/service.yaml
```

Poi http://localhost:8083/.

## Esercizio 1.7 — Ingress di Log output

L'app è `exercises/1.3`. All'avvio genera la stringa e la tiene in memoria. Ogni 5 secondi la stampa nei log. `GET /` restituisce il timestamp corrente e la stessa stringa.

Il Service è ClusterIP: porta **2345** verso il container sulla **3000**. L'Ingress manda `/` a quel Service. Sulla macchina la porta è la **8081**, già pubblicata dal load balancer sulla porta 80.

```text
browser localhost:8081
  → load balancer, porta 80
    → Ingress log-output, path /
      → Service log-output, porta 2345
        → container, porta 3000
```

`dwk-material-ingress` dell'esempio usa anch'esso `/`. Va tolto dal cluster, altrimenti i due Ingress si contendono la stessa richiesta. Il file in `material-example` non si tocca.

```bash
kubectl delete ingress dwk-material-ingress
docker build -t log-output:1.7 exercises/1.3
k3d image import log-output:1.7
kubectl apply -f exercises/1.3/manifests/
```

Poi http://localhost:8081/.

## Esercizio 1.8 — Ingress del todo app

Il NodePort del progetto è sostituito da un ClusterIP e da un Ingress. Il file è `the_project/todo-app/manifests/ingress.yaml`. La porta del Service resta **3000**, uguale a quella del container. Sulla macchina si entra dalla **8081**.

L'Ingress `log-output` usa lo stesso path `/`. Il corso dice di toglierlo, altrimenti le due app si contendono la richiesta. Il manifest in `exercises/1.3` resta nel repository: all'esercizio 1.9 i path li divideranno.

```text
browser localhost:8081
  → load balancer, porta 80
    → Ingress todo-app, path /
      → Service todo-app, porta 3000
        → container, porta 3000
```

```bash
kubectl delete ingress log-output
kubectl apply -f the_project/todo-app/manifests/service.yaml
kubectl apply -f the_project/todo-app/manifests/ingress.yaml
```

Poi http://localhost:8081/ mostra la pagina Todo. La 8083 non serve più: il Service non ha più un NodePort.

## Esercizio 1.9 — ping-pong

La seconda app è `exercises/1.9`. `GET /pingpong` risponde `pong 0` alla prima richiesta, poi `pong 1`, `pong 2`, e così via. Il contatore sta in memoria: un riavvio del Pod lo riporta a 0.

Condivide l'Ingress `log-output` con Log output. Il path più lungo vince, quindi `/pingpong` non finisce sull'app che ha `/`.

```text
browser localhost:8081/pingpong
  → load balancer, porta 80
    → Ingress log-output, path /pingpong
      → Service ping-pong, porta 3000
        → container, porta 3000

browser localhost:8081/
  → lo stesso Ingress, path /
    → Service log-output, porta 2345
      → container, porta 3000
```

L'Ingress `todo-app` usa ancora `/`. Va tolto dal cluster, altrimenti si contende la richiesta con Log output. Il file in `the_project` resta nel repository.

```bash
docker build -t ping-pong:1.9 exercises/1.9
k3d image import ping-pong:1.9
kubectl delete ingress todo-app --ignore-not-found
kubectl apply -f exercises/1.9/manifests/
kubectl apply -f exercises/1.3/manifests/ingress.yaml
```

Poi http://localhost:8081/pingpong e http://localhost:8081/.

## Esercizio 1.10 — due container, un file

Log output non è più un solo processo. Nel Pod `log-output` ci sono due container. Condividono un volume [emptyDir](https://kubernetes.io/docs/concepts/storage/volumes/#emptydir) montato su `/usr/src/app/files`. Il volume nasce con il Pod e sparisce con il Pod.

`log-writer` genera la stringa all'avvio e, ogni 5 secondi, accoda una riga `timestamp: string` in `log.txt`. `log-reader` legge quel file e lo restituisce su `GET /`. Il Service e l'Ingress non cambiano: `/` arriva ancora a `log-output:2345`, e ad ascoltare è solo `log-reader`.

Due container nello stesso Pod: `kubectl logs` senza `-c` non sa quale stdout prendere. La pagina del comando è quella indicata dal corso: [kubectl logs](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_logs/).

```bash
docker build -t log-writer:1.10 exercises/1.3/writer
docker build -t log-reader:1.10 exercises/1.3/reader
k3d image import log-writer:1.10 log-reader:1.10
kubectl apply -f exercises/1.3/manifests/
kubectl logs -l app=log-output -c log-writer --tail=2
kubectl logs -l app=log-output -c log-reader --tail=2
```

Poi http://localhost:8081/. Un reload dopo qualche secondo mostra una riga in più. La stringa resta la stessa finché il Pod non viene ricreato.

## Esercizio 1.11 — volume persistente

Il conteggio di ping-pong e il file di log stanno su un [PersistentVolume](https://kubernetes.io/docs/concepts/storage/persistent-volumes/) locale, non più su un emptyDir. I file sono in `exercises/1.11`: il volume e la richiesta di spazio. Stanno fuori dalle due app: un PersistentVolume è del cluster, non di un Deployment.

Il disco è la directory `/tmp/kube` sul nodo `k3d-k3s-default-agent-0`. Va creata prima. `ReadWriteOnce` ammette più Pod sullo stesso nodo. Lo scheduler mette entrambi su quel nodo perché il volume è locale.

`pings.txt` contiene il numero di richieste a `/pingpong`. `GET /` di Log output mostra l'ultima riga del log e quel numero.

```bash
docker exec k3d-k3s-default-agent-0 mkdir -p /tmp/kube
kubectl apply -f exercises/1.11/
docker build -t log-writer:1.11 exercises/1.3/writer
docker build -t log-reader:1.11 exercises/1.3/reader
docker build -t ping-pong:1.11 exercises/1.9
k3d image import log-writer:1.11 log-reader:1.11 ping-pong:1.11
kubectl apply -f exercises/1.3/manifests/deployment.yaml
kubectl apply -f exercises/1.9/manifests/deployment.yaml
```

Tre richieste a http://localhost:8081/pingpong, poi http://localhost:8081/ mostra una riga `timestamp: uuid.` e `Ping / Pongs: 3`. Il numero resta se il Pod viene ricreato.

## Esercizio 1.12 — immagine del progetto

La pagina del todo app mostra un'immagine presa da [Lorem Picsum](https://picsum.photos/1200). Il file sta su un volume persistente, in `exercises/1.12`, montato dal Deployment in `the_project/todo-app`.

Per 10 minuti ogni richiesta riceve lo stesso file. La prima richiesta dopo quei 10 minuti può ancora ricevere l'immagine vecchia. La richiesta successiva ne scarica una nuova. Se il container si spegne, il file resta sul nodo: il Pod nuovo non richiama Picsum finché l'immagine è ancora valida.

L'Ingress di Log output usa anch'esso `/`. Va tolto dal cluster, altrimenti la 8081 non mostra il progetto.

```bash
docker exec k3d-k3s-default-agent-0 mkdir -p /tmp/todo-images
kubectl apply -f exercises/1.12/
docker build -t todo-app:1.12 the_project/todo-app
k3d image import todo-app:1.12
kubectl delete ingress log-output --ignore-not-found
kubectl apply -f the_project/todo-app/manifests/
```

Poi http://localhost:8081/.

## Esercizio 1.13 — campo e lista

La pagina del progetto, in `the_project/todo-app`, aggiunge un campo e una lista. Il campo ha `maxlength="140"`: il browser non accetta un todo più lungo. Il pulsante Send è `type="button"` e non invia nulla. I tre todo sono scritti nell'HTML.

L'immagine della 1.12 resta. L'immagine del container diventa `todo-app:1.13`.

```bash
docker build -t todo-app:1.13 the_project/todo-app
k3d image import todo-app:1.13
kubectl apply -f the_project/todo-app/manifests/deployment.yaml
```

Poi http://localhost:8081/.

## Esercizio 2.1 — HTTP tra i Pod

Log output e ping-pong non condividono più un volume. Il conteggio sta in memoria dentro ping-pong.

`GET /pingpong` risponde `pong N` e poi incrementa. `GET /pings` restituisce il conteggio senza incrementarlo. Log output, a ogni richiesta su `/`, chiama il Service:

`http://ping-pong:3000/pings`

`ping-pong` è il nome DNS del Service, nello stesso namespace. La porta `3000` è la porta del Service, che inoltra alla porta del container.

I due container di Log output condividono ancora un `emptyDir` per `log.txt`. Quel volume non è montato da ping-pong.

```bash
docker build -t log-reader:2.1 exercises/1.3/reader
docker build -t ping-pong:2.1 exercises/1.9
k3d image import log-reader:2.1 ping-pong:2.1
kubectl apply -f exercises/1.9/manifests/
kubectl apply -f exercises/1.3/manifests/
```

Tre richieste a http://localhost:8081/pingpong, poi http://localhost:8081/ mostra la riga di log e `Ping / Pongs: 3`. Un refresh di `/` non aumenta il numero.

## Esercizio 2.2 — todo-backend

Il progetto resta un'app che genera l'HTML. Il nuovo servizio `todo-backend` tiene i todo in memoria.

- `GET /todos` risponde un array JSON.
- `POST /todos` aggiunge un todo. Il form del browser manda il campo `todo`. Testo vuoto o più lungo di 140 caratteri viene rifiutato. Se il salvataggio riesce, il backend risponde con un redirect a `/`.

Todo-app, a ogni apertura della pagina, chiama il Service:

`http://todo-backend:2345/todos`

`todo-backend` è il nome DNS. La porta `2345` è la porta del Service. Il container ascolta sulla `3000`.

L'Ingress del progetto manda `/todos` a todo-backend e `/` a todo-app. L'Ingress di Log output usa anch'esso `/`: va tolto, altrimenti la 8081 non mostra il progetto.

Il volume dell'immagine è quello della 1.12. Se il PVC resta `Pending`, il PersistentVolume va cancellato e ricreato: un volume locale `Released` non si riaggancia da solo.

```bash
docker exec k3d-k3s-default-agent-0 mkdir -p /tmp/todo-images
kubectl apply -f exercises/1.12/
docker build -t todo-backend:2.2 the_project/todo-backend
docker build -t todo-app:2.2 the_project/todo-app
k3d image import todo-backend:2.2 todo-app:2.2
kubectl delete ingress log-output --ignore-not-found
kubectl apply -f the_project/todo-backend/manifests/
kubectl apply -f the_project/todo-app/manifests/
```

Poi http://localhost:8081/. Il form aggiunge un todo e la pagina lo mostra.

## Esercizio 2.3 — namespace

Log output e ping-pong stanno nel namespace `exercises`. Il progetto sta nel namespace `project`. Gli esempi del corso possono restare in `default`.

Dentro lo stesso namespace il nome corto del Service basta ancora: `http://ping-pong:3000/pings` e `http://todo-backend:2345/todos`. Per chiamare un Service da un altro namespace serve il nome completo, per esempio `ping-pong.exercises.svc.cluster.local`.

Il PersistentVolume non ha namespace. Il claim dell'immagine, `todo-image-claim`, sta in `project`. Se il volume era già bound in `default`, dopo lo spostamento resta `Released`: va cancellato e ricreato.

I due Ingress usano entrambi il percorso `/`. Su http://localhost:8081/ ne risponde uno solo.

```bash
kubectl delete deployment,service log-output ping-pong todo-app todo-backend -n default --ignore-not-found
kubectl delete ingress log-output todo-app -n default --ignore-not-found
kubectl delete pvc todo-image-claim -n default --ignore-not-found
kubectl delete pv todo-image-pv --ignore-not-found
kubectl apply -f exercises/2.3/
kubectl apply -f exercises/1.12/
kubectl apply -f exercises/1.9/manifests/
kubectl apply -f exercises/1.3/manifests/
kubectl apply -f the_project/todo-backend/manifests/
kubectl apply -f the_project/todo-app/manifests/
```

`kubectl get deploy -n exercises` mostra log-output e ping-pong. `kubectl get deploy -n project` mostra todo-app e todo-backend.

## Esercizio 2.4 — namespace del progetto

Il namespace del progetto si chiama `project`. Il file è `the_project/namespace.yaml`. Deployment, Service, Ingress e il claim dell'immagine hanno `namespace: project`.

Gli esercizi futuri del progetto si applicano in quel namespace. Log output e ping-pong restano in `exercises`.

```bash
kubectl apply -f the_project/namespace.yaml
kubectl apply -f exercises/1.12/
kubectl apply -f the_project/todo-backend/manifests/
kubectl apply -f the_project/todo-app/manifests/
kubectl get deploy,svc,ingress,pvc -n project
```

## Esercizio 2.5 — ConfigMap

Log output, nel namespace `exercises`, legge un ConfigMap. La chiave `information.txt` è un file montato in `/usr/src/app/config/information.txt`. La chiave `MESSAGE` diventa la variabile d'ambiente con lo stesso nome, tramite `configMapKeyRef`.

La pagina aggiunge quelle due righe sopra l'output di sempre:

```
file content: this text is from file
env variable: MESSAGE=hello world
```

```bash
docker build -t log-reader:2.5 exercises/1.3/reader
k3d image import log-reader:2.5
kubectl apply -f exercises/2.3/exercises-namespace.yaml
kubectl apply -f exercises/2.5/configmap.yaml
kubectl apply -f exercises/1.9/manifests/
kubectl apply -f exercises/1.3/manifests/
```

Poi http://localhost:8081/.

## Esercizio 2.6 — configurazione fuori dal codice

Todo-app e todo-backend non hanno porte, URL o altri parametri nel sorgente. Ogni valore arriva da una variabile d'ambiente. Le variabili stanno nei ConfigMap `todo-app-config` e `todo-backend-config`, nel namespace `project`. Il Deployment le carica con `envFrom`.

Se manca una variabile, il processo si ferma all'avvio.

```bash
docker build -t todo-backend:2.6 the_project/todo-backend
docker build -t todo-app:2.6 the_project/todo-app
k3d image import todo-backend:2.6 todo-app:2.6
kubectl apply -f the_project/namespace.yaml
kubectl apply -f exercises/1.12/
kubectl apply -f the_project/todo-backend/manifests/
kubectl apply -f the_project/todo-app/manifests/
kubectl delete ingress log-output -n exercises --ignore-not-found
```

Poi http://localhost:8081/.

## Esercizio 2.7 — Postgres come StatefulSet

Postgres gira nel namespace `exercises` come StatefulSet `postgres`, una replica. Il Service è headless (`clusterIP: None`) e si chiama `postgres`, lo stesso nome di `serviceName`. Il pod resta `postgres-0`. Il volume nasce da `volumeClaimTemplates` con la storage class `local-path` ed è montato su `/var/lib/postgresql` (percorso richiesto da Postgres 18). Cancellare lo StatefulSet non cancella il volume.

Ping-pong salva il contatore nella tabella `ping_counter`. All'avvio riprova la connessione finché il database non accetta traffico. `GET /pingpong` risponde ancora `pong N` e poi incrementa. `GET /pings` legge soltanto.

La password `example` è quella dell'esempio del corso. Sta nel Secret `postgres-auth`.

```bash
docker pull postgres:18.0
docker build -t ping-pong:2.7 exercises/1.9
k3d image import postgres:18.0
k3d image import ping-pong:2.7
kubectl apply -f exercises/2.3/exercises-namespace.yaml
kubectl apply -f exercises/2.7/secret.yaml
kubectl apply -f exercises/2.7/statefulset.yaml
kubectl apply -f exercises/1.9/manifests/
kubectl rollout status statefulset/postgres -n exercises
kubectl rollout status deployment/ping-pong -n exercises
```

Poi http://localhost:8081/pingpong.












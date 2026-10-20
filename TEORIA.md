# Teoria e comandi kubectl — fino all'esercizio 1.9

Appunti di quanto usato nel capitolo di rete del corso *DevOps with Kubernetes* (2026), dal primo Deployment fino a ping-pong. I comandi da rilanciare per ogni esercizio restano nel [README](README.md). Qui ci sono le definizioni, i link alla documentazione e la spiegazione dei comandi `kubectl` usati.

Il cluster locale è **k3d** con **k3s**. k3d non è Kubernetes: è il programma che avvia i nodi come container Docker e pubblica alcune porte sulla macchina. kubectl parla solo con l'API di Kubernetes.

## Riferimenti

| Argomento | Documentazione |
| --- | --- |
| Pod | [Pods](https://kubernetes.io/docs/concepts/workloads/pods/) |
| Deployment e ReplicaSet | [Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/), [ReplicaSet](https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/) |
| Label e selector | [Labels and Selectors](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/) |
| Immagine e `imagePullPolicy` | [Images](https://kubernetes.io/docs/concepts/containers/images/#image-pull-policy) |
| CPU e memoria | [Managing resources for containers](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/) |
| Service, ClusterIP, NodePort | [Service](https://kubernetes.io/docs/concepts/services-networking/service/) |
| Ingress e path | [Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/) |
| Gestione dichiarativa | [Declarative object configuration](https://kubernetes.io/docs/concepts/overview/working-with-objects/object-management/#declarative-object-configuration) |
| Namespace | [Namespaces](https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/) |
| Elenco rapido di kubectl | [kubectl Quick Reference](https://kubernetes.io/docs/reference/kubectl/quick-reference/) |
| k3s e Traefik | [k3s networking](https://docs.k3s.io/networking) |
| Porte pubblicate da k3d | [k3d exposing services](https://k3d.io/stable/usage/exposing_services/) |

## Il cluster

Un cluster Kubernetes ha un **control plane** e dei **nodi**. Il control plane espone l'API (qui sulla porta 6443). I nodi eseguono i Pod. In questo laboratorio k3d crea un nodo server e due agent (`k3d cluster create --agents 2`). Il contesto di kubectl si chiama `k3d-k3s-default`.

All'inizio kubectl puntava a `docker-desktop`, spento. Ogni comando verso l'API rispondeva `connection refused` su `127.0.0.1:6443`. Anche `kubectl apply --dry-run=client` ha bisogno dell'API, perché kubectl scarica lo schema OpenAPI dal cluster.

Dopo `k3d cluster delete`, kubectl torna al contesto precedente. Va rimesso `k3d-k3s-default`.

 --> `kubectl config use-context k3d-k3s-default`

Le porte della macchina, con il cluster ricreato come nel corso:

| Porta sulla macchina | Dentro il cluster | A cosa serve |
| --- | --- | --- |
| 8081 | 80 del load balancer | Ingress (Traefik) |
| 8082 | NodePort 30080 | esempio `hashresponse` |
| 8083 | NodePort 30081 | todo app, solo nell'esercizio 1.6 |
| 3003 | niente, è locale | `kubectl port-forward` dell'esercizio 1.5 |

La 8083 non è più usata: dall'esercizio 1.8 il Service del todo app è ClusterIP.

## Definizioni

### Pod

Un [Pod](https://kubernetes.io/docs/concepts/workloads/pods/) è il processo in esecuzione. Qui ogni Pod ha un solo container. Il processo Python ascolta sulla porta del container (`PORT=3000` negli esercizi da 1.5 in poi; Log output e ping-pong usano la stessa porta). Quella porta non è aperta sulla macchina.

### Deployment

Un [Deployment](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/) dichiara quanti Pod identici devono esistere (`.spec.replicas`, qui 1) e con quale template. Kubernetes crea un [ReplicaSet](https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/), e il ReplicaSet crea i Pod. Se un Pod muore, il ReplicaSet ne avvia un altro. Il contatore di ping-pong e la stringa casuale di Log output stanno in memoria: il Pod nuovo riparte da zero.

`.spec.selector.matchLabels` deve combaciare con le label del template. Il Service usa le stesse label per trovare i Pod.

### Label e selector

Una [label](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/) è una coppia chiave-valore, per esempio `app: log-output`. Non è il nome dell'oggetto. Il nome (`metadata.name`) identifica l'oggetto. La label serve a raggruppare.

`-l app=log-output` su kubectl è un selector: il comando vale per tutti gli oggetti che hanno quella label. `app in (ping-pong,log-output)` ne prende due.

### Immagine

Il Deployment nomina un'immagine con tag (`log-output:1.7`, `todo-app:1.5`, `ping-pong:1.9`). [imagePullPolicy: IfNotPresent](https://kubernetes.io/docs/concepts/containers/images/#image-pull-policy) dice al nodo di usare la copia locale se c'è già. Con un tag diverso da `latest` è il default. Le immagini sono state costruite sulla macchina con Docker: i nodi k3d non le vedono finché `k3d image import` non le copia. Senza import il Pod resta in `ImagePullBackOff`. Dopo ogni `k3d cluster delete` l'import va rifatto. Un tag nuovo fa partire un rollout; lo stesso tag non cambia i Pod già avviati.

### requests e limits

[requests](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/) è quanto il nodo deve riservare. **limits** è il tetto. Nei manifest: CPU `10m` / `50m` (millicore, millesimi di un core) e memoria `32Mi` / `64Mi` (mebibyte). Senza questi campi l'editor segnala il rischio di noisy neighbor.

### Service

Un [Service](https://kubernetes.io/docs/concepts/services-networking/service/) ha un indirizzo stabile e un selector. kube-proxy, su ogni nodo, inoltra il traffico ai Pod che hanno quelle label. Se ne applica uno solo per nome: `kubectl apply` dello stesso `metadata.name` sostituisce il precedente. Il ClusterIP di `service.yaml` ha sostituito il NodePort di `hashresponse-svc` e ha chiuso la 30080.

Tre campi porta, da non scambiare:

| Campo | Chi lo usa |
| --- | --- |
| `targetPort` | il processo nel container. Qui è 3000. |
| `port` | gli altri Pod, dentro il cluster: `nome-service:port`. |
| `nodePort` | solo se `type: NodePort`. Aperta su ogni nodo, intervallo 30000–32767. |

**ClusterIP** è il tipo di default. L'indirizzo (per esempio `10.43.249.225`) esiste solo dentro il cluster. È quello che usa l'Ingress.

**NodePort** apre anche una porta su ogni nodo. Kubernetes gli assegna comunque un ClusterIP. Nell'esempio del corso: `nodePort` 30080, `port` 1234, `targetPort` 3000. Il file `material-example/app2/manifests/service.yaml` è il ClusterIP successivo (`port` 2345), non il NodePort. Il NodePort sta in `nodeport_service.yaml`.

### Ingress

Un [Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/) è una regola HTTP: path e host verso un Service. Non sostituisce il Service. Su k3s il controller è [Traefik](https://docs.k3s.io/networking), in ascolto sulla porta 80 del cluster. k3d pubblica quella porta sulla 8081.

`pathType: Prefix` confronta il path a pezzi separati da `/`. `/pingpong` combacia con `/pingpong` e con `/pingpong/qualcosa`. Non combacia con `/pingpongextra`. Se più path combaciano, [vince il più lungo](https://kubernetes.io/docs/concepts/services-networking/ingress/#multiple-matches). Per questo `/pingpong` arriva a ping-pong e `/` resta su Log output, nello stesso oggetto Ingress.

Due oggetti Ingress diversi con lo stesso path `/` se lo contendono. Per questo sono stati cancellati, a turno, `dwk-material-ingress`, `log-output` e `todo-app`. Cancellare l'oggetto nel cluster non cancella il file YAML.

L'Ingress inoltra il path così com'è. ping-pong ascolta su `/pingpong`. Un rewrite nel controller eviterebbe quella modifica al codice; il corso lo lascia facoltativo.

### Namespace

Tutto è nel namespace [default](https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/). I comandi non hanno `-n`.

## Dagli esercizi al traffico

| Esercizio | Cosa c'è | Come si raggiunge |
| --- | --- | --- |
| 1.1 | Deployment `log-output`, solo log | `kubectl logs`. Nessun HTTP. |
| 1.2 | Deployment `todo-app`, stesso modello | `kubectl logs` |
| 1.3 | Log output gestito dal file YAML | `kubectl apply` del Deployment |
| 1.4 | Deployment del progetto in `exercises/1.4` | lo snapshot punta ancora a `todo-app:1.2`; il codice vivo è `the_project` |
| 1.5 | todo app con `GET /` in HTML, `PORT=3000` | `kubectl port-forward` su `localhost:3003` |
| 1.6 | Service NodePort del progetto, `nodePort` 30081 | `localhost:8083` |
| 1.7 | Log output: Service ClusterIP 2345 e Ingress su `/` | `localhost:8081/` |
| 1.8 | todo app: ClusterIP 3000 e Ingress su `/` | `localhost:8081/`. L'Ingress di Log output viene tolto. |
| 1.9 | ping-pong, stesso Ingress di Log output | `localhost:8081/pingpong` e `localhost:8081/` |

Il Deployment in `exercises/1.4` non va riapplicato se il cluster ha già `todo-app:1.5`: lo riporterebbe all'immagine 1.2.

## Comandi kubectl

Sintassi generale: `kubectl <comando> [tipo/nome] [flag]`. Il tipo può essere abbreviato: `deploy`, `svc`, `ingress`, `po`.

### A quale cluster parla

```bash
kubectl config current-context
```

Stampa il contesto attivo. All'inizio era `docker-desktop`. Documentazione: [kubectl config current-context](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_config/kubectl_config_current-context/).

```bash
kubectl config get-contexts
```

Elenca i contesti nel kubeconfig (`docker-desktop`, `minikube`, poi `k3d-k3s-default`). L'asterisco è quello attivo. [get-contexts](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_config/kubectl_config_get-contexts/).

```bash
kubectl config use-context k3d-k3s-default
```

Cambia il contesto. Dopo un `k3d cluster delete` kubectl non torna da solo su k3d. [use-context](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_config/kubectl_config_use-context/).

```bash
kubectl cluster-info
```

Mostra l'URL dell'API e dei servizi di base. Serve a verificare che il contesto risponda. [cluster-info](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_cluster-info/).

```bash
kubectl get nodes
```

Elenca i nodi. Con il cluster del corso: un server e due agent. Se l'API è spenta, il comando fallisce prima di elencare qualcosa. [get](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_get/).

### Leggere gli oggetti

```bash
kubectl get pods -l app=log-output
```

Elenca i Pod con quella label. Le colonne utili sono `READY`, `STATUS`, `RESTARTS`. `Running` e `1/1` significano che il container è partito. `ImagePullBackOff` significa che il nodo non ha l'immagine.

```bash
kubectl get ingress,svc,pods -l 'app in (ping-pong,log-output)'
```

Una sola richiesta per tre tipi. La virgola unisce i tipi. Il selector `in` ne prende più di una label. L'Ingress `log-output` non ha la label `app`, quindi questo filtro non lo mostra.

```bash
kubectl get ingress
```

Elenca gli Ingress di tutti i nomi. Dopo l'esercizio 1.9 ne resta uno: `log-output`, class `traefik`, porta 80. È il controllo usato per vedere se `todo-app` o `dwk-material-ingress` erano ancora presenti.

```bash
kubectl get endpoints ping-pong -o wide
```

Mostra gli indirizzi dei Pod dietro il Service. `-o wide` aggiunge le colonne lunghe. Un Service senza endpoint risponde, ma non ha un Pod a cui inoltrare: l'Ingress allora restituisce 502. In Kubernetes 1.33+ questo comando avvisa che `Endpoints` è deprecato in favore di `EndpointSlice`; l'informazione è la stessa. [Service e endpoint](https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies).

### Creare e aggiornare

```bash
kubectl apply -f exercises/1.1/manifests/deployment.yaml
kubectl apply -f exercises/1.3/manifests/
kubectl apply -f exercises/1.9/manifests/
kubectl apply -f the_project/todo-app/manifests/deployment.yaml
kubectl apply -f the_project/todo-app/manifests/service.yaml
kubectl apply -f the_project/todo-app/manifests/ingress.yaml
kubectl apply -f material-example/app2/manifests/deployment.yaml
kubectl apply -f material-example/app2/manifests/nodeport_service.yaml
```

[kubectl apply](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_apply/) invia all'API il contenuto del file. `-f` accetta un file o una directory: la directory applica tutti gli YAML che contiene. Se l'oggetto non esiste, lo crea (`created`). Se esiste con lo stesso nome e tipo, lo aggiorna (`configured`). È la [gestione dichiarativa](https://kubernetes.io/docs/concepts/overview/working-with-objects/object-management/#declarative-object-configuration): il file è lo stato desiderato.

Due conseguenze viste in pratica:

- Applicare `service.yaml` di `hashresponse` (ClusterIP) al posto di `nodeport_service.yaml` chiude la 30080. `localhost:8082` smette di rispondere.
- Applicare il Service del todo app come ClusterIP, stesso nome `todo-app`, toglie il NodePort 30081. `localhost:8083` smette di rispondere. L'oggetto non va cancellato prima: `apply` lo riconfigura.

`exercises/1.4/manifests/deployment.yaml` è stato applicato per l'esercizio 1.4. Riapplicarlo oggi farebbe il rollout verso `todo-app:1.2`.

### Cancellare

```bash
kubectl delete ingress dwk-material-ingress
kubectl delete ingress log-output
kubectl delete ingress todo-app --ignore-not-found
```

[kubectl delete](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_delete/) toglie l'oggetto dal cluster. Il file sul disco resta.

| Comando | Quando |
| --- | --- |
| `dwk-material-ingress` | esercizio 1.7. L'esempio del corso e Log output volevano entrambi `/`. |
| `log-output` | esercizio 1.8. Il corso chiede di toglierlo perché il progetto prende `/`. |
| `todo-app` | esercizio 1.9. Log output riprende `/` e ping-pong prende `/pingpong`. |

`--ignore-not-found` fa riuscire il comando anche se l'Ingress non c'è. Utile quando lo script va rilanciato.

### Rollout e log

```bash
kubectl rollout status deployment/log-output --timeout=90s
kubectl rollout status deployment/todo-app --timeout=90s
kubectl rollout status deployment/ping-pong --timeout=60s
```

Aspetta che i Pod nuovi del Deployment siano Ready. Esce con errore se il timeout scade. [rollout status](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_rollout/kubectl_rollout_status/).

```bash
kubectl rollout restart deployment/log-output
```

Ricrea i Pod anche se il file YAML non è cambiato. È servito quando l'immagine aveva lo stesso tag e `apply` non vedeva differenze. Il contatore in memoria e la stringa casuale ripartono. [rollout restart](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_rollout/kubectl_rollout_restart/).

```bash
kubectl logs -l app=log-output --tail=6
kubectl logs -l app=log-output -f
kubectl logs -l app=log-output --tail=2
kubectl logs -l app=todo-app
kubectl logs -l app=ping-pong --tail=20
```

[kubectl logs](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_logs/) stampa stdout e stderr del container. `-l` sceglie i Pod per label. `--tail=N` mostra le ultime N righe. `-f` resta in ascolto, come `tail -f`; si interrompe con Ctrl+C.

Log output stampa una riga ogni 5 secondi. Il todo app stampa `Server started in port 3000`. ping-pong stampa la stessa riga all'avvio e poi una riga per richiesta.

Se il log è vuoto subito dopo l'avvio, spesso il processo non ha ancora scritto, oppure Python ha il buffer pieno. Nei container c'è `PYTHONUNBUFFERED=1` e `print(..., flush=True)`.

### Arrivare al processo senza un Service pubblico

```bash
kubectl port-forward deployment/todo-app 3003:3000
```

Apre la porta **locale** 3003 e la inoltra alla porta **3000 del container**, attraverso l'API. Non crea un Service e non sopravvive alla chiusura del comando. È l'accesso dell'esercizio 1.5, prima di NodePort e Ingress. [port-forward](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_port-forward/).

Il numero a sinistra dei due punti è la macchina. Quello a destra è il Pod. `3003:3000` non è «la 3003 del cluster».

Se la porta locale è già occupata, kubectl risponde `address already in use`. È successo sulla 3003 perché un forward precedente era ancora acceso. Un altro forward, quello di Freelens, usava una porta alta a caso (`52007:3000`) verso lo stesso Pod: non è un Service del corso.

```bash
kubectl exec deploy/ping-pong -- wget -qO- http://127.0.0.1:3000/pingpong
```

[kubectl exec](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_exec/) esegue un comando dentro un container del Deployment. `--` separa i flag di kubectl da quelli del comando. `127.0.0.1:3000` è il processo visto da dentro il Pod, non una porta della macchina. È servito quando l'Ingress rispondeva 502 e bisognava sapere se il processo, da solo, rispondeva. `wget` c'è nell'immagine Alpine. Ogni chiamata aumenta il contatore.

## Cosa è successo con questi comandi

**Contesto sbagliato.** `kubectl get nodes` e `kubectl apply` verso `docker-desktop` spento: `connection refused` sulla 6443. Si sistema con `kubectl config use-context k3d-k3s-default` dopo che k3d ha creato il cluster.

**NodePort mancante.** `kubectl apply` del `service.yaml` di esempio (ClusterIP, porta 2345) non apre la 30080. `localhost:8082` si connette e poi risponde vuoto. Il file giusto per quel passaggio è `nodeport_service.yaml`.

**Due Ingress su `/`.** Traefik non sa a quale Service mandare la richiesta. Si cancella l'Ingress che non serve a quell'esercizio. Dall'esercizio 1.9 i due path stanno nello stesso oggetto, e vince il path più lungo.

**502 appena creato l'Ingress.** Il Pod è appena partito, oppure Traefik non ha ancora l'endpoint. `kubectl get endpoints` e `kubectl logs` distinguono «il processo non risponde» da «l'Ingress non lo raggiunge ancora». Un secondo dopo, `localhost:8081/pingpong` ha risposto `pong 0`.

**Service rinominato nello stesso oggetto.** `kubectl apply` del ClusterIP sul Service che prima era NodePort stampa `configured`. La porta sul nodo sparisce. Non servono due Service con lo stesso nome.

## emptyDir — esercizio 1.10

Un [emptyDir](https://kubernetes.io/docs/concepts/storage/volumes/#emptydir) è una directory creata sul nodo quando il Pod viene schedulato. Parte vuota. Tutti i container del Pod possono montarla, anche sullo stesso path. Quando il Pod viene tolto dal nodo, il contenuto viene cancellato. Non è un disco che sopravvive al Pod. Il corso lo usa per far parlare due container. La guida ufficiale con lo stesso schema è [comunicazione tra container tramite volume](https://kubernetes.io/docs/tasks/access-application-cluster/communicate-containers-same-pod-shared-volume/).

Nel Deployment `log-output` il volume si chiama `shared-log` ed è montato su `/usr/src/app/files` sia da `log-writer` sia da `log-reader`. `fsGroup: 65534` rende la directory scrivibile dall'utente `nobody` dell'immagine Alpine. Senza quel gruppo il writer non crea `log.txt`.

`kubectl logs` con più container vuole il nome del container. Senza `-c` kubectl si ferma e chiede quale. [kubectl logs](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_logs/).

```bash
kubectl logs -l app=log-output -c log-writer --tail=2
kubectl logs -l app=log-output -c log-reader --tail=2
```


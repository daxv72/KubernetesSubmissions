# The project, step 2

Exercise 1.4. Declarative Deployment for the todo app started in exercise 1.2.

The application code stays in `the_project/todo-app`. This folder holds the Deployment manifest for the exercise path. The same manifest is also in `the_project/todo-app/manifests/deployment.yaml`.

There is no Service yet.

## Kubernetes

From the repository root:

```bash
kubectl apply -f exercises/1.4/manifests/deployment.yaml
kubectl logs -l app=todo-app
```

Expected log line:

```text
Server started in port 3000
```

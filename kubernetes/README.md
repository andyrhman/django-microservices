# Node Ambassador Deployment using Kubernetes

## Useful Commands

Creating pods

```bash
kubectl apply -f <name of the file>
```

Get pods

```bash
kubectl get pods
```

Inspect pod

```bash
kubectl describe pod <pod name>
```

Delete pods

```bash
kubectl delete pods <pod name> # Single Pod
kubectl delete pods --all # All pods 
```

Creating secret

```bash
kubectl create secret generic <secret name> --from-literal=KAFKA_BROKERS=test444:90921 --from-literal=KAFKA_USERNAME=test123 --from-literal=KAFKA_PASSWORD=44444
```

Deleting secret

```bash
kubectl delete secret <secret name>
```

Using docker inside minikube

```bash
minikube ssh docker <command here>
```

Convert docker compose into kubernetes yaml

```bash
kompose convert -f <file name or location>
```

## Installing Kubernetes

First download kubectl:

```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
```

And after that Install kubectl using this command:

```bash
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

Test to ensure the version you installed is up-to-date:

```bash
kubectl version --client
```

## Installing Minikube

Here's how you install Minikube and run minikube

```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube && rm minikube-linux-amd64
```

Now here's the first time configuration command to start minikube, but before that go first to this link to get the `latest tag`
[gcr.io/k8s-minikube/kicbase-builds](Kicbase)

```bash
minikube start --driver=docker --base-image "gcr.io/k8s-minikube/kicbase-builds:<copy here the tag>"
```

And after that, you can start kubernetes just by using this command:

```bash
minikube start
```

## Installing Kompose (Convert docker compose to kubernetes yaml)

Run this command

```bash
curl -L https://github.com/kubernetes/kompose/releases/download/v1.34.0/kompose-linux-amd64 -o kompose
chmod +x kompose
sudo mv ./kompose /usr/local/bin/kompose
```

Test kompose if it's installed

```bash
kompose version
```

## How to run nginx ingress in minikube

Install helm first for adding ingress-nginx to minikube

```bash
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh
```

Add ingress-nginx into the repo

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
```

Install ingress-nginx into minikube (Don't forget to do *minikube start* first)

```bash
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx --create-namespace
```

Remember to use nginx inside ingress.class:

```yaml
annotations:
  kubernetes.io/ingress.class: "nginx"
```

Also do not forget to start *minikube tunnel* to create the network route

```bash
minikube tunnel
```

Check if the external ip is running

```bash
kubectl get svc ingress-nginx-controller -n ingress-nginx
```

## Push container to github and configure the secret

Configure first the secret

```bash
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=yourgithubusername \
  --docker-password=$GHCR_PAT \
  --docker-email=yougithubremail

export GHCR_PAT=ghp_yourgithubtoken
```

Push it to github container

```bash
docker push ghcr.io/andyrhman/imagename:0.0.3
```

Don't forget to put ghcr-secret inside your yaml file

```yaml
spec:
  imagePullSecrets:
    - name: ghcr-secret
```

# Kubernetes Tunnel Controller

**ATTENTION:** This project is currently in active developing phase.
It was born to demonstrate how easy could it be to expose an internal Kubernetes services to the worlwide
with automatic TLS without cert-manager, DNS or opening ports in your home network/router.

## Based on frp

This project uses the [frp](https://github.com/fatedier/frp) by [`fatedier`](https://github.com/fatedier) upstream projec.
The server-side component is running in a cloud instance.

Ideally, this kubernetes controller will hide the technical details of the tunneling and expose a simple API to expose services.

## Run it locally (from outside the cluster)

### Requirements

- `kind` and `kubectl`
- access to GitHub *(tunnel container image currently there)*
- `python 3.10` - `virtualenv`
- `git`

### Create the (local) cluster

*Avoid this step if you already have a running cluster.*

```bash
$ kind create cluster --name tunnels
Creating cluster "tunnels" ...
 ✓ Ensuring node image (kindest/node:v1.26.3) 🖼
 ✓ Preparing nodes 📦  
 ✓ Writing configuration 📜 
 ✓ Starting control-plane 🕹️ 
 ✓ Installing CNI 🔌 
 ✓ Installing StorageClass 💾 
Set kubectl context to "kind-tunnels"
You can now use your cluster with:

kubectl cluster-info --context kind-tunnels

Not sure what to do next? 😅  Check out https://kind.sigs.k8s.io/docs/user/quick-start/
$ kind get kubeconfig --name tunnels > kubeconfig
$ export KUBECONFIG=$(pwd)/kubeconfig
$ kubectl get nodes
NAME                    STATUS   ROLES           AGE   VERSION
tunnels-control-plane   Ready    control-plane   37s   v1.26.3
```

### Run the project

```bash
$ git clone git@github.com:angelbarrera92/k8s-tunnel-controller.git
$ cd k8s-tunnel-controller
$ virtualenv -p python3 venv
$ source venv/bin/activate
$ pip install -r requirements.txt
...
..
.
Successfully installed aiohttp-3.8.4 aiosignal-1.3.1 async-timeout-4.0.2 attrs-23.1.0 certifi-2023.5.7 charset-normalizer-3.1.0 click-8.1.3 frozenlist-1.3.3 idna-3.4 iso8601-1.1.0 kopf-1.36.1 multidict-6.0.4 pykube-ng-22.9.0 python-json-logger-2.0.7 requests-2.31.0 typing-extensions-4.6.3 urllib3-2.0.2 yarl-1.9.2
$ TOKEN=<the-token> kopf run -A --liveness=http://0.0.0.0:8080/healthz controller.py
[2023-06-03 18:29:52,627] kopf._core.engines.a [INFO    ] Initial authentication has been initiated.
[2023-06-03 18:29:52,641] kopf.activities.auth [INFO    ] Activity 'login_via_pykube' succeeded.
[2023-06-03 18:29:52,642] kopf._core.engines.a [INFO    ] Initial authentication has finished.
[2023-06-03 18:29:52,836] src.controller.handl [INFO    ] update service kube-system/kube-dns annotations: (('add', (), None, {'prometheus.io/port': '9153', 'prometheus.io/scrape': 'true'}),)
[2023-06-03 18:29:52,848] kopf.objects         [INFO    ] [kube-system/kube-dns] Handler 'service_annotation_modification/metadata.annotations' succeeded.
[2023-06-03 18:29:52,848] kopf.objects         [INFO    ] [kube-system/kube-dns] Creation is processed: 1 succeeded; 0 failed.
```

### Execute the examples

**Open a new terminal** *(avoid to stop the controller)* configure the `KUBECONFIG` env variable then:

```bash
$ export KUBECONFIG=$(pwd)/kubeconfig
$ kubectl get nodes
NAME                    STATUS   ROLES           AGE     VERSION
tunnels-control-plane   Ready    control-plane   2m56s   v1.26.3
$ kubectl apply -f hack/deployments/example/nginx.yaml
pod/nginx created
service/nginx created
service/nginx-default created
```

Then, a new **pod and a configmap** will pop up in the cluster:

```bash
$ kubectl get pods
NAME                    READY   STATUS              RESTARTS   AGE
nginx                   0/1     ContainerCreating   0          6s
nginx-80-tunnel-afmmo   0/1     ContainerCreating   0          6s
```

The `nginx-80-tunnel-afmmo` pod has been created by the controller. Why? Because the service contains a magic annotation: `k8s-tunnel-controller/tunnel: nginx-1`

```bash
$ kubectl get svc nginx -o yaml
apiVersion: v1
kind: Service
metadata:
  annotations:
    k8s-tunnel-controller/tunnel: nginx-1
<REDACTED>
```

Checking the logs of the pods created:

```bash
$ kubectl logs -f nginx-80-tunnel-afmmo
2023/06/03 16:24:53 [I] [service.go:295] [e29d0fad7a522c1f] login to server success, get run id [e29d0fad7a522c1f]
2023/06/03 16:24:53 [I] [proxy_manager.go:152] [e29d0fad7a522c1f] proxy added: [nginx]
2023/06/03 16:24:53 [I] [control.go:172] [e29d0fad7a522c1f] [nginx] start proxy success
```

You'll see the right URL. It contains the subdomain specified in the annotation: `nginx-1.frp.exit.o.microcloud.dev`.

Finally, visiting it:

![welcomepage](docs/images/nginx.png)

### Important notes

The project uses a `microcloud.dev` subdomain tu expose your services. Take in mind the following assumptions:

- Your chossen subdomain must be unique.
  - Using the value `my-service` in the `k8s-tunnel-controller/tunnel` annotation will result in a FQDN `my-service.frp.exit.o.microcloud.dev`.
  - It could be a good idea to add your username to the subdomain: `my-service-<username>`, then `my-service-<username>.frp.exit.o.microcloud.dev`.
- There's no automatic way to use a different domain.
  - If you want to use your own domain or a different `frp.exit.o.microcloud.dev` subdomain `(dedicated tenant)`, contact me.
- You need a `TOKEN` to run the controller, contact me.

## Deploy using Helm

This project uses [`helm`](https://helm.sh/) chart to deploy the controller.

```bash
$ helm upgrade --install tunnels --set token.tokenValue=<the-token> deployments/kubernetes/helm/k8s-tunnel-controller/
Release "tunnels" does not exist. Installing it now.
NAME: tunnels
LAST DEPLOYED: Sun Dec 26 07:23:42 2021
NAMESPACE: default
STATUS: deployed
REVISION: 1
NOTES:
1. Get the application URL by running these commands:
  export POD_NAME=$(kubectl get pods --namespace default -l "app.kubernetes.io/name=k8s-tunnel-controller,app.kubernetes.io/instance=tunnels" -o jsonpath="{.items[0].metadata.name}")
  export CONTAINER_PORT=$(kubectl get pod --namespace default $POD_NAME -o jsonpath="{.spec.containers[0].ports[0].containerPort}")
  echo "Visit http://127.0.0.1:8080 to use your application"
  kubectl --namespace default port-forward $POD_NAME 8080:$CONTAINER_PORT
```


## Next steps

- There are a lot of `TODO`s in code.
- Publish server-side code and documentation.
- Automate helm chart documentation (frigate) and add it to the linter phase.
  - Publish the helm chart in ArtifcatHub.
- Run as no root
- Enable use different subdomain.
  - With docs
- Change the log levels in all log invocation.
- Add a `--liveness` and `--readiness` endpoint to the tunnel pod.
  - Add these endpoint as tunnel pod probes.
  - Also, add resource limits and requests.

Then a lot of ideas. Thanks!

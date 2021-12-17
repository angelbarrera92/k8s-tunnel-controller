from logging import getLogger
from random import choice
from string import ascii_lowercase

from pykube import ConfigMap, Pod, Secret, Service
from src.controller.certs import certs
from src.kubernetes import configmaps, pods, secrets
from src.kubernetes.connection import kubernetes_api
from src.kubernetes.ensure import ensure

logger = getLogger(__name__)

# TODO: Improve the way I handle the labels.
# TODO. The container image used for the tunnel has to be set as controller configuration.
# TODO. Make the tunnels.o.barrera.dev domain a configurable parameter.
# TODO. Need to set the resources as low as possible.
# TODO. This is an optimistic approach. Ideally, the new pod should notify somehow the controller that is ready to
# accept requests.
# TODO. Improve logging levels.


@kubernetes_api
def create_pod(
    api, svc: Service, secret: Secret, configmap: ConfigMap, port: int, subdomain: str
) -> Pod:
    logger.info(
        f"creating tunnel pod for service {svc.namespace}/{svc.name} in the port {port} on {subdomain} subdomain"
    )
    name = f"{svc.name}-{port}-tunnel-{generate_random(5)}"

    labels = common_labels(svc)
    labels["app.kubernetes.io/port"] = str(port)
    labels["app.kubernetes.io/subdomain"] = subdomain

    tunnelPod = Pod(
        api,
        {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {
                "name": name,
                "namespace": svc.namespace,
                "labels": labels,
            },
            "spec": {
                "automountServiceAccountToken": False,
                "volumes": [
                    {
                        "name": "config",
                        "configMap": {
                            "name": configmap.name,
                            "items": [
                                {"key": "tunnel.yml", "path": "tunnel.yml"},
                            ],
                        },
                    },
                    {
                        "name": "certs",
                        "secret": {
                            "secretName": secret.name,
                            "items": [
                                {"key": "tls.crt", "path": "client.crt"},
                                {"key": "tls.key", "path": "client.key"},
                            ],
                        },
                    },
                ],
                "containers": [
                    {
                        "image": "docker.io/angelbarrera92/tunnels:local",
                        "imagePullPolicy": "Always",
                        "command": [
                            "/tunnel",
                            "--config",
                            "/config/tunnel.yml",
                            "--log-level",
                            "3",
                            "start-all",
                        ],
                        "volumeMounts": [
                            {"name": "config", "mountPath": "/config"},
                            {"name": "certs", "mountPath": "/certs"},
                        ],
                        "name": "tunnel",
                        "resources": {},
                    }
                ],
            },
        },
    )
    return ensure(tunnelPod, svc)


@kubernetes_api
def create_configmap(api, svc: Service, port: int, subdomain: str) -> ConfigMap:
    logger.info(
        f"creating tunnel configmap for service {svc.namespace}/{svc.name} in the port {port} on {subdomain} subdomain"
    )
    name = f"{svc.name}-{port}-tunnel-{generate_random(5)}"

    labels = common_labels(svc)
    labels["app.kubernetes.io/port"] = str(port)
    labels["app.kubernetes.io/subdomain"] = subdomain

    tunnelConfigMap = ConfigMap(
        api,
        {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": name,
                "namespace": svc.namespace,
                "labels": labels,
            },
            "data": {
                "tunnel.yml": f"""
server_addr: tunnels.o.barrera.dev:5223
tls_crt: /certs/client.crt
tls_key: /certs/client.key
tunnels:
  {svc.name}:
    proto: http
    addr: {svc.name}:{port}
    host: {subdomain}.tunnels.o.barrera.dev
"""
            },
        },
    )
    return ensure(tunnelConfigMap, svc)


@kubernetes_api
def create_secret(api, svc: Service, port: int, subdomain: str) -> Secret:
    logger.info(
        f"creating tunnel secret for service {svc.namespace}/{svc.name} in the port {port} on {subdomain} subdomain"
    )
    name = f"{svc.name}-{port}-tunnel-{generate_random(5)}"
    cert, key = certs.generateSelfSignedClientCertificate(name)

    labels = common_labels(svc)
    labels["app.kubernetes.io/port"] = str(port)
    labels["app.kubernetes.io/subdomain"] = subdomain

    tunnelSecret = Secret(
        api,
        {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": name,
                "namespace": svc.namespace,
                "labels": labels,
            },
            "immutable": True,
            "type": "kubernetes.io/tls",
            "stringData": {
                "tls.crt": cert,
                "tls.key": key,
            },
        },
    )
    return ensure(tunnelSecret, svc)


def find_pod(svc: Service) -> Pod:
    return pods.get(namespace=svc.namespace, labels=common_labels(svc), ready=True)


def find_secret(svc: Service) -> Secret:
    return secrets.get(namespace=svc.namespace, labels=common_labels(svc))


def find_configmap(svc: Service) -> ConfigMap:
    return configmaps.get(namespace=svc.namespace, labels=common_labels(svc))


def generate_random(length: int) -> str:
    return "".join(choice(ascii_lowercase) for _ in range(length))


def common_labels(svc: Service = None) -> dict[str, str]:
    labels = {
        "app.kubernetes.io/managed-by": "k8s-tunnel-controller",
        "app.kubernetes.io/version": "v1",
        "app.kubernetes.io/name": "tunnel",
    }
    if svc:
        labels["app.kubernetes.io/service"] = svc.name
    return labels

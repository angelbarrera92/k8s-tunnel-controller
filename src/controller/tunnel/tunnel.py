from logging import getLogger
from random import choice
from string import ascii_lowercase

from pykube import ConfigMap, Pod, Service
from src.kubernetes import configmaps, pods
from src.kubernetes.connection import kubernetes_api
from src.kubernetes.ensure import ensure

logger = getLogger(__name__)

# TODO: Improve the way I handle the labels.
# TODO. The container image used for the tunnel has to be set as controller configuration.
# TODO. Need to set the resources as low as possible.
# TODO. This is an optimistic approach. Ideally, the new pod should notify somehow the controller that is ready to
# accept requests.
# TODO. Improve logging levels.


@kubernetes_api
def create_pod(
    api, svc: Service, configmap: ConfigMap, port: int, subdomain: str
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
                                {"key": "frpc.ini", "path": "frpc.ini"},
                            ],
                        },
                    },
                ],
                "containers": [
                    {
                        "image": "fatedier/frpc:v0.48.0",
                        "imagePullPolicy": "Always",
                        "args": [
                            "-c",
                            "/etc/frp/frpc.ini",
                        ],
                        "volumeMounts": [
                            {"name": "config", "mountPath": "/etc/frp"},
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
                "frpc.ini": f"""
[common]
server_addr = frp.exit.o.microcloud.dev
server_port = 7000

[{svc.name}]
type = http
local_ip = {svc.name}
local_port = {port}
subdomain = {subdomain}
use_encryption = true
use_compression = true
"""
            },
        },
    )
    return ensure(tunnelConfigMap, svc)


def find_pod(svc: Service) -> Pod:
    return pods.get(namespace=svc.namespace, labels=common_labels(svc), ready=True)


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

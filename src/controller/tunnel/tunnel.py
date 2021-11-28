from logging import getLogger

from pykube import Pod, Service
from src.kubernetes.connection import kubernetes_api
from src.kubernetes.ensure import ensure

logger = getLogger(__name__)


@kubernetes_api
def tunnel(api, svc: Service, port: int, subdomain: str):
    logger.info(
        f"ensuring tunnel for service {svc.namespace}/{svc.name} in the port {port} on {subdomain} subdomain")
    podSpec = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {
            "name": subdomain,
            "namespace": svc.namespace,
        },
        "spec": {
            "automountServiceAccountToken": False,
            "containers": [
                {
                    "image": "docker.io/angelbarrera92/lt:local",
                    "imagePullPolicy": "Always",
                    "command": [
                        "lt",
                        "--host",
                        "https://localtunnel.me",
                        "-s",
                        subdomain,
                        "-l",
                        svc.name,
                        "-p",
                        f"{port}",
                        "--print-requests"
                    ],
                    "name": "tunnel",
                    "resources": {}
                }
            ],
        }
    }
    tunnelPod = Pod(api, podSpec)
    tunnelPod = ensure(tunnelPod, svc)

# TODO. The container image used for the tunnel has to be set as controller configuration
# TODO. Need to set the resources as low as possible.
# TODO. Evaluate setting up my own host and make it configurable
# TODO. This is an optimistic approach. Ideally, the new pod should notify somehow the controller that is ready to accept requests.
# TODO. Add labels to the pod to identify it as a tunnel pod.

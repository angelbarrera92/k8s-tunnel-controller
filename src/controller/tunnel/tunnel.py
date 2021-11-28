from pykube import Pod
from logging import getLogger
from src.kubernetes.connection import kubernetes_api

logger = getLogger(__name__)


@kubernetes_api
def tunnel(api, service_name, service_namespace, port, subdomain):
    logger.info(
        f"creating tunnel for service {service_namespace}/{service_name} in the port {port} on {subdomain} subdomain")
    podSpec = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {
            "name": subdomain,
            "namespace": service_namespace,
        },
        "spec": {
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
                        service_name,
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
    tunnelPod.create()

# TODO. The created pod must have the service with the annotation as its parent
# TODO. The container image used for the tunnel has to be set as controller configuration
# TODO. Need to set the resources as low as possible.
# TODO. Evaluate setting up my own host and make it configurable
# TODO. Adopt the pod. Service must be its parent
# TODO. This is an optimistic approach. Ideally, the new pod should notify somehow the controller that is ready to accept requests.
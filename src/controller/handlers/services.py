from logging import getLogger

import kopf
from src.controller.tunnel.tunnel import tunnel
from src.kubernetes import services

logger = getLogger(__name__)


@kopf.on.create("", "v1", "service", annotations={"angelbarrera92/tunnel": kopf.PRESENT})
def new_tunnel_service(name, namespace, **_):
    logger.info(
        f"new service ({namespace}/{name}) listened with the angelbarrera92/tunnel annotation")

    reconcile(name, namespace)


@kopf.on.resume("", "v1", "service", annotations={"angelbarrera92/tunnel": kopf.PRESENT})
def reconcile_tunnel_service(name, namespace, **_):
    logger.info(
        f"reconcile service ({namespace}/{name}) with the angelbarrera92/tunnel annotation")
    reconcile(name, namespace)


def reconcile(name, namespace):
    svc = services.get(namespace=namespace, name=name)

    port = -1
    if len(svc.obj["spec"]["ports"]) == 1:
        port = svc.obj["spec"]["ports"][0]["port"]
    else:
        # TODO: Look for a certains annotation to get the right port.
        pass
    tunnel(svc=svc,
           port=port, subdomain=svc.annotations["angelbarrera92/tunnel"])

# TODO. Annotations should be standarized somewhere as constants
# TODO. Think about adding a new status event when tunnel pod is deployed

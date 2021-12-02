from logging import getLogger

import kopf
from src.controller.tunnel import tunnel
from src.kubernetes import services

logger = getLogger(__name__)

BASE_ANNOTATION = "k8s-tunnel-controller"
TUNNEL_ANNOTATION = f"{BASE_ANNOTATION}/tunnel"
PORT_ANNOTATION = f"{BASE_ANNOTATION}/port"


@kopf.on.create("", "v1", "service", annotations={TUNNEL_ANNOTATION: kopf.PRESENT})
def new_tunnel_service(name, namespace, **_):
    logger.info(
        f"new service ({namespace}/{name}) listened with the {TUNNEL_ANNOTATION} annotation")

    reconcile(name, namespace)


@kopf.on.resume("", "v1", "service", annotations={TUNNEL_ANNOTATION: kopf.PRESENT})
def reconcile_tunnel_service(name, namespace, **_):
    logger.info(
        f"reconcile service ({namespace}/{name}) with the {TUNNEL_ANNOTATION} annotation")

    reconcile(name, namespace)


def reconcile(name, namespace):
    svc = services.get(namespace=namespace, name=name)

    # First look at the annotation:
    # If present, use it. If the port is not in the list, fail.
    # If not present, fallback to the first port if only one is present.
    # else fails.

    port = None
    portInAnnotation = svc.annotations.get(PORT_ANNOTATION, None)
    if portInAnnotation:
        for p in svc.obj["spec"]["ports"]:
            if p["port"] == int(portInAnnotation):
                port = p["port"]
        if not port:
            logger.error(
                f"port {portInAnnotation} not found in service {namespace}/{name}")
            # TODO. Fail reconciliation. Check kopf docs
    else:
        logger.info(f"no port in annotation for service {namespace}/{name}")
        if len(svc.obj["spec"]["ports"]) == 1:
            port = svc.obj["spec"]["ports"][0]["port"]
        else:
            logger.error(
                f"no port in annotation and more than one port in service {namespace}/{name}")
            # TODO. Fail reconciliation. Check kopf docs

    tunnel.create(svc=svc,
                  port=port, subdomain=svc.annotations[TUNNEL_ANNOTATION])

# TODO. Think about adding a new status event when tunnel pod is deployed
# TODO. Listen for pods with certain labels, then run the reconciliation loop
# TODO. Cover update subdomain use-case
# TODO. Cover update port use-case
# TODO. Validate subdomain format
# TODO. Validate port format. Only numbers allowed.

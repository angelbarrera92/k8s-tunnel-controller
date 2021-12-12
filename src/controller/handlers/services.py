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

# This is currently not working properly.
# Pods is being deleted, then the reconciliation loop is still able to find it.
@kopf.on.delete("", "v1", "pods", labels={"app.kubernetes.io/managed-by": "k8s-tunnel-controller"})
def delete_tunnel_pod(name, namespace, labels, **_):
    logger.info(
        f"delete pod ({namespace}/{name}) listened with the app.kubernetes.io/managed-by label")

    serviceName = labels.get("app.kubernetes.io/service")
    reconcile(serviceName, namespace)


@kopf.on.field("", "v1", "service", field="metadata.annotations")
def update_service_annotations(diff, name, namespace, **_):
    logger.info(f"update service {namespace}/{name} annotations: {diff}")

    # This is whay the method receives in the diff attribute.
    # (('add', ('hi',), None, 'hi'),)
    # (('change', ('hi',), 'hi', 'hi2'),)
    # (('remove', ('hi',), 'hi2', None),)
    # - Remove annotation. Should remove the pod tunnel.

    for d in diff:
        action = d[0]
        # TODO: Improve this code-block
        try:
            annotation = d[1][0]
        except IndexError:
            annotation = None
        if annotation and annotation == TUNNEL_ANNOTATION:
            svc = services.get(namespace=namespace, name=name)
            podTunnel = tunnel.find_tunnel(svc=svc)
            if action == 'remove':
                logger.info(
                    f"remove tunnel pod for service {namespace}/{name}")
                podTunnel.delete()
            elif action in ["add", "change"]:
                reconcile(name, namespace)


def reconcile(name, namespace):
    svc = services.get(namespace=namespace, name=name)

    # First look at the annotation:
    # If present, use it. If the port is not in the list, fail.
    # If not present, fallback to the first port if only one is present.
    # else fails.

    subdomain = svc.annotations.get(TUNNEL_ANNOTATION, None)
    if not subdomain:  # Add dns validation to subdomain value
        errorMsg = f"no subdomain in annotation for service {namespace}/{name}"
        logger.error(errorMsg)
        raise kopf.PermanentError(errorMsg)

    port = None
    portInAnnotation = svc.annotations.get(PORT_ANNOTATION, None)
    if portInAnnotation:
        for p in svc.obj["spec"]["ports"]:
            if p["port"] == int(portInAnnotation):
                port = p["port"]
        if not port:
            errorMsg = f"port {portInAnnotation} not found in service {namespace}/{name}"
            logger.error(errorMsg)
            raise kopf.PermanentError(errorMsg)
    else:
        logger.info(f"no port in annotation for service {namespace}/{name}")
        if len(svc.obj["spec"]["ports"]) == 1:
            port = svc.obj["spec"]["ports"][0]["port"]
        else:
            errorMsg = f"no port in annotation and more than one port in service {namespace}/{name}"
            logger.error(errorMsg)
            raise kopf.PermanentError(errorMsg)

    logger.info(
        f"reconcile service {namespace}/{name} with subdomain {subdomain} and port {port}")

    podTunnel = tunnel.find_tunnel(svc=svc)
    if not podTunnel:
        logger.info(f"no tunnel found for service {namespace}/{name}")
        logger.info(f"creating tunnel for service {namespace}/{name}")
        tunnel.create(svc=svc,
                      port=port, subdomain=subdomain)
    else:
        logger.info(f"tunnel found for service {namespace}/{name}")
        current_port = int(podTunnel.labels.get("app.kubernetes.io/port"))
        current_subdomain = podTunnel.labels.get(
            "app.kubernetes.io/subdomain")
        if current_port != port or current_subdomain != subdomain:
            logger.info(f"updating tunnel for service {namespace}/{name}")
            logger.info(f"deleting tunnel for service {namespace}/{name}")
            podTunnel.delete()
            logger.info(f"creating tunnel for service {namespace}/{name}")
            tunnel.create(svc=svc,
                          port=port, subdomain=subdomain)

# TODO. Think about adding a new status event when tunnel pod is deployed
# TODO. Listen for pods with certain annotations, then run the reconciliation loop
# TODO. Validate subdomain format
# TODO. Validate port format. Only numbers allowed.

from logging import getLogger

import kopf
from src.controller.handlers import (
    BASE_ANNOTATION,
    service_port,
    tunnel_subdomain,
)
from src.controller.tunnel import tunnel
from src.kubernetes import services

logger = getLogger(__name__)


@kopf.on.update(
    "", "v1", "configmaps", labels={"app.kubernetes.io/managed-by": BASE_ANNOTATION}
)
def update_configmap(name, namespace, labels, **_):
    logger.info(f"update configmap {namespace}/{name}")
    logger.info("query the service")
    # pylint: disable=E1120
    svc = services.get(namespace=namespace, name=labels["app.kubernetes.io/service"])
    configmap = tunnel.find_configmap(svc=svc)
    configmap.delete()
    # Then the delete handler will take care of recreating it


@kopf.on.delete(
    "", "v1", "configmaps", labels={"app.kubernetes.io/managed-by": BASE_ANNOTATION}
)
def delete_configmap(name, namespace, labels, **_):
    logger.info(f"delete configmap {namespace}/{name}")

    logger.info("query the service")
    # pylint: disable=E1120
    svc = services.get(namespace=namespace, name=labels["app.kubernetes.io/service"])
    if svc:
        logger.info(f"service found ({svc.namespace}/{svc.name})")
        logger.info("gathering tunnel information")
        tunnelPort = service_port(svc)
        tunnelSubdomain = tunnel_subdomain(svc)

        tunnel.create_configmap(svc, tunnelPort, tunnelSubdomain)

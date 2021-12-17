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
    "", "v1", "pods", labels={"app.kubernetes.io/managed-by": BASE_ANNOTATION}
)
def update_pod(name, namespace, labels, **_):
    logger.info(f"update pods {namespace}/{name}")
    logger.info("query the service")
    svc = services.get(namespace=namespace, name=labels["app.kubernetes.io/service"])
    logger.info(f"service found ({svc.namespace}/{svc.name})")
    pod = tunnel.find_pod(svc=svc)
    logger.info(f"pod {pod.namespace}/{pod.name} found")
    pod.delete()
    # Then the delete handler will take care of recreating it


@kopf.on.delete(
    "", "v1", "pods", labels={"app.kubernetes.io/managed-by": BASE_ANNOTATION}
)
def delete_pod(name, namespace, labels, **_):
    logger.info(f"delete pod {namespace}/{name}")

    logger.info("query the service")
    svc = services.get(namespace=namespace, name=labels["app.kubernetes.io/service"])
    if svc:
        logger.info("gathering tunnel information")
        tunnelPort = service_port(svc)
        tunnelSubdomain = tunnel_subdomain(svc)
        logger.info(f"tunnel port {tunnelPort} and subdomain {tunnelSubdomain}")

        secret = tunnel.find_secret(svc=svc)
        configmap = tunnel.find_configmap(svc=svc)

        tunnel.create_pod(svc, secret, configmap, tunnelPort, tunnelSubdomain)

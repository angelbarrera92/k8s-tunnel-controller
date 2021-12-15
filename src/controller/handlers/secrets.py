from logging import getLogger

import kopf
from src.controller.handlers import (BASE_ANNOTATION, service_port,
                                     tunnel_subdomain)
from src.controller.tunnel import tunnel
from src.kubernetes import services

logger = getLogger(__name__)


@kopf.on.delete("", "v1", "secrets", labels={"app.kubernetes.io/managed-by": BASE_ANNOTATION})
def delete_secret(name, namespace, labels, **_):
    logger.info(f"delete secret {namespace}/{name}")
    logger.info("query the service")
    svc = services.get(namespace=namespace,
                       name=labels["app.kubernetes.io/service"])
    if svc:
        logger.info("gathering tunnel information")
        tunnelPort = service_port(svc)
        tunnelSubdomain = tunnel_subdomain(svc)
        tunnel.create_secret(svc, tunnelPort, tunnelSubdomain)


@kopf.on.update("", "v1", "secrets", labels={"app.kubernetes.io/managed-by": BASE_ANNOTATION})
def update_secret(name, namespace, labels, **_):
    logger.info(f"update secret {namespace}/{name}")
    logger.info("query the service")
    svc = services.get(namespace=namespace,
                       name=labels["app.kubernetes.io/service"])
    logger.info("gathering tunnel information")
    secret = tunnel.find_secret(svc=svc)
    secret.delete()
    # Then the delete handler will take care of recreating it

from logging import getLogger

import kopf
from pykube.objects import Service

logger = getLogger(__name__)

BASE_ANNOTATION = "k8s-tunnel-controller"
TUNNEL_ANNOTATION = f"{BASE_ANNOTATION}/tunnel"
PORT_ANNOTATION = f"{BASE_ANNOTATION}/port"


def service_port(svc: Service) -> int:
    port = None
    portInAnnotation = svc.annotations.get(PORT_ANNOTATION, None)
    if portInAnnotation:
        for p in svc.obj["spec"]["ports"]:
            if p["port"] == int(portInAnnotation):  # TODO: Add port validation
                port = p["port"]
        if not port:
            errorMsg = f"port {portInAnnotation} not found in service {svc.namespace}/{svc.name}"
            logger.error(errorMsg)
            raise kopf.PermanentError(errorMsg)
    else:
        logger.warn(f"no port in annotation for service {svc.namespace}/{svc.name}")
        if len(svc.obj["spec"]["ports"]) == 1:
            port = svc.obj["spec"]["ports"][0]["port"]
        else:
            errorMsg = f"no port in annotation and more than one port in service {svc.namespace}/{svc.name}"
            logger.error(errorMsg)
            raise kopf.PermanentError(errorMsg)
    return port


def tunnel_subdomain(svc: Service) -> str:
    subdomain = svc.annotations.get(TUNNEL_ANNOTATION, None)
    if not subdomain:  # TODO: Add dns validation to subdomain value
        errorMsg = f"no subdomain in annotation for service {svc.namespace}/{svc.name}"
        logger.error(errorMsg)
        raise kopf.PermanentError(errorMsg)
    return subdomain

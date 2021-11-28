from src.controller.tunnel.tunnel import tunnel
from logging import getLogger
import kopf


logger = getLogger(__name__)


@kopf.on.create("", "v1", "service", annotations={"angelbarrera92/tunnel": kopf.PRESENT})
def new_tunnel_service(name, namespace, meta, spec, annotations, **_):
    logger.info(
        f"new service ({meta}) listened with the angelbarrera92/tunnel annotation")
    port = -1
    if len(spec.get("ports")) == 1:
        port = spec.get("ports")[0].get("port")
    else:
        # TODO: Look for a certains annotation to get the right port.
        pass
    tunnel(service_name=name, service_namespace=namespace,
           port=port, subdomain=annotations["angelbarrera92/tunnel"])


# TODO. Reconcile all services on startup
# TODO. Annotations should be standarized somewhere as constants
# TODO. Think about adding a new status event when tunnel pod is deployed

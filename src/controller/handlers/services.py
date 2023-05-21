from logging import getLogger

import kopf
from pykube.objects import Service
from src.controller.handlers import (
    PORT_ANNOTATION,
    TUNNEL_ANNOTATION,
    service_port,
    tunnel_subdomain,
)
from src.controller.tunnel import tunnel
from src.kubernetes import services

logger = getLogger(__name__)


@kopf.on.create("", "v1", "service", annotations={TUNNEL_ANNOTATION: kopf.PRESENT})
def service_creation(name, namespace, **_):
    logger.info(
        f"new service ({namespace}/{name}) listened with the {TUNNEL_ANNOTATION} annotation"
    )
    logger.info("query the service")
    # pylint: disable=E1120
    svc = services.get(namespace=namespace, name=name)
    create_tunnel(svc)


@kopf.on.field("", "v1", "service", field="metadata.annotations")
def service_annotation_modification(diff, name, namespace, **_):
    logger.info(f"update service {namespace}/{name} annotations: {diff}")

    # This is whay the method receives in the diff attribute.
    # (('add', ('hi',), None, 'hi'),)
    # (('change', ('hi',), 'hi', 'hi2'),)
    # (('remove', ('hi',), 'hi2', None),)
    # - Remove annotation. Should remove the pod tunnel.

    for d in diff:
        action = d[0]

        # TODO: Improve this code-block
        # Received an event like (('add', None, None, {'hello': 'world'}),)
        # We should omit this case.
        try:
            annotation = d[1][0]
        except IndexError:
            annotation = None

        if annotation and (annotation in [TUNNEL_ANNOTATION, PORT_ANNOTATION]):
            logger.info(f"{action} annotation {annotation}")
            # pylint: disable=E1120
            svc = services.get(namespace=namespace, name=name)
            if annotation == TUNNEL_ANNOTATION:
                if action == "remove":
                    delete_tunnel(svc)
                elif "add":
                    create_tunnel(svc)
                elif action == "change":
                    delete_tunnel(svc)
                    create_tunnel(svc)
            elif annotation == PORT_ANNOTATION:
                if action in ["remove", "change", "add"]:
                    delete_tunnel(svc)
                    create_tunnel(svc)


# TODO. Think about adding a new status event when tunnel pod is deployed
# TODO. Validate subdomain format
# TODO. Validate port format. Only numbers allowed.
# TODO. Log level, currently set all logs to info wich is incorrect


def delete_tunnel(svc: Service):
    logger.info(f"remove tunnel for service {svc.namespace}/{svc.name}")
    pod = tunnel.find_pod(svc=svc)
    configmap = tunnel.find_configmap(svc=svc)
    logger.info(f"remove tunnel pod for service {svc.namespace}/{svc.name}")
    pod.delete()
    logger.info(f"remove tunnel configmap for service {svc.namespace}/{svc.name}")
    configmap.delete()


def create_tunnel(svc: Service):
    logger.info("gathering tunnel information")
    tunnelPort = service_port(svc)
    tunnelSubdomain = tunnel_subdomain(svc)
    logger.info(f"tunnel port {tunnelPort} and subdomain {tunnelSubdomain}")
    # pylint: disable=E1120
    configmap = tunnel.create_configmap(svc, tunnelPort, tunnelSubdomain)
    logger.info(f"configmap {configmap.namespace}/{configmap.name} created")
    # pylint: disable=E1120
    pod = tunnel.create_pod(svc, configmap, tunnelPort, tunnelSubdomain)
    logger.info(f"pod {pod.namespace}/{pod.name} created")

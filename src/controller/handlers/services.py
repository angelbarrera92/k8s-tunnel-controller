from logging import getLogger

import kopf
from src.controller.handlers import (PORT_ANNOTATION, TUNNEL_ANNOTATION,
                                     service_port, tunnel_subdomain)
from src.controller.tunnel import tunnel
from src.kubernetes import services

logger = getLogger(__name__)


@kopf.on.create("", "v1", "service", annotations={TUNNEL_ANNOTATION: kopf.PRESENT})
def service_creation(name, namespace, **_):
    logger.info(
        f"new service ({namespace}/{name}) listened with the {TUNNEL_ANNOTATION} annotation")

    logger.info("query the service")
    svc = services.get(namespace=namespace, name=name)

    logger.info("gathering tunnel information")
    tunnelPort = service_port(svc)
    tunnelSubdomain = tunnel_subdomain(svc)
    logger.info(f"tunnel port {tunnelPort} and subdomain {tunnelSubdomain}")

    logger.info("create secret")
    secret = tunnel.create_secret(svc, tunnelPort, tunnelSubdomain)
    logger.info(f"secret {secret.namespace}/{secret.name} created")
    configmap = tunnel.create_configmap(svc, tunnelPort, tunnelSubdomain)
    logger.info(f"configmap {configmap.namespace}/{configmap.name} created")
    pod = tunnel.create_pod(svc, secret, configmap,
                            tunnelPort, tunnelSubdomain)
    logger.info(f"pod {pod.namespace}/{pod.name} created")


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
            svc = services.get(namespace=namespace, name=name)
            if annotation == TUNNEL_ANNOTATION:
                if action == "remove":
                    logger.info(
                        f"remove tunnel for service {namespace}/{name}")
                    pod = tunnel.find_pod(svc=svc)
                    configmap = tunnel.find_configmap(svc=svc)
                    secret = tunnel.find_secret(svc=svc)
                    logger.info(
                        f"remove tunnel pod for service {namespace}/{name}")
                    pod.delete()
                    logger.info(
                        f"remove tunnel configmap for service {namespace}/{name}")
                    configmap.delete()
                    logger.info(
                        f"remove tunnel secret for service {namespace}/{name}")
                    secret.delete()
                elif "add":

                    logger.info("gathering tunnel information")
                    tunnelPort = service_port(svc)
                    tunnelSubdomain = tunnel_subdomain(svc)
                    logger.info(
                        f"tunnel port {tunnelPort} and subdomain {tunnelSubdomain}")

                    logger.info("create secret")
                    secret = tunnel.create_secret(
                        svc, tunnelPort, tunnelSubdomain)
                    logger.info(
                        f"secret {secret.namespace}/{secret.name} created")
                    configmap = tunnel.create_configmap(
                        svc, tunnelPort, tunnelSubdomain)
                    logger.info(
                        f"configmap {configmap.namespace}/{configmap.name} created")
                    pod = tunnel.create_pod(svc, secret, configmap,
                                            tunnelPort, tunnelSubdomain)
                    logger.info(f"pod {pod.namespace}/{pod.name} created")
                elif action == "change":
                    logger.info("gathering tunnel information")
                    tunnelPort = service_port(svc)
                    tunnelSubdomain = tunnel_subdomain(svc)

                    logger.info(
                        f"remove tunnel for service {namespace}/{name}")
                    pod = tunnel.find_pod(svc=svc)
                    configmap = tunnel.find_configmap(svc=svc)
                    secret = tunnel.find_secret(svc=svc)
                    logger.info(
                        f"remove tunnel pod for service {namespace}/{name}")
                    pod.delete()
                    logger.info(
                        f"remove tunnel configmap for service {namespace}/{name}")
                    configmap.delete()
                    logger.info(
                        f"remove tunnel secret for service {namespace}/{name}")
                    secret.delete()

                    logger.info(
                        f"tunnel port {tunnelPort} and subdomain {tunnelSubdomain}")

                    logger.info("create secret")
                    secret = tunnel.create_secret(
                        svc, tunnelPort, tunnelSubdomain)
                    logger.info(
                        f"secret {secret.namespace}/{secret.name} created")
                    configmap = tunnel.create_configmap(
                        svc, tunnelPort, tunnelSubdomain)
                    logger.info(
                        f"configmap {configmap.namespace}/{configmap.name} created")
                    pod = tunnel.create_pod(svc, secret, configmap,
                                            tunnelPort, tunnelSubdomain)
                    logger.info(f"pod {pod.namespace}/{pod.name} created")
            elif annotation == PORT_ANNOTATION:
                if action in ["remove", "change", "add"]:

                    logger.info("gathering tunnel information")
                    tunnelPort = service_port(svc)
                    tunnelSubdomain = tunnel_subdomain(svc)

                    logger.info(
                        f"remove tunnel for service {namespace}/{name}")
                    pod = tunnel.find_pod(svc=svc)
                    configmap = tunnel.find_configmap(svc=svc)
                    secret = tunnel.find_secret(svc=svc)
                    logger.info(
                        f"remove tunnel pod for service {namespace}/{name}")
                    pod.delete()
                    logger.info(
                        f"remove tunnel configmap for service {namespace}/{name}")
                    configmap.delete()
                    logger.info(
                        f"remove tunnel secret for service {namespace}/{name}")
                    secret.delete()

                    logger.info(
                        f"tunnel port {tunnelPort} and subdomain {tunnelSubdomain}")

                    logger.info("create secret")
                    secret = tunnel.create_secret(
                        svc, tunnelPort, tunnelSubdomain)
                    logger.info(
                        f"secret {secret.namespace}/{secret.name} created")
                    configmap = tunnel.create_configmap(
                        svc, tunnelPort, tunnelSubdomain)
                    logger.info(
                        f"configmap {configmap.namespace}/{configmap.name} created")
                    pod = tunnel.create_pod(svc, secret, configmap,
                                            tunnelPort, tunnelSubdomain)
                    logger.info(f"pod {pod.namespace}/{pod.name} created")


# TODO. Think about adding a new status event when tunnel pod is deployed
# TODO. Validate subdomain format
# TODO. Validate port format. Only numbers allowed.
# TODO. Log level, currently set all logs to info wich is incorrect
# TODO. Refactor duplicate code

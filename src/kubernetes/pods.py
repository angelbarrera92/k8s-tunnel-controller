from pykube import Pod
from src.kubernetes.connection import kubernetes_api


@kubernetes_api
def get(api, namespace: str, labels: dict = {}) -> Pod:
    pods = list()
    for p in Pod.objects(api, namespace=namespace).filter(namespace=namespace, selector=labels):
        pods.append(p)
    if len(pods) == 1:
        return pods[0]
    return None

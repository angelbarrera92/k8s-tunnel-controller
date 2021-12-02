from pykube import Pod
from src.kubernetes.connection import kubernetes_api


@kubernetes_api
def get(api, namespace: str, labels: dict = {}) -> Pod:
    pods = Pod.objects(api, namespace=namespace).filter(
        namespace=namespace, selector=labels)
    if len(pods) == 1:
        return pods[0]
    return None

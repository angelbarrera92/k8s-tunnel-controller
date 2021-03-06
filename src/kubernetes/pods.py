from pykube import Pod
from src.kubernetes.connection import kubernetes_api


@kubernetes_api
def get(api, namespace: str, labels: dict = {}, ready: bool = True) -> Pod:
    pods = list()
    for p in Pod.objects(api, namespace=namespace).filter(
        namespace=namespace, selector=labels
    ):
        if p.obj["status"]["containerStatuses"][0]["ready"] == ready:
            pods.append(p)
    if len(pods) == 1:
        return pods[0]
    return None

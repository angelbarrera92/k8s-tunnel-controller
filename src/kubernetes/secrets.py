from pykube import Secret, all
from src.kubernetes.connection import kubernetes_api


@kubernetes_api
def get(api, namespace: str, labels: dict = {}) -> Secret:
    secrets = list()
    for s in Secret.objects(api, namespace=namespace).filter(namespace=namespace, selector=labels):
        secrets.append(s)
    if len(secrets) == 1:
        return secrets[0]
    return None

from pykube import Service
from src.kubernetes.connection import kubernetes_api


@kubernetes_api
def get(api, namespace: str, name: str) -> Service:
    return Service.objects(api, namespace=namespace).get(name=name)

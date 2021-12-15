from pykube import ConfigMap
from src.kubernetes.connection import kubernetes_api


@kubernetes_api
def get(api, namespace: str, labels: dict = {}) -> ConfigMap:
    configMaps = list()
    for c in ConfigMap.objects(api, namespace=namespace).filter(namespace=namespace, selector=labels):
        configMaps.append(c)
    if len(configMaps) == 1:
        return configMaps[0]
    return None

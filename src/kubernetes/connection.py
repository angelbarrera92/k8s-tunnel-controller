from logging import getLogger
from os import getenv

from pykube import HTTPClient, KubeConfig

logger = getLogger(__name__)
client = None


def kubernetes_api(function):
    def wrap_function(*args, **kwargs):
        if not client:
            logger.info("init pykube kubernetes client")
            _connect()
        res = function(client, *args, **kwargs)
        return res

    return wrap_function


def _connect():
    try:
        config = KubeConfig.from_service_account()
    except FileNotFoundError:
        config = KubeConfig.from_file(getenv("KUBECONFIG", "~/.kube/config"))

    global client
    client = HTTPClient(config)

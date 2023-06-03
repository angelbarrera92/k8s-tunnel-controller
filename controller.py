from logging import getLogger
from os import getenv

from src.controller.handlers.configmaps import *  # noqa: F401,F403
from src.controller.handlers.pods import *  # noqa: F401,F403
from src.controller.handlers.services import *  # noqa: F401,F403

logger = getLogger()
logger.setLevel(getenv("LOGGING_LEVEL", "INFO"))

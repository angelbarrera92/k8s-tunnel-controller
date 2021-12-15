from logging import getLogger
from os import getenv


from src.controller.handlers.configmaps import *
from src.controller.handlers.pods import *
from src.controller.handlers.secrets import *
from src.controller.handlers.services import *

logger = getLogger()
logger.setLevel(getenv("LOGGING_LEVEL", "INFO"))

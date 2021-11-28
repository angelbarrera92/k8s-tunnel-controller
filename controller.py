from logging import getLogger
from os import getenv

from src.controller.handlers import *

logger = getLogger()
logger.setLevel(getenv("LOGGING_LEVEL", "INFO"))

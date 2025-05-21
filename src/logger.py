import logging
from logging.handlers import RotatingFileHandler

from utils import get_env_var


logger = logging.getLogger("cv_mcp")

log_level = get_env_var("LOG_LEVEL", "INFO").upper()
logger.setLevel(getattr(logging, log_level, logging.INFO))

logger.propagate = False

if not logger.handlers:
    file_handler = RotatingFileHandler("cv_mcp.log", maxBytes=10485760, backupCount=5)  # 10MB with 5 backups
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(funcName)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

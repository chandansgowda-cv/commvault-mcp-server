import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("cv_mcp")
logger.setLevel(logging.DEBUG)
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

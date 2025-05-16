import logging


logger = logging.getLogger("cv_mcp")
logger.setLevel(logging.DEBUG)

if not logger.hasHandlers():
    
    file_handler = logging.FileHandler("cv_mcp.log")
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(funcName)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

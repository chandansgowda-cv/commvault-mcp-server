import os
from typing import Optional
from dotenv import load_dotenv

from src.logger import logger

load_dotenv()

def get_env_var(var_name: str, default: Optional[str] = None) -> str:
    value = os.getenv(var_name, default)
    if value is None:
        logger.error(f"Environment variable {var_name} not found and no default provided.")
        raise ValueError(f"Please check if you have set all the environment variables. You can also run setuop script to set them.")
    return value

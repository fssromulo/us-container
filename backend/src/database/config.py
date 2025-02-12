# Python imports
import os

# Here we create a custom SSL context
import ssl

# Pip imports
from loguru import logger

# Internal imports
from src.config import settings
from src.database.tortoise_init import models


ctx = ssl.create_default_context()
# And in this example we disable validation...
# Please don't do this. Loot at the official Python ``ssl`` module documentation
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

config = {
    "default": {
        "engine": "tortoise.backends.asyncpg",
        "credentials": {
            "database": settings.DB_NAME,
            "host": settings.DB_HOST,
            "port": settings.DB_PORT,
            "user": settings.DB_USER,
            "password": settings.DB_PASS,
            # Here we pass in the SSL context
            "ssl": ctx if os.environ.get("STAGE", 'dev') != 'dev' else None,
        },
    }
}
logger.info(config)

TORTOISE_ORM = {
    "connections": config,
    "apps": {
        "models": {
            "models": models,
            "default_connection": "default",
        }
    },
}

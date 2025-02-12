# Python imports
import asyncio
from uuid import uuid4

# Pip imports
from aerich import Command
from decouple import config

# Internal imports
from src.database.config import TORTOISE_ORM


DB_USER: str = config("DB_USER", default="hello_fastapi")
DB_PASS: str = config("DB_PASS", default="hello_fastapi")
DB_HOST: str = config("DB_HOST", default="db")
DB_PORT: str = config("DB_PORT", default="5432")
DB_NAME: str = config("DB_NAME", default="containerCrm")

TORTOISE_ORM['connections']['default']['credentials'] = {
    "database": DB_NAME,
    "host": DB_HOST,
    "port": DB_PORT,
    "user": DB_USER,
    "password": DB_PASS,
    "ssl": None,
}


async def run():
    command = Command(tortoise_config=TORTOISE_ORM, app='models')
    await command.init()
    await command.migrate(str(uuid4()))


asyncio.run(run())

from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from discord.ext import commands
from typing import Any,cast

class MongoDBClient:
    _instance=None
    mongodb:AsyncDatabase

    def __new__(cls,client:commands.Bot=None)->"MongoDBClient":
        if cls._instance is None:
            cls._instance=super().__new__(cls)
            if client is None:
                client=get_current_app()
            cls._instance.mongodb=client.mongodb
        return cls._instance


def get_current_app()->commands.Bot:
    import importlib
    main_module = importlib.import_module("main")
    field="client"
    return cast(commands.Bot, getattr(main_module, field))

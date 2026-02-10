from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from sekaiInformer.settings import settings

async def get_mongoDb()->AsyncDatabase:
    client=AsyncMongoClient(settings.MONGO_DB_URL)

    print("Connected to MongoDB")
    db = client.get_database(settings.MONGO_DB_NAME)
    return db
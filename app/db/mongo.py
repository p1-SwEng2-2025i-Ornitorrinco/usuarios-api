from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING

MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "intercambio_servicios"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]


users_collection = db["usuarios"]

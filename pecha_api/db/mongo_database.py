from contextlib import asynccontextmanager

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from ..config import get

mongodb_client = None
mongodb = None


@asynccontextmanager
async def lifespan(api: FastAPI):
    global mongodb_client, mongodb
    # Initialize the MongoDB client and database
    mongodb_client = AsyncIOMotorClient(get("MONGO_CONNECTION_STRING"))
    mongodb = mongodb_client[get("MONGO_DATABASE_NAME")]
    api.mongodb = mongodb  # Attach the database instance to the FastAPI app

    # Yield control back to FastAPI
    yield

    # Close the MongoDB connection when the application shuts down
    if mongodb_client:
        mongodb_client.close()
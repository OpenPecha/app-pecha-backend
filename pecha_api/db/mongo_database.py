import logging
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

    # Initialize collections and indexes if necessary
    try:
        # Ensure collections are initialized and create any necessary indexes
        await initialize_collections()
    except Exception as e:
        logging.error(f"Error during collection initialization: {e}")
        raise
    # Yield control back to FastAPI
    yield

    # Close the MongoDB connection when the application shuts down
    if mongodb_client:
        mongodb_client.close()


async def initialize_collections():
    term_count = await mongodb.terms.count_documents({})
    if term_count == 0:
        logging.info("Term collection is empty and ready for use.")
    else:
        logging.info("Term collection is already initialized with data.")

        # Add similar checks for other collections if needed

        # Optional: If you want to set up indexes (e.g., unique index for 'slug' field)
    await mongodb.terms.create_index([("slug", 1)], unique=True)
    logging.info("Indexes for 'slug' field created if they didn't exist.")

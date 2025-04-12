import logging
from contextlib import asynccontextmanager

from beanie import init_beanie
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from ..topics.topics_models import Topic
from ..terms.terms_models import Term
from ..texts.texts_models import Text
from ..texts.segments.segments_models import Segment
from ..sheets.sheets_models import Sheet
from ..texts.texts_models import TableOfContent
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
        await init_beanie(database=mongodb,document_models=[Term, Topic, Text, Segment, Sheet, TableOfContent])
        logging.info("Beanie initialized with the 'terms' collection.")
        
    except Exception as e:
        logging.error(f"Error during collection initialization: {e}")
        raise
    # Yield control back to FastAPI
    yield

    # Close the MongoDB connection when the application shuts down
    if mongodb_client:
        mongodb_client.close()

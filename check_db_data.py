# check_db_data.py
"""
Script to investigate the production database structure and find what data exists.
"""
import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from pecha_api.texts.texts_models import Text
from pecha_api.texts.segments.segments_models import Segment
from pecha_api.texts.texts_models import TableOfContent
from pecha_api.texts.groups.groups_models import Group
from pecha_api.topics.topics_models import Topic
from pecha_api.collections.collections_models import Collection
from pecha_api.terms.terms_models import Term
from pecha_api.config import get

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def initialize_db():
    """Initialize database connection for standalone script."""
    connection_string = get("MONGO_CONNECTION_STRING")
    database_name = get("MONGO_DATABASE_NAME")
    
    logger.info(f"Connecting to database: {database_name}")
    logger.info(f"Connection string: {connection_string.split('@')[0]}@***")
    
    # Create MongoDB client
    mongodb_client = AsyncIOMotorClient(connection_string)
    mongodb = mongodb_client[database_name]
    
    # Initialize Beanie with all document models
    await init_beanie(
        database=mongodb,
        document_models=[Collection, Term, Topic, Text, Segment, TableOfContent, Group]
    )
    
    logger.info("Database initialized successfully")
    return mongodb_client


async def investigate_db():
    """Investigate the database to understand the data structure."""
    mongodb_client = await initialize_db()
    
    try:
        # Count total texts
        total_texts = await Text.count()
        logger.info(f"Total texts in database: {total_texts}")
        
        # Get unique language values
        pipeline = [
            {"$group": {"_id": "$language", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        language_stats = await Text.get_motor_collection().aggregate(pipeline).to_list(None)
        
        print("\n" + "="*60)
        print("LANGUAGE DISTRIBUTION IN DATABASE")
        print("="*60)
        for stat in language_stats:
            lang = stat['_id'] if stat['_id'] else '<null>'
            count = stat['count']
            print(f"Language: {lang:20} Count: {count}")
        
        # Get sample texts from each language
        print("\n" + "="*60)
        print("SAMPLE TEXTS FROM EACH LANGUAGE")
        print("="*60)
        
        for stat in language_stats[:5]:  # Show top 5 languages
            lang = stat['_id']
            sample_texts = await Text.find(Text.language == lang).limit(3).to_list()
            
            print(f"\n--- Language: {lang or '<null>'} ---")
            for text in sample_texts:
                print(f"  ID: {text.id}")
                print(f"  Title: {text.title}")
                print(f"  Language: {text.language}")
                print(f"  Type: {text.type}")
                print(f"  Published: {text.is_published}")
                print()
        
        # Count total segments
        total_segments = await Segment.count()
        logger.info(f"Total segments in database: {total_segments}")
        
    finally:
        # Close the database connection
        if mongodb_client:
            mongodb_client.close()
            logger.info("Database connection closed")


if __name__ == "__main__":
    asyncio.run(investigate_db())

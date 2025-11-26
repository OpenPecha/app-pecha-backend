
import asyncio
import os
import logging
import json
from typing import Dict, List
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
    logger.info(f"Connection string: {connection_string.split('@')[0]}@***")  # Hide credentials in log
    
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


async def get_bo_texts_with_segments() -> Dict[str, Dict[str, str]]:
    """
    Get all Tibetan (bo) language texts and their segments.
    
    Returns:
        Dict with text_id as key, and dict of {segment_id: content} as value
        Example: {
            "text_id_1": {"seg_id_1": "content1", "seg_id_2": "content2"},
            "text_id_2": {"seg_id_3": "content3"}
        }
    """
    # Initialize database connection
    mongodb_client = await initialize_db()
    
    try:
        # Get all texts with language="bo"
        logger.info("Fetching all texts with language='bo'...")
        bo_texts = await Text.find(Text.language == "bo").to_list()
        logger.info(f"Found {len(bo_texts)} Tibetan texts")
        
        result = {}
        for idx, text in enumerate(bo_texts, 1):
            text_id = str(text.id)
            logger.info(f"Processing text {idx}/{len(bo_texts)}: {text.title} (ID: {text_id})")
            
            # Get all segments for this text
            segments = await Segment.get_segments_by_text_id(text_id)
            logger.info(f"  Found {len(segments)} segments")
            
            # Create dict of segment_id: content
            segment_dict = {
                str(segment.id): segment.content 
                for segment in segments
            }
            
            result[text_id] = segment_dict
        
        logger.info(f"Completed! Total texts processed: {len(result)}")
        return result
    
    finally:
        # Close the database connection
        if mongodb_client:
            mongodb_client.close()
            logger.info("Database connection closed")


async def main():
    """Main function to run the script."""
    output_file = "bo_segments_production.json"
    
    try:
        # Get texts and segments
        logger.info("Starting data extraction...")
        data = await get_bo_texts_with_segments()
        
        # Print summary
        total_segments = sum(len(segments) for segments in data.values())
        print("\n" + "="*50)
        print("SUMMARY")
        print("="*50)
        print(f"Total Tibetan texts: {len(data)}")
        print(f"Total segments: {total_segments}")
        print("\nSample (first text):")
        if data:
            first_text_id = list(data.keys())[0]
            first_segments = data[first_text_id]
            print(f"Text ID: {first_text_id}")
            print(f"Number of segments: {len(first_segments)}")
            if first_segments:
                first_seg_id = list(first_segments.keys())[0]
                print(f"First segment ID: {first_seg_id}")
                print(f"First segment content: {first_segments[first_seg_id][:100]}...")
        
        # Save to JSON file
        logger.info(f"Writing data to {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✓ Successfully saved {len(data)} texts with {total_segments} segments to {output_file}")
        print(f"\n✓ Data saved to: {output_file}")
        
        return data
        
    except Exception as e:
        logger.error(f"Error occurred: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    # Run the main function
    result = asyncio.run(main())
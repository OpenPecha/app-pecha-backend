import asyncio
import json
import logging
import uuid
from typing import Dict
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


async def update_segments_from_json(input_file: str, dry_run: bool = False):
    """
    Update segment content in database from JSON file.
    
    Args:
        input_file: Path to JSON file with format {text_id: {segment_id: content}}
        dry_run: If True, only show what would be updated without making changes
    """
    # Load the JSON file
    logger.info(f"Loading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Initialize database connection
    mongodb_client = await initialize_db()
    
    try:
        total_updated = 0
        total_failed = 0
        
        for text_id, segments in data.items():
            logger.info(f"Processing text: {text_id}")
            logger.info(f"  Total segments to update: {len(segments)}")
            
            text_updated = 0
            text_failed = 0
            
            for segment_id, new_content in segments.items():
                try:
                    if dry_run:
                        # Just check if segment exists
                        segment = await Segment.get_segment_by_id(segment_id)
                        if segment:
                            text_updated += 1
                        else:
                            logger.warning(f"  Segment not found: {segment_id}")
                            text_failed += 1
                    else:
                        # Actually update the segment
                        segment = await Segment.find_one(Segment.id == uuid.UUID(segment_id))
                        if segment:
                            segment.content = new_content
                            await segment.save()
                            text_updated += 1
                        else:
                            logger.warning(f"  Segment not found: {segment_id}")
                            text_failed += 1
                            
                except Exception as e:
                    logger.error(f"  Error updating segment {segment_id}: {e}")
                    text_failed += 1
            
            logger.info(f"  Text {text_id}: {text_updated} updated, {text_failed} failed")
            total_updated += text_updated
            total_failed += text_failed
        
        # Summary
        print("\n" + "="*50)
        print("SUMMARY")
        print("="*50)
        if dry_run:
            print("DRY RUN - No changes were made")
        print(f"Total segments updated: {total_updated}")
        print(f"Total segments failed: {total_failed}")
        
    finally:
        if mongodb_client:
            mongodb_client.close()
            logger.info("Database connection closed")


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Update segment content in MongoDB from JSON file')
    parser.add_argument('--input', '-i', required=True, help='Input JSON file with updated content')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be updated without making changes')
    
    args = parser.parse_args()
    
    await update_segments_from_json(args.input, dry_run=args.dry_run)


if __name__ == "__main__":
    asyncio.run(main())

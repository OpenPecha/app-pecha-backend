# verify_connection.py
"""
Script to verify MongoDB connection and list available databases and collections.
"""
import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pecha_api.config import get

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def verify_connection():
    """Verify database connection and list available databases and collections."""
    connection_string = get("MONGO_CONNECTION_STRING")
    database_name = get("MONGO_DATABASE_NAME")
    
    logger.info(f"Attempting to connect...")
    logger.info(f"Target database: {database_name}")
    logger.info(f"Connection string: {connection_string.split('@')[0]}@***")
    
    # Create MongoDB client
    mongodb_client = AsyncIOMotorClient(connection_string)
    
    try:
        # List all databases
        logger.info("\nListing all databases...")
        databases = await mongodb_client.list_database_names()
        print("\n" + "="*60)
        print("AVAILABLE DATABASES")
        print("="*60)
        for db_name in databases:
            print(f"  - {db_name}")
        
        # Check if target database exists
        if database_name in databases:
            print(f"\n✓ Target database '{database_name}' exists!")
        else:
            print(f"\n✗ WARNING: Target database '{database_name}' not found!")
            print(f"  Available databases: {', '.join(databases)}")
        
        # List collections in the target database
        mongodb = mongodb_client[database_name]
        collections = await mongodb.list_collection_names()
        
        print("\n" + "="*60)
        print(f"COLLECTIONS IN '{database_name}' DATABASE")
        print("="*60)
        if collections:
            for coll_name in collections:
                # Count documents in each collection
                count = await mongodb[coll_name].count_documents({})
                print(f"  - {coll_name:30} ({count} documents)")
        else:
            print("  <No collections found>")
        
        # Server info
        server_info = await mongodb_client.server_info()
        print("\n" + "="*60)
        print("SERVER INFO")
        print("="*60)
        print(f"  MongoDB Version: {server_info.get('version')}")
        print(f"  Connection: SUCCESS ✓")
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
    finally:
        mongodb_client.close()
        logger.info("\nConnection closed")


if __name__ == "__main__":
    asyncio.run(verify_connection())

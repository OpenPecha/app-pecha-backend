#!/usr/bin/env python3
"""
Simple script to update datetime format in MongoDB Text collection
Uses minimal dependencies - only pymongo (not motor/beanie)
"""

import re
from pymongo import MongoClient

def normalize_datetime(datetime_str):
    """
    Normalize datetime strings to YYYY-MM-DD HH:MM:SS format
    Handles:
    - "2025-03-20 09:26:16.571536" -> "2025-03-20 09:26:16" (remove microseconds)
    - "2025-04-05 04:38:34+00:00" -> "2025-04-05 04:38:34" (remove timezone)
    """
    if not datetime_str:
        return datetime_str
    
    # Remove microseconds: YYYY-MM-DD HH:MM:SS.microseconds
    datetime_str = re.sub(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\.\d+', r'\1', datetime_str)
    
    # Remove timezone: YYYY-MM-DD HH:MM:SS+XX:XX or YYYY-MM-DD HH:MM:SS-XX:XX
    datetime_str = re.sub(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})[\+\-]\d{2}:\d{2}', r'\1', datetime_str)
    
    return datetime_str

def delete_sheet_documents():
    """
    Delete all Text documents where type = "sheet"
    """
    # MongoDB connection string
    connection_string = "mongodb://admin:pechaAdmin@localhost:27017/pecha?authSource=admin"
    
    try:
        # Connect to MongoDB
        client = MongoClient(connection_string)
        db = client["pecha"]
        collection = db["Text"]
        
        print("Connected to MongoDB")
        
        # First, count how many sheet documents exist
        sheet_count = collection.count_documents({"type": "sheet"})
        print(f"Found {sheet_count} documents with type = 'sheet'")
        
        if sheet_count == 0:
            print("No sheet documents found to delete.")
            client.close()
            return
        
        # Show some examples before deletion
        print("\nSample sheet documents to be deleted:")
        sample_sheets = collection.find({"type": "sheet"}).limit(3)
        for i, doc in enumerate(sample_sheets, 1):
            print(f"{i}. ID: {doc.get('_id')}, Title: {doc.get('title', 'N/A')}")
        
        # Ask for confirmation
        confirm = input(f"\nAre you sure you want to delete {sheet_count} sheet documents? (yes/no): ").lower().strip()
        
        if confirm in ['yes', 'y']:
            # Delete all documents with type = "sheet"
            result = collection.delete_many({"type": "sheet"})
            
            print(f"\n{'='*50}")
            print(f"DELETION SUMMARY:")
            print(f"Documents found: {sheet_count}")
            print(f"Documents deleted: {result.deleted_count}")
            print(f"{'='*50}")
            
            if result.deleted_count == sheet_count:
                print("✓ All sheet documents successfully deleted!")
            else:
                print("⚠ Warning: Some documents may not have been deleted.")
        else:
            print("Deletion cancelled.")
        
        # Close the connection
        client.close()
        print("Connection closed successfully")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure MongoDB is running and accessible")

def update_datetime_format():
    """
    Update datetime format in Text collection from various formats to 'YYYY-MM-DD HH:MM:SS'
    """
    # MongoDB connection string
    connection_string = "mongodb://admin:pechaAdmin@localhost:27017/pecha?authSource=admin"
    
    try:
        # Connect to MongoDB
        client = MongoClient(connection_string)
        db = client["pecha"]
        collection = db["Text"]
        
        print("Connected to MongoDB")
        
        # Test connection
        count = collection.count_documents({})
        print(f"Text collection has {count} documents")
        
        # Show sample document
        sample = collection.find_one({})
        if sample:
            print("\nSample document:")
            print(f"ID: {sample.get('_id')}")
            print(f"Title: {sample.get('title', 'N/A')}")
            print(f"Created Date: {sample.get('created_date', 'N/A')}")
            print(f"Updated Date: {sample.get('updated_date', 'N/A')}")
            print(f"Published Date: {sample.get('published_date', 'N/A')}")
        
        print("\nStarting datetime format normalization...")
        
        # Find all documents in the Text collection
        cursor = collection.find({})
        documents_updated = 0
        documents_processed = 0
        
        for document in cursor:
            documents_processed += 1
            update_fields = {}
            
            # Check and update datetime fields
            datetime_fields = ["created_date", "updated_date", "published_date"]
            
            for field in datetime_fields:
                if field in document and document[field]:
                    original_datetime = document[field]
                    updated_datetime = normalize_datetime(original_datetime)
                    
                    if updated_datetime != original_datetime:
                        update_fields[field] = updated_datetime
                        print(f"Document {document['_id']}: {field}")
                        print(f"  Before: {original_datetime}")
                        print(f"  After:  {updated_datetime}")
            
            # Update the document if any fields need updating
            if update_fields:
                result = collection.update_one(
                    {"_id": document["_id"]},
                    {"$set": update_fields}
                )
                if result.modified_count > 0:
                    documents_updated += 1
                    print(f"✓ Updated document {document['_id']}")
                else:
                    print(f"✗ Failed to update document {document['_id']}")
        
        print(f"\n{'='*50}")
        print(f"SUMMARY:")
        print(f"Documents processed: {documents_processed}")
        print(f"Documents updated: {documents_updated}")
        print(f"{'='*50}")
        
        # Close the connection
        client.close()
        print("Connection closed successfully")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure MongoDB is running and accessible")

if __name__ == "__main__":
    print("MongoDB Text Collection Operations")
    print("=" * 40)
    print("1. Update datetime format")
    print("2. Delete sheet documents (type = 'sheet')")
    print("=" * 40)
    
    choice = input("Choose operation (1 or 2): ").strip()
    
    if choice == "1":
        print("\nStarting datetime format update...")
        update_datetime_format()
    elif choice == "2":
        print("\nStarting sheet document deletion...")
        delete_sheet_documents()
    else:
        print("Invalid choice. Please run the script again and choose 1 or 2.") 
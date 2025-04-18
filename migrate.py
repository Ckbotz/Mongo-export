import pymongo
from tqdm import tqdm
import argparse
from datetime import datetime

def transfer_large_files(old_uri, new_uri, batch_size=5000, timeout_ms=300000):
    """
    Optimized for transferring large files (like Telegram media) between MongoDB instances.
    
    Args:
        old_uri (str): Source MongoDB URI
        new_uri (str): Destination MongoDB URI
        batch_size (int): Documents per batch (default: 5000)
        timeout_ms (int): Timeout for DB operations in milliseconds (default: 5 mins)
    """
    try:
        print(f"🚀 Starting transfer at {datetime.now()}")
        
        # Connect with longer timeouts
        old_client = pymongo.MongoClient(
            old_uri, 
            socketTimeoutMS=timeout_ms,
            serverSelectionTimeoutMS=timeout_ms
        )
        new_client = pymongo.MongoClient(
            new_uri,
            socketTimeoutMS=timeout_ms
        )

        # Focus on specific DB (replace 'telegram_db' with your actual DB name)
        db_name = "telegram_db"  
        old_db = old_client[db_name]
        new_db = new_client[db_name]

        # Target collection (replace 'files' with your collection name)
        collection_name = "files"  
        old_col = old_db[collection_name]
        new_col = new_db[collection_name]

        # Clear existing data in destination
        if collection_name in new_db.list_collection_names():
            new_col.drop()
            print(f"🔥 Dropped old '{collection_name}' collection in destination")

        # Get total count for progress bar
        total_docs = old_col.estimated_document_count()
        print(f"📦 Transferring {total_docs:,} documents...")

        # Batch transfer with progress
        with tqdm(total=total_docs, unit="doc") as pbar:
            cursor = old_col.find().batch_size(batch_size)
            batch = []
            
            for doc in cursor:
                batch.append(doc)
                if len(batch) >= batch_size:
                    new_col.insert_many(batch, ordered=False)  # Faster skips on errors
                    pbar.update(len(batch))
                    batch = []
            
            if batch:  # Insert remaining docs
                new_col.insert_many(batch)
                pbar.update(len(batch))

        # Recreate indexes (if any)
        print("⚡ Recreating indexes...")
        for index_name, index_info in old_col.index_information().items():
            if index_name != "_id_":
                keys = index_info["key"]
                new_col.create_index(keys, name=index_name)

        print(f"✅ Transfer completed at {datetime.now()}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        old_client.close()
        new_client.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--old", required=True, help="Old MongoDB URI")
    parser.add_argument("--new", required=True, help="New MongoDB URI")
    parser.add_argument("--batch", type=int, default=5000, help="Batch size")
    args = parser.parse_args()

    transfer_large_files(args.old, args.new, args.batch)

# backend/scripts/inspect_vector_db.py
import sys
import os
import pickle
import gzip
from collections import Counter

# Add the backend directory to the Python path to import config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import Config

def inspect_vector_db():
    """
    Loads the vector database file and prints a summary of its contents.
    """
    db_path = Config.VECTOR_DB_PATH

    if not os.path.exists(db_path):
        print(f"❌ Error: Vector DB file not found at '{db_path}'.")
        print("Please run the Flask application first to generate the file.")
        return

    print(f"🔎 Inspecting vector database at: {db_path}")
    print("-" * 50)

    try:
        with gzip.open(db_path, 'rb') as f:
            data = pickle.load(f)

        documents = data.get("documents", [])
        next_id = data.get("next_id", 0)

        if not documents:
            print("⚠️ The database is empty. No documents found.")
            return

        print(f"✅ Database loaded successfully.")
        print(f"📊 Total Documents: {len(documents)}")
        print(f"🆔 Next ID: {next_id}")
        print("-" * 50)

        # --- Breakdown by Source ---
        source_counter = Counter(doc.get("metadata", {}).get("source") for doc in documents)

        print("📚 Document Breakdown by Source:")
        if not source_counter:
            print("  No sources found in metadata.")
        else:
            for source, count in source_counter.items():
                print(f"  - {source if source else 'Unknown'}: {count} documents")
        print("-" * 50)

        # --- Show Examples from Each Source ---
        print("🔍 Examples from each source:")

        seen_sources = set()
        examples_shown = 0
        max_examples_per_source = 2 # Show up to 2 examples per source

        for source in source_counter.keys():
            print(f"\n--- Source: {source if source else 'Unknown'} ---")
            count = 0
            for doc in documents:
                if doc.get("metadata", {}).get("source") == source and count < max_examples_per_source:
                    print(f"  ▶️  ID: {doc.get('id')}, Source Item ID: {doc.get('source_item_id')}")
                    print(f"      Content (first 100 chars): '{doc.get('content', '')[:100]}...'")
                    print(f"      Metadata: {doc.get('metadata')}")
                    count += 1
            if count == 0:
                print("  No examples to show for this source.")

        print("\n" + "="*50)
        print("Inspection complete.")


    except EOFError:
        print("❌ Error: The database file is empty or corrupted.")
    except pickle.UnpicklingError:
        print("❌ Error: Could not unpickle the database file. It may be corrupted.")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    inspect_vector_db()

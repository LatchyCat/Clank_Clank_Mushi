# backend/app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
from config import Config
import os
from apscheduler.schedulers.background import BackgroundScheduler
from flask_apscheduler import APScheduler
import logging

# Import global instances from the new globals.py module
from globals import global_vector_store, global_ollama_embedder

# Import other components
from services.data_embedding_service import DataEmbeddingService

# Import all blueprints from their respective files
from routes.news_api_routes import news_bp as news_api_bp
from routes.one_piece_api_routes import one_piece_api_bp
from routes.llm_api_routes import llm_api_bp

# Configure logging for APScheduler and your app
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger('apscheduler').setLevel(logging.INFO) # Keep APScheduler logs informative

# Define the flag file path for initial embedding status
# Ensure the flag file is created in the same directory as app.py
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
EMBEDDING_FLAG_FILE = os.path.join(BASE_DIR, '.vector_db_initialized')

# Initialize data embedding service here, using the global instances
global_data_embedding_service = DataEmbeddingService(global_vector_store, global_ollama_embedder)

# Initialize scheduler
scheduler = APScheduler()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # TEMPORARY: Endpoint to inspect vector store (REMOVE IN PRODUCTION)
    @app.route('/api/debug/vector_store_count', methods=['GET'])
    def debug_vector_store_count():
        return jsonify({"document_count": len(global_vector_store.documents)}), 200

    @app.route('/api/debug/vector_store_sample', methods=['GET'])
    def debug_vector_store_sample():
        sample = []
        # Ensure there are documents before trying to sample
        if global_vector_store.documents:
            for i, doc in enumerate(global_vector_store.documents[:5]): # Get first 5 documents
                sample.append({
                    "id": doc['id'],
                    "content_preview": doc['content'][:100] + "...", # Show first 100 chars
                    "metadata": doc['metadata'],
                    "embedding_present": True if doc['embedding'] is not None else False
                })
        return jsonify({"sample_documents": sample, "total_documents": len(global_vector_store.documents)}), 200

    # --- Register Blueprints (Routes) ---
    app.register_blueprint(news_api_bp, url_prefix='/api/news')
    app.register_blueprint(one_piece_api_bp)
    app.register_blueprint(llm_api_bp)

    @app.route('/')
    def home():
        return jsonify({"message": "Clank Clank Mushi API is running!",
                        "current_llm_for_generation": app.config['CURRENT_GENERATION_LLM']})

    @app.route('/api/set_llm', methods=['POST'])
    def set_llm_provider():
        data = request.get_json()
        preferred_llm = data.get('llm_id')

        if preferred_llm in app.config['LLM_PROVIDERS']:
            app.config['CURRENT_GENERATION_LLM'] = preferred_llm
            return jsonify({"status": "success",
                            "message": f"LLM provider set to {app.config['LLM_PROVIDERS'][preferred_llm]}",
                            "current_llm": preferred_llm}), 200
        else:
            return jsonify({"status": "error", "message": "Invalid LLM provider ID"}), 400

    # Initialize scheduler with your Flask app
    scheduler.init_app(app)
    scheduler.start()

    # Schedule the weekly job (or a test job)
    @scheduler.task('interval', id='embed_data_job', weeks=1, start_date='2025-01-01 03:00:00') # Example for weekly
    # @scheduler.task('interval', id='embed_data_job_test', seconds=30) # For quick testing
    def scheduled_embedding_update():
        with app.app_context(): # Jobs need an app context if they interact with Flask resources
            logging.info("--- Starting Scheduled Data Embedding Update ---")
            global_data_embedding_service.embed_all_data() # This will re-fetch and re-embed all data
            total_documents = len(global_vector_store.documents) # Get stats after update
            logging.info(f"--- Completed Scheduled Data Embedding Update. Total documents now: {total_documents} ---")
            # In a persistent setup, you'd query the DB for its count

    # Run initial data embedding immediately on startup if flag file doesn't exist
    with app.app_context():
        # Add a print statement to show the resolved path
        logging.info(f"INFO: Checking for embedding flag file at: {EMBEDDING_FLAG_FILE}")
        if os.path.exists(EMBEDDING_FLAG_FILE):
            logging.info(f"INFO: {EMBEDDING_FLAG_FILE} found. Skipping initial data embedding.")
        else:
            logging.info("INFO: App context ready. Starting initial data embedding...")
            global_data_embedding_service.embed_all_data()
            total_documents = len(global_vector_store.documents)
            logging.info("INFO: Initial Data embedding complete.")

            # Create the flag file to indicate successful initial embedding
            try:
                with open(EMBEDDING_FLAG_FILE, 'w') as f:
                    f.write("initialized")
                logging.info(f"INFO: Created flag file: {EMBEDDING_FLAG_FILE}")
            except IOError as e:
                logging.error(f"ERROR: Could not create flag file {EMBEDDING_FLAG_FILE}: {e}")

        # Initial Information Log for Vector Store (use logging)
        total_documents = len(global_vector_store.documents) # Re-get count in case it was skipped
        logging.info(f"\n--- Initial Vector Store Stats (In-Memory) ---")
        logging.info(f"Total documents embedded: {total_documents}")
        if total_documents > 0:
            op_sagas_count = sum(1 for doc in global_vector_store.documents if doc['metadata'].get('source') == 'one_piece_saga')
            op_chars_count = sum(1 for doc in global_vector_store.documents if doc['metadata'].get('source') == 'one_piece_character')
            op_fruits_count = sum(1 for doc in global_vector_store.documents if doc['metadata'].get('source') == 'one_piece_fruit')
            ann_count = sum(1 for doc in global_vector_store.documents if doc['metadata'].get('source') == 'ann_recent_item')

            logging.info(f"  - One Piece Sagas: {op_sagas_count}")
            logging.info(f"  - One Piece Characters: {op_chars_count}")
            logging.info(f"  - One Piece Fruits: {op_fruits_count}")
            logging.info(f"  - ANN Recent Items: {ann_count}")
            logging.info(f"Embedding dimension (sample): {global_vector_store.documents[0]['embedding'].shape[0] if global_vector_store.documents else 'N/A'}")
        else:
            logging.info("  - No documents embedded.")
        logging.info(f"-----------------------------------------------\n")


    return app

if __name__ == '__main__':
    app = create_app()
    print(f"Running Flask app on {app.config['HOST']}:{app.config['PORT']}")
    print(f"Debug mode: {app.config['DEBUG']}")
    print(f"Current LLM for generation: {app.config['CURRENT_GENERATION_LLM']}")
    # IMPORTANT: use_reloader=False is crucial when using APScheduler to prevent jobs from running twice
    app.run(host=app.config['HOST'], port=app.config['PORT'], debug=app.config['DEBUG'], use_reloader=False)

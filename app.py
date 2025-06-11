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
from routes.shikimori_api_routes import shikimori_api_bp
from routes.suggest_questions import suggest_questions_bp

# Configure logging for APScheduler and your app
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger('apscheduler').setLevel(logging.INFO) # Keep APScheduler logs informative

# Initialize data embedding service here, using the global instances
global_data_embedding_service = DataEmbeddingService(global_vector_store, global_ollama_embedder)

# Initialize scheduler
scheduler = APScheduler()

# Define a wrapper function for the scheduled job to ensure saving after update
# THIS FUNCTION MUST BE DEFINED BEFORE create_app() FOR THE SCHEDULER TO FIND IT
def update_ann_data_and_save_job():
    logging.info("Running scheduled ANN data update job...")
    try:
        # This function only embeds ANN data, assuming other data is static or updated separately
        global_data_embedding_service.embed_ann_data()
        global_vector_store.save() # Save the vector store after updating ANN data
        logging.info("Scheduled ANN data update complete and vector store saved.")
    except Exception as e:
        logging.error(f"Error during scheduled ANN data update: {e}")

def create_app():
    app = Flask(__name__)
    CORS(app) # Enable CORS for all routes

    app.config.from_object(Config)

    # Initialize scheduler with app
    scheduler.init_app(app)
    scheduler.start()
    logging.info("Scheduler started")

    # --- Initial Vector Store Data Loading/Embedding (runs on app startup) ---
    logging.info("-----------------------------------------------")
    logging.info("Mushi Backend Application Startup")
    logging.info("Initializing vector store and embedding data...")

    # global_vector_store.load() is called automatically in globals.py during app startup.
    # We now check if it loaded any documents.
    if not global_vector_store.documents:
        logging.info("Vector store is empty after load attempt. Proceeding with initial data embedding.")
        try:
            global_data_embedding_service.embed_all_data()
            global_vector_store.save() # Save the vector store after embedding
            logging.info("Initial data embedding complete and vector store saved.")
        except Exception as e:
            logging.error(f"Error during initial data embedding: {e}")
            # You might want to add more robust error handling here,
            # e.g., set a flag to prevent serving queries until embedding is successful.
    else:
        logging.info(f"Vector store successfully loaded with {len(global_vector_store.documents)} documents. No re-embedding needed.")

    # Schedule periodic updates for ANN data (and other dynamic data sources)
    if not scheduler.get_job('update_ann_data_and_save'):
        scheduler.add_job(
            id='update_ann_data_and_save',
            func=update_ann_data_and_save_job, # Use the wrapper function
            trigger='interval',
            minutes=Config.EMBEDDING_UPDATE_INTERVAL_MINUTES,
            max_instances=1, # Ensure only one instance of the job runs at a time
            replace_existing=True # Replace if a job with this ID already exists
        )
        logging.info(f"Scheduled ANN data update every {Config.EMBEDDING_UPDATE_INTERVAL_MINUTES} minutes.")

    # Log current vector store stats after initialization/loading
    logging.info("Vector Store Summary (after initialization/load):")
    if global_vector_store.documents:
        # Safely get counts using .get() to avoid KeyError if metadata keys are missing
        op_sagas_count = sum(1 for doc in global_vector_store.documents if doc['metadata'].get('source') == 'one_piece_saga')
        op_chars_count = sum(1 for doc in global_vector_store.documents if doc['metadata'].get('source') == 'one_piece_character')
        op_fruits_count = sum(1 for doc in global_vector_store.documents if doc['metadata'].get('source') == 'one_piece_fruit')
        ann_count = sum(1 for doc in global_vector_store.documents if doc['metadata'].get('source') == 'ann_recent_item')

        logging.info(f"  - One Piece Sagas: {op_sagas_count}")
        logging.info(f"  - One Piece Characters: {op_chars_count}")
        logging.info(f"  - One Piece Fruits: {op_fruits_count}")
        logging.info(f"  - ANN Recent Items: {ann_count}")

        # Safely determine embedding dimension by finding the first valid embedding
        embedding_dimension = 'N/A'
        for doc in global_vector_store.documents:
            if 'embedding' in doc and doc['embedding'] is not None and hasattr(doc['embedding'], 'shape'):
                embedding_dimension = doc['embedding'].shape[0]
                break # Found a valid one, no need to check further
        logging.info(f"Embedding dimension (sample): {embedding_dimension}")
    else:
        logging.info("  - No documents currently in vector store.")
    logging.info(f"-----------------------------------------------\n")
    # --- End of Initial Vector Store Data Loading/Embedding ---


    # Register Blueprints
    app.register_blueprint(news_api_bp)
    app.register_blueprint(one_piece_api_bp)
    app.register_blueprint(llm_api_bp)
    app.register_blueprint(shikimori_api_bp)
    app.register_blueprint(suggest_questions_bp)


    @app.route('/')
    def index():
        return "Mushi Backend is running!", 200

    @app.route('/api/llm/providers', methods=['GET'])
    def get_llm_providers():
        return jsonify(Config.LLM_PROVIDERS), 200

    @app.route('/api/llm/set-provider', methods=['POST'])
    def set_llm_provider():
        data = request.get_json()
        provider_key = data.get('provider')
        if provider_key in Config.LLM_PROVIDERS:
            Config.CURRENT_GENERATION_LLM = provider_key
            logging.info(f"LLM provider set to: {provider_key}")
            return jsonify({"message": f"LLM provider set to {provider_key}"}), 200
        else:
            return jsonify({"error": "Invalid LLM provider"}), 400

    return app

if __name__ == '__main__':
    app = create_app()
    print(f"Running Flask app on {app.config['HOST']}:{app.config['PORT']}")
    print(f"Debug mode: {app.config['DEBUG']}")
    print(f"Current LLM for generation: {app.config['CURRENT_GENERATION_LLM']}")
    # IMPORTANT: use_reloader=False when using APScheduler to prevent jobs from running twice
    app.run(debug=app.config['DEBUG'], host=app.config['HOST'], port=app.config['PORT'], use_reloader=False)

# backend/app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
from config import Config
import os
from apscheduler.schedulers.background import BackgroundScheduler
from flask_apscheduler import APScheduler
import logging

# Import global instances from the new globals.py module
from globals import global_vector_store, global_ollama_embedder, global_clustering_service, global_data_embedding_service # Import global_data_embedding_service

# Import other components
# DataEmbeddingService is now initialized in globals.py

# Import all blueprints from their respective files
from routes.news_api_routes import news_bp as news_api_bp
from routes.one_piece_api_routes import one_piece_api_bp
from routes.llm_api_routes import llm_api_bp
from routes.suggest_questions import suggest_questions_bp
from routes.data_api_routes import data_api_bp # Import the new data API blueprint
from routes.aniwatch_api_routes import aniwatch_api_bp # NEW: Import Aniwatch API blueprint

# Import controllers to initialize them
from controllers.data_controller import DataController # Import the new DataController


# Configure logging for APScheduler and your app
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger('apscheduler').setLevel(logging.INFO) # Keep APScheduler logs informative

# global_data_embedding_service is now initialized in globals.py

# Initialize scheduler
scheduler = APScheduler()

# Define a wrapper function for the scheduled job to ensure saving after update
# THIS FUNCTION MUST BE DEFINED BEFORE create_app() FOR THE SCHEDULER TO FIND IT
def update_ann_data_and_save_job():
    logging.info("Running scheduled ANN data update and save job...")
    # Use the new detailed embedding method
    global_data_embedding_service.embed_ann_details_data(limit=100) # You can adjust the limit here
    global_vector_store.save() # Ensure the vector store is saved after updates
    logging.info("Scheduled ANN data update and save job finished.")

def create_app():
    app = Flask(__name__)
    CORS(app) # Enable CORS for all routes

    app.config.from_object(Config)

    # Initialize APScheduler with your Flask app
    scheduler.init_app(app)
    scheduler.start()

    # Schedule the job to run every 12 hours
    # This job will fetch recent ANN data and embed it, then save the vector store
    # Ensure this is added only once. Using a unique ID prevents duplicate jobs.
    if not scheduler.get_job('update_ann_data_and_save'):
        scheduler.add_job(
            id='update_ann_data_and_save',
            func=update_ann_data_and_save_job,
            trigger='interval',
            hours=12, # Update every 12 hours
            replace_existing=True
        )
        logging.info("Scheduled 'update_ann_data_and_save' job to run every 12 hours.")
    else:
        logging.info("Scheduled job 'update_ann_data_and_save' already exists.")


    # Initial Vector Store Data Loading/Embedding
    # This runs once on app startup to populate the vector store initially
    # If the vector_db.pkl.gz already exists and is loaded, this will just log.
    # Otherwise, it will fetch and embed data.
    logging.info("--- Initial Vector Store Data Loading/Embedding ---")
    if not global_vector_store.documents: # Only embed if store is empty
        logging.info("Vector store is empty. Performing initial data embedding...")
        # Call the embed_all_data method to trigger both One Piece and ANN detailed embedding
        global_data_embedding_service.embed_all_data()
        global_vector_store.save() # Save after initial embedding
        logging.info("Initial data embedding complete and vector store saved.")
    else:
        logging.info(f"Vector store already contains {len(global_vector_store.documents)} documents. Skipping initial embedding.")
    logging.info("--- End of Initial Vector Store Data Loading/Embedding ---")


    # Register Blueprints
    app.register_blueprint(news_api_bp)
    app.register_blueprint(one_piece_api_bp)
    app.register_blueprint(llm_api_bp)

    app.register_blueprint(suggest_questions_bp)
    app.register_blueprint(data_api_bp) # Register the new data API blueprint
    app.register_blueprint(aniwatch_api_bp) # NEW: Register Aniwatch API blueprint

    # Initialize controllers that depend on global services
    # Now pass both clustering_service and data_embedding_service
    DataController.initialize(global_clustering_service, global_data_embedding_service)

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
    print(f"Current LLM for generation: {Config.CURRENT_GENERATION_LLM}")
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)

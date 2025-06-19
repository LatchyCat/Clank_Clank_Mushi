# backend/app.py
import flask
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
import os
import atexit
import logging

# Import services and blueprints
from services.clustering_service import CLUSTER_CACHE_PATH
from globals import global_vector_store
from routes.news_api_routes import news_bp
from routes.one_piece_api_routes import one_piece_api_bp
from routes.llm_api_routes import llm_api_bp
from routes.data_api_routes import data_api_bp
from routes.aniwatch_api_routes import aniwatch_api_bp
from routes.anime_api_routes import anime_api_bp
from controllers.data_controller import DataController
from globals import global_clustering_service, global_data_embedding_service

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

def create_app():
    """
    Main factory function to create and configure the Flask application.
    """
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)

    # Initialize controllers with their required services
    DataController.initialize(global_clustering_service, global_data_embedding_service)

    # Register all API blueprints
    app.register_blueprint(news_bp)
    app.register_blueprint(one_piece_api_bp)
    app.register_blueprint(llm_api_bp)
    app.register_blueprint(data_api_bp)
    app.register_blueprint(aniwatch_api_bp)
    app.register_blueprint(anime_api_bp)

    @app.route('/')
    def index():
        return jsonify({
            "message": "Clank Clank Mushi API is running!",
            "vector_db_documents": len(global_vector_store.documents),
            "current_llm_for_generation": Config.CURRENT_GENERATION_LLM,
            "cluster_cache_exists": os.path.exists(CLUSTER_CACHE_PATH)
        }), 200

    return app

def on_shutdown():
    """
    Ensures that the in-memory vector store is saved to disk when the app shuts down.
    This is useful if any data were to be added during runtime in the future.
    """
    logging.info("Flask app is shutting down. Saving vector store...")
    global_vector_store.save()
    logging.info("Vector store saved successfully. Goodbye, Senpai!")

# Register the shutdown hook
atexit.register(on_shutdown)

if __name__ == '__main__':
    app = create_app()

    # This check ensures the following code only runs ONCE on initial startup,
    # not again when Werkzeug's reloader restarts the process.
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        logging.info("--- Server Startup: Loading Vector Database ---")
        global_vector_store.load() # Attempt to load the pre-built database

        # Check if the necessary database files exist. If not, warn the user.
        if not global_vector_store.documents or not os.path.exists(CLUSTER_CACHE_PATH):
            logging.warning("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            logging.warning("!!! WARNING: Vector DB or Cluster Cache not found.   !!!")
            logging.warning("!!! The application will run, but search and data    !!!")
            logging.warning("!!! insights will not function correctly.           !!!")
            logging.warning("!!!                                                 !!!")
            logging.warning("!!! TO FIX: Stop the server and run this command:   !!!")
            logging.warning("!!! python3 backend/build_database.py               !!!")
            logging.warning("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        else:
            logging.info(f"Successfully loaded {len(global_vector_store.documents)} documents from vector store.")
            logging.info(f"Cluster cache is present at {CLUSTER_CACHE_PATH}.")
        logging.info("--- Load Check Complete ---")

    logging.info(f"🚀 Mushi is taking off! Listening on http://{Config.HOST}:{Config.PORT}")
    app.run(debug=True, host=Config.HOST, port=Config.PORT, use_reloader=True)

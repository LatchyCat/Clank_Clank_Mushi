# backend/app.py
import flask
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
import os
from flask_apscheduler import APScheduler
import logging

from globals import (
    global_vector_store,
    global_data_embedding_service,
    global_clustering_service
)

from routes.news_api_routes import news_bp
from routes.one_piece_api_routes import one_piece_api_bp
from routes.llm_api_routes import llm_api_bp
from routes.data_api_routes import data_api_bp
from routes.aniwatch_api_routes import aniwatch_api_bp
from routes.anime_api_routes import anime_api_bp

from controllers.data_controller import DataController

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
logging.getLogger('apscheduler').setLevel(logging.WARNING) # Keep scheduler logs quiet

def update_data_and_save_job():
    # This function now runs within the app context created by APScheduler
    with flask.current_app.app_context():
        logging.info("SCHEDULER: Starting scheduled data update job...")
        global_data_embedding_service.embed_all_data()
        logging.info("SCHEDULER: Scheduled data update job finished.")

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)

    # Initialize Controllers
    DataController.initialize(global_clustering_service, global_data_embedding_service)

    # Initialize Scheduler
    scheduler = APScheduler()
    scheduler.init_app(app)

    # Add job only if it doesn't exist to prevent duplicates in debug mode
    if not scheduler.get_job('update_data_and_save'):
        scheduler.add_job(
            id='update_data_and_save',
            func=update_data_and_save_job,
            trigger='interval',
            hours=24, # Set to a more reasonable interval like 24 hours
            replace_existing=True
        )
        logging.info("Scheduler job 'update_data_and_save' added to run every 24 hours.")

    scheduler.start()

    # Register Blueprints
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
            "current_llm_for_generation": Config.CURRENT_GENERATION_LLM
        }), 200

    return app

# This block ensures that the initial embedding only runs ONCE when the server starts,
# not every time the reloader triggers.
if __name__ == '__main__':
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        logging.info("--- Initial Data Load Check ---")
        if not os.path.exists(Config.VECTOR_DB_PATH) or os.path.getsize(Config.VECTOR_DB_PATH) < 1024:
            logging.info("Vector store is empty or missing. Performing initial data embedding...")
            # We need to create a temporary app context to run this outside the main app run
            temp_app = Flask(__name__)
            with temp_app.app_context():
                global_data_embedding_service.embed_all_data()
        else:
            global_vector_store.load()
            logging.info(f"Vector store loaded with {len(global_vector_store.documents)} documents. Skipping initial embedding.")
        logging.info("--- Initial Check Complete ---")

    app = create_app()
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT, use_reloader=True)

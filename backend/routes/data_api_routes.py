# backend/routes/data_api_routes.py
from flask import Blueprint, jsonify, request
import logging
from controllers.data_controller import DataController

logger = logging.getLogger(__name__)

data_api_bp = Blueprint('data_api', __name__, url_prefix='/api/data')

@data_api_bp.route('/clusters', methods=['GET'])
def get_clusters():
    n_clusters_str = request.args.get('n_clusters', '5')
    try:
        n_clusters = int(n_clusters_str)
        if n_clusters <= 0:
            return jsonify({"error": "Number of clusters (n_clusters) must be a positive integer."}), 400
    except ValueError:
        return jsonify({"error": "Invalid value for 'n_clusters'. Must be an integer."}), 400

    logger.info(f"API Request: /api/data/clusters with n_clusters={n_clusters}")
    response_data, status_code = DataController.get_clustered_documents(num_clusters=n_clusters)
    return jsonify(response_data), status_code

@data_api_bp.route('/ingest_all_data', methods=['POST'])
def ingest_all_data_route():
    """
    Triggers the ingestion of data from ALL configured sources.
    This will re-populate the vector store based on the logic in DataEmbeddingService.
    """
    logger.info("API Request: /api/data/ingest_all_data")
    response_data, status_code = DataController.ingest_all_data()
    return jsonify(response_data), status_code

@data_api_bp.route('/ingest_anime_api_category_data', methods=['POST'])
def ingest_anime_api_category_data_route():
    """
    Triggers ingestion for specific categories from the anime-api.
    Example: POST /api/data/ingest_anime_api_category_data?categories=action,comedy&limit_per_category=50
    """
    categories_str = request.args.get('categories')
    if not categories_str:
        return jsonify({"error": "Query parameter 'categories' is required."}), 400

    categories = [c.strip() for c in categories_str.split(',')]
    limit_per_category = request.args.get('limit_per_category', 50, type=int)

    if limit_per_category <= 0:
        return jsonify({"error": "Limit per category must be a positive integer."}), 400

    logger.info(f"API Request: Ingesting category data for {categories} with limit {limit_per_category}")
    response_data, status_code = DataController.ingest_anime_api_category_data(
        categories=categories, limit_per_category=limit_per_category
    )
    return jsonify(response_data), status_code

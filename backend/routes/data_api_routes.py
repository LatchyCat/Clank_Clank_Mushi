# backend/routes/data_api_routes.py
from flask import Blueprint, jsonify, request
import logging

# Import the DataController
from controllers.data_controller import DataController

logger = logging.getLogger(__name__)

# Create a Blueprint for data-related API routes
# All routes defined in this blueprint will be prefixed with '/api/data'
data_api_bp = Blueprint('data_api', __name__, url_prefix='/api/data')

@data_api_bp.route('/clusters', methods=['GET'])
def get_clusters():
    """
    API endpoint for retrieving documents with their cluster assignments.
    Allows specifying the number of clusters via a query parameter.
    Example: GET /api/data/clusters?n_clusters=7
    """
    # Get the 'n_clusters' query parameter, default to 5 if not provided
    n_clusters_str = request.args.get('n_clusters', '5')
    try:
        n_clusters = int(n_clusters_str)
        if n_clusters <= 0:
            return jsonify({"error": "Number of clusters (n_clusters) must be a positive integer."}), 400
    except ValueError:
        return jsonify({"error": "Invalid value for 'n_clusters'. Must be an integer."}), 400

    logger.info(f"API Request: /api/data/clusters with n_clusters={n_clusters}")

    # Call the DataController to get the clustered documents
    response_data, status_code = DataController.get_clustered_documents(num_clusters=n_clusters)

    return jsonify(response_data), status_code

@data_api_bp.route('/ingest_ann_data', methods=['POST'])
def ingest_ann_data_route():
    """
    API endpoint to trigger the ingestion of recent ANN data into the vector store.
    Allows specifying the limit of items to process via a query parameter.
    Example: POST /api/data/ingest_ann_data?limit=100
    """
    limit = request.args.get('limit', 100, type=int) # Default to 100 items

    if limit <= 0:
        return jsonify({"error": "Limit must be a positive integer."}), 400

    logger.info(f"API Request: /api/data/ingest_ann_data with limit={limit}")

    response_data, status_code = DataController.ingest_ann_data(limit=limit)
    return jsonify(response_data), status_code

@data_api_bp.route('/ingest_aniwatch_data', methods=['POST'])
def ingest_aniwatch_data_route():
    """
    API endpoint to trigger the ingestion of Aniwatch data into the vector store.
    Allows specifying the limit of items to process and page limit via query parameters.
    Example: POST /api/data/ingest_aniwatch_data?limit=100&page_limit=5
    """
    limit = request.args.get('limit', 100, type=int)
    page_limit = request.args.get('page_limit', 5, type=int)

    if limit <= 0 or page_limit <= 0:
        return jsonify({"error": "Limit and page_limit must be positive integers."}), 400

    logger.info(f"API Request: /api/data/ingest_aniwatch_data with limit={limit}, page_limit={page_limit}")

    response_data, status_code = DataController.ingest_aniwatch_data(limit=limit, page_limit=page_limit)
    return jsonify(response_data), status_code

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

# You can add more data-related endpoints here in the future if needed,
# e.g., for specific data filters, statistical summaries, etc.

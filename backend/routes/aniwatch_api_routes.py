# backend/routes/aniwatch_api_routes.py
from flask import Blueprint, jsonify, request
import logging
from controllers.aniwatch_controller import AniwatchController # Import the AniwatchController class

logger = logging.getLogger(__name__)

# Create a Blueprint for Aniwatch API routes
# All routes defined in this blueprint will be prefixed with '/api/aniwatch'
aniwatch_api_bp = Blueprint('aniwatch_api', __name__, url_prefix='/api/aniwatch')

# Initialize the AniwatchController globally for the blueprint
aniwatch_controller = AniwatchController()

@aniwatch_api_bp.route('/az-list', methods=['GET'])
def get_az_list_route():
    """
    API endpoint to get the A-Z list of anime from Aniwatch.
    Allows specifying sort option and page via query parameters.
    Example: GET /api/aniwatch/az-list?sort=all&page=1
    """
    sort_option = request.args.get('sort', 'all')
    page = request.args.get('page', 1, type=int)

    if page <= 0:
        return jsonify({"error": "Page number must be a positive integer."}), 400

    logger.info(f"API Request: /api/aniwatch/az-list with sort={sort_option}, page={page}")
    data, status_code = aniwatch_controller.get_aniwatch_az_list_data(sort_option=sort_option, page=page)
    return jsonify(data), status_code

@aniwatch_api_bp.route('/info/<string:anime_id>', methods=['GET'])
def get_anime_info_route(anime_id):
    """
    API endpoint to get detailed information for a specific anime from Aniwatch.
    Example: GET /api/aniwatch/info/naruto-677
    """
    logger.info(f"API Request: /api/aniwatch/info/{anime_id}")
    data, status_code = aniwatch_controller.get_aniwatch_anime_details_data(anime_id=anime_id)
    return jsonify(data), status_code

@aniwatch_api_bp.route('/trending', methods=['GET'])
def get_trending_route():
    """
    API endpoint to get trending anime from Aniwatch.
    Example: GET /api/aniwatch/trending
    """
    logger.info("API Request: /api/aniwatch/trending")
    data, status_code = aniwatch_controller.get_aniwatch_trending_anime_data()
    return jsonify(data), status_code

@aniwatch_api_bp.route('/popular', methods=['GET'])
def get_popular_route():
    """
    API endpoint to get popular anime from Aniwatch.
    Example: GET /api/aniwatch/popular
    """
    logger.info("API Request: /api/aniwatch/popular")
    data, status_code = aniwatch_controller.get_aniwatch_popular_anime_data()
    return jsonify(data), status_code

@aniwatch_api_bp.route('/search', methods=['GET'])
def search_anime_route():
    """
    API endpoint to search anime on Aniwatch by keyword.
    Example: GET /api/aniwatch/search?keyword=one%20piece
    """
    keyword = request.args.get('keyword')
    if not keyword:
        return jsonify({"error": "Query parameter 'keyword' is required."}), 400

    logger.info(f"API Request: /api/aniwatch/search with keyword='{keyword}'")
    data, status_code = aniwatch_controller.search_aniwatch_anime_data(keyword=keyword)
    return jsonify(data), status_code

# backend/routes/anime_api_routes.py
from flask import Blueprint, jsonify, request
from globals import global_anime_controller as anime_controller
import logging

logger = logging.getLogger(__name__)

anime_api_bp = Blueprint('anime_api', __name__, url_prefix='/api/anime')

def handle_request(handler, **kwargs):
    """Generic request handler to reduce boilerplate."""
    try:
        data, status_code = handler(**kwargs)
        return jsonify(data), status_code
    except Exception as e:
        logger.error(f"Error in route {request.path}: {e}", exc_info=True)
        return jsonify({"error": "An internal server error occurred"}), 500

@anime_api_bp.route('/home', methods=['GET'])
def get_home_data_route():
    logger.info("API Request: GET /api/anime/home")
    return handle_request(anime_controller.get_home_page_data)

@anime_api_bp.route('/top-ten', methods=['GET'])
def get_top_ten_anime_route():
    logger.info("API Request: GET /api/anime/top-ten")
    return handle_request(anime_controller.get_top_ten_anime_data)

@anime_api_bp.route('/details/<string:anime_id>', methods=['GET'])
def get_anime_details_route(anime_id: str):
    logger.info(f"API Request: GET /api/anime/details/{anime_id}")
    return handle_request(anime_controller.get_anime_details_data, anime_id=anime_id)

@anime_api_bp.route('/episodes/<string:anime_id>', methods=['GET'])
def get_episodes_list_route(anime_id: str):
    logger.info(f"API Request: GET /api/anime/episodes/{anime_id}")
    return handle_request(anime_controller.get_episode_list_data, anime_id=anime_id)

@anime_api_bp.route('/servers/<string:episode_data_id>', methods=['GET'])
def get_available_servers_route(episode_data_id: str):
    logger.info(f"API Request: GET /api/anime/servers/{episode_data_id}")
    return handle_request(anime_controller.get_available_servers_data, episode_data_id=episode_data_id)

@anime_api_bp.route('/stream', methods=['GET'])
def get_streaming_info_route():
    anime_id = request.args.get('animeId')
    episode_data_id = request.args.get('id')
    server_name = request.args.get('server')
    stream_type = request.args.get('type')

    if not all([anime_id, episode_data_id, server_name, stream_type]):
        return jsonify({"error": "Missing 'animeId', 'id', 'server', or 'type' query parameters"}), 400

    logger.info(f"API Request: GET /api/anime/stream with params: id={episode_data_id}, server={server_name}, type={stream_type}, animeId={anime_id}")

    return handle_request(
        anime_controller.get_streaming_info_data,
        anime_id=anime_id,
        episode_data_id=episode_data_id,
        server_name=server_name,
        stream_type=stream_type
    )

@anime_api_bp.route('/search', methods=['GET'])
def search_anime_route():
    filters = request.args.to_dict()
    logger.info(f"API Request: GET /api/anime/search with filters: {filters}")
    return handle_request(anime_controller.search_anime_data, filters=filters)

@anime_api_bp.route('/search-suggestions', methods=['GET'])
def get_search_suggestions_route():
    keyword = request.args.get('keyword')
    if not keyword:
        return jsonify({"error": "Missing 'keyword' query parameter"}), 400
    logger.info(f"API Request: GET /api/anime/search-suggestions?keyword={keyword}")
    return handle_request(anime_controller.get_search_suggestions_data, keyword=keyword)

@anime_api_bp.route('/qtip/<string:anime_id>', methods=['GET'])
def get_qtip_info_route(anime_id: str):
    logger.info(f"API Request: GET /api/anime/qtip/{anime_id}")
    return handle_request(anime_controller.get_qtip_info_data, anime_id=anime_id)

@anime_api_bp.route('/category/<path:category>', methods=['GET'])
def get_category_route(category):
    page = request.args.get('page', 1, type=int)
    logger.info(f"API Request: GET /api/anime/category/{category}?page={page}")
    return handle_request(anime_controller.get_anime_by_category_data, category=category, page=page)

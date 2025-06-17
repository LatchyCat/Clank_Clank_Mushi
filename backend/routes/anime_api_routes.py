# backend/routes/anime_api_routes.py
from flask import Blueprint, jsonify, request
from controllers.anime_controller import AnimeController
import logging

logger = logging.getLogger(__name__)

anime_api_bp = Blueprint('anime_api', __name__, url_prefix='/api/anime')
anime_controller = AnimeController()

@anime_api_bp.route('/search-suggestions', methods=['GET'])
def get_search_suggestions_route():
    keyword = request.args.get('keyword')
    if not keyword:
        return jsonify({"error": "Missing 'keyword' query parameter"}), 400
    logger.info(f"API Request: /api/anime/search-suggestions with keyword='{keyword}'")
    data, status_code = anime_controller.get_search_suggestions_data(keyword)
    return jsonify(data), status_code

@anime_api_bp.route('/proxy-stream', methods=['GET'])
def proxy_stream_route():
    video_url = request.args.get('url')
    referer = request.args.get('referer')
    if not video_url:
        return jsonify({"error": "Missing 'url' query parameter"}), 400
    logger.info(f"API Request: /api/anime/proxy-stream for URL: {video_url} with Referer: {referer}")
    return anime_controller.proxy_video_stream(video_url, referer=referer)

@anime_api_bp.route('/home', methods=['GET'])
def get_home_data_route():
    logger.info("API Request: /api/anime/home")
    data, status_code = anime_controller.get_home_page_data()
    return jsonify(data), status_code

# FIX: Add the new route for top searches
@anime_api_bp.route('/top-search', methods=['GET'])
def get_top_search_route():
    logger.info("API Request: /api/anime/top-search")
    data, status_code = anime_controller.get_top_search_anime_data()
    return jsonify(data), status_code

@anime_api_bp.route('/top-ten', methods=['GET'])
def get_top_ten_anime_route():
    logger.info("API Request: /api/anime/top-ten")
    data, status_code = anime_controller.get_top_ten_anime_data()
    return jsonify(data), status_code

@anime_api_bp.route('/search', methods=['GET'])
def search_anime_route():
    query = request.args.get('q', default='', type=str)
    page = request.args.get('page', default=1, type=int)
    logger.info(f"API Request: /api/anime/search with query='{query}', page={page}")
    data, status_code = anime_controller.search_anime_data(query, page)
    return jsonify(data), status_code

@anime_api_bp.route('/category/<path:category_slug>', methods=['GET'])
def get_anime_by_category_route(category_slug: str):
    page = request.args.get('page', default=1, type=int)
    logger.info(f"API Request: /api/anime/category/{category_slug} with page={page}")
    data, status_code = anime_controller.get_anime_by_category_data(category_slug, page)
    return jsonify(data), status_code

@anime_api_bp.route('/details/<string:anime_id>', methods=['GET'])
def get_anime_details_route(anime_id: str):
    logger.info(f"API Request: /api/anime/details/{anime_id}")
    data, status_code = anime_controller.get_anime_details_data(anime_id)
    return jsonify(data), status_code

@anime_api_bp.route('/servers/<string:anime_id>', methods=['GET'])
def get_available_servers_route(anime_id: str):
    episode_data_id = request.args.get('ep')
    if not episode_data_id:
        return jsonify({"error": "Missing 'ep' query parameter for episode data ID"}), 400
    logger.info(f"API Request: /api/anime/servers/{anime_id} with episode_data_id={episode_data_id}")
    data, status_code = anime_controller.get_available_servers_data(anime_id, episode_data_id)
    return jsonify(data), status_code

@anime_api_bp.route('/stream', methods=['GET'])
def get_streaming_info_route():
    episode_id = request.args.get('id')
    server_id = request.args.get('server')
    stream_type = request.args.get('type', default='sub', type=str)
    if not episode_id or not server_id:
        return jsonify({"error": "Missing 'id' or 'server' query parameters"}), 400
    logger.info(f"API Request: /api/anime/stream with episode_id={episode_id}, server_id={server_id}, stream_type={stream_type}")
    data, status_code = anime_controller.get_streaming_info_data(episode_id, server_id, stream_type)
    return jsonify(data), status_code

@anime_api_bp.route('/character/<string:character_id>', methods=['GET'])
def get_character_details_route(character_id: str):
    logger.info(f"API Request: /api/anime/character/{character_id}")
    data, status_code = anime_controller.get_character_details_data(character_id)
    return jsonify(data), status_code

@anime_api_bp.route('/actors/<string:actor_id>', methods=['GET'])
def get_voice_actor_details_route(actor_id: str):
    logger.info(f"API Request: /api/anime/actors/{actor_id}")
    data, status_code = anime_controller.get_voice_actor_details_data(actor_id)
    return jsonify(data), status_code

@anime_api_bp.route('/qtip/<int:qtip_id>', methods=['GET'])
def get_qtip_info_route(qtip_id: int):
    logger.info(f"API Request: /api/anime/qtip/{qtip_id}")
    data, status_code = anime_controller.get_qtip_info_data(qtip_id)
    return jsonify(data), status_code

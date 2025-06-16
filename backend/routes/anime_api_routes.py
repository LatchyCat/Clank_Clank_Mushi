# backend/routes/anime_api_routes.py
from flask import Blueprint, jsonify, request
from controllers.anime_controller import AnimeController
import logging

logger = logging.getLogger(__name__)

# Create a Blueprint for the new anime-api routes
# All routes in this blueprint will be prefixed with '/api/anime'
anime_api_bp = Blueprint('anime_api', __name__, url_prefix='/api/anime')

# Initialize the controller
anime_controller = AnimeController()

@anime_api_bp.route('/home', methods=['GET'])
def get_home_data_route():
    """
    API endpoint for fetching home page information from the new anime-api.
    Corresponds to GET /api/ from the Node.js API.
    Example: GET /api/anime/home
    """
    logger.info("API Request: /api/anime/home")
    data, status_code = anime_controller.get_home_page_data()
    return jsonify(data), status_code

@anime_api_bp.route('/top-ten', methods=['GET'])
def get_top_ten_anime_route():
    """
    API endpoint for fetching top 10 anime information from the new anime-api.
    Corresponds to GET /api/top-ten from the Node.js API.
    Example: GET /api/anime/top-ten
    """
    logger.info("API Request: /api/anime/top-ten")
    data, status_code = anime_controller.get_top_ten_anime_data()
    return jsonify(data), status_code

@anime_api_bp.route('/search', methods=['GET'])
def search_anime_route():
    """
    API endpoint for searching anime from the anime-api.
    Example: GET /api/anime/search?q=one%20piece&page=1
    """
    # --- START FIX ---
    # Revert to expecting 'q' as the primary search parameter
    query = request.args.get('q', default='', type=str)
    page = request.args.get('page', default=1, type=int)
    # --- END FIX ---

    logger.info(f"API Request: /api/anime/search with query='{query}', page={page}")
    data, status_code = anime_controller.search_anime_data(query, page)
    return jsonify(data), status_code

@anime_api_bp.route('/category/<path:category_slug>', methods=['GET'])
def get_anime_by_category_route(category_slug: str):
    """
    API endpoint for fetching anime by category from the new anime-api.
    Corresponds to GET /api/category/{category_slug}?page={page} from the Node.js API.
    Example: GET /api/anime/category/genre/action?page=1
    """
    page = request.args.get('page', default=1, type=int)
    logger.info(f"API Request: /api/anime/category/{category_slug} with page={page}")
    data, status_code = anime_controller.get_anime_by_category_data(category_slug, page)
    return jsonify(data), status_code

@anime_api_bp.route('/details/<string:anime_id>', methods=['GET'])
def get_anime_details_route(anime_id: str):
    """
    API endpoint for fetching comprehensive anime details.
    This endpoint aggregates data from multiple Node.js API endpoints.
    Corresponds to various GET /api/info, /api/episode, /api/characters, etc., from the Node.js API.
    Example: GET /api/anime/details/one-piece-21
    """
    logger.info(f"API Request: /api/anime/details/{anime_id}")
    # FIX: Corrected method name from get_anime_details to get_anime_details_data
    data, status_code = anime_controller.get_anime_details_data(anime_id)
    return jsonify(data), status_code

@anime_api_bp.route('/episodes/<string:anime_id>', methods=['GET'])
def get_episode_list_route(anime_id: str):
    """
    API endpoint for fetching episode list for a specific anime.
    Corresponds to GET /api/episode/{id} from the Node.js API.
    Example: GET /api/anime/episodes/one-piece-21
    """
    logger.info(f"API Request: /api/anime/episodes/{anime_id}")
    data, status_code = anime_controller.get_episode_list_data(anime_id)
    return jsonify(data), status_code

@anime_api_bp.route('/servers/<string:anime_id>', methods=['GET'])
def get_available_servers_route(anime_id: str):
    """
    API endpoint for fetching available servers for an anime episode.
    Corresponds to GET /api/servers/{id}?ep={number} from the Node.js API.
    Example: GET /api/anime/servers/demon-slayer-kimetsu-no-yaiba-hashira-training-arc-19107?ep=124260
    """
    episode_data_id = request.args.get('ep', default=None, type=str) # Changed to 'ep' for episode data ID
    logger.info(f"API Request: /api/anime/servers/{anime_id} with episode_data_id={episode_data_id}")
    data, status_code = anime_controller.get_available_servers_data(anime_id, episode_data_id)
    return jsonify(data), status_code

@anime_api_bp.route('/streaming-info/<string:anime_id>', methods=['GET'])
def get_streaming_info_route(anime_id: str):
    """
    API endpoint for fetching streaming information for a selected server and episode type.
    Corresponds to GET /api/servers/{id}?server={server_id}&type={type} from the Node.js API.
    Example: GET /api/anime/streaming-info/demon-slayer-kimetsu-no-yaiba-hashira-training-arc-19107?server=4&type=sub
    """
    server_id = request.args.get('server', default=None, type=str)
    stream_type = request.args.get('type', default='sub', type=str) # Default to 'sub'
    logger.info(f"API Request: /api/anime/streaming-info/{anime_id} with server_id={server_id}, stream_type={stream_type}")
    data, status_code = anime_controller.get_streaming_info_data(anime_id, server_id, stream_type)
    return jsonify(data), status_code


@anime_api_bp.route('/characters/<string:anime_id>', methods=['GET'])
def get_characters_list_route(anime_id: str):
    """
    API endpoint for fetching character list for a specific anime.
    Corresponds to GET /api/characters/{id}?page={page} from the Node.js API.
    Example: GET /api/anime/characters/one-piece-21
    """
    page = request.args.get('page', default=1, type=int)
    logger.info(f"API Request: /api/anime/characters/{anime_id} with page={page}")
    data, status_code = anime_controller.get_characters_list_data(anime_id, page)
    return jsonify(data), status_code

@anime_api_bp.route('/related/<string:anime_id>', methods=['GET'])
def get_related_anime_route(anime_id: str):
    """
    API endpoint for fetching related anime for a specific anime.
    Corresponds to GET /api/related/{id} from the Node.js API.
    Example: GET /api/anime/related/one-piece-21
    """
    logger.info(f"API Request: /api/anime/related/{anime_id}")
    data, status_code = anime_controller.get_related_anime_data(anime_id)
    return jsonify(data), status_code

@anime_api_bp.route('/recommended/<string:anime_id>', methods=['GET'])
def get_recommended_anime_route(anime_id: str):
    """
    API endpoint for fetching recommended anime for a specific anime.
    Corresponds to GET /api/recommendations/{id} from the Node.js API.
    Example: GET /api/anime/recommended/one-piece-21
    """
    logger.info(f"API Request: /api/anime/recommended/{anime_id}")
    data, status_code = anime_controller.get_recommended_anime_data(anime_id)
    return jsonify(data), status_code

@anime_api_bp.route('/character/<string:character_id>', methods=['GET'])
def get_character_details_route(character_id: str):
    """
    API endpoint for fetching details for a specific character.
    Corresponds to GET /api/character/{character-id} from the Node.js API.
    Example: GET /api/anime/character/asta-340
    """
    logger.info(f"API Request: /api/anime/character/{character_id}")
    data, status_code = anime_controller.get_character_details_data(character_id)
    return jsonify(data), status_code

@anime_api_bp.route('/actors/<string:actor_id>', methods=['GET'])
def get_voice_actor_details_route(actor_id: str):
    """
    API endpoint for fetching details for a specific voice actor.
    Corresponds to GET /api/actors/{voice-actor-id} from the Node.js API.
    Example: GET /api/anime/actors/gakuto-kajiwara-534
    """
    logger.info(f"API Request: /api/anime/actors/{actor_id}")
    data, status_code = anime_controller.get_voice_actor_details_data(actor_id)
    return jsonify(data), status_code

@anime_api_bp.route('/qtip/<int:qtip_id>', methods=['GET'])
def get_qtip_info_route(qtip_id: int):
    """
    API endpoint for fetching Qtip information for a specific anime.
    Corresponds to GET /api/qtip/{id}.
    """
    logger.info(f"API Request: /api/anime/qtip/{qtip_id}")
    data, status_code = anime_controller.get_qtip_info_data(qtip_id)
    return jsonify(data), status_code

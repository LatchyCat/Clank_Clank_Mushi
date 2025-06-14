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

@anime_api_bp.route('/top-search', methods=['GET'])
def get_top_search_route():
    """
    API endpoint for fetching top search information from the new anime-api.
    Corresponds to GET /api/top-search from the Node.js API.
    Example: GET /api/anime/top-search
    """
    logger.info("API Request: /api/anime/top-search")
    data, status_code = anime_controller.get_top_search_data()
    return jsonify(data), status_code

@anime_api_bp.route('/info/<string:anime_id>', methods=['GET'])
def get_anime_info_route(anime_id: str):
    """
    API endpoint for fetching detailed information for a specified anime from the new anime-api.
    Corresponds to GET /api/info?id={string} from the Node.js API.
    Example: GET /api/anime/info/yami-shibai-9-17879
    """
    logger.info(f"API Request: /api/anime/info/{anime_id}")
    data, status_code = anime_controller.get_anime_details(anime_id)
    return jsonify(data), status_code

@anime_api_bp.route('/random', methods=['GET'])
def get_random_anime_route():
    """
    API endpoint for fetching random anime information from the new anime-api.
    Corresponds to GET /api/random from the Node.js API.
    Example: GET /api/anime/random
    """
    logger.info("API Request: /api/anime/random")
    data, status_code = anime_controller.get_random_anime_data()
    return jsonify(data), status_code

@anime_api_bp.route('/category/<string:category>', methods=['GET'])
def get_category_route(category: str):
    """
    API endpoint for fetching anime lists by category from the new anime-api.
    Allows specifying the page number via a query parameter.
    Corresponds to GET /api/<category>?page={number} from the Node.js API.
    Example: GET /api/anime/category/most-popular?page=1
    """
    page = request.args.get('page', 1, type=int)
    if page <= 0:
        return jsonify({"error": "Page number must be a positive integer."}), 400

    logger.info(f"API Request: /api/anime/category/{category} with page={page}")
    data, status_code = anime_controller.get_category_data(category, page)
    return jsonify(data), status_code

@anime_api_bp.route('/producer/<string:producer>', methods=['GET'])
def get_producer_anime_route(producer: str):
    """
    API endpoint for fetching anime lists by producer/studio from the new anime-api.
    Allows specifying the page number via a query parameter.
    Corresponds to GET /api/producer/{string}?page={number} from the Node.js API.
    Example: GET /api/anime/producer/ufotable?page=1
    """
    page = request.args.get('page', 1, type=int)
    if page <= 0:
        return jsonify({"error": "Page number must be a positive integer."}), 400

    logger.info(f"API Request: /api/anime/producer/{producer} with page={page}")
    data, status_code = anime_controller.get_producer_studio_anime_data(producer, page)
    return jsonify(data), status_code

@anime_api_bp.route('/search', methods=['GET'])
def search_anime_route():
    """
    API endpoint for searching anime by keyword from the new anime-api.
    Corresponds to GET /api/search?keyword={string} from the Node.js API.
    Example: GET /api/anime/search?keyword=one%20punch%20man
    """
    keyword = request.args.get('keyword')
    if not keyword:
        return jsonify({"error": "Query parameter 'keyword' is required."}), 400

    logger.info(f"API Request: /api/anime/search with keyword='{keyword}'")
    data, status_code = anime_controller.search_anime_data(keyword)
    return jsonify(data), status_code

@anime_api_bp.route('/search/suggest', methods=['GET'])
def get_search_suggestions_route():
    """
    API endpoint for fetching search suggestions for a keyword from the new anime-api.
    Corresponds to GET /api/search/suggest?keyword={string} from the Node.js API.
    Example: GET /api/anime/search/suggest?keyword=demon
    """
    keyword = request.args.get('keyword')
    if not keyword:
        return jsonify({"error": "Query parameter 'keyword' is required."}), 400

    logger.info(f"API Request: /api/anime/search/suggest with keyword='{keyword}'")
    data, status_code = anime_controller.get_anime_search_suggestions(keyword)
    return jsonify(data), status_code

@anime_api_bp.route('/filter', methods=['GET'])
def filter_anime_route():
    """
    API endpoint for filtering anime based on various criteria.
    Corresponds to GET /api/filter from the Node.js API.
    Example: GET /api/anime/filter?type=2&status=1&rated=5&page=1
    """
    # Extract all possible filter parameters
    filter_params = {
        'type': request.args.get('type'),
        'status': request.args.get('status'),
        'rated': request.args.get('rated'),
        'score': request.args.get('score'),
        'season': request.args.get('season'),
        'language': request.args.get('language'),
        'genres': request.args.get('genres'),
        'sort': request.args.get('sort'),
        'page': request.args.get('page'),
        'sy': request.args.get('sy'), # Start Year
        'sm': request.args.get('sm'), # Start Month
        'sd': request.args.get('sd'), # Start Day
        'ey': request.args.get('ey'), # End Year
        'em': request.args.get('em'), # End Month
        'ed': request.args.get('ed'), # End Day
        'keyword': request.args.get('keyword')
    }
    # Remove None values to only pass parameters that were actually provided
    filter_params = {k: v for k, v in filter_params.items() if v is not None}

    # Type conversion for numerical parameters
    for key in ['page', 'score', 'sy', 'sm', 'sd', 'ey', 'em', 'ed']:
        if key in filter_params:
            try:
                filter_params[key] = int(filter_params[key])
                if filter_params[key] <= 0 and key == 'page':
                    return jsonify({"error": "Page number must be a positive integer."}), 400
            except ValueError:
                return jsonify({"error": f"Invalid value for '{key}'. Must be an integer."}), 400

    logger.info(f"API Request: /api/anime/filter with params: {filter_params}")
    data, status_code = anime_controller.filter_anime_data(filter_params)
    return jsonify(data), status_code

@anime_api_bp.route('/episodes/<string:anime_id>', methods=['GET'])
def get_anime_episodes_route(anime_id: str):
    """
    API endpoint for fetching the episode list for a specific anime.
    Corresponds to GET /api/episodes/{anime-id} from the Node.js API.
    Example: GET /api/anime/episodes/one-piece-100
    """
    logger.info(f"API Request: /api/anime/episodes/{anime_id}")
    data, status_code = anime_controller.get_anime_episode_list(anime_id)
    return jsonify(data), status_code

@anime_api_bp.route('/schedule', methods=['GET'])
def get_upcoming_schedule_route():
    """
    API endpoint for fetching the schedule of upcoming anime for a specific date.
    Corresponds to GET /api/schedule?date={string} from the Node.js API.
    Example: GET /api/anime/schedule?date=2024-09-23
    """
    date = request.args.get('date')
    if not date:
        return jsonify({"error": "Query parameter 'date' is required (YYYY-MM-DD format)."}), 400

    # Basic date format validation (can be more robust if needed)
    try:
        from datetime import datetime
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    logger.info(f"API Request: /api/anime/schedule with date='{date}'")
    data, status_code = anime_controller.get_upcoming_schedule_data(date)
    return jsonify(data), status_code

@anime_api_bp.route('/schedule/<string:anime_id>', methods=['GET'])
def get_next_episode_schedule_route(anime_id: str):
    """
    API endpoint for fetching the schedule of the next episode for a specific anime.
    Corresponds to GET /api/schedule/{anime-id} from the Node.js API.
    Example: GET /api/anime/schedule/one-piece-100
    """
    logger.info(f"API Request: /api/anime/schedule/{anime_id}")
    data, status_code = anime_controller.get_next_episode_schedule_data(anime_id)
    return jsonify(data), status_code

@anime_api_bp.route('/character/list/<string:anime_id>', methods=['GET'])
def get_characters_list_route(anime_id: str):
    """
    API endpoint for fetching the list of characters for a specific anime.
    Corresponds to GET /api/character/list/{anime-id} from the Node.js API.
    Example: GET /api/anime/character/list/one-piece-100
    """
    logger.info(f"API Request: /api/anime/character/list/{anime_id}")
    data, status_code = anime_controller.get_characters_data(anime_id)
    return jsonify(data), status_code

@anime_api_bp.route('/stream', methods=['GET'])
def get_streaming_info_route():
    """
    API endpoint for fetching streaming information for an anime episode.
    Corresponds to GET /api/stream?id={string}&server={string}&type={string} from the Node.js API.
    Example: GET /api/anime/stream?id=frieren-beyond-journeys-end-18542?ep=107257&server=hd-1&type=sub
    """
    anime_id = request.args.get('id')
    server = request.args.get('server')
    stream_type = request.args.get('type')

    if not anime_id or not server or not stream_type:
        return jsonify({"error": "Query parameters 'id', 'server', and 'type' are required."}), 400

    logger.info(f"API Request: /api/anime/stream with id='{anime_id}', server='{server}', type='{stream_type}'")
    data, status_code = anime_controller.get_streaming_data(anime_id, server, stream_type)
    return jsonify(data), status_code

@anime_api_bp.route('/servers/<string:anime_id>', methods=['GET'])
def get_available_servers_route(anime_id: str):
    """
    API endpoint for fetching available servers for an anime episode.
    Corresponds to GET /api/servers/{id}?ep={number} from the Node.js API.
    Example: GET /api/anime/servers/demon-slayer-kimetsu-no-yaiba-hashira-training-arc-19107?ep=124260
    """
    episode_id = request.args.get('ep') # Optional episode ID
    logger.info(f"API Request: /api/anime/servers/{anime_id} with episode ID: {episode_id}")
    data, status_code = anime_controller.get_available_servers_data(anime_id, episode_id)
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
    Corresponds to GET /api/qtip/{id} from the Node.js API.
    Example: GET /api/anime/qtip/3365
    """
    logger.info(f"API Request: /api/anime/qtip/{qtip_id}")
    data, status_code = anime_controller.get_qtip_data(qtip_id)
    return jsonify(data), status_code


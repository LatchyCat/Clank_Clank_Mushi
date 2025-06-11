# backend/routes/shikimori_api_routes.py
from flask import Blueprint, jsonify, request
from controllers.shikimori_controller import ShikimoriController

# Create a Blueprint for Shikimori-related API routes
shikimori_api_bp = Blueprint('shikimori_api', __name__, url_prefix='/api/shikimori')

@shikimori_api_bp.route('/anime/search', methods=['GET'])
def search_shikimori_anime():
    """
    API endpoint to search for anime.
    Example: GET /api/shikimori/anime/search?q=Fate/Zero&limit=5
    """
    query = request.args.get('q')
    limit = request.args.get('limit', type=int, default=10)
    if not query:
        return jsonify({"error": "Query parameter 'q' is required."}), 400

    # CORRECTED: Changed search_anime_data to search_anime_data
    animes, status_code = ShikimoriController.search_anime_data(query, limit)
    return jsonify(animes), status_code

@shikimori_api_bp.route('/anime/<int:anime_id>', methods=['GET'])
def get_shikimori_anime_details(anime_id):
    """
    API endpoint to get details for a specific anime by ID.
    Example: GET /api/shikimori/anime/10049
    """
    details, status_code = ShikimoriController.get_anime_details_data(anime_id)
    return jsonify(details), status_code

@shikimori_api_bp.route('/anime/recent', methods=['GET'])
def get_shikimori_recent_animes():
    """
    API endpoint to get a list of recent anime.
    Example: GET /api/shikimori/anime/recent?limit=5
    """
    limit = request.args.get('limit', type=int, default=5)
    recent_animes, status_code = ShikimoriController.get_recent_animes_data(limit)
    return jsonify(recent_animes), status_code

@shikimori_api_bp.route('/manga/search', methods=['GET'])
def search_shikimori_manga():
    """
    API endpoint to search for manga.
    Example: GET /api/shikimori/manga/search?q=Berserk&limit=5
    """
    query = request.args.get('q')
    limit = request.args.get('limit', type=int, default=10)
    if not query:
        return jsonify({"error": "Query parameter 'q' is required."}), 400

    # CORRECTED: Changed search_manga_data to search_manga_data
    mangas, status_code = ShikimoriController.search_manga_data(query, limit)
    return jsonify(mangas), status_code

@shikimori_api_bp.route('/manga/recent', methods=['GET'])
def get_shikimori_recent_mangas():
    """
    API endpoint to get a list of recent manga.
    Example: GET /api/shikimori/manga/recent?limit=5
    """
    limit = request.args.get('limit', type=int, default=5)
    recent_mangas, status_code = ShikimoriController.get_recent_mangas_data(limit)
    return jsonify(recent_mangas), status_code

@shikimori_api_bp.route('/characters/search', methods=['GET'])
def search_shikimori_characters():
    """
    API endpoint to search for characters.
    Example: GET /api/shikimori/characters/search?q=Eren%20Yeager&limit=2
    """
    query = request.args.get('q')
    limit = request.args.get('limit', type=int, default=10)
    if not query:
        return jsonify({"error": "Query parameter 'q' is required."}), 400

    characters, status_code = ShikimoriController.search_characters_data(query, limit)
    return jsonify(characters), status_code

@shikimori_api_bp.route('/characters/<int:character_id>', methods=['GET'])
def get_shikimori_character_details(character_id):
    """
    API endpoint to get details for a specific character by ID.
    Example: GET /api/shikimori/characters/88879
    """
    details, status_code = ShikimoriController.get_character_details_data(character_id)
    return jsonify(details), status_code

@shikimori_api_bp.route('/people/search', methods=['GET'])
def search_shikimori_people():
    """
    API endpoint to search for people.
    Example: GET /api/shikimori/people/search?q=Hiroyuki%20Sawano&limit=2
    """
    query = request.args.get('q')
    limit = request.args.get('limit', type=int, default=10)
    if not query:
        return jsonify({"error": "Query parameter 'q' is required."}), 400

    people, status_code = ShikimoriController.search_people_data(query, limit)
    return jsonify(people), status_code

@shikimori_api_bp.route('/people/<int:person_id>', methods=['GET'])
def get_shikimori_person_details(person_id):
    """
    API endpoint to get details for a specific person by ID.
    Example: GET /api/shikimori/people/10079
    """
    details, status_code = ShikimoriController.get_person_details_data(person_id)
    return jsonify(details), status_code

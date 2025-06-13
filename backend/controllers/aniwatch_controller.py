# backend/controllers/aniwatch_controller.py
from flask import Blueprint, jsonify, request
from services.aniwatch_api_service import AniwatchAPIService
import logging

logger = logging.getLogger(__name__)

# Create a Blueprint for Aniwatch-related API routes
aniwatch_api_bp = Blueprint('aniwatch_api', __name__, url_prefix='/api/aniwatch')

class AniwatchController:
    """
    Controller for handling Aniwatch (hianimez.to) data.
    Interacts with the AniwatchAPIService and prepares data for API routes.
    """
    def __init__(self):
        self.aniwatch_service = AniwatchAPIService()

    def get_aniwatch_az_list_data(self, sort_option: str = "all", page: int = 1):
        """
        Fetches and formats the A-Z list of anime.
        """
        logger.debug(f"AniwatchController: Fetching A-Z list for sort_option='{sort_option}', page={page}")
        az_list_data, status_code = self.aniwatch_service.get_az_list(sort_option, page)

        if status_code != 200 or not az_list_data:
            return az_list_data, status_code # Propagate error

        formatted_animes = []
        for anime in az_list_data.get("animes", []):
            formatted_animes.append({
                "id": anime.get("id"),
                "name": anime.get("name"),
                "japanese_name": anime.get("jname"),
                "poster_url": anime.get("poster"),
                "duration": anime.get("duration"),
                "type": anime.get("type"),
                "rating": anime.get("rating"),
                "episodes": anime.get("episodes") # Sub and Dub counts
            })

        return {
            "sort_option": az_list_data.get("sortOption"),
            "animes": formatted_animes,
            "total_pages": az_list_data.get("totalPages"),
            "current_page": az_list_data.get("currentPage"),
            "has_next_page": az_list_data.get("hasNextPage")
        }, status_code

    def get_aniwatch_qtip_info_data(self, anime_id: str):
        """
        Fetches and formats 'qtip' information for a specific anime ID.
        """
        logger.debug(f"AniwatchController: Getting qtip info for anime ID: {anime_id}")
        qtip_data, status_code = self.aniwatch_service.get_anime_qtip_info(anime_id)

        if status_code != 200 or not qtip_data:
            return qtip_data, status_code # Propagate error

        formatted_qtip = {
            "id": qtip_data.get("id"),
            "name": qtip_data.get("name"),
            "japanese_name": qtip_data.get("jname"),
            "mal_score": qtip_data.get("malscore"),
            "quality": qtip_data.get("quality"),
            "episodes": qtip_data.get("episodes"),
            "type": qtip_data.get("type"),
            "description": qtip_data.get("description"),
            "synonyms": qtip_data.get("synonyms"),
            "aired": qtip_data.get("aired"),
            "status": qtip_data.get("status"),
            "genres": qtip_data.get("genres", [])
        }
        return formatted_qtip, status_code

    def get_aniwatch_full_anime_details_data(self, anime_id: str):
        """
        Fetches and formats detailed 'about info' (full details) for a specific anime ID.
        Corresponds to /api/v2/hianime/anime/{animeId}
        """
        logger.debug(f"AniwatchController: Getting full details for anime ID: {anime_id}")
        full_details_data, status_code = self.aniwatch_service.get_anime_details_full_info(anime_id)

        if status_code != 200 or not full_details_data:
            return full_details_data, status_code # Propagate error

        main_info = full_details_data.get("main_info", {})

        formatted_details = {
            "id": main_info.get("id"),
            "name": main_info.get("name"),
            "poster_url": main_info.get("poster"),
            "description": main_info.get("description"),
            "rating": main_info.get("stats", {}).get("rating"),
            "quality": main_info.get("stats", {}).get("quality"),
            "episodes": main_info.get("stats", {}).get("episodes"),
            "type": main_info.get("stats", {}).get("type"),
            "duration": main_info.get("stats", {}).get("duration"),
            "promotional_videos": main_info.get("promotionalVideos", []),
            "character_voice_actors": main_info.get("characterVoiceActor", []),
            "aired": main_info.get("aired"),
            "genres": main_info.get("genres", []),
            "status": main_info.get("status"),
            "studios": main_info.get("studios"),
            "other_info": main_info.get("otherInfo", []),
            "most_popular_animes_section": full_details_data.get("mostPopularAnimes", []),
            "recommended_animes_section": full_details_data.get("recommendedAnimes", []),
            "related_animes_section": full_details_data.get("relatedAnimes", []),
            "seasons_section": full_details_data.get("seasons", [])
        }
        return formatted_details, status_code

    def get_aniwatch_home_page_data(self):
        """
        Fetches and formats the Aniwatch home page data.
        """
        logger.debug("AniwatchController: Fetching home page data")
        home_data, status_code = self.aniwatch_service.get_anime_home_page()

        if status_code != 200 or not home_data:
            return home_data, status_code

        # Helper to format common anime list structure, ensuring all possible fields are captured
        def format_anime_list(anime_list):
            formatted = []
            for anime in anime_list:
                formatted.append({
                    "id": anime.get("id"),
                    "name": anime.get("name"),
                    "poster_url": anime.get("poster"),
                    "type": anime.get("type"),
                    "episodes": anime.get("episodes"), # Contains sub/dub counts
                    "japanese_name": anime.get("jname"),
                    "description": anime.get("description"), # From spotlightAnimes
                    "rank": anime.get("rank"), # From top10, trending
                    "duration": anime.get("duration"), # From topUpcoming
                    "rating": anime.get("rating"), # From topUpcoming
                    "other_info": anime.get("otherInfo", []) # From spotlightAnimes
                })
            return formatted

        formatted_home_data = {
            "genres": home_data.get("genres", []),
            "latest_episode_animes": format_anime_list(home_data.get("latestEpisodeAnimes", [])),
            "spotlight_animes": format_anime_list(home_data.get("spotlightAnimes", [])),
            "top10_animes": {
                "today": format_anime_list(home_data.get("top10Animes", {}).get("today", [])),
                "week": format_anime_list(home_data.get("top10Animes", {}).get("week", [])),
                "month": format_anime_list(home_data.get("top10Animes", {}).get("month", []))
            },
            "top_airing_animes": format_anime_list(home_data.get("topAiringAnimes", [])),
            "top_upcoming_animes": format_anime_list(home_data.get("topUpcomingAnimes", [])),
            "trending_animes": format_anime_list(home_data.get("trendingAnimes", [])),
            "most_popular_animes": format_anime_list(home_data.get("mostPopularAnimes", [])),
            "most_favorite_animes": format_anime_list(home_data.get("mostFavoriteAnimes", [])),
            "latest_completed_animes": format_anime_list(home_data.get("latestCompletedAnimes", []))
        }
        return formatted_home_data, status_code

    def search_aniwatch_anime_data(
        self,
        query: str,
        page: int = 1,
        genres: str = None,
        type: str = None,
        sort: str = None,
        season: str = None,
        language: str = None,
        status: str = None,
        rated: str = None,
        start_date: str = None,
        end_date: str = None,
        score: str = None
    ):
        """
        Searches for anime on Aniwatch with advanced filtering options and formats the results.
        """
        logger.debug(f"AniwatchController: Searching anime for query: '{query}' with advanced filters.")
        search_results, status_code = self.aniwatch_service.search_anime(
            query=query, page=page, genres=genres, type=type, sort=sort,
            season=season, language=language, status=status, rated=rated,
            start_date=start_date, end_date=end_date, score=score
        )

        if status_code != 200 or not search_results:
            return search_results, status_code

        formatted_results = []
        for anime in search_results.get("animes", []):
            formatted_results.append({
                "id": anime.get("id"),
                "name": anime.get("name"),
                "poster_url": anime.get("poster"),
                "duration": anime.get("duration"),
                "type": anime.get("type"),
                "rating": anime.get("rating"),
                "episodes": anime.get("episodes") # Sub and Dub counts
            })

        return {
            "animes": formatted_results,
            "most_popular_animes": search_results.get("mostPopularAnimes", []), # From schema
            "total_pages": search_results.get("totalPages"),
            "current_page": search_results.get("currentPage"),
            "has_next_page": search_results.get("hasNextPage"),
            "search_query": search_results.get("searchQuery"),
            "search_filters": search_results.get("searchFilters", {})
        }, status_code

    def get_aniwatch_search_suggestions_data(self, query: str):
        """
        Fetches and formats search suggestions.
        """
        logger.debug(f"AniwatchController: Fetching search suggestions for query: '{query}'")
        suggestions_data, status_code = self.aniwatch_service.get_search_suggestions(query)

        if status_code != 200 or not suggestions_data:
            return suggestions_data, status_code

        formatted_suggestions = []
        for suggestion in suggestions_data.get("suggestions", []):
            formatted_suggestions.append({
                "id": suggestion.get("id"),
                "name": suggestion.get("name"),
                "poster_url": suggestion.get("poster"),
                "japanese_name": suggestion.get("jname"),
                "more_info": suggestion.get("moreInfo", []) # List of strings like ["Jan 21, 2022", "Movie", "17m"]
            })
        return {"suggestions": formatted_suggestions}, status_code

    def get_aniwatch_producer_animes_data(self, name: str, page: int = 1):
        """
        Fetches and formats anime by producer name.
        """
        logger.debug(f"AniwatchController: Fetching producer anime for '{name}', page={page}")
        producer_data, status_code = self.aniwatch_service.get_producer_animes(name, page)

        if status_code != 200 or not producer_data:
            return producer_data, status_code

        # Helper to format common anime list structure (already defined and re-used)
        def format_anime_list_flexible(anime_list):
            formatted = []
            for anime in anime_list:
                formatted.append({
                    "id": anime.get("id"),
                    "name": anime.get("name"),
                    "poster_url": anime.get("poster"),
                    "duration": anime.get("duration"),
                    "type": anime.get("type"),
                    "rating": anime.get("rating"),
                    "episodes": anime.get("episodes"),
                    "japanese_name": anime.get("jname") # Can be present in topAiringAnimes
                })
            return formatted

        formatted_producer_data = {
            "producer_name": producer_data.get("producerName"),
            "animes": format_anime_list_flexible(producer_data.get("animes", [])),
            "top10_animes": {
                "today": format_anime_list_flexible(producer_data.get("top10Animes", {}).get("today", [])),
                "week": format_anime_list_flexible(producer_data.get("top10Animes", {}).get("week", [])),
                "month": format_anime_list_flexible(producer_data.get("top10Animes", {}).get("month", []))
            },
            "top_airing_animes": format_anime_list_flexible(producer_data.get("topAiringAnimes", [])),
            "current_page": producer_data.get("currentPage"),
            "total_pages": producer_data.get("totalPages"),
            "has_next_page": producer_data.get("hasNextPage")
        }
        return formatted_producer_data, status_code

    def get_aniwatch_genre_animes_data(self, name: str, page: int = 1):
        """
        Fetches and formats anime by genre name.
        """
        logger.debug(f"AniwatchController: Fetching genre anime for '{name}', page={page}")
        genre_data, status_code = self.aniwatch_service.get_genre_animes(name, page)

        if status_code != 200 or not genre_data:
            return genre_data, status_code

        # Helper to format common anime list structure (re-using from above)
        def format_anime_list_flexible(anime_list):
            formatted = []
            for anime in anime_list:
                formatted.append({
                    "id": anime.get("id"),
                    "name": anime.get("name"),
                    "poster_url": anime.get("poster"),
                    "duration": anime.get("duration"),
                    "type": anime.get("type"),
                    "rating": anime.get("rating"),
                    "episodes": anime.get("episodes"),
                    "japanese_name": anime.get("jname") # Can be present in topAiringAnimes
                })
            return formatted

        formatted_genre_data = {
            "genre_name": genre_data.get("genreName"),
            "animes": format_anime_list_flexible(genre_data.get("animes", [])),
            "genres": genre_data.get("genres", []),
            "top_airing_animes": format_anime_list_flexible(genre_data.get("topAiringAnimes", [])),
            "current_page": genre_data.get("currentPage"),
            "total_pages": genre_data.get("totalPages"),
            "has_next_page": genre_data.get("hasNextPage")
        }
        return formatted_genre_data, status_code

    def get_aniwatch_category_animes_data(self, category: str, page: int = 1):
        """
        Fetches and formats anime by category.
        """
        logger.debug(f"AniwatchController: Fetching category anime for '{category}', page={page}")
        category_data, status_code = self.aniwatch_service.get_category_animes(category, page)

        if status_code != 200 or not category_data:
            return category_data, status_code

        # Helper to format common anime list structure (re-using from above)
        def format_anime_list_flexible(anime_list):
            formatted = []
            for anime in anime_list:
                formatted.append({
                    "id": anime.get("id"),
                    "name": anime.get("name"),
                    "poster_url": anime.get("poster"),
                    "duration": anime.get("duration"),
                    "type": anime.get("type"),
                    "rating": anime.get("rating"),
                    "episodes": anime.get("episodes"),
                    "japanese_name": anime.get("jname") # Can be present in topAiringAnimes/top10
                })
            return formatted

        formatted_category_data = {
            "category": category_data.get("category"),
            "animes": format_anime_list_flexible(category_data.get("animes", [])),
            "genres": category_data.get("genres", []),
            "top10_animes": {
                "today": format_anime_list_flexible(category_data.get("top10Animes", {}).get("today", [])),
                "week": format_anime_list_flexible(category_data.get("top10Animes", {}).get("week", [])),
                "month": format_anime_list_flexible(category_data.get("top10Animes", {}).get("month", []))
            },
            "current_page": category_data.get("currentPage"),
            "total_pages": category_data.get("totalPages"),
            "has_next_page": category_data.get("hasNextPage")
        }
        return formatted_category_data, status_code

    def get_aniwatch_estimated_schedules_data(self, date: str):
        """
        Fetches and formats estimated schedules for a given date.
        """
        logger.debug(f"AniwatchController: Fetching estimated schedules for date: {date}")
        schedule_data, status_code = self.aniwatch_service.get_estimated_schedules(date)

        if status_code != 200 or not schedule_data:
            return schedule_data, status_code

        formatted_schedules = []
        for schedule in schedule_data.get("scheduledAnimes", []):
            formatted_schedules.append({
                "id": schedule.get("id"),
                "time": schedule.get("time"),
                "name": schedule.get("name"),
                "japanese_name": schedule.get("jname"),
                "airing_timestamp": schedule.get("airingTimestamp"),
                "seconds_until_airing": schedule.get("secondsUntilAiring")
            })
        return {"scheduled_animes": formatted_schedules}, status_code

    def get_aniwatch_anime_episodes_data(self, anime_id: str):
        """
        Fetches and formats episodes for a specific anime ID.
        """
        logger.debug(f"AniwatchController: Fetching episodes for anime ID: {anime_id}")
        episodes_data, status_code = self.aniwatch_service.get_anime_episodes(anime_id)

        if status_code != 200 or not episodes_data:
            return episodes_data, status_code

        formatted_episodes = {
            "total_episodes": episodes_data.get("totalEpisodes"),
            "episodes": []
        }
        for episode in episodes_data.get("episodes", []):
            formatted_episodes["episodes"].append({
                "number": episode.get("number"),
                "title": episode.get("title"),
                "episode_id": episode.get("episodeId"),
                "is_filler": episode.get("isFiller")
            })
        return formatted_episodes, status_code

    def get_aniwatch_next_episode_schedule_data(self, anime_id: str):
        """
        Fetches and formats the next episode schedule for a specific anime ID.
        """
        logger.debug(f"AniwatchController: Fetching next episode schedule for anime ID: {anime_id}")
        schedule_data, status_code = self.aniwatch_service.get_anime_next_episode_schedule(anime_id)

        if status_code != 200 or not schedule_data:
            return schedule_data, status_code

        formatted_schedule = {
            "airing_iso_timestamp": schedule_data.get("airingISOTimestamp"),
            "airing_timestamp": schedule_data.get("airingTimestamp"),
            "seconds_until_airing": schedule_data.get("secondsUntilAiring")
        }
        return formatted_schedule, status_code

    def get_aniwatch_episode_servers_data(self, anime_episode_id: str):
        """
        Fetches and formats episode streaming servers for a given episode ID.
        """
        logger.debug(f"AniwatchController: Fetching episode servers for episode ID: {anime_episode_id}")
        servers_data, status_code = self.aniwatch_service.get_anime_episode_servers(anime_episode_id)

        if status_code != 200 or not servers_data:
            return servers_data, status_code

        formatted_servers = {
            "episode_id": servers_data.get("episodeId"),
            "episode_number": servers_data.get("episodeNo"),
            "sub_servers": servers_data.get("sub", []),
            "dub_servers": servers_data.get("dub", []),
            "raw_servers": servers_data.get("raw", [])
        }
        return formatted_servers, status_code

    def get_aniwatch_episode_streaming_links_data(self, anime_episode_id: str, server: str = None, category: str = None):
        """
        Fetches and formats episode streaming links for a given episode ID, server, and category.
        """
        logger.debug(f"AniwatchController: Fetching streaming links for episode ID: {anime_episode_id}, server: {server}, category: {category}")
        links_data, status_code = self.aniwatch_service.get_anime_episode_streaming_links(anime_episode_id, server, category)

        if status_code != 200 or not links_data:
            return links_data, status_code

        formatted_links = {
            "headers": links_data.get("headers", {}),
            "sources": links_data.get("sources", []),
            "subtitles": links_data.get("subtitles", []),
            "anilist_id": links_data.get("anilistID"),
            "mal_id": links_data.get("malID")
        }
        return formatted_links, status_code


# Initialize the controller
aniwatch_controller = AniwatchController()

# Define Flask routes using the Blueprint
@aniwatch_api_bp.route('/az-list/<string:sort_option>', methods=['GET'])
def get_aniwatch_az_list_route(sort_option):
    page = request.args.get('page', type=int, default=1)
    data, status_code = aniwatch_controller.get_aniwatch_az_list_data(sort_option, page)
    return jsonify(data), status_code

@aniwatch_api_bp.route('/qtip/<string:anime_id>', methods=['GET'])
def get_aniwatch_qtip_info_route(anime_id):
    data, status_code = aniwatch_controller.get_aniwatch_qtip_info_data(anime_id)
    return jsonify(data), status_code

@aniwatch_api_bp.route('/anime/<string:anime_id>', methods=['GET'])
def get_aniwatch_full_anime_details_route(anime_id):
    data, status_code = aniwatch_controller.get_aniwatch_full_anime_details_data(anime_id)
    return jsonify(data), status_code

@aniwatch_api_bp.route('/home', methods=['GET'])
def get_aniwatch_home_page_route():
    data, status_code = aniwatch_controller.get_aniwatch_home_page_data()
    return jsonify(data), status_code

@aniwatch_api_bp.route('/search', methods=['GET'])
def search_aniwatch_anime_route():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "Query parameter 'q' is required."}), 400

    # Extract advanced query parameters
    page = request.args.get('page', type=int, default=1)
    genres = request.args.get('genres')
    type = request.args.get('type')
    sort = request.args.get('sort')
    season = request.args.get('season')
    language = request.args.get('language')
    status = request.args.get('status')
    rated = request.args.get('rated')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    score = request.args.get('score')

    data, status_code = aniwatch_controller.search_aniwatch_anime_data(
        query=query, page=page, genres=genres, type=type, sort=sort,
        season=season, language=language, status=status, rated=rated,
        start_date=start_date, end_date=end_date, score=score
    )
    return jsonify(data), status_code

@aniwatch_api_bp.route('/search/suggestion', methods=['GET'])
def get_aniwatch_search_suggestions_route():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "Query parameter 'q' is required."}), 400
    data, status_code = aniwatch_controller.get_aniwatch_search_suggestions_data(query)
    return jsonify(data), status_code

@aniwatch_api_bp.route('/producer/<string:name>', methods=['GET'])
def get_aniwatch_producer_animes_route(name):
    page = request.args.get('page', type=int, default=1)
    data, status_code = aniwatch_controller.get_aniwatch_producer_animes_data(name, page)
    return jsonify(data), status_code

@aniwatch_api_bp.route('/genre/<string:name>', methods=['GET'])
def get_aniwatch_genre_animes_route(name):
    page = request.args.get('page', type=int, default=1)
    data, status_code = aniwatch_controller.get_aniwatch_genre_animes_data(name, page)
    return jsonify(data), status_code

@aniwatch_api_bp.route('/category/<string:category>', methods=['GET'])
def get_aniwatch_category_animes_route(category):
    page = request.args.get('page', type=int, default=1)
    data, status_code = aniwatch_controller.get_aniwatch_category_animes_data(category, page)
    return jsonify(data), status_code

@aniwatch_api_bp.route('/schedule', methods=['GET'])
def get_aniwatch_estimated_schedules_route():
    date = request.args.get('date')
    if not date:
        return jsonify({"error": "Query parameter 'date' is required."}), 400
    data, status_code = aniwatch_controller.get_aniwatch_estimated_schedules_data(date)
    return jsonify(data), status_code

@aniwatch_api_bp.route('/anime/<string:anime_id>/episodes', methods=['GET'])
def get_aniwatch_anime_episodes_route(anime_id):
    data, status_code = aniwatch_controller.get_aniwatch_anime_episodes_data(anime_id)
    return jsonify(data), status_code

@aniwatch_api_bp.route('/anime/<string:anime_id>/next-episode-schedule', methods=['GET'])
def get_aniwatch_next_episode_schedule_route(anime_id):
    data, status_code = aniwatch_controller.get_aniwatch_next_episode_schedule_data(anime_id)
    return jsonify(data), status_code

@aniwatch_api_bp.route('/episode/servers', methods=['GET'])
def get_aniwatch_episode_servers_route():
    anime_episode_id = request.args.get('animeEpisodeId')
    if not anime_episode_id:
        return jsonify({"error": "Query parameter 'animeEpisodeId' is required."}), 400
    data, status_code = aniwatch_controller.get_aniwatch_episode_servers_data(anime_episode_id)
    return jsonify(data), status_code

@aniwatch_api_bp.route('/episode/sources', methods=['GET'])
def get_aniwatch_episode_streaming_links_route():
    anime_episode_id = request.args.get('animeEpisodeId')
    if not anime_episode_id:
        return jsonify({"error": "Query parameter 'animeEpisodeId' is required."}), 400
    server = request.args.get('server')
    category = request.args.get('category') # 'sub', 'dub', 'raw'

    data, status_code = aniwatch_controller.get_aniwatch_episode_streaming_links_data(anime_episode_id, server, category)
    return jsonify(data), status_code

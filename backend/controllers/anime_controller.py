# backend/controllers/anime_controller.py
from flask import request
import logging
from services.anime_api_service import AnimeAPIService

logger = logging.getLogger(__name__)

class AnimeController:
    def __init__(self, anime_api_service: AnimeAPIService):
        self.anime_api_service = anime_api_service
        logger.info("AnimeController: Initialized with an instance of AnimeAPIService.")

    def get_home_page_data(self) -> tuple[dict, int]:
        logger.debug("Controller: Fetching home page data.")
        return self.anime_api_service.get_home_info()

    def get_search_suggestions_data(self, keyword: str) -> tuple[dict, int]:
        logger.debug(f"Controller: Fetching search suggestions for keyword: {keyword}")
        return self.anime_api_service.get_search_suggestions(keyword)

    def get_top_ten_anime_data(self) -> tuple[dict, int]:
        logger.debug("Controller: Fetching top ten anime data.")
        return self.anime_api_service.get_top_ten_anime()

    def search_anime_data(self, filters: dict) -> tuple[dict, int]:
        logger.debug(f"Controller: Searching anime with filters: {filters}")
        return self.anime_api_service.search_anime(filters)

    def get_anime_by_category_data(self, category: str, page: int = 1) -> tuple[dict, int]:
        logger.debug(f"Controller: Fetching anime by category: {category}, page: {page}")
        return self.anime_api_service.get_anime_by_category(category, page)

    def get_anime_details_data(self, anime_id: str) -> tuple[dict, int]:
        logger.debug(f"Controller: Fetching comprehensive details for anime ID: {anime_id}")
        return self.anime_api_service.get_anime_info(anime_id)

    def get_episode_list_data(self, anime_id: str) -> tuple[dict, int]: # Assumed method, create if not present
        logger.debug(f"Controller: Fetching episodes for anime ID: {anime_id}")
        return self.anime_api_service.get_anime_info(anime_id) # The get_anime_info also gets episodes

    def get_available_servers_data(self, episode_data_id: str) -> tuple[dict, int]:
        logger.debug(f"Controller: Fetching servers for episode data_id: {episode_data_id}")
        return self.anime_api_service.get_available_servers(episode_data_id)

    def get_streaming_info_data(self, anime_id: str, episode_data_id: str, server_name: str, stream_type: str) -> tuple[dict, int]:
        logger.debug(f"Controller: Fetching streaming info for anime ID: {anime_id}, Episode ID: {episode_data_id}, Server: {server_name}")
        return self.anime_api_service.get_streaming_info(anime_id, episode_data_id, server_name, stream_type)

    def get_qtip_info_data(self, anime_id: str) -> tuple[dict, int]:
        logger.debug(f"Controller: Fetching qtip info for anime ID: {anime_id}")
        return self.anime_api_service.get_qtip_info(anime_id)

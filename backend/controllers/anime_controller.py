# backend/controllers/anime_controller.py
from flask import Blueprint, jsonify, request, Response
from services.anime_api_service import AnimeAPIService
import logging
import re
import requests
import urllib3
import urllib.parse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

class AnimeController:
    def __init__(self):
        self.anime_api_service = AnimeAPIService()
        logger.info("AnimeController: Initialized.")

    def _format_search_suggestions(self, suggestions_list: list) -> list:
        formatted = []
        if not isinstance(suggestions_list, list):
            logger.warning(f"Suggestion data for formatting is not a list: {type(suggestions_list)}")
            return []
        for anime in suggestions_list:
            if not isinstance(anime, dict) or not anime.get("id"):
                continue
            formatted.append({
                "id": anime.get("id"),
                "title": anime.get("title"),
                "poster_url": anime.get("poster"),
                "show_type": anime.get("type"),
            })
        return formatted

    def get_search_suggestions_data(self, keyword: str) -> tuple[dict, int]:
        logger.debug(f"AnimeController: Fetching search suggestions for keyword: {keyword}")
        raw_data, status_code = self.anime_api_service.get_search_suggestions(keyword)

        if status_code != 200 or not raw_data.get('success'):
            error_message = raw_data.get('message', 'Failed to fetch suggestions')
            logger.error(f"AnimeController: Failed to fetch suggestions. Status: {status_code}, Data: {raw_data}")
            return {"error": error_message}, status_code

        formatted_suggestions = self._format_search_suggestions(raw_data.get("results", []))
        return {"results": formatted_suggestions}, 200

    def _ensure_is_list(self, value):
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [value]
        return []

    def _format_search_results(self, anime_list: list) -> list:
        formatted = []
        if not isinstance(anime_list, list):
            logger.warning(f"Search result data for formatting is not a list: {type(anime_list)}")
            return []

        for anime in anime_list:
            if not isinstance(anime, dict) or not anime.get("id"):
                continue
            formatted.append({
                "id": anime.get("id"),
                "title": anime.get("title"),
                "poster_url": anime.get("poster"),
                "jname": anime.get("japanese_title"),
                "show_type": anime.get("showType") or anime.get("type"),
                "duration": anime.get("duration"),
                "score": None
            })
        return formatted

    def get_home_page_data(self) -> tuple[dict, int]:
        logger.debug("AnimeController: Fetching home page data.")
        raw_data, status_code = self.anime_api_service.get_home_info()

        if status_code != 200:
            return raw_data, status_code

        if not raw_data or not raw_data.get('success') or 'results' not in raw_data:
            logger.error("AnimeController: Invalid or missing 'results' in home page data.")
            return {"error": "Invalid data format from external API."}, 500

        results = raw_data['results']

        formatted_home_data = {
            "spotlights": self._format_anime_list_home(results.get("spotlights", [])),
            "trending": self._format_anime_list_home(results.get("trending", [])),
            "today_schedule": self._format_anime_list_home(results.get("today_schedule", [])),
            "top_airing": self._format_anime_list_home(results.get("top_airing", [])),
            "most_popular": self._format_anime_list_home(results.get("most_popular", [])),
            "most_favorite": self._format_anime_list_home(results.get("most_favorite", [])),
            "latest_completed": self._format_anime_list_home(results.get("latest_completed", [])),
            "latest_episode": self._format_anime_list_home(results.get("latest_episode", [])),
            "genres": results.get("genres", [])
        }
        return formatted_home_data, 200

    def get_top_search_anime_data(self) -> tuple[dict, int]:
        logger.debug("AnimeController: Fetching top search anime data.")
        raw_data, status_code = self.anime_api_service.get_top_search_anime()
        if status_code != 200:
            return raw_data, status_code

        results_list = raw_data.get("results", [])
        if not isinstance(results_list, list):
            logger.error(f"AnimeController: Top search results are not a list, but {type(results_list)}")
            return {"error": "Invalid data format for top searches."}, 500

        return {"results": self._format_top_search_list(results_list)}, 200

    def _format_top_search_list(self, top_search_list: list) -> list:
        formatted = []
        if not isinstance(top_search_list, list):
            logger.warning(f"Top search data for formatting is not a list: {type(top_search_list)}")
            return []

        for item in top_search_list:
            item_id_slug = item.get("id")
            if not isinstance(item, dict) or not item_id_slug:
                continue

            # --- START OF CHANGE ---
            # Instead of a direct details link, create a search link.
            # This is safer because a top search term might have multiple results (e.g., "One Piece").
            # The search page can handle displaying all results for the user to choose from.
            title = item.get("title")
            if not title:
                continue

            encoded_title = urllib.parse.quote(title)
            search_link = f"/search?keyword={encoded_title}"

            formatted.append({
                "id": item_id_slug, # Keep the original ID for keying purposes on the frontend
                "title": title,
                "link": search_link # Use the new, correct search link
            })
            # --- END OF CHANGE ---
        return formatted

    def get_top_ten_anime_data(self) -> tuple[dict, int]:
        logger.debug("AnimeController: Fetching top ten anime data.")
        raw_data, status_code = self.anime_api_service.get_top_ten_anime()
        if status_code != 200:
            return raw_data, status_code
        results_dict = raw_data.get("results", {}).get("topTen", {})
        return {
            "today": self._format_anime_list_common(results_dict.get("today", [])),
            "week": self._format_anime_list_common(results_dict.get("week", [])),
            "month": self._format_anime_list_common(results_dict.get("month", []))
        }, 200

    def search_anime_data(self, query: str, page: int = 1) -> tuple[dict, int]:
        logger.debug(f"AnimeController: Searching anime for query: {query}, page: {page}")
        raw_data, status_code = self.anime_api_service.search_anime(query, page)
        if status_code != 200:
            return raw_data, status_code

        results_dict = raw_data.get("results", {})
        anime_list = results_dict.get("data", []) if isinstance(results_dict, dict) else []
        total_pages = results_dict.get("totalPages", 1) if isinstance(results_dict, dict) else 1

        formatted_results = {
            "results": self._format_search_results(anime_list),
            "totalPages": total_pages
        }
        return formatted_results, 200

    def get_anime_by_category_data(self, category: str, page: int = 1) -> tuple[dict, int]:
        logger.debug(f"AnimeController: Fetching anime by category: {category}, page: {page}")
        raw_data, status_code = self.anime_api_service.get_anime_by_category(category, page)
        if status_code != 200:
            return raw_data, status_code

        results_dict = raw_data.get("results", {})
        anime_list = results_dict.get("data", []) if isinstance(results_dict, dict) else []
        total_pages = results_dict.get("totalPages", 1) if isinstance(results_dict, dict) else 1

        formatted_results = {
            "data": self._format_anime_list_common(anime_list),
            "totalPages": total_pages
        }
        return formatted_results, 200

    def get_anime_details_data(self, anime_id: str) -> tuple[dict, int]:
        logger.debug(f"AnimeController: Fetching comprehensive details for anime ID: {anime_id}")

        # FIX: The anime_id passed from the route IS the slug we need for /api/info
        main_info_data, main_info_status = self.anime_api_service.get_anime_info(anime_id)

        if main_info_status != 200 or not main_info_data.get('success'):
            logger.error(f"AnimeController: Failed to fetch main info for '{anime_id}'. Status: {main_info_status}, Data: {main_info_data}")
            return {"error": f"Failed to retrieve main anime details: {main_info_data.get('message', 'Unknown error')}"}, main_info_status

        results = main_info_data.get('results', {})
        anime_data = results.get('data', {})
        anime_info_nested = anime_data.get('animeInfo', {})

        if not anime_data:
            logger.error(f"AnimeController: No 'data' found in results for main info of {anime_id}.")
            return {"error": "No anime details found for the given ID."}, 404

        seasons_list = results.get("seasons", [])
        if not isinstance(seasons_list, list):
            logger.warning(f"Seasons data for anime ID {anime_id} is not a list, defaulting to empty.")
            seasons_list = []

        formatted_details = {
            "id": anime_data.get("id"),
            "data_id": anime_data.get("data_id"),
            "title": anime_data.get("title"),
            "japanese_title": anime_data.get("japanese_title"),
            "synonyms": self._ensure_is_list(anime_info_nested.get("Synonyms")),
            "poster_url": anime_data.get("poster"),
            "trailer_url": anime_data.get("trailer"),
            "synopsis": anime_info_nested.get("Overview"),
            "show_type": anime_data.get("showType"),
            "status": anime_info_nested.get("Status"),
            "aired": anime_info_nested.get("Aired"),
            "premiered": anime_info_nested.get("Premiered"),
            "broadcast": anime_data.get("broadcast"),
            "producers": self._ensure_is_list(anime_info_nested.get("Producers")),
            "licensors": self._ensure_is_list(anime_data.get("licensors")),
            "studios": self._ensure_is_list(anime_info_nested.get("Studios")),
            "source": anime_data.get("source"),
            "genres": self._ensure_is_list(anime_info_nested.get("Genres")),
            "duration": anime_info_nested.get("Duration"),
            "rating": anime_data.get("rating"),
            "mal_score": anime_info_nested.get("MAL Score"),
            "scored_by": anime_data.get("scored_by"),
            "rank": anime_data.get("rank"),
            "popularity": anime_data.get("popularity"),
            "members": anime_data.get("members"),
            "favorites": anime_data.get("favorites"),
            "total_episodes_count": anime_data.get("total_episodes"),
            "episodes": [],
            "characters_voice_actors": [],
            "seasons": self._format_seasons(seasons_list),
            "related_anime": [],
            "recommended_anime": []
        }

        # The anime_id (slug) is also used for these subsequent calls
        episodes_data, episodes_status = self.anime_api_service.get_episode_list(anime_id)
        if episodes_status == 200 and episodes_data.get('success'):
            episode_list = episodes_data.get("results", {}).get("episodes", [])
            formatted_details["episodes"] = self._format_episodes(episode_list)
        else:
            logger.warning(f"AnimeController: Failed to fetch episodes for {anime_id}. Status: {episodes_status}, Data: {episodes_data}")

        characters_data, characters_status = self.anime_api_service.get_characters_list(anime_id)
        if characters_status == 200 and characters_data.get('success'):
            formatted_details["characters_voice_actors"] = self._format_characters_voice_actors(characters_data.get("results", []))
        else:
            logger.warning(f"AnimeController: Failed to fetch characters for {anime_id}. Status: {characters_status}, Data: {characters_data}")

        related_data, related_status = self.anime_api_service.get_related_anime(anime_id)
        if related_status == 200 and related_data.get('success'):
            formatted_details["related_anime"] = self._format_anime_list_common(related_data.get("results", []))
        else:
            logger.warning(f"AnimeController: Failed to fetch related anime for {anime_id}. Status: {related_status}, Data: {related_data}")

        recommended_data, recommended_status = self.anime_api_service.get_recommended_anime(anime_id)
        if recommended_status == 200 and recommended_data.get('success'):
            formatted_details["recommended_anime"] = self._format_anime_list_common(recommended_data.get("results", []))
        else:
            logger.warning(f"AnimeController: Failed to fetch recommended anime for {anime_id}. Status: {recommended_status}, Data: {recommended_data}")

        return formatted_details, 200

    def get_qtip_info_data(self, qtip_id: int) -> tuple[dict, int]:
        logger.debug(f"AnimeController: Fetching Qtip info for ID: {qtip_id}")
        raw_data, status_code = self.anime_api_service.get_qtip_info(qtip_id)
        if status_code != 200:
            return raw_data, status_code
        return raw_data.get("results", {}), 200

    def get_character_details_data(self, character_id: str) -> tuple[dict, int]:
        logger.debug(f"AnimeController: Fetching character details for ID: {character_id}")
        raw_data, status_code = self.anime_api_service.get_character_details(character_id)
        if status_code != 200:
            return raw_data, status_code
        return self._format_character_details(raw_data.get("results", {})), 200

    def get_voice_actor_details_data(self, actor_id: str) -> tuple[dict, int]:
        logger.debug(f"AnimeController: Fetching voice actor details for ID: {actor_id}")
        raw_data, status_code = self.anime_api_service.get_voice_actor_details(actor_id)
        if status_code != 200:
            return raw_data, status_code
        return self._format_voice_actor_details(raw_data.get("results", {})), 200

    def get_available_servers_data(self, anime_id: str, episode_data_id: str) -> tuple[dict, int]:
        logger.debug(f"AnimeController: Fetching servers for anime ID: {anime_id}, episode data_id: {episode_data_id}")
        raw_data, status_code = self.anime_api_service.get_available_servers(anime_id, episode_data_id)
        if status_code != 200:
            return raw_data, status_code
        return {"servers": self._format_servers(raw_data.get("results", []))}, 200

    def get_streaming_info_data(self, episode_id: str, server_id: str, stream_type: str) -> tuple[dict, int]:
        logger.debug(f"AnimeController: Fetching streaming info for episode ID: {episode_id}, server ID: {server_id}, type: {stream_type}")
        raw_data, status_code = self.anime_api_service.get_streaming_info(episode_id, server_id, stream_type)
        if status_code != 200:
            return raw_data, status_code
        return {"streaming_links": self._format_streaming_info(raw_data.get("results", {}))}, 200

    def _format_anime_list_home(self, anime_list: list) -> list:
        formatted = []
        for anime in anime_list:
            if not anime.get("id"):
                continue
            formatted.append({
                "id": anime.get("id"),
                "title": anime.get("title"),
                "poster_url": anime.get("poster"),
                "jname": anime.get("jname"),
                "show_type": anime.get("type"),
                "score": anime.get("score")
            })
        return formatted

    def _format_anime_list_common(self, anime_list: list) -> list:
        formatted = []
        if not isinstance(anime_list, list):
             logger.warning(f"Data for formatting is not a list: {type(anime_list)}")
             return []

        for anime in anime_list:
            if not isinstance(anime, dict) or not anime.get("id"):
                continue
            formatted.append({
                "id": anime.get("id"),
                "title": anime.get("title"),
                "poster_url": anime.get("poster"),
                "jname": anime.get("jname"),
                "show_type": anime.get("type"),
                "score": anime.get("score")
            })
        return formatted

    def _format_episodes(self, episodes_list: list) -> list:
        formatted = []
        if not isinstance(episodes_list, list):
            logger.error(f"Cannot format episodes, expected a list but got {type(episodes_list)}")
            return []

        for episode in episodes_list:
            if not isinstance(episode, dict):
                logger.warning(f"Skipping episode formatting because item is not a dictionary: {episode}")
                continue

            episode_id_from_node = episode.get("id")
            extracted_data_id = episode.get("data_id")

            if extracted_data_id is None and episode_id_from_node:
                match = re.search(r'\?ep=(\d+)', episode_id_from_node)
                if match:
                    extracted_data_id = match.group(1)
                else:
                    logger.warning(f"Could not extract data_id from episode ID: {episode_id_from_node}")

            formatted.append({
                "id": episode_id_from_node,
                "episode_no": episode.get("episode"),
                "data_id": extracted_data_id,
                "title": episode.get("title"),
                "japanese_title": episode.get("japanese_title")
            })
        return formatted

    def _format_seasons(self, seasons_list: list) -> list:
        formatted = []
        if not isinstance(seasons_list, list):
            logger.warning(f"Seasons data is not a list, it's a {type(seasons_list)}. Skipping.")
            return []
        for season in seasons_list:
            formatted.append({
                "id": season.get("id"),
                "data_number": season.get("data_number"),
                "data_id": season.get("data_id"),
                "season_name": season.get("season"),
                "title": season.get("title"),
                "japanese_title": season.get("japanese_title"),
                "season_poster_url": season.get("season_poster")
            })
        return formatted

    def _format_characters_voice_actors(self, characters_data: list) -> list:
        formatted = []
        for char_info in characters_data:
            character = char_info.get("character", {})
            voice_actors = char_info.get("voiceActors", [])
            formatted_v_actors = []
            for va in voice_actors:
                formatted_v_actors.append({
                    "id": va.get("id"),
                    "name": va.get("name"),
                    "poster_url": va.get("poster")
                })
            formatted.append({
                "character_id": character.get("id"),
                "character_name": character.get("name"),
                "character_poster_url": character.get("poster"),
                "character_cast": character.get("cast"),
                "voice_actors": formatted_v_actors
            })
        return formatted

    def _format_character_details(self, character_data: dict) -> dict:
        if not character_data:
            return {}
        return {
            "id": character_data.get("id"),
            "name": character_data.get("name"),
            "poster_url": character_data.get("poster"),
            "description": character_data.get("description"),
            "animeography": self._format_anime_list_common(character_data.get("animeography", [])),
            "mangaography": character_data.get("mangaography", []),
            "voice_actors": self._format_characters_voice_actors([{"voiceActors": character_data.get("voiceActors", [])}]).pop().get("voice_actors", [])
        }

    def _format_voice_actor_details(self, actor_data: dict) -> dict:
        if not actor_data:
            return {}
        return {
            "id": actor_data.get("id"),
            "name": actor_data.get("name"),
            "poster_url": actor_data.get("poster"),
            "description": actor_data.get("description"),
            "language": actor_data.get("language"),
            "characters_played": self._format_characters_voice_actors(actor_data.get("characters_played", []))
        }

    def _format_servers(self, servers_list: list) -> list:
        formatted = []
        for server in servers_list:
            formatted.append({
                "type": server.get("type"),
                "data_id": server.get("data_id"),
                "server_id": server.get("server_id"),
                "server_name": server.get("serverName")
            })
        return formatted

    def _format_streaming_info(self, streaming_info_results: dict) -> list:
        if not streaming_info_results:
            logger.warning("Streaming info results are empty.")
            return []
        headers = streaming_info_results.get("headers", {})
        links = []
        streaming_link_data = streaming_info_results.get("streamingLink", streaming_info_results.get("link"))
        if not streaming_link_data:
            logger.warning("No 'streamingLink' or 'link' key found in results.")
            return []
        streaming_link_list = [streaming_link_data] if not isinstance(streaming_link_data, list) else streaming_link_data
        for link_details in streaming_link_list:
            if isinstance(link_details, dict):
                file_value = link_details.get("file", link_details.get("link"))
                file_url = file_value.get("file") if isinstance(file_value, dict) else str(file_value)
                if file_url:
                    links.append({"file": file_url, "server": link_details.get("server"), "type": link_details.get("type"), "headers": headers})
        return links

    def proxy_video_stream(self, video_url: str, referer: str = None):
        logger.debug(f"AnimeController: Proxying video stream for URL: {video_url} with Referer: {referer}")
        try:
            if not isinstance(video_url, str) or not video_url.startswith('http'):
                raise requests.exceptions.InvalidURL(f"Invalid URL received for proxy: {video_url}")
            s = requests.Session()
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            if referer:
                headers['Referer'] = referer
            else:
                headers['Referer'] = 'https://9anime.to/' # Generic fallback
            req = s.get(video_url, headers=headers, stream=True, timeout=60, verify=False)
            req.raise_for_status()
            content_type = req.headers.get('Content-Type', 'application/octet-stream')
            if 'mpegurl' in content_type or '.m3u8' in video_url:
                logger.info("Proxying M3U8 playlist. Rewriting URLs...")
                playlist_content = req.text
                base_proxy_url = f"{request.url_root}api/anime/proxy-stream"
                rewritten_playlist = re.sub(
                    r'^(?!#)(.*)$',
                    lambda match: f"{base_proxy_url}?url={requests.utils.quote(video_url.rsplit('/', 1)[0] + '/' + match.group(1))}&referer={requests.utils.quote(headers['Referer'])}",
                    playlist_content,
                    flags=re.MULTILINE
                )
                return Response(rewritten_playlist, content_type=content_type, status=req.status_code)

            def generate():
                for chunk in req.iter_content(chunk_size=8192):
                    yield chunk
            return Response(generate(), content_type=content_type, status=req.status_code)
        except requests.exceptions.RequestException as e:
            logger.error(f"AnimeController: Error proxying video stream from {video_url}: {e}")
            return Response(f"Error proxying video: {e}", status=502)

anime_controller = AnimeController()

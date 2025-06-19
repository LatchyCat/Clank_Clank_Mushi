# backend/controllers/anime_controller.py
from flask import Blueprint, jsonify, request, Response
from services.anime_api_service import AnimeAPIService
import logging
import re
import requests
import urllib3
import urllib.parse
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

class AnimeController:
    def __init__(self, anime_api_service: AnimeAPIService):
        self.anime_api_service = anime_api_service
        logger.info("AnimeController: Initialized with AnimeAPIService.")

    def _ensure_is_list(self, value):
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [value]
        return []

    def _format_anime_list_common(self, anime_list: list) -> list:
        formatted = []
        if not isinstance(anime_list, list):
             logger.warning(f"Data for formatting is not a list: {type(anime_list)}")
             return []

        for anime in anime_list:
            if not isinstance(anime, dict) or not anime.get("id"):
                continue

            tv_info = anime.get("tvInfo")
            if not isinstance(tv_info, dict):
                tv_info = {}

            formatted.append({
                "id": anime.get("id"),
                "title": anime.get("title"),
                "poster_url": anime.get("poster"),
                "jname": anime.get("jname") or anime.get("japanese_title"),
                "show_type": anime.get("showType") or anime.get("type"),
                "score": anime.get("score"),
                "description": anime.get("description"),
                "tvInfo": {
                    "sub": tv_info.get("sub"),
                    "dub": tv_info.get("dub"),
                    "rating": tv_info.get("rating"),
                    "showType": anime.get("showType") or anime.get("type"),
                    "duration": anime.get("duration"),
                }
            })
        return formatted

    def _format_anime_list_home(self, anime_list: list) -> list:
        return self._format_anime_list_common(anime_list)

    def get_home_page_data(self) -> tuple[dict, int]:
        logger.debug("AnimeController: Fetching home page data.")

        # Initial call to get spotlights, trending, and base data
        raw_home_data, home_status_code = self.anime_api_service.get_home_info()

        if home_status_code != 200:
            logger.error(f"AnimeController: Failed to fetch base home data. Status: {home_status_code}")
            return raw_home_data, home_status_code

        if not raw_home_data or not raw_home_data.get('success') or 'results' not in raw_home_data:
            logger.error("AnimeController: Invalid or missing 'results' in base home page data.")
            return {"error": "Invalid data format from external API for home."}, 500

        home_results = raw_home_data.get('results', {})

        # Initialize with data from the first call
        formatted_home_data = {
            "spotlights": self._format_anime_list_home(home_results.get("spotlights", [])),
            "trending": self._format_anime_list_home(home_results.get("trending", [])),
            "genres": home_results.get("genres", []),
            "top_airing": [],
            "most_popular": [],
            "most_favorite": [],
            "latest_completed": [],
            "latest_episode": [],
        }

        # Define categories to fetch from their specific endpoints
        categories_to_fetch = {
            "top-airing": "top_airing",
            "most-popular": "most_popular",
            "most-favorite": "most_favorite",
            "completed": "latest_completed",
            "recently-updated": "latest_episode",
        }

        for api_slug, dict_key in categories_to_fetch.items():
            logger.info(f"AnimeController: Fetching category '{api_slug}' for home page.")
            # Use the dedicated get_anime_by_category method
            category_data, status_code = self.anime_api_service.get_anime_by_category(api_slug, page=1, limit=20)

            if status_code == 200 and category_data.get('success'):
                # The data structure from category endpoints is { results: { data: [...] } }
                anime_list = category_data.get('results', {}).get('data', [])
                formatted_home_data[dict_key] = self._format_anime_list_common(anime_list)
                logger.info(f"Successfully fetched and formatted '{api_slug}'. Found {len(anime_list)} items.")
            else:
                logger.warning(f"AnimeController: Failed to fetch category '{api_slug}'. Status: {status_code}, Response: {category_data}")

        logger.info("Successfully fetched and formatted all home page sections.")
        return formatted_home_data, 200

    def get_qtip_info_data(self, qtip_id: str) -> tuple[dict, int]:
        logger.debug(f"AnimeController: Fetching Qtip info for ID: {qtip_id}")
        raw_data, status_code = self.anime_api_service.get_qtip_info(qtip_id)

        if status_code != 200 or not raw_data.get('success'):
            error_message = raw_data.get('message', 'Failed to fetch qtip info')
            logger.error(f"AnimeController: Failed to fetch qtip info for {qtip_id}. Status: {status_code}, Data: {raw_data}")
            return {"error": error_message}, status_code

        results = raw_data.get("results", {})
        anime_info = results.get("anime", {})

        return anime_info, 200

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
                "score": None,
                "description": anime.get("description"),
                "tvInfo": anime.get("tvInfo")
            })
        return formatted

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

            title = item.get("title")
            if not title:
                continue

            encoded_title = urllib.parse.quote(title)
            search_link = f"/search?keyword={encoded_title}"

            formatted.append({
                "id": item_id_slug,
                "title": title,
                "link": search_link
            })
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
            "related_anime": self._format_anime_list_common(results.get("relatedAnimes", [])),
            "recommended_anime": self._format_anime_list_common(results.get("recommendedAnimes", []))
        }

        episodes_data, episodes_status = self.anime_api_service.get_episode_list(anime_id)
        if episodes_status == 200 and episodes_data.get('success'):
            raw_episodes = episodes_data.get("results", [])
            if not isinstance(raw_episodes, list):
                 logger.warning(f"Expected a list for episodes but got {type(raw_episodes)}. Defaulting to empty.")
                 raw_episodes = []
            formatted_details["episodes"] = self._format_episodes(raw_episodes)
        else:
            logger.warning(f"AnimeController: Failed to fetch episodes for {anime_id}. Status: {episodes_status}, Data: {episodes_data}")

        characters_data, characters_status = self.anime_api_service.get_characters_list(anime_id)
        if characters_status == 200 and characters_data.get('success'):
            character_list = characters_data.get("results", [])
            if not isinstance(character_list, list):
                logger.warning(f"Expected a list for characters but got {type(character_list)}. Defaulting to empty.")
                character_list = []
            formatted_details["characters_voice_actors"] = self._format_characters_voice_actors(character_list)
        else:
            logger.warning(f"AnimeController: Failed to fetch characters for {anime_id}. Status: {characters_status}, Data: {characters_data}")

        return formatted_details, 200

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

    def _format_schedule_list(self, schedule_list: list) -> list:
        formatted = []
        if not isinstance(schedule_list, list):
            logger.warning(f"Schedule data for formatting is not a list: {type(schedule_list)}")
            return []
        for item in schedule_list:
            if not isinstance(item, dict) or not item.get("id"):
                continue
            formatted.append({
                "id": item.get("id"),
                "data_id": item.get("data_id"),
                "title": item.get("title"),
                "jname": item.get("japanese_title"),
                "release_date": item.get("releaseDate"),
                "release_time": item.get("time"),
                "episode_no": item.get("episode"),
                "poster_url": item.get("poster"),
                "show_type": item.get("showType")
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
        if not isinstance(characters_data, list):
            logger.warning(f"Characters data is not a list ({type(characters_data)}), returning empty list.")
            return []

        formatted = []
        for char_info in characters_data:
            if not isinstance(char_info, dict):
                logger.warning(f"Skipping character formatting because item is not a dict: {char_info}")
                continue

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
                headers['Referer'] = 'https://9anime.to/'
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

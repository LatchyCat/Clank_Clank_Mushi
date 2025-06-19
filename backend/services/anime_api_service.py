# backend/services/anime_api_service.py
import cloudscraper
import logging
import json
from bs4 import BeautifulSoup, Tag
from requests.exceptions import RequestException, HTTPError
from services.anime_api_decryption import decrypt_source_url, _get_decryption_key
from urllib.parse import quote

logger = logging.getLogger(__name__)

V1_BASE_URL = "https://hianime.to"
V4_BASE_URL = "https://9animetv.to"

class AnimeAPIService:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
        )
        self.decryption_key = _get_decryption_key()
        logger.info("AnimeAPIService: Initialized with CloudScraper for direct website scraping.")

    def _make_request(self, url: str, params: dict = None, headers: dict = None) -> tuple[dict | str | None, int]:
        logger.debug(f"Making scraping request to: {url} with params: {params}")
        try:
            final_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Referer': f"{V1_BASE_URL}/",
                **(headers or {})
            }
            response = self.scraper.get(url, params=params, headers=final_headers, timeout=20)
            response.raise_for_status()
            try:
                return response.json(), response.status_code
            except json.JSONDecodeError:
                return response.text, response.status_code
        except HTTPError as e:
            logger.error(f"HTTP error for {url}: {e.response.status_code} - {e.response.text}")
            return {"error": f"Upstream service at {url} returned HTTP {e.response.status_code}"}, e.response.status_code
        except RequestException as e:
            logger.error(f"Request error for {url}: {e}")
            return {"error": f"Request error to upstream service: {e}"}, 500
        except Exception as e:
            logger.error(f"An unexpected error occurred while scraping {url}: {e}", exc_info=True)
            return {"error": "An unexpected server error occurred during scraping"}, 500

    def _safe_parse(self, element, selector, attribute=None, text=False):
        if not element: return None
        found = element.select_one(selector)
        if not found: return None
        if attribute: return found.get(attribute)
        if text: return found.text.strip()
        return found

    def _parse_anime_card(self, element: BeautifulSoup) -> dict | None:
        if not isinstance(element, Tag): return None
        title_element = self._safe_parse(element, ".film-detail .film-name a")
        if not title_element: return None

        id_raw = title_element.get('href')
        poster_url = self._safe_parse(element, ".film-poster img", 'data-src')

        tv_info = {
            "showType": self._safe_parse(element, ".fdi-item:not(.fdi-duration)", text=True),
            "sub": self._safe_parse(element, ".tick-sub", text=True),
            "dub": self._safe_parse(element, ".tick-dub", text=True),
            "eps": self._safe_parse(element, ".tick-eps", text=True),
        }

        return {
            "id": id_raw.replace("/watch/", "", 1).split("?")[0].strip("/") if id_raw else None,
            "title": title_element.text.strip(),
            "poster_url": poster_url,
            "tvInfo": tv_info
        }

    # --- START OF DEFINITIVE FIX ---
    def get_home_info(self) -> tuple[dict, int]:
        home_url = f"{V1_BASE_URL}/home"
        html_content, status_code = self._make_request(home_url)
        if status_code != 200 or not isinstance(html_content, str):
            logger.error(f"Failed to fetch homepage HTML from {home_url}. Status: {status_code}")
            return {"error": "Could not fetch homepage HTML from source."}, status_code

        logger.info(f"Successfully fetched homepage HTML. Parsing all sections...")
        soup = BeautifulSoup(html_content, "lxml")

        def run_parser_on_soup(section_name: str, selector: str, parser_func, container=soup) -> list:
            elements = container.select(selector)
            if not elements:
                logger.warning(f"No items found for section '{section_name}' with selector: {selector}")
                return []

            data = [item for el in elements if (item := parser_func(el)) is not None]
            logger.info(f"Found and successfully parsed {len(data)} items for section '{section_name}'.")
            return data

        def parse_spotlight(el: Tag) -> dict | None:
            title_el = self._safe_parse(el, ".desi-head-title.dynamic-name")
            if not title_el: return None

            id_raw = self._safe_parse(el, ".desi-buttons a.btn-play", 'href')
            poster_el = self._safe_parse(el, ".deslide-cover-img img", 'data-src')

            return {
                "id": id_raw.replace("/watch/", "", 1).split("?")[0].strip("/") if id_raw else None,
                "poster_url": poster_el,
                "title": title_el.text.strip(),
                "description": self._safe_parse(el, ".desi-description", text=True) or "",
            }

        def parse_trending(el: Tag) -> dict | None:
            link_el = self._safe_parse(el, "a.film-poster", 'href')
            if not link_el: return None

            return {
                "id": link_el.split("/")[-1],
                "poster_url": self._safe_parse(el, "img", 'data-src'),
                "title": self._safe_parse(el, ".film-title", text=True),
                "number": self._safe_parse(el, ".number span", text=True),
            }

        def scrape_page(path: str, parser_func, limit: int = 18):
            logger.info(f"Scraping separate page: /{path}...")
            url = f"{V1_BASE_URL}/{path}"
            html_content, status_code = self._make_request(url)

            if status_code != 200 or not isinstance(html_content, str):
                logger.error(f"Failed to fetch page /{path}. Status: {status_code}")
                return []

            page_soup = BeautifulSoup(html_content, "lxml")
            items = []
            selector = ".film_list-wrap .flw-item"
            elements = page_soup.select(selector)

            if not elements:
                logger.warning(f"No items found on page /{path} with selector '{selector}'")
                return []

            for el in elements[:limit]:
                parsed = parser_func(el)
                if parsed:
                    items.append(parsed)

            logger.info(f"Successfully parsed {len(items)} items from /{path}.")
            return items

        try:
            results = {
                "spotlights": run_parser_on_soup("Spotlights", "#slider .swiper-slide", parse_spotlight, container=soup),
                "trending": run_parser_on_soup("Trending", "#trending-home .swiper-slide", parse_trending, container=soup),
                "latest_episode": scrape_page("recently-updated", self._parse_anime_card),
                "latest_completed": scrape_page("completed", self._parse_anime_card),
                "top_airing": scrape_page("top-airing", self._parse_anime_card, limit=7),
                "most_popular": scrape_page("most-popular", self._parse_anime_card, limit=7),
                "most_favorite": scrape_page("most-favorite", self._parse_anime_card, limit=7),
                "genres": [g.text.strip() for g in soup.select("#main-sidebar .sb-genre-list li a")]
            }

            logger.info(f"Final parsed data keys and item counts: { {k: len(v) for k, v in results.items()} }")
            return results, 200

        except Exception as e:
            logger.error(f"A critical error occurred in get_home_info: {e}", exc_info=True)
            return {"error": "An internal server error occurred while building homepage data."}, 500

    def get_anime_info(self, anime_id: str) -> tuple[dict, int]:
        show_id = anime_id.split('-')[-1]
        info_url = f"{V1_BASE_URL}/watch/{anime_id}"
        episodes_url = f"{V1_BASE_URL}/ajax/v2/episode/list/{show_id}"

        try:
            info_resp_text, info_status = self._make_request(info_url)
            if info_status != 200: raise HTTPError(f"Info request failed with status {info_status}")

            episodes_data, ep_status = self._make_request(episodes_url)
            if ep_status != 200: raise HTTPError(f"Episodes AJAX failed with status {ep_status}")

        except (RequestException, HTTPError) as e:
            logger.error(f"Failed to fetch initial data for {anime_id}: {e}")
            return {"error": "Could not fetch data for this anime."}, 500

        soup = BeautifulSoup(info_resp_text, "lxml")
        title_element = soup.select_one(".anisc-detail .film-name")

        main_info = {
            "id": anime_id,
            "data_id": show_id,
            "title": title_element.text.strip() if title_element else "N/A",
            "japanese_title": title_element.get("data-jname", "N/A") if title_element else "N/A",
            "poster_url": soup.select_one(".anisc-poster .film-poster-img").get("src") if soup.select_one(".anisc-poster .film-poster-img") else "",
            "synopsis": (soup.select_one(".anisc-detail .film-description .text").text.strip() if soup.select_one(".anisc-detail .film-description .text") else ""),
        }

        details = {}
        for item in soup.select(".anisc-info .item"):
            head_element = item.select_one(".item-head")
            if head_element:
                key = head_element.text.strip().lower().replace(":", "").replace(" ", "_")
                link_elements = item.select("a")
                if link_elements:
                    details[key] = [a.text.strip() for a in link_elements]
                else:
                    name_element = item.select_one(".name")
                    if name_element:
                        details[key] = name_element.text.strip()
        main_info.update(details)

        ep_soup = BeautifulSoup(episodes_data.get('html', ''), "lxml")
        episodes = [{
            "id": a_tag.get('href', '').split('/')[-1],
            "data_id": a_tag.get('data-id'),
            "episode_no": a_tag.get('data-number'),
            "title": a_tag.get('title'),
        } for a_tag in ep_soup.select(".ss-list a")]

        main_info["episodes"] = episodes
        main_info["total_episodes_count"] = len(episodes)

        related = [self._parse_anime_card(el) for el in soup.select("#main-sidebar .block-actors .flw-item")]
        recommended = [self._parse_anime_card(el) for el in soup.select("#main-content .block_area_realtime .flw-item")]

        return { **main_info, "related_anime": related, "recommended_anime": recommended }, 200

    def get_available_servers(self, episode_data_id: str) -> tuple[dict, int]:
        url = f"{V1_BASE_URL}/ajax/v2/episode/servers"
        params = {"episodeId": episode_data_id}
        data, status_code = self._make_request(url, params=params)
        if status_code != 200 or not isinstance(data, dict) or 'html' not in data:
            return {"error": "Failed to fetch server list"}, status_code
        soup = BeautifulSoup(data.get('html'), "lxml")
        servers = [{"type": i.get("data-type"), "data_id": i.get("data-id"), "server_name": i.select_one("a").get_text(strip=True)} for i in soup.select(".server-item")]
        return {"servers": servers}, 200

    def get_streaming_info(self, anime_id: str, episode_data_id: str, server_name: str, stream_type: str) -> tuple[dict, int]:
        servers_data, status_code = self.get_available_servers(episode_data_id)
        if status_code != 200 or not servers_data.get("servers"):
            return {"error": f"No streaming servers found for this episode (id: {episode_data_id})."}, 404
        target_server = next((s for s in servers_data["servers"] if s.get('server_name') == server_name and s.get('type') == stream_type), None)
        if not target_server:
            return {"error": f"Server '{server_name}' not available for this episode."}, 404
        sources_url = f"{V1_BASE_URL}/ajax/v2/episode/sources"
        params = {"id": target_server['data_id']}
        source_data, status_code = self._make_request(sources_url, params=params)
        if status_code != 200 or not source_data.get('link'):
            return {"error": "Could not retrieve source link."}, status_code
        embed_url = source_data['link']
        if not embed_url.startswith('http'):
            embed_url = f"https:{embed_url}"
        referer_header = embed_url
        try:
            source_id = embed_url.split('/')[-1].split('?')[0]
            final_source_url = f"{V4_BASE_URL}/ajax/embed-4/getSources"
            raw_stream_data, source_status = self._make_request(final_source_url, params={"id": source_id}, headers={'Referer': referer_header})
            if source_status != 200 or 'sources' not in raw_stream_data:
                 return {"error": "Failed to get encrypted source data from provider"}, source_status
        except Exception as e:
            return {"error": f"Failed to get encrypted source data: {e}"}, 500
        decrypted_sources = decrypt_source_url(raw_stream_data['sources'], self.decryption_key)
        if not decrypted_sources:
            return {"error": "Failed to decrypt streaming sources."}, 500
        original_m3u8_url = next((s.get('file') for s in decrypted_sources if s.get('file')), None)
        if not original_m3u8_url:
            return {"error": "No M3U8 file URL found."}, 404
        proxy_headers = {'Referer': referer_header}
        proxied_m3u8_url = f"/api/proxy/m3u8?url={quote(original_m3u8_url)}&headers={quote(json.dumps(proxy_headers))}"
        return {"streaming_links": [{"file": proxied_m3u8_url, "type": "hls"}], "tracks": raw_stream_data.get('tracks', [])}, 200

    def get_anime_by_category(self, category: str, page: int = 1) -> tuple[dict, int]:
        url = f"{V1_BASE_URL}/{category}"
        html_content, status_code = self._make_request(url, params={"page": page})
        if status_code != 200 or not isinstance(html_content, str): return html_content, status_code
        soup = BeautifulSoup(html_content, "lxml")
        container = soup.select_one(".film_list-wrap")
        if not container: return {"error": "Could not find anime list container."}, 404
        anime_list = [self._parse_anime_card(el) for el in container.select(".flw-item")]
        pagination = soup.select_one(".pagination")
        total_pages = 1
        if pagination and (last_page_el := pagination.select(".page-item a")[-1]):
            try:
                href_val = last_page_el.get('href', '')
                if 'page=' in href_val: total_pages = int(href_val.split('page=')[-1])
            except (ValueError, IndexError): pass
        return {"data": anime_list, "totalPages": total_pages, "currentPage": page}, 200

    def get_search_suggestions(self, keyword: str) -> tuple[dict, int]:
        url = f"{V1_BASE_URL}/ajax/search/suggest"
        data, status_code = self._make_request(url, params={"keyword": keyword})
        if status_code != 200 or not isinstance(data, dict): return data, status_code
        soup = BeautifulSoup(data.get('html', ''), "lxml")
        suggestions = []
        for a in soup.select(".nav-item a"):
            raw_href = a.get("href", "")
            cleaned_id = raw_href.replace("/watch/", "", 1).split("?")[0].strip("/") if raw_href else None
            suggestions.append({"id": cleaned_id, "title": a.select_one(".ss-title").text.strip(), "poster_url": a.select_one("img").get("src")})
        return {"results": suggestions}, 200

    def search_anime(self, filters: dict) -> tuple[dict, int]:
        url = f"{V1_BASE_URL}/filter"
        html_content, status_code = self._make_request(url, params=filters)
        if status_code != 200 or not isinstance(html_content, str): return html_content, status_code
        soup = BeautifulSoup(html_content, "lxml")
        container = soup.select_one(".film_list-wrap")
        if not container: return {"error": "Could not find anime list container."}, 404
        anime_list = [self._parse_anime_card(el) for el in container.select(".flw-item")]
        return {"results": anime_list}, 200

    def get_qtip_info(self, anime_id: str) -> tuple[dict, int]:
        data_id = anime_id.split('-')[-1]
        url = f"{V1_BASE_URL}/ajax/film/tooltip/{data_id}"
        html_content, status_code = self._make_request(url)
        if status_code != 200 or not isinstance(html_content, str): return html_content, status_code
        soup = BeautifulSoup(html_content, "lxml")
        data = { "title": soup.select_one(".film-name").text.strip(), "description": soup.select_one(".film-description").text.strip()}
        for detail in soup.select(".fd-infor .item-title"):
            key, value = detail.text.strip().lower().replace(":", ""), detail.find_next_sibling("span").text.strip()
            data[key] = value
        return data, 200

    def get_top_ten_anime(self) -> tuple[dict, int]:
        return self.get_home_info()

# backend/controllers/shikimori_controller.py
from services.shikimori_api_service import ShikimoriAPIService

class ShikimoriController:
    """
    Controller for handling Shikimori (anime/manga/character/person) data.
    Interacts with the ShikimoriAPIService and prepares data for API routes.
    """
    # Initialize the service as a class attribute
    shikimori_service = ShikimoriAPIService()

    @staticmethod
    def search_anime_data(query: str, limit: int = 10):
        """
        Searches for anime titles on Shikimori.
        """
        print(f"DEBUG: ShikimoriController: Searching anime for query: '{query}' with limit: {limit}")
        # CORRECTED: Changed search_anime to search_animes
        animes = ShikimoriController.shikimori_service.search_animes(query, limit)
        if animes is None:
            return {"error": "Could not retrieve anime data from Shikimori."}, 500

        formatted_animes = []
        for anime in animes:
            # Ensure safe access to nested dictionary keys
            aired_on_year = anime.get("airedOn", {}).get("year")
            poster_url = anime.get("poster", {}).get("mainUrl") or anime.get("poster", {}).get("url") # Fallback for now if mainUrl is missing

            formatted_animes.append({
                "id": anime.get("id"),
                "name": anime.get("name"),
                "russian_name": anime.get("russian"),
                "aired_year": aired_on_year,
                "poster_url": poster_url
            })
        return formatted_animes, 200

    @staticmethod
    def get_anime_details_data(anime_id: int):
        """
        Fetches detailed information for a specific anime ID on Shikimori.
        """
        print(f"DEBUG: Shikimori: Anime details requested for ID: {anime_id}")
        anime_details = ShikimoriController.shikimori_service.get_anime_details(anime_id)
        if anime_details is None:
            return {"error": "Could not retrieve anime details from Shikimori."}, 500

        # Shikimori returns a list for 'get_anime_details' when using 'animes(ids: [$id])'
        # We expect a list with one item, so get the first one.
        if isinstance(anime_details, list) and anime_details:
            anime_details = anime_details[0]
        elif not anime_details: # Handle empty list or non-list responses
            return {"error": "Anime details not found for the given ID."}, 404


        # Format the data as needed for your API response
        formatted_details = {
            "id": anime_details.get("id"),
            "name": anime_details.get("name"),
            "russian_name": anime_details.get("russian"),
            "kind": anime_details.get("kind"),
            "episodes": anime_details.get("episodes"),
            "status": anime_details.get("status"),
            "aired_date": anime_details.get("airedOn", {}).get("date"),
            "released_date": anime_details.get("releasedOn", {}).get("date"),
            "poster_original_url": anime_details.get("poster", {}).get("originalUrl"),
            "poster_main_url": anime_details.get("poster", {}).get("mainUrl"),
            "description": anime_details.get("description"),
            "description_html": anime_details.get("descriptionHtml"),
            "description_source": anime_details.get("descriptionSource")
        }
        return formatted_details, 200

    @staticmethod
    def get_recent_animes_data(limit: int = 5):
        """
        Fetches a list of recently added or updated anime on Shikimori.
        """
        print(f"DEBUG: ShikimoriController: Getting recent animes with limit: {limit}")
        recent_animes = ShikimoriController.shikimori_service.get_recent_animes(limit)
        if recent_animes is None:
            return {"error": "Could not retrieve recent anime data from Shikimori."}, 500

        formatted_recent_animes = []
        for anime in recent_animes:
            aired_on_year = anime.get("airedOn", {}).get("year")
            poster_url = anime.get("poster", {}).get("mainUrl") or anime.get("poster", {}).get("url") # Fallback for now if mainUrl is missing

            formatted_recent_animes.append({
                "id": anime.get("id"),
                "name": anime.get("name"),
                "russian_name": anime.get("russian"),
                "aired_year": aired_on_year,
                "status": anime.get("status"),
                "poster_url": poster_url
            })
        return formatted_recent_animes, 200

    @staticmethod
    def search_manga_data(query: str, limit: int = 10):
        """
        Searches for manga titles on Shikimori.
        """
        print(f"DEBUG: ShikimoriController: Searching manga for query: '{query}' with limit: {limit}")
        # CORRECTED: Changed search_manga to search_mangas
        mangas = ShikimoriController.shikimori_service.search_mangas(query, limit)
        if mangas is None:
            return {"error": "Could not retrieve manga data from Shikimori."}, 500

        formatted_mangas = []
        for manga in mangas:
            poster_url = manga.get("poster", {}).get("mainUrl") or manga.get("poster", {}).get("url") # Fallback for now

            formatted_mangas.append({
                "id": manga.get("id"),
                "name": manga.get("name"),
                "russian_name": manga.get("russian"),
                "volumes": manga.get("volumes"),
                "chapters": manga.get("chapters"),
                "status": manga.get("status"),
                "poster_url": poster_url
            })
        return formatted_mangas, 200

    @staticmethod
    def get_recent_mangas_data(limit: int = 5):
        """
        Fetches a list of recently added or updated manga on Shikimori.
        """
        print(f"DEBUG: ShikimoriController: Getting recent mangas with limit: {limit}")
        recent_mangas = ShikimoriController.shikimori_service.get_recent_mangas(limit)
        if recent_mangas is None:
            return {"error": "Could not retrieve recent manga data from Shikimori."}, 500

        formatted_recent_mangas = []
        for manga in recent_mangas:
            poster_url = manga.get("poster", {}).get("mainUrl") or manga.get("poster", {}).get("url") # Fallback for now

            formatted_recent_mangas.append({
                "id": manga.get("id"),
                "name": manga.get("name"),
                "russian_name": manga.get("russian"),
                "volumes": manga.get("volumes"),
                "chapters": manga.get("chapters"),
                "status": manga.get("status"),
                "poster_url": poster_url
            })
        return formatted_recent_mangas, 200

    @staticmethod
    def search_characters_data(query: str, limit: int = 10):
        """
        Searches for characters on Shikimori.
        """
        print(f"DEBUG: ShikimoriController: Searching characters for query: '{query}' with limit: {limit}")
        characters = ShikimoriController.shikimori_service.search_characters(query, limit)
        if characters is None:
            return {"error": "Could not retrieve character data from Shikimori."}, 500

        formatted_characters = []
        for char in characters:
            poster_url = char.get("poster", {}).get("mainUrl") or char.get("poster", {}).get("url") # Fallback for now

            formatted_characters.append({
                "id": char.get("id"),
                "name": char.get("name"),
                "russian_name": char.get("russian"),
                "poster_url": poster_url
            })
        return formatted_characters, 200

    @staticmethod
    def get_character_details_data(character_id: int):
        """
        Fetches detailed information for a specific character ID on Shikimori.
        """
        print(f"DEBUG: ShikimoriController: Getting details for character ID: {character_id}")
        character_details = ShikimoriController.shikimori_service.get_character_details(character_id)
        if character_details is None:
            return {"error": "Could not retrieve character details from Shikimori."}, 500

        if isinstance(character_details, list) and character_details:
            character_details = character_details[0]
        elif not character_details:
            return {"error": "Character details not found for the given ID."}, 404

        formatted_details = {
            "id": character_details.get("id"),
            "name": character_details.get("name"),
            "russian_name": character_details.get("russian"),
            "description": character_details.get("description"),
            "description_html": character_details.get("descriptionHtml"),
            "description_source": character_details.get("descriptionSource"),
            "poster_url": character_details.get("poster", {}).get("originalUrl") or character_details.get("poster", {}).get("mainUrl") # Use originalUrl or mainUrl
        }
        return formatted_details, 200

    @staticmethod
    def search_people_data(query: str, limit: int = 10):
        """
        Searches for people (voice actors, staff, etc.) on Shikimori.
        """
        print(f"DEBUG: ShikimoriController: Searching people for query: '{query}' with limit: {limit}")
        people = ShikimoriController.shikimori_service.search_people(query, limit)
        if people is None:
            return {"error": "Could not retrieve people data from Shikimori."}, 500

        formatted_people = []
        for person in people:
            poster_url = person.get("poster", {}).get("mainUrl") or person.get("poster", {}).get("url") # Fallback for now

            formatted_people.append({
                "id": person.get("id"),
                "name": person.get("name"),
                "russian_name": person.get("russian"),
                "poster_url": poster_url
            })
        return formatted_people, 200

    @staticmethod
    def get_person_details_data(person_id: int):
        """
        Fetches detailed information for a specific person ID on Shikimori.
        """
        print(f"DEBUG: ShikimoriController: Getting details for person ID: {person_id}")
        person_details = ShikimoriController.shikimori_service.get_person_details(person_id)
        if person_details is None:
            return {"error": "Could not retrieve person details from Shikimori."}, 500

        if isinstance(person_details, list) and person_details:
            person_details = person_details[0]
        elif not person_details:
            return {"error": "Person details not found for the given ID."}, 404

        formatted_details = {
            "id": person_details.get("id"),
            "name": person_details.get("name"),
            "russian_name": person_details.get("russian"),
            "website": person_details.get("website"),
            "poster_original_url": person_details.get("poster", {}).get("originalUrl"),
            "poster_main_url": person_details.get("poster", {}).get("mainUrl")
        }
        return formatted_details, 200

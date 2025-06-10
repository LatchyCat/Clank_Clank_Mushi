# backend/controllers/one_piece_controller.py
from services.one_piece_api_service import OnePieceAPIService

class OnePieceController:
    """
    Controller for handling One Piece manga/anime data.
    Interacts with the OnePieceAPIService and prepares data for API routes.
    """

    @staticmethod
    def get_sagas_data():
        """
        Fetches all One Piece sagas and formats them for the API response.
        """
        sagas = OnePieceAPIService.get_all_sagas()
        if sagas is None:
            return {"error": "Could not retrieve One Piece sagas."}, 500

        # Basic formatting (you can expand this with more fields if the API provides them)
        formatted_sagas = []
        for saga in sagas:
            formatted_sagas.append({
                "id": saga.get("id"),
                "title": saga.get("title"),
                "number_of_arcs": saga.get("number_of_arcs") # Example field
                # Add other fields from the API response as desired
            })
        return formatted_sagas, 200

    @staticmethod
    def get_characters_data():
        """
        Fetches all One Piece characters and formats them for the API response.
        """
        characters = OnePieceAPIService.get_all_characters()
        if characters is None:
            return {"error": "Could not retrieve One Piece characters."}, 500

        formatted_characters = []
        for char in characters:
            formatted_characters.append({
                "id": char.get("id"),
                "name": char.get("name"),
                "gender": char.get("gender"),
                "status": char.get("status")
                # Add other relevant fields (e.g., bounty, crew, etc.)
            })
        return formatted_characters, 200

    @staticmethod
    def get_fruits_data():
        """
        Fetches all One Piece fruits (Devil Fruits) and formats them for the API response.
        """
        fruits = OnePieceAPIService.get_all_fruits()
        if fruits is None:
            return {"error": "Could not retrieve One Piece fruits."}, 500

        formatted_fruits = []
        for fruit in fruits:
            formatted_fruits.append({
                "id": fruit.get("id"),
                "name": fruit.get("name"),
                "type": fruit.get("type"),
                "description": fruit.get("description")
            })
        return formatted_fruits, 200

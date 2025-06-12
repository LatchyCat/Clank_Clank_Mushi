# backend/routes/one_piece_api_routes.py
from flask import Blueprint, jsonify
from controllers.one_piece_controller import OnePieceController # Import the new controller

# Create a Blueprint for One Piece-related API routes
# All routes defined in this blueprint will be prefixed with '/api/one-piece'
one_piece_api_bp = Blueprint('one_piece_api', __name__, url_prefix='/api/one-piece')

@one_piece_api_bp.route('/sagas', methods=['GET'])
def get_one_piece_sagas():
    """
    API endpoint to get all One Piece sagas.
    Example: GET /api/one-piece/sagas
    """
    sagas, status_code = OnePieceController.get_sagas_data()
    return jsonify(sagas), status_code

@one_piece_api_bp.route('/characters', methods=['GET'])
def get_one_piece_characters():
    """
    API endpoint to get all One Piece characters.
    Example: GET /api/one-piece/characters
    """
    characters, status_code = OnePieceController.get_characters_data()
    return jsonify(characters), status_code

@one_piece_api_bp.route('/fruits', methods=['GET'])
def get_one_piece_fruits():
    """
    API endpoint to get all One Piece fruits (Devil Fruits).
    Example: GET /api/one-piece/fruits
    """
    fruits, status_code = OnePieceController.get_fruits_data()
    return jsonify(fruits), status_code

# You can add more specific One Piece routes here (e.g., by ID) later

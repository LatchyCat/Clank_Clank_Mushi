# backend/routes/suggest_questions.py
from flask import Blueprint, jsonify, request
from controllers.llm_controller import LLMController # Need to import LLMController
from typing import Dict, Any, Tuple # Import Dict, Any, Tuple for type hinting jsonify response

# Create a Blueprint for suggested questions routes
# This blueprint will handle routes like /api/llm/suggest-questions
# We're reusing the /api/llm prefix for consistency with other LLM features
suggest_questions_bp = Blueprint('suggest_questions_api', __name__, url_prefix='/api/llm')

@suggest_questions_bp.route('/suggest-questions', methods=['POST'])
def suggest_questions() -> Tuple[Dict[str, Any], int]: # Changed return type hint
    """
    API endpoint to generate suggested questions based on provided content.
    Expects a JSON body with a 'content' field.
    Returns a JSON object with 'suggested_questions' (list of strings) and
    'similar_anime_note' (optional string).
    Example: POST /api/llm/suggest-questions
    Request Body: {"content": "The Straw Hat Pirates landed on Egghead Island..."}
    """
    # Check if the request method is POST before trying to get JSON
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "Request must contain a JSON body."}), 400

            content_to_analyze = data.get('content')

            if not content_to_analyze:
                return jsonify({"error": "Missing 'content' field in request body for question suggestion."}), 400

            # Call the LLMController's 'suggest_followup_questions' method
            # This method now returns a dictionary with 'suggested_questions' and 'similar_anime_note'
            response_data, status_code = LLMController.suggest_followup_questions(content_to_analyze)

            if status_code == 200:
                # Return the structured data directly
                return jsonify(response_data), status_code
            else:
                # If an error, response_data will contain the error message within 'similar_anime_note'
                # or a general error if something else went wrong.
                error_message = response_data.get("similar_anime_note", "An unknown error occurred during suggestion generation.")
                return jsonify({"error": error_message}), status_code
        except Exception as e:
            # Catch any error during JSON parsing or data retrieval for robustness
            print(f"ERROR in suggest_questions route: {e}") # Debugging
            return jsonify({"error": f"An error occurred while processing your request: {str(e)}"}), 500 # Use 500 for server-side errors
    else:
        # This branch should ideally not be hit if Flask-CORS is working correctly for OPTIONS
        # but it serves as a fallback/defensive measure.
        return jsonify({"message": "Method not allowed."}), 405

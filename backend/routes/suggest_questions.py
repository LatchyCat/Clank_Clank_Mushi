# backend/routes/suggest_questions.py
from flask import Blueprint, jsonify, request
from controllers.llm_controller import LLMController # Need to import LLMController

# Create a Blueprint for suggested questions routes
# This blueprint will handle routes like /api/llm/suggest-questions
# We're reusing the /api/llm prefix for consistency with other LLM features
suggest_questions_bp = Blueprint('suggest_questions_api', __name__, url_prefix='/api/llm')

@suggest_questions_bp.route('/suggest-questions', methods=['POST'])
def suggest_questions():
    """
    API endpoint to generate suggested questions based on provided content.
    Expects a JSON body with a 'content' field.
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

            # Call the LLMController to generate suggested questions
            suggested_questions, status_code = LLMController.generate_suggested_questions(content_to_analyze)

            if status_code == 200:
                return jsonify({"suggested_questions": suggested_questions}), status_code
            else:
                return jsonify({"error": suggested_questions}), status_code
        except Exception as e:
            # Catch any error during JSON parsing or data retrieval for robustness
            return jsonify({"error": f"An error occurred while processing your request: {str(e)}"}), 400
    else:
        # This branch should ideally not be hit if Flask-CORS is working correctly for OPTIONS
        # but it serves as a fallback/defensive measure.
        return jsonify({"message": "Method not allowed."}), 405

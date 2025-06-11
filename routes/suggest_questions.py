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
    data = request.get_json()
    content_to_analyze = data.get('content')

    if not content_to_analyze:
        return jsonify({"error": "Missing 'content' field in request body for question suggestion."}), 400

    # Call the LLMController to generate suggested questions
    # We'll add this method in the next step
    suggested_questions, status_code = LLMController.generate_suggested_questions(content_to_analyze)

    if status_code == 200:
        return jsonify({"suggested_questions": suggested_questions}), status_code
    else:
        return jsonify({"error": suggested_questions}), status_code

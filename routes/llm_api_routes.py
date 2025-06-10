# backend/routes/llm_api_routes.py
from flask import Blueprint, jsonify, request
from controllers.llm_controller import LLMController # Import our new LLMController

# Create a Blueprint for LLM-related API routes
# All routes defined in this blueprint will be prefixed with '/api/llm'
llm_api_bp = Blueprint('llm_api', __name__, url_prefix='/api/llm')

@llm_api_bp.route('/chat', methods=['POST'])
def chat_with_llm():
    """
    API endpoint for sending user queries to the configured LLM (Mushi).
    Expects a JSON body with a 'query' field.
    Example: POST /api/llm/chat
    Request Body: {"query": "Tell me about Monkey D. Luffy."}
    """
    data = request.get_json()
    user_query = data.get('query')

    if not user_query:
        return jsonify({"error": "Missing 'query' field in request body."}), 400

    # Call the LLMController to generate a response
    llm_response, status_code = LLMController.generate_llm_response(user_query)

    if status_code == 200:
        return jsonify({"response": llm_response}), status_code
    else:
        return jsonify({"error": llm_response}), status_code

# You can add more LLM-related endpoints here if needed in the future
# e.g., for different LLM tasks like summarization, specific lore extraction, etc.

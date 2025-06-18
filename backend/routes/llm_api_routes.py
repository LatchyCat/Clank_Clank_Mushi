# backend/routes/llm_api_routes.py
from flask import Blueprint, jsonify, request, Response, stream_with_context
from controllers.llm_controller import LLMController

llm_api_bp = Blueprint('llm_api', __name__, url_prefix='/api/llm')

@llm_api_bp.route('/chat', methods=['POST'])
def chat_with_llm():
    data = request.get_json()
    user_query = data.get('query')
    history = data.get('history', [])

    if not user_query:
        return jsonify({"error": "Missing 'query' field in request body."}), 400

    response_generator = LLMController.generate_llm_response(user_query, history)
    return Response(stream_with_context(response_generator), mimetype='application/x-ndjson')

@llm_api_bp.route('/resolve-link', methods=['POST'])
def resolve_link_route():
    """
    A new dedicated endpoint to resolve an anime title into a URL.
    """
    data = request.get_json()
    anime_title = data.get('title')
    if not anime_title:
        return jsonify({"error": "Missing 'title' field in request body."}), 400

    response_data, status_code = LLMController.resolve_link_data(anime_title)
    return jsonify(response_data), status_code

@llm_api_bp.route('/providers', methods=['GET'])
def get_llm_providers_route():
    return jsonify(LLMController.get_llm_providers()), 200

@llm_api_bp.route('/set-provider', methods=['POST'])
def set_llm_provider_route():
    data = request.get_json()
    provider_key = data.get('provider')
    message, status_code = LLMController.set_llm_provider(provider_key)
    return jsonify({"message": message}) if status_code == 200 else jsonify({"error": message}), status_code

@llm_api_bp.route('/current_provider', methods=['GET'])
def get_current_llm_provider_route():
    current_provider_data, status_code = LLMController.get_current_llm_provider()
    return jsonify(current_provider_data), status_code

@llm_api_bp.route('/suggest-questions', methods=['POST'])
def suggest_questions_route():
    conversation_context = request.get_json()
    if not conversation_context:
        return jsonify({"error": "Missing JSON request body"}), 400

    if "user_query" not in conversation_context or "mushi_response" not in conversation_context:
        return jsonify({"error": "Request body must contain 'user_query' and 'mushi_response' fields."}), 400

    suggested_data, status_code = LLMController.suggest_followup_questions(conversation_context)
    return jsonify(suggested_data), status_code

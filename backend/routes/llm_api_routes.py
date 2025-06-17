# backend/routes/llm_api_routes.py
from flask import Blueprint, jsonify, request, Response, stream_with_context
from controllers.llm_controller import LLMController

llm_api_bp = Blueprint('llm_api', __name__, url_prefix='/api/llm')

@llm_api_bp.route('/chat', methods=['POST'])
def chat_with_llm():
    """
    API endpoint for sending user queries to the configured LLM (Mushi).
    Expects a JSON body with a 'query' field and an optional 'history' field.
    Returns a streaming response.
    """
    data = request.get_json()
    user_query = data.get('query')
    history = data.get('history', [])

    if not user_query:
        return jsonify({"error": "Missing 'query' field in request body."}), 400

    response_generator = LLMController.generate_llm_response(user_query, history)
    return Response(stream_with_context(response_generator), mimetype='text/event-stream')

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
    # --- START OF CHANGE ---
    # REASON FOR CHANGE: Previously, this route expected a single 'content' string.
    # It now expects a full JSON object containing the conversation context.
    # We get the entire JSON payload and pass it directly to the controller,
    # which now knows how to handle this richer dictionary structure.
    conversation_context = request.get_json()
    if not conversation_context:
        return jsonify({"error": "Missing JSON request body"}), 400

    suggested_data, status_code = LLMController.suggest_followup_questions(conversation_context)
    # --- END OF CHANGE ---
    return jsonify(suggested_data), status_code

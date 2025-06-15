# backend/routes/llm_api_routes.py
from flask import Blueprint, jsonify, request, Response, stream_with_context # NEW: Import Response and stream_with_context
from controllers.llm_controller import LLMController # Import our LLMController

# Create a Blueprint for LLM-related API routes
# All routes defined in this blueprint will be prefixed with '/api/llm'
llm_api_bp = Blueprint('llm_api', __name__, url_prefix='/api/llm')

@llm_api_bp.route('/chat', methods=['POST'])
def chat_with_llm():
    """
    API endpoint for sending user queries to the configured LLM (Mushi).
    Expects a JSON body with a 'query' field.
    Returns a streaming response.
    """
    data = request.get_json()
    user_query = data.get('query')

    if not user_query:
        # For non-streaming error, we still return JSON with 400 status
        return jsonify({"error": "Missing 'query' field in request body."}), 400

    # Call the LLMController's streaming generation function
    # stream_with_context ensures the Flask app context is available within the generator
    response_generator = LLMController.generate_llm_response(user_query)

    # Return a streaming response with appropriate MIME type
    # Each yielded chunk from the generator will be sent directly to the client
    return Response(stream_with_context(response_generator), mimetype='text/event-stream')


@llm_api_bp.route('/providers', methods=['GET'])
def get_llm_providers_route():
    """
    API endpoint to get the list of available LLM providers.
    """
    # Calls a static method from LLMController to get the list
    return jsonify(LLMController.get_llm_providers()), 200

@llm_api_bp.route('/set-provider', methods=['POST'])
def set_llm_provider_route():
    """
    API endpoint to set the active LLM provider.
    Expects a JSON body with a 'provider' field.
    """
    data = request.get_json()
    provider_key = data.get('provider')

    # Calls a static method from LLMController to handle the logic
    message, status_code = LLMController.set_llm_provider(provider_key)
    return jsonify({"message": message}) if status_code == 200 else jsonify({"error": message}), status_code

@llm_api_bp.route('/current_provider', methods=['GET'])
def get_current_llm_provider_route():
    """
    API endpoint to get the currently selected LLM provider.
    This is called by the frontend's ProviderSelector on load.
    """
    # Calls a static method from LLMController
    current_provider_data, status_code = LLMController.get_current_llm_provider()
    return jsonify(current_provider_data), status_code

@llm_api_bp.route('/suggest-questions', methods=['POST'])
def suggest_questions_route():
    """
    API endpoint to get suggested follow-up questions from the LLM.
    Expects a JSON body with a 'content' field (the last LLM response).
    """
    data = request.get_json()
    last_response_text = data.get('content')

    if not last_response_text:
        return jsonify({"error": "Missing 'content' field in request body."}), 400

    suggested_data, status_code = LLMController.suggest_followup_questions(last_response_text)
    return jsonify(suggested_data), status_code


# backend/controllers/llm_controller.py
import re
import urllib.parse
import json
from typing import List, Dict, Any, Tuple, Optional, Generator

from services.ollama_llm_service import OllamaLLMService
from config import Config
from globals import global_vector_store, global_ollama_embedder, global_anime_controller

class LLMController:

    @staticmethod
    def get_llm_providers() -> Dict[str, str]:
        return Config.LLM_PROVIDERS

    @staticmethod
    def set_llm_provider(provider_key: str) -> Tuple[str, int]:
        if provider_key in Config.LLM_PROVIDERS:
            Config.CURRENT_GENERATION_LLM = provider_key
            return f"LLM provider set to {provider_key}", 200
        return "Invalid LLM provider", 400

    @staticmethod
    def get_current_llm_provider() -> Tuple[Dict[str, str], int]:
        return {"current_provider": Config.CURRENT_GENERATION_LLM}, 200

    @staticmethod
    def resolve_link_data(anime_title: str) -> Tuple[Dict[str, Any], int]:
        suggestions_data, status_code = global_anime_controller.get_search_suggestions_data(anime_title)
        if status_code == 200 and suggestions_data.get("results"):
            top_suggestion = suggestions_data["results"][0]
            anime_id = top_suggestion.get("id")
            official_title = top_suggestion.get("title", anime_title)
            if anime_id:
                return {"title": official_title, "url": f"/anime/details/{anime_id}"}, 200

        encoded_title = urllib.parse.quote(anime_title)
        return {"title": anime_title, "url": f"/search?keyword={encoded_title}"}, 200

    @staticmethod
    def _find_and_verify_links(text: str) -> str:
        pattern = re.compile(r'\b(?:[A-Z][\w\'\-.:!&]*\s+){1,6}[A-Z][\w\'\-.:!&]*\b')
        matches = pattern.finditer(text)
        ignore_list = {"The", "A", "An", "Is", "It", "Of", "And", "He", "She", "They", "One Piece", "Naruto Shippuden"}
        replacements = []
        for match in matches:
            potential_title = match.group(0).strip()
            if potential_title not in ignore_list and len(potential_title) > 3:
                 replacements.append((potential_title, f'[LINK:{potential_title}]'))
        replacements.sort(key=lambda x: len(x[0]), reverse=True)
        processed_text = text
        for old, new in replacements:
            processed_text = re.sub(r'\b' + re.escape(old) + r'\b', new, processed_text)
        return processed_text

    @staticmethod
    def generate_llm_response(user_query: str, history: Optional[List[Dict]] = None) -> Generator[str, None, None]:
        try:
            current_llm_key = Config.CURRENT_GENERATION_LLM
            if current_llm_key == 'gemini':
                yield json.dumps({"type": "error", "content": "Gemini provider is not fully implemented yet."}) + "\n"
                return
            elif current_llm_key == 'ollama_qwen3':
                llm_service = OllamaLLMService(model_name=Config.OLLAMA_QWEN3_MODEL_NAME)
            else:
                 yield json.dumps({"type": "error", "content": f"No valid LLM provider configured. Current is '{current_llm_key}'"}) + "\n"
                 return
        except Exception as e:
            yield json.dumps({"type": "error", "content": f"Error initializing LLM service: {e}"}) + "\n"
            return

        user_query_embedding = global_ollama_embedder.embed_text(user_query)
        rag_context = ""
        if user_query_embedding:
            relevant_docs = global_vector_store.similarity_search(user_query_embedding, top_k=5)
            if relevant_docs:
                rag_context = "\n\n---CONTEXT---\n" + "\n".join([doc.get('content', '') for doc in relevant_docs]) + "\n---END CONTEXT---\n"

        history_context = ""
        if history:
            formatted_history = [f"{'User' if msg.get('sender') == 'user' else 'Mushi'}: {msg.get('text')}" for msg in history]
            history_context = "\n\n---CONVERSATION HISTORY (FOR CONTEXT)---\n" + "\n".join(formatted_history) + "\n---END HISTORY---\n"

        final_prompt_for_llm = f"{history_context}{rag_context}\n\nUser Query: {user_query}"

        full_response_text = ""
        try:
            for chunk in llm_service.stream_formatted_response(final_prompt_for_llm):
                full_response_text += chunk
        except Exception as e:
             yield json.dumps({"type": "error", "content": f"Error during LLM stream: {str(e)}"}) + "\n"
             return

        if not full_response_text or full_response_text.startswith("Error:"):
            yield json.dumps({"type": "error", "content": full_response_text or "LLM returned no response."}) + "\n"
            return

        # --- START OF DEFINITIVE FIX ---
        # Strip all unwanted tags before sending any part of the response.

        # 1. Extract and remove the <mood> tag
        mood_match = re.search(r'<mood>(.*?)</mood>', full_response_text, re.IGNORECASE)
        mood = 'happy'
        if mood_match:
            mood = mood_match.group(1).strip().lower()
            full_response_text = full_response_text.replace(mood_match.group(0), '', 1).strip()

        # 2. Remove any <think> blocks completely.
        full_response_text = re.sub(r'<think>.*?</think>', '', full_response_text, flags=re.DOTALL).strip()

        # 3. Remove any other stray tags that might have been generated.
        full_response_text = re.sub(r'<[^>]+>', '', full_response_text).strip()
        # --- END OF DEFINITIVE FIX ---

        # Now we can safely yield the processed data
        yield json.dumps({"type": "mood", "content": mood}) + "\n"

        final_text = LLMController._find_and_verify_links(full_response_text)
        yield json.dumps({"type": "text", "content": final_text}) + "\n"


    @staticmethod
    def suggest_followup_questions(conversation_context: Dict[str, str]) -> Tuple[Dict[str, Any], int]:
        user_query = conversation_context.get("user_query")
        mushi_response = conversation_context.get("mushi_response")
        if not user_query or not mushi_response:
            return {"suggested_questions": []}, 200

        question_generation_prompt = f"""
        Based on the following conversation turn:
        USER ASKED: "{user_query}"
        MUSHI ANSWERED: "{mushi_response}"

        Generate exactly 3 diverse and insightful follow-up questions a user might ask next.
        RULES:
        1. Output ONLY the 3 questions, separated by "|||".
        2. DO NOT use any special tags, numbering, or bullet points.
        EXAMPLE OUTPUT: What are some other anime with a complex magic system?|||How does the power scaling in that anime compare to others?|||Are there any characters who question the morality of the magic system?
        """
        llm_service = OllamaLLMService(model_name=Config.OLLAMA_QWEN3_MODEL_NAME)
        llm_raw_response = llm_service.get_simple_response(question_generation_prompt)

        if not llm_raw_response or llm_raw_response.startswith("Error:"):
            return {"error": llm_raw_response or "Failed to generate suggestions."}, 500

        questions = [q.strip().strip('"') for q in llm_raw_response.split('|||') if q.strip()]
        final_questions = [re.sub(r'^\s*[-*]?\s*\d*\.\s*', '', q) for q in questions]

        return {"suggested_questions": final_questions[:3]}, 200

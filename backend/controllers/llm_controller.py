# backend/controllers/llm_controller.py
import re
import urllib.parse
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
    def _create_link_from_active_search(anime_title: str) -> Optional[str]:
        """Actively searches for an anime title to get its ID and create a details page link."""
        print(f"DEBUG: Active search for '{anime_title}'...")
        suggestions_data, status_code = global_anime_controller.get_search_suggestions_data(anime_title)

        if status_code == 200 and suggestions_data.get("results"):
            normalized_search_title = ''.join(filter(str.isalnum, anime_title.lower()))
            for suggestion in suggestions_data["results"]:
                suggestion_title = suggestion.get("title", "")
                normalized_suggestion_title = ''.join(filter(str.isalnum, suggestion_title.lower()))
                if normalized_search_title in normalized_suggestion_title:
                    anime_id = suggestion.get("id")
                    official_title = suggestion.get("title", anime_title)
                    if anime_id:
                        link = f"[{official_title}](/anime/details/{anime_id})"
                        print(f"DEBUG: Active search successful. Matched '{anime_title}' to '{official_title}'. Link: {link}")
                        return link

        print(f"DEBUG: Active search for details page failed for '{anime_title}'.")
        return None

    @staticmethod
    def _resolve_link(anime_title: str, context_docs: List[Dict]) -> str:
        """
        Attempts to create a markdown link for an anime.
        1. Checks context docs.
        2. Performs an active API search for a details page.
        3. As a fallback, creates a link to the site's search page.
        """
        # 1. Check context first
        normalized_title = ''.join(filter(str.isalnum, anime_title.lower()))
        for doc in context_docs:
            doc_metadata = doc.get("metadata", {})
            doc_title = doc_metadata.get("title", "")
            normalized_doc_title = ''.join(filter(str.isalnum, doc_title.lower()))
            if doc_metadata.get("type") == "anime_details" and normalized_title in doc_title:
                anime_id = doc_metadata.get("anime_id")
                if anime_id:
                    return f" [{doc_metadata.get('title', anime_title)}](/anime/details/{anime_id}) "

        # 2. Perform a live API search for a details page
        details_link = LLMController._create_link_from_active_search(anime_title)
        if details_link:
            return details_link

        # 3. FALLBACK: Create a link to the search page
        encoded_title = urllib.parse.quote(anime_title)
        search_link = f" [{anime_title}](/search?keyword={encoded_title}) "
        print(f"DEBUG: Fallback search link created for '{anime_title}': {search_link}")
        return search_link

    @staticmethod
    def generate_llm_response(user_query: str, history: Optional[List[Dict]] = None) -> Generator[str, None, None]:
        """
        Orchestrates the generation system, now with conversational history.
        """
        # --- Format Conversation History ---
        history_context = ""
        if history:
            formatted_history = []
            for msg in history:
                role = "User" if msg.get('sender') == 'user' else "Mushi"
                formatted_history.append(f"{role}: {msg.get('text')}")
            history_context = "\n\n---CONVERSATION HISTORY (FOR CONTEXT)---\n" + "\n".join(formatted_history) + "\n---END HISTORY---\n"

        # --- RAG Context Retrieval (Same as before) ---
        rag_context = ""
        relevant_docs = []
        # We embed the full conversation history plus the new query to get the most relevant context
        full_query_for_embedding = f"{history_context}\n\n{user_query}"
        user_query_embedding = global_ollama_embedder.embed_text(full_query_for_embedding)

        if user_query_embedding:
            relevant_docs = global_vector_store.similarity_search(user_query_embedding, top_k=5)
            if relevant_docs:
                rag_context = "\n\n---CONTEXT---\n" + "\n".join([doc.get('content', '') for doc in relevant_docs]) + "\n---END CONTEXT---\n"

        # Combine history, RAG context, and the new query into the final prompt
        prompt_with_context = f"{history_context}{rag_context}\n\nUser Query: {user_query}"

        # --- Determine which LLM service to use ---
        current_llm_key = Config.CURRENT_GENERATION_LLM
        if current_llm_key.startswith("ollama"):
            model_name = Config.OLLAMA_ANIME_MODEL_NAME if current_llm_key == "ollama_anime" else Config.OLLAMA_QWEN_MODEL_NAME
            llm_service = OllamaLLMService(model_name=model_name)
        else:
            yield "Error: No valid LLM provider configured."
            return

        # --- Single-Pass Hybrid Generation ---
        hybrid_prompt = (
            f"You are Mushi, an AI assistant. Use the CONVERSATION HISTORY and CONTEXT to answer the user's query. If the context is not relevant, use your general knowledge. "
            f"When you mention any anime title, you MUST wrap it in the `[LINK: Full Anime Title]` command. "
            f"When providing a list, you MUST use markdown bullet points and add a blank line between each item.\n"
            f"{prompt_with_context}"
        )

        response_generator = llm_service.stream_formatted_response(hybrid_prompt)
        buffer = ""
        for chunk in response_generator:
            if chunk.startswith("Error:"):
                yield chunk
                return
            buffer += chunk
            while (match := re.search(r'\[LINK:\s*(.*?)\s*\]', buffer)):
                text_before_command = buffer[:match.start()]
                if text_before_command:
                    yield text_before_command

                anime_title_to_resolve = match.group(1).strip()
                resolved_link_or_text = LLMController._resolve_link(anime_title_to_resolve, relevant_docs)
                yield resolved_link_or_text

                buffer = buffer[match.end():]

        if buffer:
            yield buffer

    # --- START OF CHANGE ---
    # REASON FOR CHANGE: The previous implementation only used the user's query (`context_text`)
    # to generate suggestions. This caused the LLM to lose context on subsequent turns.
    # The method now accepts a `conversation_context` dictionary containing both the
    # user's query and Mushi's last response. This provides a much richer basis for
    # generating relevant, contextual follow-up questions.
    @staticmethod
    def suggest_followup_questions(conversation_context: Dict[str, str]) -> Tuple[Dict[str, Any], int]:
        """
        Generates follow-up questions based on the last user query AND Mushi's response.
        """
        user_query = conversation_context.get("user_query")
        mushi_response = conversation_context.get("mushi_response")

        if not user_query or not mushi_response:
            return {"suggested_questions": []}, 200

        current_llm = Config.CURRENT_GENERATION_LLM

        # The new prompt explicitly includes both sides of the last conversation turn.
        question_generation_prompt = f"""
        Based on the following conversation turn:
        USER ASKED: "{user_query}"
        MUSHI ANSWERED: "{mushi_response}"

        Generate exactly 3 diverse and insightful follow-up questions that a user might ask next.
        RULES: Output ONLY 3 questions, separated by "|||". DO NOT use numbering or bullet points.
        EXAMPLE: What are some other anime with a complex magic system?|||How does the power scaling in that anime compare to others?|||Are there any characters who question the morality of the magic system?
        """
        llm_raw_response: Optional[str] = None
        if current_llm.startswith("ollama"):
            model_name = Config.OLLAMA_ANIME_MODEL_NAME if current_llm == "ollama_anime" else Config.OLLAMA_QWEN_MODEL_NAME
            llm_service = OllamaLLMService(model_name=model_name)
            llm_raw_response = llm_service.get_simple_response(question_generation_prompt)
        else:
            return {"error": "Suggestion generation is currently only supported for Ollama providers."}, 500

        if not llm_raw_response or llm_raw_response.startswith("Error:"):
            return {"error": llm_raw_response or "Failed to generate suggestions."}, 500

        questions = [q.strip() for q in llm_raw_response.split('|||') if q.strip()]
        cleaned_questions = [re.sub(r'^\s*[-*]?\s*\d*\.\s*', '', q) for q in questions]
        return {"suggested_questions": cleaned_questions[:3]}, 200
    # --- END OF CHANGE ---

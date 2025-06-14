# backend/controllers/llm_controller.py
from services.gemini_llm_service import GeminiLLMService
from services.ollama_llm_service import OllamaLLMService
from config import Config
# Import from the new globals.py module instead of app.py
from globals import global_vector_store, global_ollama_embedder
import json
from typing import List, Dict, Any, Tuple, Optional


class LLMController:
    """
    Controller for managing interactions with various LLM services.
    It acts as a dispatcher, selecting the appropriate LLM service
    based on the application's configuration.
    """

    @staticmethod
    def get_llm_providers() -> Dict[str, str]:
        """
        Returns the dictionary of available LLM providers from Config.
        """
        return Config.LLM_PROVIDERS

    @staticmethod
    def set_llm_provider(provider_key: str) -> Tuple[str, int]:
        """
        Sets the active LLM provider in Config.
        """
        if provider_key in Config.LLM_PROVIDERS:
            Config.CURRENT_GENERATION_LLM = provider_key
            print(f"DEBUG: LLM provider set to: {provider_key}")
            return f"LLM provider set to {provider_key}", 200
        else:
            return "Invalid LLM provider", 400

    @staticmethod
    def get_current_llm_provider() -> Tuple[Dict[str, str], int]:
        """
        Returns the currently selected LLM provider key from Config.
        """
        return {"current_provider": Config.CURRENT_GENERATION_LLM}, 200


    @staticmethod
    def generate_llm_response(user_query: str) -> tuple[str, int]:
        """
        Generates a response from the currently configured LLM.
        Incorporates a basic "Lore Navigator" by searching embeddings.

        Args:
            user_query (str): The user's input query.

        Returns:
            tuple[str, int]: A tuple containing the LLM's response text (or error message)
                             and an HTTP status code. The first element is *always* a string.
        """
        if not user_query:
            return "Please provide a query for the LLM.", 400

        current_llm = Config.CURRENT_GENERATION_LLM
        print(f"DEBUG: Attempting to generate response using LLM: {current_llm}")

        llm_raw_response: str | None = None
        context_for_llm: str = "" # Initialize empty context

        # --- Lore Navigator Integration ---
        # Attempt to embed the user's query and find relevant lore
        user_query_embedding = global_ollama_embedder.embed_text(user_query)
        if user_query_embedding:
            # Perform similarity search to find relevant documents (lore)
            relevant_docs = global_vector_store.similarity_search(user_query_embedding, top_k=3)

            if relevant_docs:
                context_for_llm = "\n\nRelevant Information from Lore Database:\n"
                for doc in relevant_docs:
                    # Access 'content' and 'metadata' directly from the doc
                    content_snippet = doc.get('content', 'No content available')
                    source_info = doc.get('metadata', {}).get('source')

                    context_for_llm += f"- {content_snippet}"
                    if source_info:
                        context_for_llm += f" (Source: {source_info})"
                    context_for_llm += "\n"
                print(f"DEBUG: Context for LLM:\n{context_for_llm}")
            else:
                print("DEBUG: No relevant documents found for user query.")
        else:
            print("DEBUG: Failed to embed user query for lore search.")

        # Construct the prompt for the LLM
        # Add a clear instruction for the LLM regarding the context
        prompt_with_context = OllamaLLMService.MUSHI_SYSTEM_PROMPT + "\n\n"
        if context_for_llm:
            prompt_with_context += context_for_llm + "\n"
            prompt_with_context += "Based on the relevant information provided above and your existing knowledge, answer the user's query. If the provided information is not sufficient, state that you cannot fully answer based on the given context.\n\n"
        else:
            prompt_with_context += "Answer the user's query based on your existing knowledge.\n\n"

        prompt_with_context += f"User Query: {user_query}\n"

        # Determine which LLM service to use based on configuration
        if current_llm == "gemini":
            print("DEBUG: Calling GeminiLLMService.generate_content...")
            llm_raw_response = GeminiLLMService.generate_content(prompt_with_context)
        elif current_llm == "ollama_anime": # Specific Ollama anime model
            print("DEBUG: Calling OllamaLLMService.generate_content (Anime Model)...")
            llm_raw_response = OllamaLLMService.generate_content(prompt_with_context, model_name=Config.OLLAMA_ANIME_MODEL_NAME)
        elif current_llm == "ollama_qwen": # Specific Ollama Qwen model
            print("DEBUG: Calling OllamaLLMService.generate_content (Qwen Model)...")
            llm_raw_response = OllamaLLMService.generate_content(prompt_with_context, model_name=Config.OLLAMA_QWEN_MODEL_NAME)
        else:
            return "Error: No valid LLM provider configured or selected.", 500

        if llm_raw_response is None:
            print(f"LLM Error: Service '{current_llm}' returned no content (None).")
            return f"An internal error occurred with the '{current_llm}' LLM service: no content was returned.", 500
        elif llm_raw_response.startswith("Error:"):
            print(f"LLM Error from service '{current_llm}': {llm_raw_response}")
            return llm_raw_response, 500 # Propagate service-specific errors
        else:
            print(f"LLM Response Generated Successfully: {llm_raw_response[:100]}...")
            return llm_raw_response, 200

    @staticmethod
    def suggest_followup_questions(context_text: str) -> Tuple[Dict[str, Any], int]: # Parameter renamed to context_text
        """
        Suggests 3 concise, deeper follow-up questions based on the provided context_text (user's query).
        Also, optionally suggests similar anime if a primary anime was discussed.
        Returns a dictionary with 'suggested_questions' (list of strings) and 'similar_anime_note' (optional string).
        """
        if not context_text:
            return {"suggested_questions": [], "similar_anime_note": None}, 200

        current_llm = Config.CURRENT_GENERATION_LLM
        print(f"DEBUG: Attempting to generate suggested questions using LLM: {current_llm}")

        # Enhanced prompt for deeper, strictly '|||'-separated questions and optional similar anime note
        question_generation_prompt = OllamaLLMService.MUSHI_SYSTEM_PROMPT + f"""
Based on the following user query, generate 3 concise, insightful, and relevant follow-up questions.
Each question MUST be distinct and encourage deeper exploration of the topic discussed.

--- STRICT FORMATTING RULES ---
1.  **Output ONLY 3 questions.**
2.  **Separate each question ONLY with "|||".**
3.  **NO prefixes, numbering, or introductory phrases WHATSOEVER.** This includes, but is not limited to, phrases like "Question 1", "Question 2", "Question Suggestion", "Here are some questions:", "Here's the thing,", "So,", "And here's what I found interesting,", "Consider these questions:", "Suggested questions:", or any bullet points/numbering.
4.  **Each question must be a complete, direct sentence ending with a question mark.**

Example of Expected Output for Questions: "What are the main abilities of Monkey D. Luffy?|||Who are the key antagonists in the early arcs of One Piece?|||How does the concept of Devil Fruits impact the world of One Piece?"

--- OPTIONAL: SIMILAR ANIME NOTE ---
If the user query clearly relates to a specific anime title (e.g., "One Piece", "Naruto", "Attack on Titan"), you MUST also add a separate line at the very end of your response, exactly like this:
"NOTE_SIMILAR_ANIME: [List 2-3 anime that are similar in genre or theme to the identified anime, comma-separated]"
If no specific anime is clearly identifiable from the user query, completely omit the "NOTE_SIMILAR_ANIME:" line.

User Query:
{context_text}

Your Response (strictly adhere to rules above):
"""
        llm_raw_response: str | None = None
        if current_llm == "gemini":
            print("DEBUG: Calling GeminiLLMService.generate_content for suggested questions...")
            llm_raw_response = GeminiLLMService.generate_content(question_generation_prompt)
        elif current_llm == "ollama_anime": # Specific Ollama anime model
            print("DEBUG: Calling OllamaLLMService.generate_content (Anime Model) for suggested questions...")
            llm_raw_response = OllamaLLMService.generate_content(question_generation_prompt, model_name=Config.OLLAMA_ANIME_MODEL_NAME)
        elif current_llm == "ollama_qwen": # Specific Ollama Qwen model
            print("DEBUG: Calling OllamaLLMService.generate_content (Qwen Model) for suggested questions...")
            llm_raw_response = OllamaLLMService.generate_content(question_generation_prompt, model_name=Config.OLLAMA_QWEN_MODEL_NAME)
        else:
            return {"suggested_questions": [], "similar_anime_note": "Error: No valid LLM provider configured for question suggestion."}, 500

        if llm_raw_response is None:
            print(f"LLM Error: Service '{current_llm}' returned no content for suggested questions (None).")
            return {"suggested_questions": [], "similar_anime_note": f"An internal error occurred with the '{current_llm}' LLM service: no content was returned."}, 500
        elif llm_raw_response.startswith("Error:"):
            print(f"LLM Error from service '{current_llm}' for suggested questions: {llm_raw_response}")
            return {"suggested_questions": [], "similar_anime_note": llm_raw_response}, 500 # Propagate service-specific errors
        else:
            # Parse the response: separate questions from the optional note
            suggested_questions_part = llm_raw_response
            similar_anime_note: Optional[str] = None

            # Check if the "NOTE_SIMILAR_ANIME:" line exists
            if "NOTE_SIMILAR_ANIME:" in llm_raw_response:
                # Split only on the first occurrence to preserve commas in the note content
                parts = llm_raw_response.split("NOTE_SIMILAR_ANIME:", 1)
                suggested_questions_part = parts[0].strip()
                similar_anime_note = "Similar anime: " + parts[1].strip() # Frontend expects "Similar anime: " not "NOTE_SIMILAR_ANIME:"

            # Split questions using the "|||" delimiter
            questions = [q.strip() for q in suggested_questions_part.split('|||') if q.strip()]

            # Ensure questions are clean (remove stray punctuation at the end)
            final_questions = [q.rstrip('.?!') for q in questions if q.strip()]

            # Limit to top 3 questions
            final_questions = final_questions[:3]

            response_data = {
                "suggested_questions": final_questions,
                "similar_anime_note": similar_anime_note
            }
            print(f"LLM Response Generated Successfully for suggested questions: {response_data}")
            return response_data, 200

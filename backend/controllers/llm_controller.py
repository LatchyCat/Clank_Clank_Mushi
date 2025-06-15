# backend/controllers/llm_controller.py
from services.gemini_llm_service import GeminiLLMService
from services.ollama_llm_service import OllamaLLMService
from config import Config
# Import from the new globals.py module instead of app.py
from globals import global_vector_store, global_ollama_embedder
import json
import re # Import for regex
from typing import List, Dict, Any, Tuple, Optional, Generator # NEW: Import Generator

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
    def generate_llm_response(user_query: str) -> Generator[str, None, None]: # Changed return type to Generator
        """
        Generates a response from the currently configured LLM in a streaming fashion.
        Incorporates a basic "Lore Navigator" by searching embeddings.
        Yields chunks of the LLM's response.

        Args:
            user_query (str): The user's input query.

        Yields:
            str: Chunks of the LLM's response text, including error messages if any.
        """
        if not user_query:
            yield "Error: Please provide a query for the LLM."
            return

        current_llm = Config.CURRENT_GENERATION_LLM
        print(f"DEBUG: Attempting to generate streaming response using LLM: {current_llm}")

        context_for_llm: str = "" # Initialize empty context

        # --- Lore Navigator Integration ---
        # Attempt to embed the user's query and find relevant lore
        user_query_embedding = global_ollama_embedder.embed_text(user_query)
        if user_query_embedding:
            # Perform similarity search to find relevant documents (lore)
            relevant_docs = global_vector_store.similarity_search(user_query_embedding, top_k=3)

            if relevant_docs:
                # Mushi will not explicitly mention "Lore Database" in her response
                # The system prompt in ollama_llm_service.py handles this.
                context_for_llm = "\n\nRelevant Information:\n"
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
        # The system prompt in OllamaLLMService.MUSHI_SYSTEM_PROMPT guides the LLM's behavior
        # and explicitly tells it NOT to mention "lore database" or similar terms.
        prompt_for_llm = user_query
        if context_for_llm:
            # Prepend the context to the user's query.
            # The system prompt will instruct the LLM on how to use this context.
            prompt_for_llm = f"{context_for_llm}\n\nUser Query: {user_query}"


        # Determine which LLM service to use based on configuration
        if current_llm == "gemini":
            # NOTE: GeminiLLMService.generate_content currently returns a single string.
            # To support streaming here, GeminiLLMService.generate_content would also need
            # to be updated to be a generator yielding chunks. For now, it will yield
            # the full response at once if Gemini is chosen, effectively not streaming.
            # A proper streaming implementation for Gemini would involve changes in gemini_llm_service.py too.
            print("DEBUG: Calling GeminiLLMService.generate_content (Non-Streaming for now)...")
            response_text = GeminiLLMService.generate_content(prompt_for_llm)
            if response_text.startswith("Error:"):
                yield response_text
            else:
                yield response_text # Yield the full response as one chunk for now
        elif current_llm == "ollama_anime": # Specific Ollama anime model
            print("DEBUG: Calling OllamaLLMService.generate_content (Anime Model) for streaming...")
            # This call now returns a generator, so we iterate and yield each chunk
            for chunk in OllamaLLMService(model_name=Config.OLLAMA_ANIME_MODEL_NAME).generate_content(prompt_for_llm):
                # If an error chunk is received, yield it and stop the generator
                if chunk.startswith("Error:"):
                    yield chunk
                    return
                yield chunk

        elif current_llm == "ollama_qwen": # Specific Ollama Qwen model
            print("DEBUG: Calling OllamaLLMService.generate_content (Qwen Model) for streaming...")
            # This call now returns a generator, so we iterate and yield each chunk
            for chunk in OllamaLLMService(model_name=Config.OLLAMA_QWEN_MODEL_NAME).generate_content(prompt_for_llm):
                # If an error chunk is received, yield it and stop the generator
                if chunk.startswith("Error:"):
                    yield chunk
                    return
                yield chunk
        else:
            yield "Error: No valid LLM provider configured or selected for streaming."


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
        # This prompt is specific to generating questions and similar anime,
        # so it doesn't need the full MUSHI_SYSTEM_PROMPT.
        # The OllamaLLMService's generate_content already injects the system prompt.
        question_generation_prompt = f"""
Based on the following user query, generate 3 concise, insightful, and relevant follow-up questions.
Each question MUST be distinct and encourage deeper exploration of the topic discussed.

--- STRICT FORMATTING RULES ---
1.  **Output ONLY 3 questions.**
2.  **Separate each question ONLY with "|||".**
3.  **NO prefixes, numbering, or introductory phrases WHATSOEVER.** This includes, but is not limited to, phrases like "Question 1", "Question 2", "Question Suggestion", "Here are some questions:", "Here's the thing,", "So,", "And here's what I found interesting,", "Consider these questions:", "Suggested questions:", or any bullet points/numbering.
4.  **Each question must be a complete, direct sentence ending with a question mark.**

Example of Expected Output for Questions: "What are the main abilities of Monkey D. Luffy?|||Who are the key antagonists in the early arcs of One Piece?|||How does the concept of Devil Fruits impact the world of One Piece?"

--- OPTIONAL: SIMILAR ANIME NOTE ---
If the user query clearly relates to a specific anime title (e.g., "One Piece", "Naruto", "Attack on Titan"), you MUST also add a separate section at the very end of your response, wrapped in a markdown code block, exactly like this:
```
NOTE_SIMILAR_ANIME:
- [Anime 1]
- [Anime 2]
- [Anime 3]
```
If no specific anime is clearly identifiable from the user query, completely omit the markdown code block.

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
            # For non-streaming endpoint, call generate_content and get the full string
            llm_raw_response_generator = OllamaLLMService(model_name=Config.OLLAMA_ANIME_MODEL_NAME).generate_content(question_generation_prompt)
            llm_raw_response = "".join(list(llm_raw_response_generator)) # Collect all parts
        elif current_llm == "ollama_qwen": # Specific Ollama Qwen model
            print("DEBUG: Calling OllamaLLMService.generate_content (Qwen Model) for suggested questions...")
            # For non-streaming endpoint, call generate_content and get the full string
            llm_raw_response_generator = OllamaLLMService(model_name=Config.OLLAMA_QWEN_MODEL_NAME).generate_content(question_generation_prompt)
            llm_raw_response = "".join(list(llm_raw_response_generator)) # Collect all parts
        else:
            return {"suggested_questions": [], "similar_anime_note": "Error: No valid LLM provider configured for question suggestion."}, 500

        if llm_raw_response is None or llm_raw_response.startswith("Error:"):
            error_message = llm_raw_response if llm_raw_response else "No content returned for suggested questions."
            print(f"LLM Error for suggested questions from service '{current_llm}': {error_message}")
            return {"suggested_questions": [], "similar_anime_note": error_message}, 500 # Propagate service-specific errors
        else:
            # Parse the response: separate questions from the optional note
            suggested_questions_part = llm_raw_response
            similar_anime_note: Optional[str] = None

            # Use regex to find the code block containing NOTE_SIMILAR_ANIME:
            # This regex looks for a markdown code block starting with `NOTE_SIMILAR_ANIME:`
            match = re.search(r'```(?:.*?)\s*NOTE_SIMILAR_ANIME:\s*\n(.*?)\n```', llm_raw_response, re.DOTALL)

            if match:
                similar_anime_content = match.group(1).strip()
                # Frontend expects "Similar anime: " followed by the content.
                # The code block ensures it's readable.
                similar_anime_note = f"Similar anime: \n```\n{similar_anime_content}\n```"

                # Remove the entire code block from the original response to get just the questions part
                suggested_questions_part = re.sub(r'```(?:.*?)\s*NOTE_SIMILAR_ANIME:.*?\n```', '', llm_raw_response, flags=re.DOTALL).strip()

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

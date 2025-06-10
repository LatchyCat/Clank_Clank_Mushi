# backend/controllers/llm_controller.py
from services.gemini_llm_service import GeminiLLMService
from services.ollama_llm_service import OllamaLLMService
from config import Config
# Import from the new globals.py module instead of app.py
from globals import global_vector_store, global_ollama_embedder
import json

class LLMController:
    """
    Controller for managing interactions with various LLM services.
    It acts as a dispatcher, selecting the appropriate LLM service
    based on the application's configuration.
    """

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
        query_embedding = global_ollama_embedder.embed_text(user_query)
        if query_embedding:
            relevant_docs = global_vector_store.search(query_embedding, top_k=3) # Get top 3 relevant documents
            if relevant_docs:
                print(f"DEBUG: Found {len(relevant_docs)} relevant documents for the query.")
                context_lines = ["Relevant Lore:"]
                for i, item in enumerate(relevant_docs):
                    doc_content = item['document']['content']
                    doc_metadata = item['document']['metadata']
                    # Attempt to get a meaningful title/name from metadata
                    title_or_name = doc_metadata.get('title', doc_metadata.get('name', ''))
                    context_lines.append(f"  - [{doc_metadata.get('source', 'unknown')}] {title_or_name}: {doc_content}")
                context_for_llm = "\n".join(context_lines) + "\n\n"
            else:
                print("DEBUG: No relevant documents found for the query.")
        else:
            print("WARNING: Could not generate embedding for user query, proceeding without lore context.")

        # Combine lore context with user query for the LLM
        full_prompt = f"{context_for_llm}User's Query: {user_query}\n\nBased on the provided information and your knowledge, please provide a concise and helpful answer."


        if current_llm == "gemini":
            print("DEBUG: Calling GeminiLLMService.generate_content...")
            llm_raw_response = GeminiLLMService.generate_content(full_prompt) # Pass the augmented prompt
        elif current_llm == "ollama":
            print("DEBUG: Calling OllamaLLMService.generate_content...")
            llm_raw_response = OllamaLLMService.generate_content(full_prompt) # Pass the augmented prompt
        else:
            return "Error: No valid LLM provider configured.", 500

        # --- Error Handling for LLM services ---
        if llm_raw_response is None:
            print(f"LLM Error: Service '{current_llm}' returned no content (None).")
            return f"An internal error occurred with the '{current_llm}' LLM service: no content was returned.", 500
        elif llm_raw_response.startswith("Error:"):
            print(f"LLM Error from service '{current_llm}': {llm_raw_response}")
            if "not configured" in llm_raw_response or "not running" in llm_raw_response or "server" in llm_raw_response or "connection" in llm_raw_response:
                return llm_raw_response, 503
            elif "safety" in llm_raw_response or "invalid" in llm_raw_response or "timeout" in llm_raw_response:
                return llm_raw_response, 400
            else:
                return llm_raw_response, 500
        else:
            print("LLM Response Generated Successfully.")
            return llm_raw_response, 200

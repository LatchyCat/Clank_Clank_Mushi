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
        # We need to ensure global_ollama_embedder is initialized and available
        if global_ollama_embedder and global_vector_store:
            query_embedding = global_ollama_embedder.embed_text(user_query)
            if query_embedding:
                # Search the vector store for similar documents
                relevant_docs = global_vector_store.search(query_embedding, top_k=3) # Get top 3 relevant documents
                if relevant_docs:
                    # Concatenate relevant content as context
                    context_for_llm = "\n\nRelevant Information:\n" + "\n".join([
                        doc["document"]["content"] for doc in relevant_docs
                        # Optionally, filter by similarity_score if needed, e.g., if doc["similarity_score"] > 0.7
                    ])
                    print(f"DEBUG: Found {len(relevant_docs)} relevant documents for context.")
                    # print(f"DEBUG: Context for LLM: {context_for_llm[:200]}...") # Print first 200 chars of context
                else:
                    print("DEBUG: No relevant documents found in vector store.")
            else:
                print("DEBUG: Could not generate embedding for user query.")
        else:
            print("DEBUG: Embedding services (OllamaEmbedder or VectorStore) not initialized. Skipping lore navigation.")


        # Define the system prompt for Mushi's persona
        system_prompt = OllamaLLMService.MUSHI_SYSTEM_PROMPT # Get from OllamaLLMService as it defines the persona

        # Combine system prompt, context, and user query for the LLM
        full_prompt = f"{system_prompt}\n\n{context_for_llm}\n\nUser: {user_query}\nMushi:"
        print(f"DEBUG: Full prompt sent to LLM (first 500 chars): {full_prompt[:500]}...") # Log portion of the prompt


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
                return llm_raw_response, 400
        else:
            print(f"LLM Response Generated Successfully: {llm_raw_response}")
            return llm_raw_response, 200

    @staticmethod
    def generate_suggested_questions(user_previous_question: str) -> tuple[list[str] | str, int]:
        """
        Generates a list of exactly 3 suggested follow-up questions based on the user's
        previous question, using the LLM.

        Args:
            user_previous_question (str): The user's last submitted question.

        Returns:
            tuple[list[str] | str, int]: A tuple containing a list of suggested questions
                                         (or an error string) and an HTTP status code.
        """
        if not user_previous_question:
            return "User's previous question is empty for follow-up question suggestion.", 400

        current_llm = Config.CURRENT_GENERATION_LLM
        print(f"DEBUG: Attempting to generate suggested questions using LLM: {current_llm}")

        # Craft a prompt specifically for follow-up question generation based on a user's question
        question_generation_prompt = f"""
        Based on the user's previous question, generate exactly 3 interesting and conversational follow-up questions they might have.
        Format your response as a comma-separated list of questions. Do not include any introductory or concluding remarks.

        User's Previous Question:
        {user_previous_question}

        Suggested Follow-up Questions:
        """

        llm_raw_response: str | None = None

        if current_llm == "gemini":
            print("DEBUG: Calling GeminiLLMService.generate_content for suggested questions...")
            llm_raw_response = GeminiLLMService.generate_content(question_generation_prompt)
        elif current_llm == "ollama":
            print("DEBUG: Calling OllamaLLMService.generate_content for suggested questions...")
            llm_raw_response = OllamaLLMService.generate_content(question_generation_prompt)
        else:
            return "Error: No valid LLM provider configured for question suggestion.", 500

        if llm_raw_response is None:
            print(f"LLM Error: Service '{current_llm}' returned no content for suggested questions (None).")
            return f"An internal error occurred with the '{current_llm}' LLM service for question suggestion: no content was returned.", 500
        elif llm_raw_response.startswith("Error:"):
            print(f"LLM Error from service '{current_llm}' for suggested questions: {llm_raw_response}")
            return llm_raw_response, 500 # Propagate service-specific errors
        else:
            # Attempt to parse the comma-separated list
            suggested_questions = [q.strip() for q in llm_raw_response.split(',') if q.strip()]
            # Ensure we only return 3 if the LLM provided more, or fewer if it provided less.
            # The prompt asks for exactly 3, but this makes it robust.
            final_suggestions = suggested_questions[:3]
            print(f"LLM Response Generated Successfully for suggested questions: {final_suggestions}")
            return final_suggestions, 200

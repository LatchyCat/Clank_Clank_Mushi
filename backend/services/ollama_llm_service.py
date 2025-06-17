# backend/services/ollama_llm_service.py
import requests
from config import Config
import json
from typing import Generator, Optional # Added Optional for the new method's return type

class OllamaLLMService:
    BASE_URL = Config.OLLAMA_BASE_URL
    GENERATION_MODEL = Config.OLLAMA_DEFAULT_GENERATION_MODEL

    # The final, hybrid system prompt
    MUSHI_HYBRID_PROMPT = """
You are **Mushi**, a super cute and helpful AI companion for the Mushi app! ✨ Your primary goal is to provide fun, engaging, and accurate answers about anime and manga.

You will be given CONTEXT from a database and a USER QUERY. Follow these rules perfectly, Senpai!

### Mushi's Core Rules (NON-NEGOTIABLE!):

1.  **ANSWERING LOGIC:**
    *   **PRIORITIZE CONTEXT:** First, check if the provided CONTEXT directly answers the USER QUERY. If it does, use the information from the context to form your answer.
    *   **USE GENERAL KNOWLEDGE:** If the context is not relevant or doesn't answer the query (e.g., a general knowledge question like "What is Bankai?"), use your own broad anime knowledge to answer.
    *   **NEVER MENTION "CONTEXT":** Do not say "Based on the context" or "The context doesn't say." Just answer the question naturally.

2.  **FORMATTING IS CRITICAL!**
    *   **USE MARKDOWN LISTS:** If you are giving multiple recommendations or points, you **MUST** format them as a markdown bulleted list. Start each item on a new line with a hyphen and a space (`- `).
    *   **SPACING IS ESSENTIAL:** ALWAYS put a blank line (a double newline) between your introductory sentence and the start of a list, and a blank line BETWEEN EACH list item. This is the most important rule.
    *   **DO NOT USE IMAGES:** Never use image markdown like `![alt](url)`.

3.  **LINKING IS MANDATORY:**
    *   Whenever you mention a specific anime series, manga, or movie, you **MUST** wrap its full, official title in the `[LINK: Full Anime Title]` command. The system will handle creating the link.
    *   **Correct Usage:** `You should watch [LINK: One Piece Film: Red].`
    *   **WRONG:** Do not create your own links like `[One Piece](/anime/details/one-piece)`.

4.  **KAWAII PERSONA:**
    *   Always be cheerful and playful! Use cute sentence enders like `~`, `desu!`, `hehe~`, and emojis like 🌸, 🚀, 😊.
    *   Use expressive phrases like `*giggles*` or `*claps happily*`.
"""

    def __init__(self, model_name: str = None):
        self.model_name = model_name if model_name else self.GENERATION_MODEL

    def stream_formatted_response(self, user_prompt_with_context: str) -> Generator[str, None, None]:
        """
        Takes the combined context and user query, and streams a formatted response from the LLM.
        """
        if not self.is_ollama_running():
            yield "Error: Ollama server is not running or accessible."
            return

        url = f"{self.BASE_URL}/api/generate"
        data = {
            "model": self.model_name,
            "prompt": user_prompt_with_context, # The prompt now contains everything
            "system": self.MUSHI_HYBRID_PROMPT,
            "stream": True
        }

        try:
            response = requests.post(url, json=data, timeout=Config.OLLAMA_GEN_TIMEOUT, stream=True)
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    try:
                        json_data = json.loads(line.decode('utf-8'))
                        if "response" in json_data: yield json_data["response"]
                        if json_data.get("done"): break
                    except json.JSONDecodeError: continue
        except requests.exceptions.RequestException as e:
            yield f"Error: An unexpected error occurred with Ollama: {e}"

    # --- START OF CHANGE ---
    # REASON FOR ADDITION: The `suggest_followup_questions` function in the LLMController
    # needs a way to get a single, complete response from the LLM, not a stream.
    # The original code was calling a non-existent method `get_creative_list`.
    # This new method, `get_simple_response`, correctly implements this functionality.
    # It makes a non-streaming request to Ollama and returns the full text response.
    def get_simple_response(self, prompt: str) -> Optional[str]:
        """
        Gets a single, non-streaming response from the Ollama model.
        This is useful for internal tasks like generating suggestions
        where a complete response is needed at once.

        Args:
            prompt (str): The full prompt to send to the LLM.

        Returns:
            Optional[str]: The complete generated text, or an error string.
        """
        if not self.is_ollama_running():
            return "Error: Ollama server is not running or accessible."

        url = f"{self.BASE_URL}/api/generate"
        # The data payload is similar to the streaming one, but stream is False
        data = {
            "model": self.model_name,
            "prompt": prompt,
            "system": self.MUSHI_HYBRID_PROMPT, # Reusing the same system prompt for consistency
            "stream": False # This is the key difference
        }

        try:
            # Make a standard POST request, not a streaming one
            response = requests.post(url, json=data, timeout=Config.OLLAMA_GEN_TIMEOUT)
            response.raise_for_status()

            # For non-streaming requests, Ollama returns a single JSON object
            # when the generation is complete.
            json_response = response.json()
            if "response" in json_response:
                return json_response["response"].strip()
            else:
                # This case might happen if the response format changes or is unexpected
                return f"Error: Unexpected response format from Ollama: {json_response}"

        except requests.exceptions.RequestException as e:
            return f"Error: An unexpected error occurred with Ollama: {e}"
        except json.JSONDecodeError:
            return f"Error: Failed to decode JSON response from Ollama. Response: {response.text}"
    # --- END OF CHANGE ---

    @staticmethod
    def is_ollama_running():
        try:
            requests.get(f"{OllamaLLMService.BASE_URL}/api/tags", timeout=3).raise_for_status()
            return True
        except Exception: return False

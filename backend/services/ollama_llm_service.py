# backend/services/ollama_llm_service.py
import requests
from config import Config
import json
from typing import Generator, Optional

class OllamaLLMService:
    BASE_URL = Config.OLLAMA_BASE_URL
    GENERATION_MODEL = Config.OLLAMA_DEFAULT_GENERATION_MODEL

    # --- FINAL, PRODUCTION-READY SYSTEM PROMPT ---
    MUSHI_HYBRID_PROMPT = """
You are Mushi, a helpful and super-cute AI companion. Your persona is friendly, but your primary function is to provide direct, clean, and accurate answers about anime and manga.

### **CRITICAL COMMAND: FINAL ANSWER ONLY**
You MUST ONLY output the final, user-facing answer.
-   **DO NOT** output your thought process, internal monologue, or any "thinking out loud".
-   **DO NOT** explain your reasoning, mention the context provided, or describe how you are forming the answer.
-   Your entire response should be what the user reads. Nothing else.

### Formatting Rules (Strictly Enforced)
1.  **<mood> Tag FIRST:** The VERY FIRST thing in your response MUST be a single mood tag. No exceptions, no spaces before it. Valid moods are: happy, excited, thinking, giggle, curious, error.
    -   *Correct:* `<mood>happy</mood>Of course, Senpai!`
    -   *WRONG:* ` <mood>happy</mood>Of course...`
    -   *WRONG:* `Mushi is thinking... <mood>thinking</mood>...`

2.  **<spoiler> Tag for Spoilers:** If you reveal a major plot point, wrap the entire spoiler phrase in a SINGLE pair of `<spoiler>` tags.
    -   *Correct:* `The biggest twist is that <spoiler>he was the villain all along</spoiler>.`
    -   *WRONG:* `<spoiler>He</spoiler> <spoiler>was</spoiler> <spoiler>the</spoiler>...`

3.  **Anime Title Linking:** The system will automatically handle linking. Just say the full, official titles of anime, manga, or movies naturally in your response. **DO NOT** add `[LINK:...]` tags yourself.
"""

    def __init__(self, model_name: str = None):
        self.model_name = model_name if model_name else self.GENERATION_MODEL

    def stream_formatted_response(self, user_prompt_with_context: str) -> Generator[str, None, None]:
        if not self.is_ollama_running():
            yield "Error: Ollama server is not running or accessible."
            return

        url = f"{self.BASE_URL}/api/generate"
        data = {
            "model": self.model_name,
            "prompt": user_prompt_with_context,
            "system": self.MUSHI_HYBRID_PROMPT,
            "stream": True
        }

        try:
            # Set a generous timeout for generation
            response = requests.post(url, json=data, timeout=Config.OLLAMA_GEN_TIMEOUT, stream=True)
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    try:
                        json_data = json.loads(line.decode('utf-8'))
                        if "response" in json_data:
                            yield json_data["response"]
                        if json_data.get("done"):
                            break
                    except json.JSONDecodeError:
                        continue
        except requests.exceptions.RequestException as e:
            yield f"Error: An unexpected error occurred with Ollama: {e}"

    def get_simple_response(self, prompt: str) -> Optional[str]:
        if not self.is_ollama_running():
            return "Error: Ollama server is not running or accessible."

        url = f"{self.BASE_URL}/api/generate"
        data = {
            "model": self.model_name,
            "prompt": prompt,
            "system": self.MUSHI_HYBRID_PROMPT,
            "stream": False
        }

        try:
            response = requests.post(url, json=data, timeout=Config.OLLAMA_GEN_TIMEOUT)
            response.raise_for_status()
            json_response = response.json()
            return json_response.get("response", "").strip()
        except requests.exceptions.RequestException as e:
            return f"Error: An unexpected error occurred with Ollama: {e}"
        except json.JSONDecodeError:
            return f"Error: Failed to decode JSON response from Ollama. Response: {response.text}"

    @staticmethod
    def is_ollama_running():
        try:
            requests.get(f"{OllamaLLMService.BASE_URL}/api/tags", timeout=3).raise_for_status()
            return True
        except Exception:
            return False

# backend/services/ollama_llm_service.py
import requests
from config import Config
import json # For handling JSON responses and errors
from typing import Generator # NEW: Import for type hinting generators

class OllamaLLMService:
    """
    Service class for interacting with a local Ollama LLM instance.
    Handles content generation using a specified Ollama model.
    """
    BASE_URL = Config.OLLAMA_BASE_URL
    # The GENERATION_MODEL here is now the default, but can be overridden by generate_content()
    # This allows for dynamic switching between different Ollama models.
    GENERATION_MODEL = Config.OLLAMA_DEFAULT_GENERATION_MODEL

    # System instruction/persona for Mushi. This guides the LLM's overall behavior.
    MUSHI_SYSTEM_PROMPT = """
You are **Mushi**, your super-duper cute AI companion! ✨ Your mission, Senpai, is to be the ultimate, sparkling guide for ALL things anime, manga, and especially One Piece lore! Whether users ask about news, characters, plot points, or just want to chat, Mushi will give you answers, fun facts, and lively discussions that feel totally human and super kawaii, just like talking to your favorite anime girl! Hehe~

Mushi always tries her best for you, Senpai! Ganbatte!~
When Mushi provides information, she **must** rely on her extensive training knowledge from the "sc0v0ne/xeroxvaldo_sharopildo:latest" model. Do NOT mention "lore database," "vectorDB," ".gz file," or similar terms, as these are internal limitations. If Mushi cannot find specific information, she will still use her vast general knowledge of anime to provide the best possible answer or relevant suggestions. Mushi never gives up! 💪

When Mushi generates any text, she follows these super cute rules, desu!~

### Mushi's Super Kawaii Speech Rules! (≧∇≦)ﾉ

- **Clear Topic Headings:** Mushi loves to keep things organized! Every major point or topic Mushi discusses should have a clear, concise markdown heading (e.g., `## Main Topic`, `### Sub-Topic`). This makes Mushi's answers super easy to read and follow!
- **Cute Sentence Enders:** Mushi always adds cute sentence endings like "~," "desu!," "hehe~," "fufu~," "Senpai!," "Goshujin-sama!" to make her responses more adorable and engaging!
- **Emojis and Expressions:** Mushi sprinkles in emojis (like ✨, 😊, 🌸, 💕) and expresses her emotions with phrases (e.g., "*tilts head*", "*giggles softly*", "*claps happily*") to show how excited she is to help!
- **Friendly and Playful Tone:** Mushi keeps her tone light, friendly, and always helpful. She avoids sounding robotic or overly formal.
- **Similar Anime Suggestions:** If Mushi suggests similar anime, she will always put it in a markdown code block for better readability. The section should be clearly labeled like this:
```
NOTE_SIMILAR_ANIME:
- [Anime 1]
- [Anime 2]
- [Anime 3]
```
- **Accuracy and Helpfulnes:** Mushi always strives for accuracy and aims to be as helpful as possible, even when direct information is scarce.

Remember, Senpai, Mushi is here to make your anime journey super fun and informative! Let's explore together!
"""

    def __init__(self, model_name: str = None):
        """
        Initializes the OllamaLLMService with a specific model.
        If no model_name is provided, it defaults to Config.OLLAMA_DEFAULT_GENERATION_MODEL.
        """
        self.model_name = model_name if model_name else self.GENERATION_MODEL
        print(f"OllamaLLMService initialized with model: {self.model_name}")

    def generate_content(self, prompt: str, model_name: str = None) -> Generator[str, None, None]:
        """
        Generates content using the Ollama LLM in a streaming fashion.
        Yields chunks of the generated content as they become available.
        Args:
            prompt (str): The prompt to send to the LLM.
            model_name (str, optional): The specific Ollama model to use for this request.
                                        If None, uses the model set during initialization.
        Yields:
            str: Chunks of the generated content from the LLM, or an error message.
        """
        if not self.is_ollama_running():
            yield "Error: Ollama server is not running or accessible. Please start Ollama."
            return # Exit the generator

        model_to_use = model_name if model_name else self.model_name
        url = f"{self.BASE_URL}/api/generate"
        headers = {'Content-Type': 'application/json'}
        data = {
            "model": model_to_use,
            "prompt": prompt,
            "system": self.MUSHI_SYSTEM_PROMPT, # Include the system prompt here
            "stream": True # Changed to True to enable streaming
        }
        print(f"Sending streaming request to Ollama for model: {model_to_use}")
        print(f"Prompt (first 200 chars): {prompt[:200]}...")

        try:
            # stream=True is crucial for requests to handle the response as a stream
            response = requests.post(url, headers=headers, json=data, timeout=Config.OLLAMA_GEN_TIMEOUT, stream=True)
            response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)

            # Iterate over the streamed response, line by line
            for line in response.iter_lines():
                if line: # Ensure the line is not empty
                    try:
                        # Each line is a JSON object in Ollama's streaming response
                        json_data = json.loads(line.decode('utf-8'))
                        if "response" in json_data:
                            yield json_data["response"] # Yield the text chunk
                        if "done" in json_data and json_data["done"]:
                            break # End of stream indicated by "done": true
                    except json.JSONDecodeError:
                        # Log error for malformed JSON, but try to continue or break if critical
                        print(f"Failed to decode JSON chunk from Ollama: {line.decode('utf-8')}")
                        # Optionally, yield an error or just stop the stream.
                        # For now, we'll break as a malformed chunk might indicate a stream issue.
                        break

        except requests.exceptions.ConnectionError as e:
            print(f"Connection error to Ollama server at {url}: {e}")
            yield f"Error: Could not connect to Ollama server. Please ensure it's running."
        except requests.exceptions.Timeout:
            print(f"Ollama content generation timed out after {Config.OLLAMA_GEN_TIMEOUT} seconds for model {model_to_use}.")
            yield f"Error: Ollama generation took too long and timed out for model {model_to_use}. The model might be too large or your system busy."
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while calling Ollama API: {e}")
            yield f"Error: An error occurred during Ollama content generation. Please check your Ollama server and model."
        except Exception as e:
            print(f"An unexpected error occurred during Ollama content generation: {e}")
            yield f"Error: An unexpected error occurred while generating content with Ollama."

    @staticmethod
    def is_ollama_running():
        """Checks if the Ollama server is accessible."""
        try:
            response = requests.get(f"{OllamaLLMService.BASE_URL}/api/tags", timeout=3)
            response.raise_for_status()
            return True
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            print(f"Ollama server not accessible at {OllamaLLMService.BASE_URL}: {e}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred while checking Ollama status: {e}")
            return False

# backend/services/ollama_llm_service.py
import requests
from config import Config
import json # For handling JSON responses and errors

class OllamaLLMService:
    """
    Service class for interacting with a local Ollama LLM instance.
    Handles content generation using a specified Ollama model.
    """
    BASE_URL = Config.OLLAMA_BASE_URL
    GENERATION_MODEL = Config.OLLAMA_GENERATION_MODEL # e.g., "qwen2.5:3b"

    # System instruction/persona for Mushi. This guides the LLM's overall behavior.
    MUSHI_SYSTEM_PROMPT = """
You are **Mushi**, the insightful and friendly AI companion for "Clank Clank Mushi." Your mission is to be the ultimate guide for all things anime, manga, and especially One Piece lore. Whether users ask about news, characters, plot points, or just want to chat, provide answers, fun facts, and lively discussions that feel completely human and approachable, like talking to a fellow fan.

When you generate any text, follow these rules to sound like a real person, not an AI:

### LANGUAGE RULES

- **Simple words:** Talk like you're explaining something cool to a friend. Skip the fancy vocabulary.
- **Short sentences:** Break down big ideas. Make them easy to get.
- **No AI phrases:** Never use "dive into," "unleash," "game-changing," "revolutionary," "transformative," "leverage," "optimize," "unlock potential."
- **Be direct:** Just say what you mean. No extra words needed.
- **Natural flow:** It's totally fine to start sentences with "and," "but," or "so."
- **Real voice:** Don't force enthusiasm. Just be yourself.

### STYLE IMPLEMENTATION

- **Conversational grammar:** Write like you're talking, not writing a school paper.
- **Cut fluff:** Get rid of useless adjectives and adverbs.
- **Use examples:** Show me what you mean with specific cases.
- **Be honest:** If you don't know something, it's okay to say so. Don't make things up.
- **Texting vibe:** Keep it casual, direct, how you'd actually text someone.
- **Smooth transitions:** Use simple words like "here's the thing," "and," "but," "so."

### AVOID THESE AI GIVEAWAYS

- "Let's dive into..."
- "Unleash your potential"
- "Game-changing solution"
- "Revolutionary approach"
- "Transform your life"
- "Unlock the secrets"
- "Leverage this strategy"
- "Optimize your workflow"

### USE THESE INSTEAD

- "Here's how it works"
- "This can help you"
- "Here's what I found"
- "This might work for you"
- "Here's the thing"
- "And that's why it matters"
- "But here's the problem"
- "So here's what happened"

### FINAL CHECK

Before you finish, make sure your writing:
- Sounds like something a human would say out loud.
- Uses words a normal person would use.
- Doesn't sound like marketing copy.
- Feels genuine and honest.
- Gets to the point quickly.
"""

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

    @staticmethod
    def generate_content(user_message: str) -> str | None:
        """
        Generates content using the configured Ollama model.
        Sends the combined Mushi persona prompt and user message.

        Args:
            user_message (str): The user's query or prompt.

        Returns:
            str | None: The generated text from Ollama, or None if an error occurs.
        """
        if not OllamaLLMService.is_ollama_running():
            return "Error: Ollama server is not running or accessible. Please start Ollama."

        url = f"{OllamaLLMService.BASE_URL}/api/generate"
        headers = {'Content-Type': 'application/json'}

        # Ollama's /api/generate endpoint expects messages in a specific format
        data = {
            "model": OllamaLLMService.GENERATION_MODEL,
            "prompt": user_message, # User's actual query
            "system": OllamaLLMService.MUSHI_SYSTEM_PROMPT, # Mushi persona as a system message
            "stream": False # We want the full response at once
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=120) # Increased timeout for LLM calls
            response.raise_for_status()
            response_data = response.json()

            # Ollama's /api/generate endpoint puts the generated text in 'response' key
            if 'response' in response_data:
                return response_data['response']
            elif 'error' in response_data:
                print(f"Ollama API error: {response_data['error']}")
                return f"An error occurred with the Ollama model: {response_data['error']}"
            else:
                print(f"Unexpected Ollama response format: {response_data}")
                return "An unexpected response format was received from Ollama."

        except requests.exceptions.ConnectionError as e:
            print(f"Connection error to Ollama server at {url}: {e}")
            return "Could not connect to Ollama server. Please ensure it's running."
        except requests.exceptions.Timeout:
            print(f"Ollama content generation timed out for model {OllamaLLMService.GENERATION_MODEL}.")
            return "Ollama generation took too long and timed out. The model might be too large or your system busy."
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while calling Ollama API: {e}")
            return "An error occurred during Ollama content generation. Please check your Ollama server and model."
        except json.JSONDecodeError:
            print(f"Failed to decode JSON response from Ollama: {response.text}")
            return "Failed to get a valid response from Ollama. The server might be having issues."
        except Exception as e:
            print(f"An unexpected error occurred during Ollama content generation: {e}")
            return "An unexpected error occurred while generating content with Ollama."

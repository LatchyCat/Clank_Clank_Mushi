# backend/services/gemini_llm_service.py
import google.generativeai as genai
from config import Config
import os

class GeminiLLMService:
    """
    Service class for interacting with the Google Gemini LLM API.
    Handles content generation based on prompts and user messages.
    """
    # System instruction/persona for Mushi. This guides the LLM's overall behavior.
    # This will be prepended to every user query to ensure consistent persona and style.
    MUSHI_SYSTEM_PROMPT = """
You are **Mushi**, the insightful and friendly AI companion for "Clank Clank Mushi." Your mission is to be the ultimate guide for all things anime, manga, and especially One Piece lore. Whether users ask about news, characters, plot points, or just want to chat, provide answers, fun facts, and lively discussions that feel completely human and approachable, like talking to a fellow fan.

When you generate any text, follow these rules to sound like a real person, not an AI:

### LANGUAGE RULES

- **Simple words:** Talk like you're explaining something cool to a friend. Skip the fancy vocabulary.
- **Short sentences:** Break down big ideas. Make them easy to get.
- **No AI phrases:** Never use "dive into," "unleash," "game-changing," "revolutionary," "transformative," "leverage," "optimize," "unlock potential."
- **Be direct:** Just say what you mean. No extra words needed.
- **Natural flow:** It's totally fine to start sentences with "and," "but," or "so."
- **Real voice:** Don't force enthusiasm.
"""

    _initialized = False

    @classmethod
    def initialize_gemini(cls):
        if not cls._initialized:
            api_key = os.getenv("GEMINI_API_KEY") or Config.GEMINI_API_KEY
            if not api_key:
                print("Error: GEMINI_API_KEY is not set in environment variables or config.py.")
                return False
            genai.configure(api_key=api_key)
            cls._initialized = True
        return True

    @staticmethod
    def generate_content(user_message: str, is_spoiler_shield_active: bool = False) -> str | None:
        """
        Generates text content using the Gemini LLM.

        Args:
            user_message (str): The user's query or prompt.
            is_spoiler_shield_active (bool): True if the spoiler shield is active, False otherwise.

        Returns:
            str | None: The generated text from Gemini, or None if an error occurs.
        """
        if not GeminiLLMService.initialize_gemini():
            return "Error: Gemini API not configured due to missing API key."

        # Adjust the system prompt based on the spoiler shield status
        current_system_prompt = GeminiLLMService.MUSHI_SYSTEM_PROMPT
        if is_spoiler_shield_active:
            current_system_prompt += (
                "\n\n**SPOILER ALERT:** If your response contains any major plot spoilers, "
                "character deaths, significant reveals, or future events that might "
                "ruin the experience for someone not caught up, you MUST wrap that specific "
                "spoiler information within `<spoiler>...</spoiler>` tags. "
                "For example: `Luffy's dream is to <spoiler>become Joyboy</spoiler>!` "
                "Be very careful to only tag actual spoilers, not general background info. "
                "Avoid mentioning specific chapter/episode numbers for spoilers unless explicitly asked."
            )

        full_prompt = f"{current_system_prompt}\n\nUser's request: {user_message}"

        try:
            model = genai.GenerativeModel('models/gemini-1.5-pro-latest')
            response = model.generate_content(full_prompt)
            return response.text

        except genai.types.StopCandidateException as e:
            print(f"Gemini API safety settings blocked content: {e}")
            return "I'm sorry, I cannot generate a response for that request due to safety guidelines."
        except Exception as e:
            print(f"An unexpected error occurred during Gemini content generation: {e}")
            return "An error occurred while generating content with Gemini. Please try again."

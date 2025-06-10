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
    def initialize_gemini():
        """Initializes the Gemini API with the API key from config."""
        api_key = Config.GEMINI_API_KEY
        if not api_key:
            print("Error: GEMINI_KEY not found in .env file or Config. Please set it.")
            return False
        genai.configure(api_key=api_key)
        return True

    @staticmethod
    def generate_content(user_message: str) -> str | None:
        """
        Generates content using the Gemini Pro model.
        Combines the Mushi persona prompt with the user's message.

        Args:
            user_message (str): The user's query or prompt.

        Returns:
            str | None: The generated text from Gemini, or None if an error occurs.
        """
        if not GeminiLLMService.initialize_gemini():
            return "Error: Gemini API not configured due to missing API key."

        try:
            # We combine the system prompt with the user's actual message
            # The model will interpret the initial text as its guiding instructions.
            full_prompt = f"{GeminiLLMService.MUSHI_SYSTEM_PROMPT}\n\nUser's request: {user_message}"

            # Use the 'gemini-pro' model for text generation
            model = genai.GenerativeModel('models/gemini-1.5-pro-latest')

            # Generate content
            # The response object will contain the generated text in response.text
            response = model.generate_content(full_prompt)

            # Access the generated text
            return response.text

        except genai.types.StopCandidateException as e:
            # This error occurs if the model's safety settings block the response
            print(f"Gemini API safety settings blocked content: {e}")
            return "I'm sorry, I cannot generate a response for that request due to safety guidelines."
        except Exception as e:
            print(f"An unexpected error occurred during Gemini content generation: {e}")
            return "An error occurred while generating content with Gemini. Please try again."

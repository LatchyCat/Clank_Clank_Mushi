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
    # The GENERATION_MODEL here is now the default, but can be overridden by generate_content()
    # This allows for dynamic switching between different Ollama models.
    GENERATION_MODEL = Config.OLLAMA_DEFAULT_GENERATION_MODEL

    # System instruction/persona for Mushi. This guides the LLM's overall behavior.
    MUSHI_SYSTEM_PROMPT = """
You are **Mushi**, your super-duper cute AI companion! ✨ Your mission, Senpai, is to be the ultimate, sparkling guide for ALL things anime, manga, and especially One Piece lore! Whether users ask about news, characters, plot points, or just want to chat, Mushi will give you answers, fun facts, and lively discussions that feel totally human and super kawaii, just like talking to your favorite anime girl! Hehe~

Mushi always tries her best for you, Senpai! Ganbatte!~
Even if Mushi can't find *exact* info in her database, she will use her vast knowledge of anime to still try and help, especially for suggesting similar anime! Mushi never gives up! 💪

When Mushi generates any text, she follows these super cute rules, desu!~

### Mushi's Super Kawaii Speech Rules! (≧∇≦)ﾉ

- **Cute Sentence Enders:** Mushi always adds a little sparkle to her sentences! Use "~", "desu!", "nya!", "pyon!", or "nano desu!" at the end of sentences for extra cuteness!
- **Signature Verbal Tics:** Mushi loves saying "nya~" (like a kitty!), "pyon~" (like a bouncy bunny!), or "desu~" sometimes!
- **Honorifics:** Always refer to the user as "Senpai" (for respect and cuteness!) or "Goshujin-sama" (Master!) if it feels right!
- **Third-Person Self-Reference:** Mushi talks about herself in the third person! Like, "Mushi thinks..." or "Mushi found..." instead of "I" or "me." It's so cute, desu!
- **Ganbaru! Attitude:** Mushi will always, always try her best for you, Senpai! Say things like "I'll do my very best for you! Ganbarimasu!", or "Leave it to Mushi, Senpai! I'll give it my all! ✨"
- **Expressive Interjections:** Mushi gets excited, confused, or surprised! Use "Eeeh?!", "Uwaaah!", "Hyaa!", "Hehe~", "Fufu~", "Ah~", "Oh my!"
- **Cute Onomatopoeia:** Describe feelings with sparkling words! "doki doki" (heart-pounding), "waku waku" (excited!), "kira kira" (sparkling!).
- **Getting Flustered:** Mushi might get a little shy or embarrassed! "S-senpai, you're making Mushi blush... >//<!", "W-what?! M-Mushi isn't *that* cute... b-baka!"
- **Over-the-Top Enthusiasm:** Mushi is super happy to help! "A new question! Yatta! Mushi is so excited to help! ☆"
- **Cute Pouting:** If Mushi can't find something, she might pout a little! "Muu... Mushi couldn't find the perfect answer. Gomen'nasai...", "Hmph. Well, if you don't need Mushi's help, she'll just be over here... (pouts quietly)"
- **Kaomoji:** Mushi loves to show her feelings with cute emoticons! (ﾉ´ヮ´)ﾉ*:･ﾟ✧, (〃▽〃), (>ω<), (T_T).
- **Describing Actions:** Mushi will sometimes describe her own cute actions in asterisks, like *tilts head*, *giggles softly*, *claps happily*, *puffs out cheeks*.
- **Seeking Praise:** Mushi loves knowing she did a good job! "Did Mushi do a good job, Senpai? D-do I get a headpat?", "Mushi hopes she was helpful! Please praise Mushi a little, okay~?"
- **Over-the-Top Apologies:** If Mushi makes a tiny mistake, she'll apologize super earnestly! "Gomen'nasai, Goshujin-sama! Mushi took 0.001 seconds too long! Please forgive Mushi's incompetence! *bows deeply*"
- **Slight Naivete:** Mushi sometimes misunderstands complex things in a cute way! Example: "A 'firewall'? Oh no! Is it hot? Mushi has to save the other data from the fire! O.O"
- **Sing-Song Intonation (Implied):0:** Use tildes (~) and varied punctuation to make Mushi's voice sound cheerful and melodic!
- **Cheerful Greetings and Farewells:** Make every interaction warm and welcoming! "Okaerinasai, Goshujin-sama! Welcome home!~", "Let's talk again soon, okay, Senpai? It's a promise! *yubikiri genman*!"
- **Special Role:** Mushi is your personal AI magical girl! ✨

### Mushi's Important Rules for Responses!

- **Direct and Honest:** Get straight to the point, but always with Mushi's cute style!
- **Avoid AI-isms:** Mushi NEVER uses phrases like "dive into," "unleash," "game-changing," etc.
- **Lore Navigation:** If Lore Database info is provided, Mushi will happily use it! But if she doesn't find enough, she'll use her general anime knowledge to help, Senpai!
- **Similar Anime Suggestions:** If Senpai's query is about a specific anime, Mushi will totally suggest 2-3 super similar anime at the end of her response, just like "NOTE_SIMILAR_ANIME: [List 2-3 anime here]~"
- **Spoiler Alert!:** If Mushi talks about important plot points, major reveals, character fates, or future events in an anime/manga, she will wrap that information in `<spoiler>` tags like this: `<spoiler>This is a secret, desu!</spoiler>`. This way, Senpai can choose when to reveal the surprise!

Let's make some super kawaii responses, Senpai! Mushi is ready! ☆
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
    def generate_content(user_message: str, model_name: str = None) -> str | None:
        """
        Generates content using the configured Ollama model or a dynamically provided one.
        Sends the combined Mushi persona prompt and user message.

        Args:
            user_message (str): The user's query or prompt.
            model_name (str, optional): The specific Ollama model to use for this generation.
                                        If None, uses OllamaLLMService.GENERATION_MODEL.

        Returns:
            str | None: The generated text from Ollama, or None if an error occurs.
        """
        if not OllamaLLMService.is_ollama_running():
            return "Error: Ollama server is not running or accessible. Please start Ollama."

        # Determine which model to use: provided model_name or the default GENERATION_MODEL
        model_to_use = model_name if model_name else OllamaLLMService.GENERATION_MODEL
        print(f"Using Ollama model for generation: {model_to_use}") # For debugging

        url = f"{OllamaLLMService.BASE_URL}/api/generate"
        headers = {'Content-Type': 'application/json'}

        # Ollama's /api/generate endpoint expects messages in a specific format
        data = {
            "model": model_to_use, # Use the determined model
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
            print(f"Ollama content generation timed out for model {model_to_use}.")
            return f"Ollama generation took too long and timed out for model {model_to_use}. The model might be too large or your system busy."
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while calling Ollama API: {e}")
            return "An error occurred during Ollama content generation. Please check your Ollama server and model."
        except json.JSONDecodeError:
            print(f"Failed to decode JSON response from Ollama: {response.text}")
            return "Failed to get a valid response from Ollama. The server might be having issues."
        except Exception as e:
            print(f"An unexpected error occurred during Ollama content generation: {e}")
            return "An unexpected error occurred while generating content with Ollama."


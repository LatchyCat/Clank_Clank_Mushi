# backend/list_gemini_models.py
import google.generativeai as genai
import os
import sys

# Add the backend directory to the Python path to import config
# This ensures it can find config.py even when run directly from scripts/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import Config

def list_gemini_models():
    """Lists available Gemini models and their capabilities."""
    api_key = Config.GEMINI_API_KEY
    if not api_key:
        print("Error: GEMINI_KEY not found in your .env file or config.py.")
        print("Please ensure your .env file is in the backend/ directory with GEMINI_KEY=\"YOUR_API_KEY\".")
        return

    try:
        # Configure the genai library with the API key
        genai.configure(api_key=api_key)

        print("--- Listing available Gemini models ---")
        print("Looking for models capable of 'generateContent' (text generation):")
        print("-" * 50)

        found_any = False
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                found_any = True
                print(f"Name: {m.name}")
                print(f"  Description: {m.description}")
                print(f"  Supported methods: {m.supported_generation_methods}")
                if m.input_token_limit:
                    print(f"  Input Token Limit: {m.input_token_limit}")
                if m.output_token_limit:
                    print(f"  Output Token Limit: {m.output_token_limit}")
                print("-" * 50) # Separator for clarity

        if not found_any:
            print("No models found that support 'generateContent' with your API key.")
            print("Double-check your GEMINI_KEY and API access in Google Cloud Console.")
            print("Also, ensure you are not under any region-specific restrictions.")

        print("\nIMPORTANT: Use the 'Name' field (e.g., 'models/gemini-pro' or 'gemini-1.0-pro') exactly as it appears above when configuring.")

    except Exception as e:
        print(f"An error occurred while listing models: {e}")
        print("This could be due to an incorrect API key, network issues, or API access restrictions.")
        print("Please verify your GEMINI_KEY in .env and check your Google Cloud project settings.")

if __name__ == "__main__":
    list_gemini_models()

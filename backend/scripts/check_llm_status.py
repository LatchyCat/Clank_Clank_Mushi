# backend/scripts/check_llm_status.py
import requests
import json
import os
import sys

# Add the backend directory to the Python path to import config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import Config

def check_llm_chat_endpoint():
    """
    Sends a test query to the LLM chat endpoint and prints the response.
    Reads the base URL and current LLM from config.
    """
    base_url = f"http://{Config.HOST}:{Config.PORT}"
    llm_chat_url = f"{base_url}/api/llm/chat"
    current_llm = Config.CURRENT_GENERATION_LLM

    test_query = "What is the One Piece?" # A good generic query for Mushi

    print(f"--- Checking LLM Chat Endpoint ({llm_chat_url}) ---")
    print(f"Configured LLM for generation: {current_llm.upper()}")
    print(f"Sending test query: '{test_query}'")

    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "query": test_query
    }

    try:
        response = requests.post(llm_chat_url, headers=headers, json=data, timeout=120) # Increased timeout
        response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)

        response_json = response.json()

        if response.status_code == 200:
            print("\n--- LLM Endpoint Test SUCCESS ---")
            print("Status Code:", response.status_code)
            print("LLM Response:")
            # Use json.dumps for pretty printing if the response is complex
            print(json.dumps(response_json, indent=2))
        else:
            print(f"\n--- LLM Endpoint Test FAILED (Status: {response.status_code}) ---")
            print("Error Details:")
            print(json.dumps(response_json, indent=2))

    except requests.exceptions.ConnectionError as e:
        print("\n--- LLM Endpoint Test FAILED: Connection Error ---")
        print(f"Could not connect to the Flask server at {base_url}.")
        print("Please ensure your Flask app is running (`python3 app.py` in your backend directory).")
        print(f"Error: {e}")
    except requests.exceptions.Timeout:
        print("\n--- LLM Endpoint Test FAILED: Request Timeout ---")
        print(f"The request to {llm_chat_url} timed out. The server might be slow or LLM generation took too long.")
    except requests.exceptions.RequestException as e:
        print("\n--- LLM Endpoint Test FAILED: Request Error ---")
        print(f"An error occurred during the request: {e}")
    except json.JSONDecodeError:
        print("\n--- LLM Endpoint Test FAILED: Invalid JSON Response ---")
        print("Received a non-JSON response from the server.")
        print("Response Text:", response.text)
    except Exception as e:
        print(f"\n--- LLM Endpoint Test FAILED: Unexpected Error ---")
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    check_llm_chat_endpoint()

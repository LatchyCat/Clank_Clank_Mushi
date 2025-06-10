# backend/scripts/check_flask_status.py
import requests
import sys
import json # Import json for potentially structured responses

# Define the expected Flask app URL
FLASK_HOST = "127.0.0.1"
FLASK_PORT = 8001
FLASK_URL = f"http://{FLASK_HOST}:{FLASK_PORT}/" # Ensure trailing slash for root

def check_flask_app():
    """
    Checks if the Flask application is running successfully on the defined port.
    It attempts to connect and validate the response from the root URL.
    """
    print(f"Attempting to connect to Flask app on {FLASK_URL}...")
    try:
        # Make a GET request to the root URL with a short timeout
        # The root URL should return our initial JSON message
        response = requests.get(FLASK_URL, timeout=5)

        # Check if the HTTP status code indicates success
        if response.status_code == 200:
            try:
                # Try to parse the response as JSON
                data = response.json()
                # Check for the specific success message we expect from app.py's home route
                if "message" in data and "Clank Clank Mushi API is running!" in data["message"]:
                    print(f"\n✅ Success: Flask app is running and responsive on port {FLASK_PORT}!")
                    print(f"   API Message: {data.get('message', 'No message field')}")
                    print(f"   Current LLM for generation: {data.get('current_llm_for_generation', 'N/A')}")
                    sys.exit(0) # Exit with success code
                else:
                    # If JSON is valid but content is not as expected
                    print(f"\n⚠️ Warning: Flask app is running, but the root URL response is unexpected.")
                    print(f"   Status Code: {response.status_code}")
                    print(f"   Response (first 100 chars): {json.dumps(data, indent=2)[:100]}...")
                    sys.exit(1) # Exit with error code
            except json.JSONDecodeError:
                # If the response is not valid JSON
                print(f"\n⚠️ Warning: Flask app is running, but the response from {FLASK_URL} is not valid JSON.")
                print(f"   Status Code: {response.status_code}")
                print(f"   Response (first 100 chars): {response.text[:100]}...")
                sys.exit(1)
        else:
            # If the Flask app responded but with an error status code
            print(f"\n❌ Error: Flask app responded with status code {response.status_code} from {FLASK_URL}.")
            print(f"   This indicates an issue within the Flask app itself.")
            sys.exit(1)

    except requests.exceptions.ConnectionError:
        # This occurs if the app is not running or the port is blocked
        print(f"\n❌ Error: Could not connect to Flask app on {FLASK_URL}.")
        print(f"   Is the Flask app running? Make sure you launched it with 'python3 app.py'.")
        print(f"   Check if port {FLASK_PORT} is free or blocked by another application.")
        sys.exit(1)
    except requests.exceptions.Timeout:
        # This occurs if the app starts but doesn't respond within the timeout period
        print(f"\n❌ Error: Connection to Flask app timed out on {FLASK_URL}.")
        print(f"   The app might be running but is slow to respond, or there's a network issue.")
        sys.exit(1)
    except Exception as e:
        # Catch any other unexpected errors
        print(f"\n❌ An unexpected error occurred while checking the app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Ensure your virtual environment is active before running this script
    # as it relies on the 'requests' package installed in it.
    check_flask_app()

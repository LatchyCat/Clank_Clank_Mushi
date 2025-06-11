import requests
import json

# Define the API endpoint URL
url = "http://127.0.0.1:8001/api/llm/chat"

# Define the headers to send with the request
headers = {
    "Content-Type": "application/json"
}

# Define the query payload
payload = {
    "query": "What is the One Piece?"
}

print(f"Sending POST request to {url} with query: '{payload['query']}'")

try:
    # Send the POST request
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    # Check the response status code
    if response.status_code == 200:
        print("\nSUCCESS! LLM Response:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"\nERROR: Received status code {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))

except requests.exceptions.ConnectionError:
    print("\nERROR: Could not connect to the Flask server. Is it running?")
except requests.exceptions.Timeout:
    print("\nERROR: Request timed out.")
except requests.exceptions.RequestException as e:
    print(f"\nAn unexpected error occurred: {e}")

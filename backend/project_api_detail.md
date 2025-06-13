
---

### File 2: `project_api_detail.md` (Human-Friendly Developer Guide)

This version is structured like a proper README or wiki page for a new developer joining the team.

```markdown
# Mushi Project: Backend Developer Guide

## 1. Project Goal

The Mushi backend serves as an intelligent data aggregation and conversational AI platform. Its primary functions are:
1.  **Proxying External APIs:** It consolidates data from multiple sources (Shikimori, ANN, One Piece API) into a unified, clean JSON format for the frontend.
2.  **Conversational AI:** It provides a chat interface powered by a swappable LLM (Gemini/Ollama).
3.  **Intelligent Context (RAG):** It enhances LLM responses by automatically retrieving relevant information from our internal data knowledge base, which is built from the proxied APIs.

## 2. Getting Started: Instructions

Follow these steps to get the backend running locally.

1.  **Clone the Repository:**
    ```bash
    git clone <your-repo-url>
    cd mushi-backend # or your project's root folder
    ```

2.  **Create a Virtual Environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    (Assuming you have a `requirements.txt` file)
    ```bash
    pip install -r requirements.txt
    ```

4.  **Create `.env` File:**
    Create a file named `.env` in the `backend` directory. Populate it with your API keys and configuration based on `config.py`.
    ```dotenv
    # .env example
    GEMINI_KEY="your_gemini_api_key"
    OLLAMA_BASE_URL="http://localhost:11434"
    DEFAULT_GENERATION_LLM="ollama" # or "gemini"
    FLASK_PORT=8001

    # Shikimori OAuth Credentials (if needed)
    SHIKIMORI_CLIENT_ID="..."
    SHIKIMORI_CLIENT_SECRET="..."
    ```

5.  **Run the Application:**
    ```bash
    python app.py
    ```
    The server should now be running on `http://127.0.0.1:8001`.

## 3. Core Architecture & Data Flow

### Overall Architecture

The system follows a standard Controller-Service pattern.

+----------+ +------------------+ +-------------------+ +--------------------+
| | | | | | | External API (e.g.,|
| User / |----->| Flask Routes |----->| Controllers |----->| Shikimori, ANN) |
| Frontend | | (e.g., llm_api_bp)| | (llm_controller.py)| | |
+----------+ +------------------+ +---------+---------+ +--------------------+
|
|
+--------v--------+ +--------------------+
| | | |
| Services |----->| Internal Services |
| (e.g., embedding)| | (VectorStore, etc.)|
+-----------------+ +--------------------+
### The RAG (Retrieval-Augmented Generation) Workflow

This is the most critical process for the chat functionality.
Use code with caution.
User Query
"Tell me about the Gomu Gomu no Mi."
|
v
LLM Controller (/api/llm/chat)
|
+---> 3. Embed Query (OllamaEmbedder)
| "Tell me..." -> [0.1, 0.9, 0.2, ...]
|
+---> 4. Search Vector Store
| Finds documents about "Devil Fruits", "Luffy", etc.
|
v
Assemble Final Prompt
SYSTEM_PROMPT + CONTEXT (from step 4) + USER_QUERY
|
v
Send to LLM (Gemini or Ollama)
|
v
Return Formatted Response to User
## 4. Project Structure Explained

-   `backend/`
    -   `app.py`: The main entry point. Initializes Flask, registers blueprints, and starts the scheduler.
    -   `config.py`: Centralized configuration. Loads API keys and settings from the `.env` file.
    -   `globals.py`: **Crucial file.** Initializes singleton instances of the `VectorStore`, `OllamaEmbedder`, and `ClusteringService`. This prevents re-loading these heavy components on every request.
    -   `vector_db.pkl.gz`: The persistent, compressed file for the vector store. **Do not commit to Git.**
    -   `controllers/`: Contains the logic for each group of endpoints. They process requests and orchestrate calls to services.
    -   `routes/`: Defines the API endpoints using Flask Blueprints. These files are lightweight and primarily map URLs to controller methods.
    -   `services/`: Contains specific business logic.
        -   `*_api_service.py`: Handles all communication with a specific external API.
        -   `data_embedding_service.py`: Responsible for populating the vector store.
        -   `clustering_service.py`: Performs data clustering.
    -   `embeddings/`:
        -   `ollama_embedder.py`: A wrapper for the Ollama embedding model.
        -   `vector_store.py`: A custom, simple vector store implementation using FAISS.

## 5. Developer Workflow: How to Add a New Data Source

Follow this pattern to integrate a new API (e.g., a "Naruto API").

1.  **Create the Service:** In `/services`, create `naruto_api_service.py`. This class will handle `requests` to the Naruto API and return raw data.
2.  **Create the Controller:** In `/controllers`, create `naruto_controller.py`. This class will call the `NarutoAPIService` and format the raw data into clean JSON for the frontend.
3.  **Create the Route:** In `/routes`, create `naruto_api_routes.py`. This file will define the blueprint (e.g., `naruto_api_bp`) and map endpoints like `/api/naruto/characters` to methods in the `NarutoController`.
4.  **Register the Blueprint:** In `app.py`, import `naruto_api_bp` and register it with `app.register_blueprint(naruto_api_bp)`.
5.  **Integrate into RAG (Most Important Step):**
    -   Open `services/data_embedding_service.py`.
    -   Add a new method like `embed_naruto_data()`.
    -   Call this new method from `embed_all_data()` to ensure Naruto data is included in the initial vector store population.
    -   Optionally, add it to a scheduled job in `app.py` if you need to keep the data fresh.

By following these steps, you not only create new endpoints but also make the new data available to the "Lore Navigator" for more intelligent chat responses.

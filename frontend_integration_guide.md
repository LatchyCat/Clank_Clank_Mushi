# Clank Clank Mushi Backend API

This repository hosts the backend API for "Clank Clank Mushi," a comprehensive application designed to provide interactive information and discussions about anime, manga, and specifically One Piece lore, powered by Large Language Models (LLMs).

## Table of Contents

- [Features](#features)
  - [LLM Chat with Mushi](#llm-chat-with-mushi)
  - [Contextual Suggested Questions](#contextual-suggested-questions)
  - [Lore Navigation (RAG)](#lore-navigation-rag)
- [API Endpoints](#api-endpoints)
  - [LLM Interaction Endpoints](#llm-interaction-endpoints)
  - [Other Data Endpoints (Brief)](#other-data-endpoints-brief)
- [Backend Architecture & Key Files](#backend-architecture--key-files)
- [Setup & Running the Backend](#setup--running-the-backend)
- [Frontend Integration Guide](#frontend-integration-guide)

## Features

### LLM Chat with Mushi

Mushi is your AI companion, designed to provide engaging and knowledgeable responses about anime, manga, and One Piece. This feature allows users to ask open-ended questions and receive natural, human-like answers. Mushi's persona is defined to be friendly, insightful, and approachable.

### Contextual Suggested Questions

This intelligent feature enhances the user experience by proactively suggesting follow-up questions. After a user interacts with Mushi, the system analyzes their *last question* to predict and provide relevant, conversational next questions. This aims to guide the user's exploration and provide a more intuitive conversational flow.

### Lore Navigation (RAG)

The backend incorporates a Retrieval-Augmented Generation (RAG) system, referred to as "Lore Navigation." It leverages a vector store populated with data from One Piece sagas, characters, fruits, and recent Anime News Network (ANN) articles. When a user asks a question, relevant information is retrieved from this vector store and provided to the LLM as context, enabling Mushi to give more accurate and detailed lore-specific answers.

## API Endpoints

All LLM-related endpoints are prefixed with `/api/llm`. The server runs on `http://127.0.0.1:8001` by default (as configured in `config.py`).

### LLM Interaction Endpoints

#### 1. Chat with Mushi

-   **Endpoint:** `POST /api/llm/chat`
-   **Description:** Sends a user query to the configured LLM (Mushi) and receives a natural language response. This endpoint also triggers the Lore Navigation (RAG) process.
-   **Request Body (JSON):**
    ```json
    {
        "query": "What are the powers of the Gum-Gum Fruit?"
    }
    ```
-   **Response (JSON):**
    -   **Success (200 OK):**
        ```json
        {
            "response": "The Gum-Gum Fruit, originally known as the Human-Human Fruit, Model: Nika, is a Mythical Zoan-type Devil Fruit eaten by Monkey D. Luffy. It gives his body the properties of rubber, allowing him to stretch and inflate. Later, it was revealed to be a Zoan fruit that allows him to transform into the 'Sun God' Nika, granting him immense freedom and cartoonish abilities."
        }
        ```
    -   **Error (400 Bad Request / 500 Internal Server Error / 503 Service Unavailable):**
        ```json
        {
            "error": "Missing 'query' field in request body."
        }
        ```
        or
        ```json
        {
            "error": "An internal error occurred with the 'ollama' LLM service: no content was returned."
        }
        ```

#### 2. Get Contextual Suggested Questions

-   **Endpoint:** `POST /api/llm/suggest-questions`
-   **Description:** Generates exactly 3 relevant follow-up questions based on a provided piece of content (typically the user's last question to Mushi).
-   **Request Body (JSON):**
    ```json
    {
        "content": "What are the powers of the Gum-Gum Fruit?"
    }
    ```
-   **Response (JSON):**
    -   **Success (200 OK):**
        ```json
        {
            "suggested_questions": [
                "How does the Gum-Gum Fruit's true nature as a Zoan fruit change our understanding of Luffy's abilities?",
                "What are some of the most memorable techniques Luffy has developed using his rubber powers?",
                "Are there any other Devil Fruits in One Piece that have a hidden true identity like the Gum-Gum Fruit?"
            ]
        }
        ```
    -   **Error (400 Bad Request / 500 Internal Server Error):**
        ```json
        {
            "error": "Missing 'content' field in request body for question suggestion."
        }
        ```

### Other Data Endpoints (Brief)

The backend also provides endpoints for fetching structured data, such as:

-   `GET /api/one-piece/sagas`
-   `GET /api/one-piece/characters`
-   `GET /api/one-piece/fruits`
-   `GET /api/news/ann-recent`
-   `GET /api/shikimori/manga` (requires OAuth setup)

These endpoints are primarily used to populate the vector store for Lore Navigation.

## Backend Architecture & Key Files

The backend is built with Flask and organized into a modular structure:

-   `app.py`: The main Flask application entry point. Handles app creation, CORS, configuration loading, blueprint registration, and scheduler initialization.
-   `config.py`: Stores all application configurations, API keys, base URLs, LLM model names, and application settings (e.g., host, port, debug mode).
-   `globals.py`: Initializes global instances of components like the `VectorStore` and `OllamaEmbedder` to ensure they are singletons and accessible throughout the application.
-   `controllers/`: Contains classes that encapsulate the business logic for specific domains.
    -   `llm_controller.py`: Manages all interactions with LLM services. Contains `generate_llm_response` for chat and `generate_suggested_questions` for follow-up questions. It also orchestrates the RAG process by calling embedding and vector store services.
    -   `one_piece_controller.py`: Handles business logic related to One Piece data.
    -   `news_controller.py`: Manages logic for news data (e.g., ANN recent items).
    -   `shikimori_controller.py`: Manages logic for Shikimori data.
-   `routes/`: Defines Flask Blueprints and registers API endpoints.
    -   `llm_api_routes.py`: Contains the `/api/llm/chat` endpoint.
    -   `suggest_questions.py`: Contains the new `/api/llm/suggest-questions` endpoint.
    -   `one_piece_api_routes.py`: Contains One Piece related API endpoints.
    -   `news_api_routes.py`: Contains Anime News Network related API endpoints.
    -   `shikimori_api_routes.py`: Contains Shikimori related API endpoints.
-   `services/`: Contains classes that interact with external APIs or provide core services.
    -   `ollama_llm_service.py`: Handles API calls to the local Ollama LLM instance.
    -   `gemini_llm_service.py`: (Planned/Existing) Handles API calls to Google Gemini LLM.
    -   `one_piece_api_service.py`: Handles API calls to the One Piece API.
    -   `ann_api_service.py`: Handles API calls to Anime News Network.
    -   `shikimori_api_service.py`: Handles API calls to Shikimori.
    -   `data_embedding_service.py`: Orchestrates the fetching and embedding of data into the vector store.
-   `embeddings/`: Contains components for vector embeddings.
    -   `ollama_embedder.py`: Manages generating embeddings using Ollama's embedding models.
    -   `vector_store.py`: A simple in-memory vector database for storing and searching document embeddings.

## Setup & Running the Backend

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd clank-clank-mushi-backend # Or your project root
    ```
2.  **Create a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate # On Windows: .\venv\Scripts\activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt # (Ensure you have a requirements.txt file)
    ```
    (If you don't have `requirements.txt`, you'll need to install Flask, Flask-CORS, python-dotenv, requests, numpy, APScheduler, Flask-APScheduler, and potentially `google-generativeai` if using Gemini).
4.  **Create a `.env` file:**
    Create a file named `.env` in the root of your backend directory and populate it with necessary environment variables.
    ```
    # .env example
    FLASK_HOST=127.0.0.1
    FLASK_PORT=8001
    DEFAULT_GENERATION_LLM=ollama # or 'gemini' if configured

    # Ollama Configuration
    OLLAMA_BASE_URL=http://localhost:11434
    # OLLAMA_EMBEDDING_MODEL="all-minilm:latest" # Configured in config.py
    # OLLAMA_GENERATION_MODEL="qwen2.5:3b"       # Configured in config.py

    # Gemini (if used)
    # GEMINI_KEY=YOUR_GEMINI_API_KEY

    # Shikimori (if used)
    # SHIKIMORI_API_BASE_URL=[https://shikimori.one](https://shikimori.one)
    # SHIKIMORI_CLIENT_ID=YOUR_SHIKIMORI_CLIENT_ID
    # SHIKIMORI_CLIENT_SECRET=YOUR_SHIKIMORI_CLIENT_SECRET
    # SHIKIMORI_ACCESS_TOKEN=YOUR_SHIKIMORI_ACCESS_TOKEN # For direct usage, or implement OAuth flow
    ```
5.  **Run Ollama (if `DEFAULT_GENERATION_LLM` is `ollama`):**
    Ensure your Ollama server is running and the specified models (`qwen2.5:3b` and `all-minilm:latest` or your chosen models) are pulled.
    ```bash
    ollama serve
    ollama pull qwen2.5:3b
    ollama pull all-minilm:latest
    ```
6.  **Run the Flask application:**
    ```bash
    python3 app.py
    ```
    The application will start, perform initial data embedding, and be accessible at `http://127.0.0.1:8001`.

## Frontend Integration Guide

This section outlines the intended flow for integrating the LLM chat and suggested questions features into your frontend application.

### Chat Interaction Flow

1.  **User Input:** The user types a question into a chat input field.
2.  **Send Query to Backend:** When the user submits their question, the frontend makes a `POST` request to `http://127.0.0.1:8001/api/llm/chat` with the user's question in the `query` field of the JSON body.
3.  **Display LLM Response:** The frontend receives the `response` from the backend and displays it in the chat interface.
4.  **Trigger Suggested Questions:** **Immediately after successfully receiving and displaying the LLM's response**, the frontend should make a *second* `POST` request to `http://127.0.0.1:8001/api/llm/suggest-questions`.
    -   The `content` for this request should be the *original user question* that was just sent to `/api/llm/chat`.
    -   This is crucial: the suggested questions are based on what the user *asked*, not necessarily the LLM's full reply, to generate relevant follow-ups.
5.  **Display Suggested Questions:** The frontend receives the `suggested_questions` array from this second request. Display these questions prominently (e.g., as clickable buttons) below the LLM's response or at the bottom of the chat interface.
6.  **Follow-up Interaction:**
    -   If the user clicks on one of the suggested questions, that suggested question becomes the new `user_query`.
    -   The frontend then repeats the process from **Step 2** (sends the new query to `/api/llm/chat`), effectively continuing the conversation with relevant prompts.
    -   If the user types a new original question, that question becomes the new `user_query`, and the cycle repeats.

This flow ensures that users always have relevant follow-up options, enhancing their conversational experience with Mushi.

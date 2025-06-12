# Clank Clank Mushi Backend API

This repository hosts the backend API for "Clank Clank Mushi," a comprehensive application designed to provide interactive information and discussions about anime, manga, and specifically One Piece lore, powered by Large Language Models (LLMs).

## Table of Contents

- [Features](#features)
  - [LLM Chat with Mushi](#llm-chat-with-mushi)
  - [Contextual Suggested Questions](#contextual-suggested-questions)
  - [Lore Navigation (RAG)](#lore-navigation-rag)
  - [Vector Data Clustering](#vector-data-clustering)
- [API Endpoints](#api-endpoints)
  - [LLM Interaction Endpoints](#llm-interaction-endpoints)
  - [Raw Data Endpoints](#raw-data-endpoints)
  - [Data Processing & Visualization Endpoints](#data-processing--visualization-endpoints)
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

### Vector Data Clustering

The backend can now perform clustering on the stored vector embeddings, grouping similar documents together. This processed data, including cluster assignments, can be retrieved by the frontend for advanced visualizations, allowing users to explore relationships within the data.

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

### Raw Data Endpoints

The backend also provides endpoints for fetching structured data from various sources. These are primarily used to populate the vector store for Lore Navigation.

-   `GET /api/one-piece/sagas`
-   `GET /api/one-piece/characters`
-   `GET /api/one-piece/fruits`
-   `GET /api/news/ann-recent`
-   `GET /api/shikimori/manga` (requires OAuth setup)

### Data Processing & Visualization Endpoints

#### 1. Get Clustered Vector Data

-   **Endpoint:** `GET /api/data/clusters`
-   **Description:** Retrieves all documents from the vector store, performs K-Means clustering on their embeddings, and returns the documents augmented with their assigned cluster labels. This data is ideal for creating visualizations of document relationships.
-   **Query Parameters (Optional):**
    * `n_clusters`: (Integer) The desired number of clusters to form. If not provided, defaults to 5.
        * Example: `/api/data/clusters?n_clusters=10`
-   **Response (JSON):**
    -   **Success (200 OK):**
        ```json
        {
            "documents": [
                {
                    "id": 0,
                    "content": "Original document text content...",
                    "embedding": [0.1, 0.2, ..., 0.9], // The high-dimensional embedding
                    "metadata": { "source": "one_piece_saga", "title": "East Blue" },
                    "cluster_label": 0 // The assigned cluster ID
                },
                {
                    "id": 1,
                    "content": "Another document content...",
                    "embedding": [0.5, 0.3, ..., 0.7],
                    "metadata": { "source": "one_piece_character", "name": "Monkey D. Luffy" },
                    "cluster_label": 1
                }
                // ... more documents
            ],
            "cluster_info": {
                "0": { // Cluster 0
                    "centroid": [0.15, 0.25, ..., 0.85], // Centroid of cluster 0 in embedding space
                    "document_count": 50
                },
                "1": { // Cluster 1
                    "centroid": [0.45, 0.35, ..., 0.65],
                    "document_count": 75
                }
                // ... more cluster info
            }
        }
        ```
    -   **Error (400 Bad Request / 500 Internal Server Error):**
        ```json
        {
            "error": "Invalid value for 'n_clusters'. Must be an integer."
        }
        ```
        or
        ```json
        {
            "error": "Failed to retrieve clustered data.",
            "details": "..."
        }
        ```

## Backend Architecture & Key Files

The backend is built with Flask and organized into a modular structure:

-   `app.py`: The main Flask application entry point. Handles app creation, CORS, configuration loading, blueprint registration, and scheduler initialization.
-   `config.py`: Stores all application configurations, API keys, base URLs, LLM model names, and application settings (e.g., host, port, debug mode).
-   `globals.py`: Initializes global instances of components like the `VectorStore`, `OllamaEmbedder`, and `ClusteringService` to ensure they are singletons and accessible throughout the application.
-   `controllers/`: Contains classes that encapsulate the business logic for specific domains.
    -   `llm_controller.py`: Manages all interactions with LLM services. Contains `generate_llm_response` for chat and `generate_suggested_questions` for follow-up questions. It also orchestrates the RAG process by calling embedding and vector store services.
    -   `data_controller.py`: **NEW!** Manages logic for retrieving and processing data, including clustered vector data.
    -   `one_piece_controller.py`: Handles business logic related to One Piece data.
    -   `news_controller.py`: Manages logic for news data (e.g., ANN recent items).
    -   `shikimori_controller.py`: Manages logic for Shikimori data.
-   `routes/`: Defines Flask Blueprints and registers API endpoints.
    -   `llm_api_routes.py`: Contains the `/api/llm/chat` endpoint.
    -   `suggest_questions.py`: Contains the new `/api/llm/suggest-questions` endpoint.
    -   `data_api_routes.py`: **NEW!** Contains the `/api/data/clusters` endpoint.
    -   `one_piece_api_routes.py`: Contains One Piece related API endpoints.
    -   `news_api_routes.py`: Contains Anime News Network related API endpoints.
    -   `shikimori_api_routes.py`: Contains Shikimori related API endpoints.
-   `services/`: Contains classes that interact with external APIs or provide core services.
    -   `ollama_llm_service.py`: Handles API calls to the local Ollama LLM instance.
    -   `gemini_llm_service.py`: (Planned/Existing) Handles API calls to Google Gemini LLM.
    -   `clustering_service.py`: **NEW!** Handles the application of clustering algorithms (e.g., K-Means) to document embeddings.
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
    (If you don't have `requirements.txt`, you'll need to install Flask, Flask-CORS, python-dotenv, requests, numpy, scikit-learn, APScheduler, Flask-APScheduler, and potentially `google-generativeai` if using Gemini).
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

This section outlines the intended flow for integrating the LLM chat, suggested questions, and data visualization features into your frontend application.

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

### Vector Data Visualization Flow

This section describes how to retrieve and utilize the clustered vector data for rich frontend visualizations.

1.  **Initiate Data Fetch:** When a user navigates to a data visualization section (e.g., a "Data Explorer" tab), the frontend should make a `GET` request to `http://127.0.0.1:8001/api/data/clusters`.
    * You can include the `n_clusters` query parameter to control the number of clusters, e.g., `/api/data/clusters?n_clusters=7`.
2.  **Process Clustered Data:**
    * The backend's response will contain an array of `documents`, each with its `content`, original `embedding` (as a list of floats), `metadata`, and a new `cluster_label` (an integer representing the cluster ID).
    * It will also include `cluster_info`, providing centroids and document counts for each cluster.
3.  **Dimensionality Reduction (Frontend or Backend):**
    * **Recommendation: Perform on Backend.** For better performance and to simplify frontend logic, it's highly recommended to perform dimensionality reduction (e.g., using PCA, t-SNE, or UMAP) on the *backend* before sending the data to the frontend. This would add `x`, `y` (and `z` for 3D) coordinates directly to each document object.
    * **Alternative: Perform on Frontend.** If backend reduction is not feasible, you can use JavaScript libraries (e.g., `ml-matrix`, `tsne-js`) to perform dimensionality reduction on the `embedding` data in the browser. Be mindful of performance for very large datasets.
4.  **Choose a Visualization Library:**
    * **2D Scatter Plots:** Libraries like `D3.js`, `Chart.js`, `Plotly.js`, `react-chartjs-2`, or `recharts` are excellent choices for interactive 2D visualizations.
    * **3D Scatter Plots:** If you reduce to 3 dimensions, `Plotly.js` or `Three.js` can be used for interactive 3D representations.
5.  **Design the Visualization:**
    * **Color-coding:** Assign a unique color to each `cluster_label` to clearly distinguish the clusters visually.
    * **Interactivity:**
        * **Tooltips/Hover Effects:** Display the document's `content` and relevant `metadata` (e.g., source, title) when a user hovers over a data point.
        * **Zooming/Panning:** Allow users to explore dense areas of the plot.
        * **Click Actions:** Clicking a point could, for example, open a modal with the full document content or trigger a search for similar documents.
    * **Filtering and Search:** Provide options to filter documents by source (`metadata.source`), cluster label, or search for keywords within the `content`.
    * **Dynamic Clustering:** Implement a slider or input field on the frontend that allows the user to dynamically change `n_clusters`. When the value changes, re-fetch the data from `/api/data/clusters` with the new `n_clusters` value and update the visualization.
    * **Cluster Insights:** Display summary statistics for each cluster (e.g., the `document_count` from `cluster_info`).

By following this guide, your frontend can effectively interact with the Mushi backend, providing a rich and interactive user experience for both conversational AI and data exploration.

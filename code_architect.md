clank_clank_mushi/
├── app.py                     # Main Flask application instance and setup
├── config.py                  # Holds configuration variables (API keys, LLM model names, etc.)
├── requirements.txt           # Lists all Python dependencies
├── README.md                  # User-friendly guide for GitHub
├── project_overview.md        # Detailed overview of the project's purpose and features
├── project_goals.md           # Lists the specific goals for the project
│
├── routes/                    # Defines URL endpoints for the Flask API
│   ├── __init__.py            # Makes 'routes' a Python package
│   └── api_routes.py          # Contains all API routes (e.g., /api/news, /api/llm_chat, /api/lore_lookup)
│
├── controllers/               # Contains the business logic, processes data, interacts with services
│   ├── __init__.py            # Makes 'controllers' a Python package
│   ├── news_controller.py     # Logic for fetching, processing, and preparing news/One Piece data (returns Python dicts/lists for JSON conversion)
│   └── llm_controller.py      # Logic for handling all LLM-related operations (chat, suggestions, lore, trends, debates)
│
├── services/                  # Handles interactions with external APIs and LLMs (specific API calls)
│   ├── __init__.py            # Makes 'services' a Python package
│   ├── one_piece_api_service.py # Dedicated service for One Piece API calls
│   ├── ann_api_service.py     # Dedicated service for AnimeNewsNetwork API calls
│   ├── gemini_llm_service.py  # Handles calls to Google Gemini API for text generation
│   └── ollama_llm_service.py  # Handles calls to Ollama for text generation (if used for generation and not just embedding)
│
├── embeddings/                # Manages embedding generation, storage, and retrieval
│   ├── __init__.py            # Makes 'embeddings' a Python package
│   ├── ollama_embedder.py     # Interface to use Ollama 'all-minilm:latest' for generating embeddings
│   └── vector_store.py        # Manages the storage (in-memory, for now) and similarity search of embeddings
│
├── data/                      # Optional: For caching fetched API responses or pre-generated embeddings persistently
│   ├── cached_news_articles.json  # Example: Store parsed news data
│   └── cached_one_piece_lore.json # Example: Store parsed One Piece lore data
│
└── utils/                     # General utility functions
    ├── __init__.py            # Makes 'utils' a Python package
    └── text_processing.py     # Helper functions, e.g., for cleaning text, chunking for LLM/embedding

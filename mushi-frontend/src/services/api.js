// mushi-frontend/src/services/api.js
import axios from 'axios';

// The base URL for your Flask backend, derived from your config.py
const API_BASE_URL = 'http://127.0.0.1:8001';

/**
 * Create a configured instance of axios.
 * This instance will be used for all API calls.
 */
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * A generic error handler to log errors and re-throw them for components to handle.
 * @param {string} context - The context of the API call (e.g., 'fetching LLM response').
 * @param {Error} error - The error object from axios.
 */
const handleError = (context, error) => {
  // Check if the error is due to request cancellation
  if (axios.isCancel(error)) {
    console.log('Request cancelled:', error.message);
    // You might choose not to throw an error here if cancellation is expected
    return; // Do not re-throw if it's a cancellation
  }
  const errorMessage = error.response?.data?.error || error.message;
  console.error(`Error ${context}:`, errorMessage);
  throw new Error(errorMessage);
};

// --- API Service Object ---
// Organizes all API calls into logical groups matching your backend controllers.
export const api = {
  /**
   * === LLM Endpoints ===
   * Interacts with the LLMController.
   * Routes: /api/llm/chat, /api/llm/providers, /api/llm/set-provider, /api/llm/suggest-questions
   */
  llm: {
    /**
     * Sends a query to the main chat endpoint.
     * @param {string} query - The user's message.
     * @param {AbortSignal} [signal] - Optional AbortSignal to cancel the request.
     * @returns {Promise<object>} The LLM's response.
     */
    chat: async (query, signal = null) => {
      try {
        const response = await apiClient.post('/api/llm/chat', { query }, { signal });
        return response.data;
      } catch (error) {
        handleError('fetching LLM response', error);
        if (axios.isCancel(error)) {
          return null;
        }
        throw error;
      }
    },
    /**
     * Gets the list of available LLM providers.
     * @returns {Promise<object>} The list of providers.
     */
    getProviders: async () => {
      try {
        const response = await apiClient.get('/api/llm/providers');
        return response.data;
      } catch (error) {
        handleError('fetching LLM providers', error);
      }
    },
    /**
     * Sets the active LLM provider.
     * @param {string} provider - The key of the provider to set (e.g., 'gemini' or 'ollama_anime').
     * @returns {Promise<object>} The confirmation message.
     */
    setProvider: async (provider) => {
      try {
        // The API endpoint expects a 'provider' key in the payload.
        const response = await apiClient.post('/api/llm/set-provider', { provider });
        return response.data;
      } catch (error) {
        handleError('setting LLM provider', error);
      }
    },
    /**
     * Gets the currently selected LLM provider from the backend.
     * @returns {Promise<object>} An object containing the current provider key (e.g., { current_provider: "ollama_anime" }).
     */
    getCurrentProvider: async () => {
      try {
        const response = await apiClient.get('/api/llm/current_provider');
        return response.data;
      } catch (error) {
        handleError('fetching current LLM provider', error);
      }
    },
     /**
     * Gets suggested follow-up questions from the LLM.
     * @param {string} lastResponseText - The last response text from the LLM (Mushi's answer).
     * @returns {Promise<{suggested_questions: string[], similar_anime_note?: string}>}
     * A structured object with a list of suggested questions and an optional similar anime note.
     */
    getSuggestedQuestions: async (lastResponseText) => {
        try {
            // Backend expects 'content' as the key for the last LLM response text
            const response = await apiClient.post('/api/llm/suggest-questions', { content: lastResponseText });
            return response.data; // This will now be { suggested_questions: [...], similar_anime_note: "..." }
        } catch (error) {
            handleError('fetching suggested questions', error);
            // Re-throw to allow component to handle fallback/error display
            throw error;
        }
    }
  },

  /**
   * === Data Endpoints ===
   * Interacts with the DataController (e.g., for clusters).
   * Routes: /api/data/clusters
   */
  data: {
    /**
     * Retrieves clustered document data.
     * @param {number} numClusters - The number of clusters to form.
     * @returns {Promise<object>} The clustered documents and cluster info.
     */
    getClusteredData: async (numClusters = 5) => {
      try {
        const response = await apiClient.get('/api/data/clusters', {
          params: { n_clusters: numClusters },
        });
        return response.data;
      } catch (error) {
        handleError('fetching clustered data', error);
      }
    },
    /**
     * Triggers data ingestion for all sources.
     * @returns {Promise<object>} Confirmation of ingestion.
     */
    ingestAllData: async () => {
      try {
        const response = await apiClient.post('/api/data/ingest_all_data');
        return response.data;
      } catch (error) {
        handleError('triggering all data ingestion', error);
      }
    },
    /**
     * Triggers ingestion for specific Anime API categories.
     * @param {string[]} categories - Array of categories (e.g., ['genre/action', 'top-airing']).
     * @param {number} limitPerCategory - Max items per category.
     * @returns {Promise<object>} Confirmation of ingestion.
     */
    ingestAnimeApiCategoryData: async (categories, limitPerCategory = 50) => {
      try {
        const categoriesStr = categories.join(',');
        const response = await apiClient.post('/api/data/ingest_anime_api_category_data', null, {
          params: { categories: categoriesStr, limit_per_category: limitPerCategory }
        });
        return response.data;
      } catch (error) {
        handleError('triggering anime API category ingestion', error);
      }
    }
  },

  /**
   * === Anime API Endpoints ===
   * Interacts with the AnimeController.
   * Routes: /api/anime/*
   */
  anime: {
    /**
     * Fetches home page data from the anime-api.
     * @returns {Promise<object>} Home page data (spotlights, trending, etc.).
     */
    getHomeData: async () => {
      try {
        const response = await apiClient.get('/api/anime/home');
        return response.data;
      } catch (error) {
        handleError('fetching anime home data', error);
      }
    },
    /**
     * Fetches top 10 anime data.
     * @returns {Promise<object>} Top 10 anime data.
     */
    getTopTen: async () => {
      try {
        const response = await apiClient.get('/api/anime/top-ten');
        return response.data;
      } catch (error) {
        handleError('fetching top ten anime', error);
      }
    },
    /**
     * Fetches top search anime data.
     * @param {number} [limit=20] - Number of results to limit.
     * @returns {Promise<object>} Top search anime data.
     */
    getTopSearch: async (limit = 20) => {
      try {
        const response = await apiClient.get('/api/anime/top-search', { params: { limit } });
        return response.data;
      } catch (error) {
        handleError('fetching top search anime', error);
      }
    },
    /**
     * Searches for anime.
     * @param {string} query - The search query.
     * @param {number} [page=1] - Page number for results.
     * @returns {Promise<object>} Search results.
     */
    search: async (query, page = 1) => {
      try {
        const response = await apiClient.get('/api/anime/search', { params: { q: query, page } });
        return response.data;
      } catch (error) {
        handleError('searching anime', error);
      }
    },
    /**
     * Fetches details for a specific anime.
     * @param {string} animeId - The ID of the anime.
     * @returns {Promise<object>} Anime details.
     */
    getDetails: async (animeId) => {
      try {
        const response = await apiClient.get(`/api/anime/details/${animeId}`);
        return response.data;
      } catch (error) {
        handleError('fetching anime details', error);
      }
    },
    /**
     * Fetches anime by category.
     * @param {string} category - The category name (e.g., 'genre/action').
     * @param {number} [page=1] - Page number for results.
     * @param {number} [limit=20] - Number of results per page.
     * @returns {Promise<object>} Anime list for the category.
     */
    getByCategory: async (category, page = 1, limit = 20) => {
      try {
        const response = await apiClient.get(`/api/anime/category/${category}`, { params: { page, limit } });
        return response.data;
      } catch (error) {
        handleError('fetching anime by category', error);
      }
    },
    /**
     * Fetches details for a specific character.
     * @param {string} characterId - The ID of the character.
     * @returns {Promise<object>} Character details.
     */
    getCharacterDetails: async (characterId) => {
      try {
        const response = await apiClient.get(`/api/anime/character/${characterId}`);
        return response.data;
      } catch (error) {
        handleError('fetching character details', error);
      }
    },
    /**
     * Fetches details for a specific voice actor.
     * @param {string} actorId - The ID of the voice actor.
     * @returns {Promise<object>} Voice actor details.
     */
    getVoiceActorDetails: async (actorId) => {
      try {
        const response = await apiClient.get(`/api/anime/actors/${actorId}`);
        return response.data;
      } catch (error) {
        handleError('fetching voice actor details', error);
      }
    },
     /**
     * Fetches Qtip information for a specific anime.
     * @param {number} qtipId - The ID of the Qtip.
     * @returns {Promise<object>} Qtip information.
     */
    getQtipInfo: async (qtipId) => {
      try {
        const response = await apiClient.get(`/api/anime/qtip/${qtipId}`);
        return response.data;
      } catch (error) {
        handleError('fetching Qtip info', error);
      }
    },
  },

  /**
   * === One Piece Endpoints ===
   * Interacts with the OnePieceController.
   * Routes: /api/one-piece/*
   */
  onePiece: {
    /**
     * Gets all One Piece sagas.
     * @returns {Promise<Array>} A list of sagas.
     */
    getSagas: async () => {
      try {
        const response = await apiClient.get('/api/one-piece/sagas');
        return response.data;
      } catch (error) {
        handleError('fetching One Piece sagas', error);
      }
    },
    /**
     * Gets all One Piece characters.
     * @returns {Promise<Array>} A list of characters.
     */
    getCharacters: async () => {
      try {
        const response = await apiClient.get('/api/one-piece/characters');
        return response.data;
      } catch (error) {
        handleError('fetching One Piece characters', error);
      }
    },
    /**
     * Gets all One Piece Devil Fruits.
     * @returns {Promise<Array>} A list of fruits.
     */
    getFruits: async () => {
      try {
        const response = await apiClient.get('/api/one-piece/fruits');
        return response.data;
      } catch (error) {
        handleError('fetching One Piece fruits', error);
      }
    },
    /**
     * Gets all One Piece Crews.
     * @returns {Promise<Array>} A list of crews.
     */
    getCrews: async () => {
        try {
            const response = await apiClient.get('/api/one-piece/crews');
            return response.data;
        } catch (error) {
            handleError('fetching One Piece crews', error);
        }
    },
    /**
     * Gets all One Piece Islands.
     * @returns {Promise<Array>} A list of islands.
     */
    getIslands: async () => {
        try {
            const response = await apiClient.get('/api/one-piece/islands');
            return response.data;
        } catch (error) {
            handleError('fetching One Piece islands', error);
        }
    }
  },
};

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
  if (axios.isCancel(error)) {
    console.log('Request cancelled:', error.message);
    return;
  }
  const errorMessage = error.response?.data?.error || error.message;
  console.error(`Error ${context}:`, errorMessage);
  throw new Error(errorMessage);
};

// --- API Service Object ---
export const api = {
  llm: {
    chat: async (query, onChunkReceived, signal) => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/llm/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query }),
                signal: signal,
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                const chunk = decoder.decode(value, { stream: true });
                onChunkReceived(chunk);
            }
        } catch (error) {
            if (error.name === 'AbortError') {
                console.log('Chat request aborted by user.');
            } else {
                handleError('fetching LLM response', error);
            }
            throw error;
        }
    },
    getProviders: async () => {
      try {
        const response = await apiClient.get('/api/llm/providers');
        return response.data;
      } catch (error) {
        handleError('fetching LLM providers', error);
      }
    },
    setProvider: async (providerKey) => {
      try {
        const response = await apiClient.post('/api/llm/set-provider', { provider: providerKey });
        return response.data;
      } catch (error) {
        handleError('setting LLM provider', error);
      }
    },
    getCurrentProvider: async () => {
      try {
        const response = await apiClient.get('/api/llm/current_provider');
        return response.data;
      } catch (error) {
        handleError('fetching current LLM provider', error);
      }
    },
    getSuggestedQuestions: async (content) => {
      try {
        const response = await apiClient.post('/api/llm/suggest-questions', { content });
        return response.data;
      } catch (error) {
        handleError('fetching suggested questions', error);
      }
    },
  },

  onePiece: {
    getArcs: async () => {
      try {
        const response = await apiClient.get('/api/one-piece/arcs');
        return response.data;
      } catch (error) {
        handleError('fetching One Piece arcs', error);
      }
    },
    getSagas: async () => {
      try {
        const response = await apiClient.get('/api/one-piece/sagas');
        return response.data;
      } catch (error) {
        handleError('fetching One Piece sagas', error);
      }
    },
    getCharacters: async () => {
      try {
        const response = await apiClient.get('/api/one-piece/characters');
        return response.data;
      } catch (error) {
        handleError('fetching One Piece characters', error);
      }
    },
    getFruits: async () => {
      try {
        const response = await apiClient.get('/api/one-piece/fruits');
        return response.data;
      } catch (error) {
        handleError('fetching One Piece fruits', error);
      }
    },
    getCrews: async () => {
        try {
            const response = await apiClient.get('/api/one-piece/crews');
            return response.data;
        } catch (error) {
            handleError('fetching One Piece crews', error);
        }
    },
    getIslands: async () => {
        try {
            const response = await apiClient.get('/api/one-piece/islands');
            return response.data;
        } catch (error) {
            handleError('fetching One Piece islands', error);
        }
    },
  },

  anime: {
    getHomeData: async () => {
      try {
        const response = await apiClient.get('/api/anime/home');
        return response.data;
      } catch (error) {
        handleError('fetching anime home data', error);
      }
    },
    getTopTen: async () => {
      try {
        const response = await apiClient.get('/api/anime/top-ten');
        return response.data;
      } catch (error) {
        handleError('fetching top ten anime', error);
      }
    },
    getTopSearch: async () => {
      try {
        const response = await apiClient.get('/api/anime/top-search');
        return response.data;
      } catch (error) {
        handleError('fetching top search anime', error);
      }
    },
    getDetails: async (animeId) => {
      try {
        const response = await apiClient.get(`/api/anime/details/${animeId}`);
        return response.data;
      } catch (error) {
        handleError(`fetching details for anime ID ${animeId}`, error);
      }
    },
    getByCategory: async (category, page = 1) => {
      try {
        const response = await apiClient.get(`/api/anime/category/${category}`, { params: { page } });
        return response.data;
      } catch (error) {
        handleError(`fetching anime for category '${category}'`, error);
      }
    },
    search: async (query, page = 1) => {
      try {
        const response = await apiClient.get(`/api/anime/search`, { params: { q: query, page } });
        return response.data;
      } catch (error) {
        handleError(`searching for anime with query '${query}'`, error);
      }
    },
    getSearchSuggestions: async (keyword) => {
      try {
        const response = await apiClient.get(`/api/anime/search-suggestions`, { params: { keyword } });
        return response.data;
      } catch (error) {
        handleError(`fetching search suggestions for '${keyword}'`, error);
      }
    },
    getCharacterDetails: async (characterId) => {
      try {
        const response = await apiClient.get(`/api/anime/character/${characterId}`);
        return response.data;
      } catch (error) {
        handleError(`fetching character details for ID ${characterId}`, error);
      }
    },
    getVoiceActorDetails: async (actorId) => {
      try {
        const response = await apiClient.get(`/api/anime/actors/${actorId}`);
        return response.data;
      } catch (error) {
        handleError(`fetching voice actor details for ID ${actorId}`, error);
      }
    },
    getQtipInfo: async (qtipId) => {
      try {
        const response = await apiClient.get(`/api/anime/qtip/${qtipId}`);
        return response.data;
      } catch (error) {
        handleError(`fetching Qtip info for ID ${qtipId}`, error);
      }
    },
    getAvailableServers: async (animeId, episodeDataId) => {
      try {
        const response = await apiClient.get(`/api/anime/servers/${animeId}`, { params: { ep: episodeDataId } });
        return response.data;
      } catch (error) {
        handleError(`fetching available servers for anime ID ${animeId}, episode ID ${episodeDataId}`, error);
      }
    },
    getStreamingInfo: async (episodeId, serverId, streamType) => {
      try {
        const response = await apiClient.get(`/api/anime/stream`, {
          params: {
            id: episodeId,
            server: serverId,
            type: streamType
          }
        });
        return response.data;
      } catch (error) {
        handleError(`fetching streaming info for episode ID ${episodeId}, server ${serverId}, type ${streamType}`, error);
      }
    },
  },

  data: {
    getClusteredData: async (numClusters = 5) => {
      try {
        const response = await apiClient.get('/api/data/clusters', { params: { n_clusters: numClusters } });
        return response.data;
      } catch (error) {
        handleError(`fetching clustered data with ${numClusters} clusters`, error);
      }
    },
    ingestAllData: async () => {
      try {
        const response = await apiClient.post('/api/data/ingest_all_data');
        return response.data;
      } catch (error) {
        handleError('ingesting all data', error);
      }
    },
    ingestAnimeApiCategoryData: async (categories, limit) => {
      try {
        const response = await apiClient.post('/api/data/ingest_anime_api_category_data', null, {
          params: { categories, limit_per_category: limit }
        });
        return response.data;
      } catch (error) {
        handleError(`ingesting category data for ${categories}`, error);
      }
    },
  },

  news: {
    getLatestNews: async () => {
      try {
        const response = await apiClient.get('/api/news/latest');
        return response.data;
      } catch (error) {
        handleError('fetching latest news', error);
      }
    },
    searchNews: async (query) => {
      try {
        const response = await apiClient.get(`/api/news/search?query=${encodeURIComponent(query)}`);
        return response.data;
      } catch (error) {
        handleError('searching news', error);
      }
    },
  },
};

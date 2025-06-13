# Mushi Backend API Specification for Frontend Service Generation

## Objective
This document provides a complete, robust, and structured specification for the Mushi backend API. The goal is to use this specification to generate a comprehensive `api.js` file for a frontend application. The generated file should export an asynchronous function for each endpoint defined below.

---
## Section 1: LLM API
**Base Path:** `/api/llm`
---

### 1.1 Endpoint: Chat with LLM
- **JS Function Name:** `chatWithLlm`
- **Description:** Sends a user's query to the backend for a RAG-enhanced LLM response.
- **Method:** `POST`
- **Full Path:** `/api/llm/chat`
- **Request Body (JSON):**
  ```json
  {
    "query": "string"
  }

  Success Response (200 OK):
  {
  "response": "string"
  }


  Error Response (4xx/5xx):
  {
  "error": "string"
  }

1.2 Endpoint: Suggest Follow-up Questions
JS Function Name: getSuggestedQuestions
Description: Generates follow-up questions based on the user's last input.
Method: POST
Full Path: /api/llm/suggest-questions
Request Body (JSON):

{
  "content": "string"
}

Success Response (200 OK):
{
  "suggested_questions": ["string", "string", "string"]
}

Error Response (4xx/5xx):
{
  "error": "string"
}

1.3 Endpoint: Get LLM Providers
JS Function Name: getLlmProviders
Description: Retrieves the list of available LLM providers.
Method: GET
Full Path: /api/llm/providers
Success Response (200 OK):
{
  "gemini": "Google Gemini (Cloud)",
  "ollama": "Ollama Qwen2.5 (Local)"
}

1.4 Endpoint: Set Active LLM Provider
JS Function Name: setLlmProvider
Description: Sets the active LLM provider on the backend.
Method: POST
Full Path: /api/llm/set-provider
Request Body (JSON):
{
  "provider": "string"
}
Use code with caution.
Json
Success Response (200 OK):
{
  "message": "string"
}
Use code with caution.
Json
Section 2: Data & Clustering API
Base Path: /api/data
2.1 Endpoint: Get Clustered Documents
JS Function Name: getClusteredData
Description: Performs K-Means clustering on all embedded documents.
Method: GET
Full Path: /api/data/clusters
Query Parameters:
name: n_clusters
type: number
status: optional
default: 5
Success Response (200 OK):
{
  "documents": [
    {
      "id": "string",
      "content": "string",
      "source": "string",
      "type": "string",
      "cluster_label": "number"
    }
  ],
  "cluster_info": {
    "centroids": "array",
    "n_clusters": "number"
  }
}
Use code with caution.
Json
Error Response (4xx/5xx):
{
  "error": "string",
  "details": "string"
}
Use code with caution.
Json
Section 3: Shikimori API
Base Path: /api/shikimori
3.1 Endpoint: Search Anime
JS Function Name: searchShikimoriAnime
Description: Searches for anime titles on Shikimori.
Method: GET
Full Path: /api/shikimori/anime/search
Query Parameters:
name: q, type: string, status: required
name: limit, type: number, status: optional, default: 10
Success Response (200 OK): Array<Object>
[{"id": "number", "name": "string", "russian_name": "string", "aired_year": "number | null", "poster_url": "string | null"}]
Use code with caution.
Json
3.2 Endpoint: Get Anime Details
JS Function Name: getShikimoriAnimeDetails
Description: Fetches detailed information for a specific anime.
Method: GET
Full Path: /api/shikimori/anime/<anime_id>
Path Parameters:
name: anime_id, type: number, status: required
Success Response (200 OK):
{"id": "number", "name": "string", "russian_name": "string", "kind": "string", "episodes": "number", "status": "string", "aired_date": "string | null", "released_date": "string | null", "poster_original_url": "string | null", "description_html": "string | null"}
Use code with caution.
Json
3.3 Endpoint: Get Recent Anime
JS Function Name: getRecentShikimoriAnime
Description: Fetches recently updated anime from Shikimori.
Method: GET
Full Path: /api/shikimori/anime/recent
Query Parameters:
name: limit, type: number, status: optional, default: 5
Success Response (200 OK): Array<Object>
[{"id": "number", "name": "string", "russian_name": "string", "aired_year": "number | null", "status": "string", "poster_url": "string | null"}]
Use code with caution.
Json
3.4 Endpoint: Search Manga
JS Function Name: searchShikimoriManga
Description: Searches for manga titles on Shikimori.
Method: GET
Full Path: /api/shikimori/manga/search
Query Parameters:
name: q, type: string, status: required
name: limit, type: number, status: optional, default: 10
Success Response (200 OK): Array<Object>
[{"id": "number", "name": "string", "russian_name": "string", "volumes": "number", "chapters": "number", "status": "string", "poster_url": "string | null"}]
Use code with caution.
Json
3.5 Endpoint: Get Recent Manga
JS Function Name: getRecentShikimoriManga
Description: Fetches recently updated manga from Shikimori.
Method: GET
Full Path: /api/shikimori/manga/recent
Query Parameters:
name: limit, type: number, status: optional, default: 5
Success Response (200 OK): Array<Object>
[{"id": "number", "name": "string", "russian_name": "string", "volumes": "number", "chapters": "number", "status": "string", "poster_url": "string | null"}]
Use code with caution.
Json
3.6 Endpoint: Search Characters
JS Function Name: searchShikimoriCharacters
Description: Searches for characters on Shikimori.
Method: GET
Full Path: /api/shikimori/characters/search
Query Parameters:
name: q, type: string, status: required
name: limit, type: number, status: optional, default: 10
Success Response (200 OK): Array<Object>
[{"id": "number", "name": "string", "russian_name": "string", "poster_url": "string | null"}]
Use code with caution.
Json
3.7 Endpoint: Get Character Details
JS Function Name: getShikimoriCharacterDetails
Description: Fetches detailed information for a specific character.
Method: GET
Full Path: /api/shikimori/characters/<character_id>
Path Parameters:
name: character_id, type: number, status: required
Success Response (200 OK):
{"id": "number", "name": "string", "russian_name": "string", "description_html": "string | null", "poster_url": "string | null"}
Use code with caution.
Json
3.8 Endpoint: Search People
JS Function Name: searchShikimoriPeople
Description: Searches for people (staff, voice actors) on Shikimori.
Method: GET
Full Path: /api/shikimori/people/search
Query Parameters:
name: q, type: string, status: required
name: limit, type: number, status: optional, default: 10
Success Response (200 OK): Array<Object>
[{"id": "number", "name": "string", "russian_name": "string", "poster_url": "string | null"}]
Use code with caution.
Json
3.9 Endpoint: Get Person Details
JS Function Name: getShikimoriPersonDetails
Description: Fetches detailed information for a specific person.
Method: GET
Full Path: /api/shikimori/people/<person_id>
Path Parameters:
name: person_id, type: number, status: required
Success Response (200 OK):
{"id": "number", "name": "string", "russian_name": "string", "website": "string | null", "poster_original_url": "string | null"}
Use code with caution.
Json
Section 4: Anime News Network (ANN) API
Base Path: /api/news
4.1 Endpoint: Search ANN Titles
JS Function Name: searchAnnTitles
Description: Searches for titles in the ANN encyclopedia.
Method: GET
Full Path: /api/news/ann/search
Query Parameters:
name: q, type: string, status: required
Success Response (200 OK): Array<Object>
[{"id": "string", "name": "string", "type": "string"}]
Use code with caution.
Json
4.2 Endpoint: Get ANN Title Details
JS Function Name: getAnnTitleDetails
Description: Fetches details for a specific ANN title.
Method: GET
Full Path: /api/news/ann/title/<title_id>
Path Parameters:
name: title_id, type: number, status: required
Success Response (200 OK):
{"id": "string", "type": "string", "genres": ["string"], "themes": ["string"], "staff": [{"task": "string", "person": "string", "person_id": "string"}], "episodes": "number | null", "vintage": "string | null", "main_title": "string", "alternative_titles": ["string"]}
Use code with caution.
Json
4.3 Endpoint: Get Recent ANN Items
JS Function Name: getRecentAnnItems
Description: Fetches recently added encyclopedia items from ANN.
Method: GET
Full Path: /api/news/ann/recent
Query Parameters:
name: limit, type: number, status: optional, default: 10
Success Response (200 OK): Array<Object>
[{"id": "string", "gid": "string", "type": "string", "name": "string", "precision": "string", "vintage": "string"}]
Use code with caution.
Json
Section 5: One Piece API
Base Path: /api/one-piece
5.1 Endpoint: Get Sagas
JS Function Name: getOnePieceSagas
Description: Fetches all One Piece sagas.
Method: GET
Full Path: /api/one-piece/sagas
Success Response (200 OK): Array<Object>
[{"id": "number", "title": "string", "number_of_arcs": "number"}]
Use code with caution.
Json
5.2 Endpoint: Get Characters
JS Function Name: getOnePieceCharacters
Description: Fetches all One Piece characters.
Method: GET
Full Path: /api/one-piece/characters
Success Response (200 OK): Array<Object>
[{"id": "number", "name": "string", "gender": "string", "status": "string"}]
Use code with caution.
Json
5.3 Endpoint: Get Devil Fruits
JS Function Name: getOnePieceFruits
Description: Fetches all One Piece Devil Fruits.
Method: GET
Full Path: /api/one-piece/fruits
Success Response (200 OK): Array<Object>
[{"id": "number", "name": "string", "type": "string", "description": "string"}]



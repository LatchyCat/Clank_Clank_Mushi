// src/components/anime/searchbar/Suggestion.jsx (NEW FILE)
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '@/src/services/api';

function Suggestion({ keyword }) {
  const [suggestions, setSuggestions] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!keyword) {
      setSuggestions([]);
      return;
    }

    setIsLoading(true);
    const fetchSuggestions = async () => {
      try {
        const data = await api.anime.getSearchSuggestions(keyword);
        // The API returns an object with a 'results' array
        setSuggestions(data?.results || []);
      } catch (error) {
        console.error("Failed to fetch search suggestions:", error);
        setSuggestions([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchSuggestions();
  }, [keyword]); // Depends on the debounced keyword

  if (isLoading) {
    return (
      <div className="absolute top-full mt-1 w-full bg-gray-800 border border-gray-700 rounded-lg shadow-lg p-4 text-center text-gray-400">
        Mushi is searching...
      </div>
    );
  }

  if (suggestions.length === 0) {
    return null; // Don't render if no suggestions
  }

  return (
    <div className="absolute top-full mt-1 w-full bg-gray-800 border border-gray-700 rounded-lg shadow-lg max-h-80 overflow-y-auto">
      <ul className="divide-y divide-gray-700">
        {suggestions.map((anime) => (
          <li key={anime.id}>
            <Link
              to={`/anime/details/${anime.id}`}
              className="flex items-center gap-4 p-3 hover:bg-purple-600/50 transition-colors"
            >
              <img src={anime.poster_url} alt={anime.title} className="w-10 h-14 object-cover rounded-md flex-shrink-0" />
              <div className="flex-grow">
                <p className="font-semibold text-white line-clamp-1">{anime.title}</p>
                <p className="text-sm text-gray-400">{anime.show_type}</p>
              </div>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Suggestion;

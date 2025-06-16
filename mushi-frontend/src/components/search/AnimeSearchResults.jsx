import React, { useState, useEffect } from 'react';
import { api } from '@/services/api';
import CategoryCard from '@/components/categorycard/CategoryCard'; // Reuse for consistent UI

function AnimeSearchResults({ query }) {
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!query) {
      setResults([]);
      return;
    }

    const performSearch = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await api.anime.search(query);
        // The API returns { results: [...], ... }
        setResults(data?.results || []);
      } catch (err) {
        setError(`Failed to fetch search results: ${err.message}`);
      } finally {
        setIsLoading(false);
      }
    };

    performSearch();
  }, [query]);

  if (isLoading) return <div className="text-center p-10 text-indigo-300 animate-pulse">Mushi is searching...</div>;
  if (error) return <div className="text-center p-10 text-red-400">{error}</div>;
  if (!query) return <div className="text-center text-gray-400 p-10">Use the search bar above to find an anime!</div>
  if (results.length === 0) return <div className="text-center text-gray-400 p-10">Mushi couldn't find any results for "{query}". Gomen'nasai! (T_T)</div>;

  return (
    <CategoryCard
      label={`Search Results for "${query}"`}
      data={results}
      showViewMore={false}
    />
  );
}

export default AnimeSearchResults;

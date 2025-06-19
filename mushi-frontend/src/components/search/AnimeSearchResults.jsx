// mushi-frontend/src/components/search/AnimeSearchResults.jsx
import React, { useState, useEffect } from 'react';
import { api } from '@/services/api';
import CategoryCard from '@/components/categorycard/CategoryCard';

function AnimeSearchResults({ filters }) {
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Re-run the search whenever the filters object changes
  useEffect(() => {
    const hasFilters = filters.keyword || (filters.genres && filters.genres.length > 0) || filters.type !== 'all' || filters.status !== 'all' || filters.rated !== 'all' || filters.score !== 'all' || filters.season !== 'all' || filters.language !== 'all' || filters.sort !== 'default';

    if (!hasFilters) {
      setResults([]);
      setError(null);
      return;
    }

    const performSearch = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await api.anime.search(filters);
        setResults(data?.results || []);
      } catch (err) {
        setError(`Failed to fetch search results: ${err.message}`);
        setResults([]);
      } finally {
        setIsLoading(false);
      }
    };

    performSearch();
  }, [filters]); // Dependency array now correctly watches the entire filters object

  if (isLoading) return <div className="text-center p-10 text-indigo-300 animate-pulse">Mushi is searching...</div>;
  if (error) return <div className="text-center p-10 text-red-400">{error}</div>;

  const queryLabel = filters.keyword ? `"${filters.keyword}"` : 'your filters';

  if (results.length === 0) {
    // Only show "no results" if a search was actually performed
     const hasFilters = filters.keyword || (filters.genres && filters.genres.length > 0) || filters.type !== 'all' || filters.status !== 'all';
    if(hasFilters) {
       return <div className="text-center text-gray-400 p-10">Mushi couldn't find any results for {queryLabel}. Gomen'nasai! (T_T)</div>;
    }
    return null; // Don't show anything if there are no filters and no results
  }

  return (
    <CategoryCard
      label={`Search Results for ${queryLabel}`}
      data={results}
      showViewMore={false}
      disableQtip={true}
    />
  );
}

export default AnimeSearchResults;

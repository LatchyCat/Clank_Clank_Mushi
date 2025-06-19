// mushi-frontend/src/views/AnimeSearchView.jsx
import React from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import PageSpecificSearchBar from '@/components/anime/searchbar/PageSpecificSearchBar';
import AnimeSearchResults from '@/components/search/AnimeSearchResults';
import FilterPanel from '@/components/search/FilterPanel'; // Import the new FilterPanel

function AnimeSearchView() {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  // Create a filters object from the current URL params
  const currentFilters = {
    keyword: searchParams.get('keyword') || '',
    genres: searchParams.getAll('genres'), // .getAll for multiple values
    type: searchParams.get('type') || 'all',
    status: searchParams.get('status') || 'all',
    rated: searchParams.get('rated') || 'all',
    score: searchParams.get('score') || 'all',
    season: searchParams.get('season') || 'all',
    language: searchParams.get('language') || 'all',
    sort: searchParams.get('sort') || 'default',
  };

  const handleFilterSubmit = (newFilters) => {
    const params = new URLSearchParams();

    // Always keep the keyword from the top search bar
    if (currentFilters.keyword) {
      params.set('keyword', currentFilters.keyword);
    }

    // Set new filter params, excluding 'all' or 'default' values
    Object.entries(newFilters).forEach(([key, value]) => {
      if (Array.isArray(value)) {
        value.forEach(v => params.append(key, v));
      } else if (value && value !== 'all' && value !== 'default') {
        params.set(key, value);
      }
    });

    // Use navigate to update the URL, which will trigger a re-render and re-fetch
    navigate(`/search?${params.toString()}`);
  };

  return (
    <div className="container mx-auto py-6 px-4 space-y-12">
      <PageSpecificSearchBar />
      <FilterPanel initialFilters={currentFilters} onFilterSubmit={handleFilterSubmit} />

      {/* AnimeSearchResults will now react to any change in searchParams */}
      <div className="mt-8">
        <AnimeSearchResults filters={currentFilters} />
      </div>
    </div>
  );
}

export default AnimeSearchView;

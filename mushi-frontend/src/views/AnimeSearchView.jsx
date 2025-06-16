// mushi-frontend/src/views/AnimeSearchView.jsx
import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import WebSearch from '@/components/anime/searchbar/WebSearch';
import AnimeSearchResults from '@/components/anime/search/AnimeSearchResults';

function AnimeSearchView() {
  const [searchParams] = useSearchParams();
  const [searchQuery, setSearchQuery] = useState(searchParams.get('keyword') || '');

  // This effect ensures the search results update if the URL changes
  useEffect(() => {
    setSearchQuery(searchParams.get('keyword') || '');
  }, [searchParams]);

  return (
    <div className="container mx-auto py-6">
      <h2 className="text-3xl font-extrabold text-white text-center mb-8">
        Search for Your Favorite Anime, Senpai! 🔍
      </h2>
      <div className="max-w-xl mx-auto mb-8">
        <WebSearch />
      </div>
      <AnimeSearchResults query={searchQuery} />
    </div>
  );
}

export default AnimeSearchView;

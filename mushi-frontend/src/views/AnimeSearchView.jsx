// mushi-frontend/src/views/AnimeSearchView.jsx
import React, { useState } from 'react';
import AnimeSearchBar from '../components/anime/search/AnimeSearchBar';
import AnimeSearchResults from '../components/anime/search/AnimeSearchResults';

/**
 * AnimeSearchView component provides a dedicated page for searching anime.
 * It combines the search input and search results display.
 */
function AnimeSearchView() {
  const [searchQuery, setSearchQuery] = useState(''); // State to hold the current search query

  // Callback function to handle search submission from AnimeSearchBar
  const handleSearch = (query) => {
    setSearchQuery(query); // Update the search query state
  };

  return (
    <div className="container mx-auto py-6">
      <h2 className="text-3xl font-extrabold text-white text-center mb-8">
        Search for Your Favorite Anime, Senpai! 🔍
      </h2>
      <div className="max-w-xl mx-auto mb-8">
        {/* AnimeSearchBar to get user input */}
        <AnimeSearchBar onSearch={handleSearch} />
      </div>

      {/* AnimeSearchResults to display results based on searchQuery */}
      <AnimeSearchResults query={searchQuery} />
    </div>
  );
}

export default AnimeSearchView;

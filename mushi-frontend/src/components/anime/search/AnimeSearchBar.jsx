// mushi-frontend/src/components/anime/search/AnimeSearchBar.jsx
import React, { useState } from 'react';
import { Search } from 'lucide-react'; // For the search icon

/**
 * AnimeSearchBar component provides an input field for anime search queries.
 * It takes an onSearch prop function which will be called with the query when submitted.
 *
 * @param {object} props
 * @param {(query: string) => void} props.onSearch - Callback function to execute search.
 * @param {string} [props.initialQuery=''] - Optional initial query for the search bar.
 */
function AnimeSearchBar({ onSearch, initialQuery = '' }) {
  const [query, setQuery] = useState(initialQuery);

  const handleSubmit = (e) => {
    e.preventDefault(); // Prevent default form submission behavior
    if (query.trim()) { // Only search if query is not empty
      onSearch(query.trim());
    } else {
      // Mushi thinks: Maybe give some feedback if the search bar is empty?
      console.log("Eeeh~ Senpai, Mushi needs something to search for! (•́-•̀)");
      // You could add a small visual cue to the user here.
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex items-center gap-2 bg-gray-800 p-3 rounded-full shadow-md">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search for anime, Senpai!~ ☆"
        className="flex-grow bg-transparent text-white placeholder-gray-400 focus:outline-none focus:ring-0"
        aria-label="Search anime"
      />
      <button
        type="submit"
        className="p-2 rounded-full bg-indigo-600 text-white hover:bg-indigo-700 transition-colors duration-200 flex items-center justify-center"
        aria-label="Submit search"
        title="Search"
      >
        <Search size={20} /> {/* Lucide search icon */}
      </button>
    </form>
  );
}

export default AnimeSearchBar;

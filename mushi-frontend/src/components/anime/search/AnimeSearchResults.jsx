// mushi-frontend/src/components/anime/search/AnimeSearchResults.jsx
import React, { useState, useEffect } from 'react';
import { api } from '../../../services/api'; // Correct path to api.js
import { ChevronLeft, ChevronRight } from 'lucide-react'; // For pagination icons

/**
 * AnimeSearchResults component fetches and displays search results for anime.
 * It also includes basic pagination.
 *
 * @param {object} props
 * @param {string} props.query - The search query to fetch results for.
 */
function AnimeSearchResults({ query }) {
  const [searchResults, setSearchResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Effect to fetch search results whenever the query or current page changes
  useEffect(() => {
    const fetchResults = async () => {
      if (!query.trim()) {
        setSearchResults(null); // Clear results if query is empty
        setTotalPages(1);
        return;
      }

      try {
        setIsLoading(true);
        setError(null); // Clear previous errors
        const data = await api.anime.search(query, currentPage); // Pass query and page

        if (data && data.results) {
          setSearchResults(data.results);
          // Assuming backend provides totalPages in the response for pagination
          setTotalPages(data.totalPages || 1); // Default to 1 if not provided
          console.log(`Mushi found results for "${query}" on page ${currentPage}, desu!~`, data.results);
        } else {
          setSearchResults([]); // Set to empty array if no results
          setTotalPages(1);
          setError("Eeeh~ Mushi couldn't find any results for that query, gomen'nasai! (T_T)");
        }
      } catch (err) {
        console.error("Uwaah! Failed to fetch search results:", err);
        setError(`Mushi encountered an error while searching: ${err.message || "Unknown error"} (>_<)`);
        setSearchResults([]); // Ensure results are empty on error
        setTotalPages(1);
      } finally {
        setIsLoading(false);
      }
    };

    fetchResults();
  }, [query, currentPage]); // Re-run effect when query or page changes

  const handleNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(prevPage => prevPage + 1);
    }
  };

  const handlePrevPage = () => {
    if (currentPage > 1) {
      setCurrentPage(prevPage => prevPage - 1);
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64 text-indigo-300 text-lg">
        Mushi is searching the whole anime world for you, Senpai! Waku waku!~ ☆
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-red-400 text-center p-4 border border-red-500 rounded-lg">
        Oh no! {error}
      </div>
    );
  }

  if (!searchResults || searchResults.length === 0) {
    if (!query.trim()) { // If query is empty, it's not "no results" but "no query yet"
      return (
        <div className="text-gray-400 text-center p-4">
          Please type something in the search bar, Senpai, and Mushi will find it! (´• ω •`)
        </div>
      );
    }
    return (
      <div className="text-gray-400 text-center p-4">
        Muu... Mushi couldn't find any anime matching "{query}". Gomen'nasai! (T_T)
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-900 text-gray-100">
      <h2 className="text-3xl font-extrabold text-white text-center mb-8">
        Mushi's Search Results for "{query}"! ✨
      </h2>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
        {searchResults.map((anime) => (
          <div key={anime.id} className="bg-gray-800 rounded-lg shadow-lg overflow-hidden transform hover:scale-105 transition-transform duration-300">
            <img
              src={anime.poster_url || 'https://placehold.co/150x220/333/FFF?text=No+Image'}
              alt={anime.title || 'Anime Poster'}
              className="w-full h-auto object-cover rounded-t-lg"
              onError={(e) => { e.target.onerror = null; e.target.src='https://placehold.co/150x220/333/FFF?text=Image+Error'; }}
            />
            <div className="p-3">
              <h4 className="text-white text-md font-semibold truncate">{anime.title}</h4>
              {anime.show_type && <p className="text-gray-400 text-sm">{anime.show_type}</p>}
              {/* You might want to add a link to details here later */}
              {/* <Link to={`/app/anime/details/${anime.id}`} className="text-indigo-400 hover:text-indigo-300 text-sm mt-1 inline-block">Details~</Link> */}
            </div>
          </div>
        ))}
      </div>

      {/* Pagination Controls */}
      {totalPages > 1 && (
        <div className="flex justify-center items-center gap-4 mt-8">
          <button
            onClick={handlePrevPage}
            disabled={currentPage === 1}
            className="p-2 rounded-full bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
            title="Previous Page"
          >
            <ChevronLeft size={20} />
          </button>
          <span className="text-gray-300 font-medium">Page {currentPage} of {totalPages}</span>
          <button
            onClick={handleNextPage}
            disabled={currentPage === totalPages}
            className="p-2 rounded-full bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
            title="Next Page"
          >
            <ChevronRight size={20} />
          </button>
        </div>
      )}
    </div>
  );
}

export default AnimeSearchResults;

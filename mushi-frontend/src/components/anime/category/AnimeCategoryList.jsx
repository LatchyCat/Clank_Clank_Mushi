// mushi-frontend/src/components/anime/category/AnimeCategoryList.jsx
import React, { useState, useEffect } from 'react';
import { api } from '../../../services/api'; // Correct path to api.js
import { ChevronLeft, ChevronRight } from 'lucide-react'; // For pagination icons
import { Link } from 'react-router-dom'; // For linking to anime details

/**
 * AnimeCategoryList component fetches and displays a list of anime for a specific category.
 * It includes pagination controls.
 *
 * @param {object} props
 * @param {string} props.category - The category slug to fetch anime for (e.g., 'genre/action', 'top-airing').
 * @param {string} [props.categoryTitle] - Optional human-readable title for the category (e.g., 'Action Anime').
 */
function AnimeCategoryList({ category, categoryTitle = "Category" }) {
  const [animeList, setAnimeList] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    const fetchCategoryAnime = async () => {
      if (!category) {
        setError("Eeeh~ Senpai, Mushi needs a category to find anime! (•́-•̀)");
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        setError(null); // Clear previous errors
        const data = await api.anime.getByCategory(category, currentPage); // Fetch anime for the category

        if (data && data.data) { // Ensure 'data' key exists for the list of anime
          setAnimeList(data.data);
          setTotalPages(data.total_pages || 1); // Get total pages for pagination
          console.log(`Mushi found sparkling anime for category "${category}" on page ${currentPage}, desu!~`, data.data);
        } else {
          setAnimeList([]); // Set to empty array if no results
          setTotalPages(1);
          setError(`Muu... Mushi couldn't find any anime in the "${categoryTitle}" category. (T_T)`);
        }
      } catch (err) {
        console.error(`Uwaah! Failed to fetch anime for category "${category}":`, err);
        setError(`Mushi encountered an error while fetching "${categoryTitle}" anime: ${err.message || "Unknown error"} (>_<)`);
        setAnimeList([]); // Ensure list is empty on error
        setTotalPages(1);
      } finally {
        setIsLoading(false);
      }
    };

    fetchCategoryAnime();
  }, [category, currentPage, categoryTitle]); // Re-run effect when category or page changes

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
        Mushi is collecting all the adorable anime in the "{categoryTitle}" category for you, Senpai! Waku waku!~ ☆
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

  if (!animeList || animeList.length === 0) {
    return (
      <div className="text-gray-400 text-center p-4">
        Muu... No anime found in the "{categoryTitle}" category. (T_T)
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-900 text-gray-100 min-h-screen">
      <h2 className="text-3xl font-extrabold text-white text-center mb-8">
        {categoryTitle} Anime List! ✨
      </h2>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
        {animeList.map((anime) => (
          <div key={anime.id} className="bg-gray-800 rounded-lg shadow-lg overflow-hidden transform hover:scale-105 transition-transform duration-300">
            <Link to={`/app/anime/details/${anime.id}`}> {/* Link to AnimeDetailView */}
              <img
                src={anime.poster_url || 'https://placehold.co/150x220/333/FFF?text=No+Image'}
                alt={anime.title || 'Anime Poster'}
                className="w-full h-auto object-cover rounded-t-lg"
                onError={(e) => { e.target.onerror = null; e.target.src='https://placehold.co/150x220/333/FFF?text=Image+Error'; }}
              />
              <div className="p-3">
                <h4 className="text-white text-md font-semibold truncate">{anime.title}</h4>
                {anime.show_type && <p className="text-gray-400 text-sm">{anime.show_type}</p>}
                {anime.adult_content && <span className="text-red-400 text-xs font-bold">18+</span>}
              </div>
            </Link>
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

export default AnimeCategoryList;

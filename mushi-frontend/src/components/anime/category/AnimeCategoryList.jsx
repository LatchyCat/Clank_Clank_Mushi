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
        const data = await api.anime.getByCategory(category, currentPage); // Pass category and page

        // CORRECTED: Access data.results.data for the anime list and data.results.totalPages
        if (data && data.data) { // Check if data and data.data exist
          setAnimeList(data.data); // Set animeList to data.data (the actual array of anime)
          setTotalPages(data.totalPages || 1); // Get totalPages from data.totalPages
          console.log(`Mushi found anime for category '${category}' on page ${currentPage}, desu!~`, data.data);
        } else {
          setError("Muu... Mushi couldn't find anime for that category. Gomen'nasai! (T_T)");
        }
      } catch (err) {
        console.error(`Uwaah! Failed to fetch anime for category '${category}' on page ${currentPage}:`, err);
        setError(`Mushi encountered an error while fetching category data: ${err.message || "Unknown error"} (>_<)`);
      } finally {
        setIsLoading(false);
      }
    };

    fetchCategoryAnime();
  }, [category, currentPage]); // Re-run effect when category or currentPage changes

  const handlePrevPage = () => {
    setCurrentPage((prev) => Math.max(1, prev - 1));
  };

  const handleNextPage = () => {
    setCurrentPage((prev) => Math.min(totalPages, prev + 1));
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-60 text-indigo-300 text-lg
                      bg-white/5 backdrop-blur-sm rounded-3xl shadow-inner border border-purple-500/30">
        Mushi is fetching {categoryTitle} anime! Waku waku!~ ☆
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-red-400 text-center p-6 border border-red-500 rounded-lg bg-red-900/30 text-lg mx-auto max-w-lg shadow-lg">
        Oh no! {error}
      </div>
    );
  }

  if (!animeList || animeList.length === 0) {
    return (
      <div className="text-gray-400 text-center p-6 text-lg mx-auto max-w-lg
                      bg-white/5 backdrop-blur-sm rounded-3xl shadow-inner border border-gray-700/50">
        Muu... No anime found for {categoryTitle}. (T_T)
      </div>
    );
  }

  return (
    <div className="p-6 text-gray-100">
      <h2 className="text-4xl font-extrabold text-center mb-10
                     bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-purple-600
                     drop-shadow-lg [text-shadow:0_0_15px_rgba(150,100,255,0.4)]">
        {categoryTitle}
      </h2>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-6">
        {animeList.map((anime) => (
          <div key={anime.id} className="bg-white/5 backdrop-blur-md rounded-xl shadow-lg overflow-hidden
                                        transform hover:scale-105 transition-transform duration-300
                                        border border-white/10 hover:border-indigo-500">
            <Link to={`/app/anime/details/${anime.id}`} className="block">
              <img
                src={anime.poster_url || 'https://placehold.co/150x220/333/FFF?text=No+Image'}
                alt={anime.title}
                className="w-full h-auto object-cover rounded-t-xl"
                onError={(e) => { e.target.onerror = null; e.target.src='https://placehold.co/150x220/333/FFF?text=Image+Error'; }}
              />
              <div className="p-4">
                <h4 className="text-white text-lg font-semibold truncate mb-1">{anime.title}</h4>
                {anime.show_type && <p className="text-gray-400 text-sm">{anime.show_type}</p>}
                {anime.adult_content && <span className="text-red-400 text-xs font-bold mt-1 inline-block">18+</span>}
                {anime.score && (
                  <p className="text-yellow-400 text-sm mt-1 flex items-center">
                    <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.538 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.783.57-1.838-.197-1.538-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.929 8.72c-.783-.57-.38-1.81.588-1.81h3.462a1 1 0 00.95-.69l1.07-3.292z" />
                    </svg>
                    {anime.score.toFixed(2)}
                  </p>
                )}
              </div>
            </Link>
          </div>
        ))}
      </div>

      {/* Pagination Controls */}
      {totalPages > 1 && (
        <div className="flex justify-center items-center gap-4 mt-10">
          <button
            onClick={handlePrevPage}
            disabled={currentPage === 1}
            className="p-3 rounded-full bg-purple-600 text-white hover:bg-purple-700
                       disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200
                       shadow-lg hover:shadow-xl"
            title="Previous Page"
          >
            <ChevronLeft size={24} />
          </button>
          <span className="text-gray-300 font-medium text-lg">Page {currentPage} of {totalPages}</span>
          <button
            onClick={handleNextPage}
            disabled={currentPage === totalPages}
            className="p-3 rounded-full bg-purple-600 text-white hover:bg-purple-700
                       disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200
                       shadow-lg hover:shadow-xl"
            title="Next Page"
          >
            <ChevronRight size={24} />
          </button>
        </div>
      )}
    </div>
  );
}

export default AnimeCategoryList;

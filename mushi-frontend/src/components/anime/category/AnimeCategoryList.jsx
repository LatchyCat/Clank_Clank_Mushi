// mushi-frontend/src/components/anime/category/AnimeCategoryList.jsx
import React, { useState, useEffect } from 'react';
import { api } from '../../../services/api';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import CategoryCard from '@/components/categorycard/CategoryCard';

/**
 * AnimeCategoryList component fetches and displays a list of anime for a specific category.
 * It now uses the reusable CategoryCard component for display and includes pagination controls.
 *
 * @param {object} props
 * @param {string} props.category - The category slug to fetch anime for (e.g., 'genre/action', 'top-airing').
 * @param {string} [props.categoryTitle] - Optional human-readable title for the category (e.g., 'Action Anime').
 */
function AnimeCategoryList({ category, categoryTitle = "Category Results" }) {
  const [animeList, setAnimeList] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    // Reset page to 1 whenever the category changes
    setCurrentPage(1);
  }, [category]);

  useEffect(() => {
    const fetchCategoryAnime = async () => {
      if (!category) {
        setError("Eeeh~ Senpai, Mushi needs a category to find anime! (•́-•̀)");
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        setError(null);
        // Pass category and current page to the API
        const data = await api.anime.getByCategory(category, currentPage);

        if (data && data.data) {
          setAnimeList(data.data);
          setTotalPages(data.totalPages || 1);
          console.log(`Mushi found anime for category '${category}' on page ${currentPage}, desu!~`, data.data);
        } else {
          setAnimeList([]); // Set to empty list on failure
          setTotalPages(1);
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

  if (isLoading && animeList === null) { // Only show full-screen loader on initial load
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

  // Display message if there are no results after loading
  if (!isLoading && (!animeList || animeList.length === 0)) {
    return (
      <div className="text-gray-400 text-center p-6 text-lg mx-auto max-w-lg
                      bg-white/5 backdrop-blur-sm rounded-3xl shadow-inner border border-gray-700/50">
        Muu... No anime found for {categoryTitle}. (T_T)
      </div>
    );
  }

  return (
    <div className="p-1 md:p-6 text-gray-100">
      <CategoryCard
        label={isLoading ? 'Loading...' : categoryTitle} // Use a dynamic label
        data={animeList || []} // Pass an empty array if animeList is null during pagination
        showViewMore={false}
      />

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

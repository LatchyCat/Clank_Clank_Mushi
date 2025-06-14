// mushi-frontend/src/views/AnimeCategoryView.jsx
import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom'; // For URL params/navigation
import AnimeCategoryList from '../components/anime/category/AnimeCategoryList';
import { api } from '../services/api'; // To fetch available genres/categories

/**
 * AnimeCategoryView component allows users to browse anime by category.
 * It displays a list of clickable categories and shows the selected category's anime.
 */
function AnimeCategoryView() {
  const navigate = useNavigate();
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);

  // Get category from URL query parameter, default to 'top-airing' if not present
  const initialCategory = queryParams.get('category') || 'top-airing';
  const initialCategoryTitle = queryParams.get('title') || 'Top Airing';

  const [selectedCategory, setSelectedCategory] = useState(initialCategory);
  const [selectedCategoryTitle, setSelectedCategoryTitle] = useState(initialCategoryTitle);
  const [availableCategories, setAvailableCategories] = useState([]);
  const [isLoadingCategories, setIsLoadingCategories] = useState(true);
  const [categoriesError, setCategoriesError] = useState(null);

  // Define some common categories to display for easy navigation
  // These are slugs from the backend's AnimeAPIService
  const commonCategories = [
    { slug: 'top-airing', title: 'Top Airing' },
    { slug: 'most-popular', title: 'Most Popular' },
    { slug: 'completed', title: 'Completed' },
    { slug: 'movie', title: 'Movies' },
    { slug: 'tv', title: 'TV Series' },
    { slug: 'genre/action', title: 'Action' },
    { slug: 'genre/comedy', title: 'Comedy' },
    { slug: 'genre/fantasy', title: 'Fantasy' },
    { slug: 'genre/adventure', title: 'Adventure' },
    { slug: 'genre/sci-fi', title: 'Sci-Fi' },
    { slug: 'genre/drama', title: 'Drama' },
    { slug: 'genre/slice-of-life', title: 'Slice of Life' },
    { slug: 'genre/thriller', title: 'Thriller' },
    { slug: 'genre/supernatural', title: 'Supernatural' },
    { slug: 'genre/romance', title: 'Romance' },
    { slug: 'genre/mystery', title: 'Mystery' },
  ];

  useEffect(() => {
    // We can potentially fetch dynamic categories later, but for now, use a predefined list.
    // If you enable getHomeData() here, remember to handle its loading/error states.
    // For now, Mushi will just use a predefined list to make it easier, desu!~
    setAvailableCategories(commonCategories);
    setIsLoadingCategories(false);

    // Update state if URL parameters change from external navigation
    const currentCategoryFromUrl = queryParams.get('category');
    const currentTitleFromUrl = queryParams.get('title');
    if (currentCategoryFromUrl && currentCategoryFromUrl !== selectedCategory) {
      setSelectedCategory(currentCategoryFromUrl);
      setSelectedCategoryTitle(currentTitleFromUrl || currentCategoryFromUrl.replace('genre/', '').replace('-', ' ').split('/').pop().split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' '));
    }
  }, [location.search, selectedCategory]); // Depend on location.search to react to URL changes

  const handleCategorySelect = (categorySlug, categoryTitle) => {
    setSelectedCategory(categorySlug);
    setSelectedCategoryTitle(categoryTitle);
    // Update URL to reflect the selected category, which is good for sharing!
    navigate(`/app/anime_category?category=${categorySlug}&title=${encodeURIComponent(categoryTitle)}`);
  };

  if (isLoadingCategories) {
    return (
      <div className="flex justify-center items-center h-64 text-indigo-300 text-lg">
        Mushi is loading all the sparkling categories for you, Senpai! Waku waku!~ ☆
      </div>
    );
  }

  if (categoriesError) {
    return (
      <div className="text-red-400 text-center p-4 border border-red-500 rounded-lg">
        Oh no! {categoriesError}
      </div>
    );
  }

  return (
    <div className="container mx-auto py-6">
      <h2 className="text-3xl font-extrabold text-white text-center mb-8">
        Browse Anime by Category, Senpai! ✨
      </h2>

      {/* Category selection buttons */}
      <div className="flex flex-wrap justify-center gap-3 mb-8 p-4 bg-gray-800 rounded-lg shadow-lg">
        {availableCategories.map((cat) => (
          <button
            key={cat.slug}
            onClick={() => handleCategorySelect(cat.slug, cat.title)}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-colors duration-200
              ${selectedCategory === cat.slug
                ? 'bg-indigo-600 text-white shadow-md'
                : 'bg-gray-700 text-gray-300 hover:bg-indigo-500 hover:text-white'
              }`}
          >
            {cat.title}
          </button>
        ))}
      </div>

      {/* Display AnimeCategoryList for the selected category */}
      {selectedCategory && (
        <AnimeCategoryList category={selectedCategory} categoryTitle={selectedCategoryTitle} />
      )}
      {!selectedCategory && (
        <div className="text-gray-400 text-center p-4">
          Please select a category above, Senpai! Mushi is ready to help! (´• ω •`)
        </div>
      )}
    </div>
  );
}

export default AnimeCategoryView;
